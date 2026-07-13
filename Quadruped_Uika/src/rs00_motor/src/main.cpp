#include "motor_ros2/motor_cfg.h"
#include "motor_ros2/motor_config.h"
#include "interfaces/msg/motor_command12.hpp"
#include "interfaces/msg/motor_feedback12.hpp"
#include "stdint.h"
#include <std_msgs/msg/empty.hpp>
#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <memory>
#include <mutex>
#include <rclcpp/node.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <thread>
#include <unistd.h>
#include <vector>

const auto COMMAND_PERIOD = std::chrono::milliseconds(5);
const auto FEEDBACK_PERIOD = std::chrono::milliseconds(5);
const auto DIAG_LOG_PERIOD = std::chrono::seconds(1);
constexpr int ENABLE_MAX_ATTEMPTS = 5;
const auto ENABLE_CONFIRM_TIMEOUT = std::chrono::milliseconds(100);
const auto ENABLE_STATUS_POLL_PERIOD = std::chrono::milliseconds(5);
const auto FEEDBACK_STALE_TIMEOUT = std::chrono::milliseconds(100);
// ==================================================================


namespace {

using Command12 = interfaces::msg::MotorCommand12;
using Command = interfaces::msg::MotorCommand;
using Feedback12 = interfaces::msg::MotorFeedback12;
using Feedback = interfaces::msg::MotorFeedback;

const std::array<Command Command12::*, rs00_motor::kMotorCount> kCommandFields = {{
    &Command12::fl_hip, &Command12::fl_thigh, &Command12::fl_calf,
    &Command12::fr_hip, &Command12::fr_thigh, &Command12::fr_calf,
    &Command12::rl_hip, &Command12::rl_thigh, &Command12::rl_calf,
    &Command12::rr_hip, &Command12::rr_thigh, &Command12::rr_calf,
}};

const std::array<Feedback Feedback12::*, rs00_motor::kMotorCount> kFeedbackFields = {{
    &Feedback12::fl_hip, &Feedback12::fl_thigh, &Feedback12::fl_calf,
    &Feedback12::fr_hip, &Feedback12::fr_thigh, &Feedback12::fr_calf,
    &Feedback12::rl_hip, &Feedback12::rl_thigh, &Feedback12::rl_calf,
    &Feedback12::rr_hip, &Feedback12::rr_thigh, &Feedback12::rr_calf,
}};

}  // namespace

class MotorControlSample : public rclcpp::Node {
public:
  MotorControlSample()
      : rclcpp::Node("motor_control_set_node"),
        received_first_command_(false) {

    const auto &configs = rs00_motor::motor_configs();
    motors_.reserve(configs.size());
    motor_initialized_.assign(configs.size(), false);
    motor_enabled_.assign(configs.size(), false);
    for (const auto &cfg : configs) {
      motors_.push_back(std::make_unique<RobStrideMotor>(
          cfg.can_iface, cfg.master_id, cfg.motor_id, cfg.actuator_type));
    }

    // 依次初始化每个电机，跳过失败的
    size_t initialized_count = 0;
    for (size_t i = 0; i < motors_.size(); ++i) {
      if (!rclcpp::ok() || !running_) {
        break;
      }
      try {
        std::lock_guard<std::mutex> lock(motors_mutex_);
        motors_[i]->Get_RobStrite_Motor_parameter(0x7005);
        usleep(1000);
        // 启动节点时先清故障并确保电机不使能，避免电机追随上一次内部目标位置。
        motors_[i]->Disenable_Motor(1);
        usleep(1000);
        motors_[i]->Set_RobStrite_Motor_parameter(0X7005, move_control_mode, Set_mode);
        usleep(1000);
        motors_[i]->Get_RobStrite_Motor_parameter(0x7005);
        usleep(1000);
        motor_initialized_[i] = true;
        initialized_count++;
        const auto [error_code, pattern, run_mode] = motors_[i]->return_status();
        RCLCPP_INFO(this->get_logger(),
                    "Motor %zu init status: error=%u pattern=%u run_mode=%u",
                    i, error_code, pattern, run_mode);
      } catch (const std::exception &e) {
        RCLCPP_WARN(this->get_logger(), "Motor %zu init failed: %s", i,
                    e.what());
      }
    }
    RCLCPP_INFO(this->get_logger(), "Motor init finished: %zu/%zu initialized, all disabled",
                initialized_count, motors_.size());

    // 创建电机反馈发布者
    feedback_pub_ = this->create_publisher<interfaces::msg::MotorFeedback12>("/motor_feedback", 10);

    // 创建定时器，按 200Hz 发布一次反馈。
    feedback_timer_ = this->create_wall_timer(
        FEEDBACK_PERIOD,
        [this]() {
          this->publish_feedback();
        });

    // 创建电机命令订阅
    command_sub_ = this->create_subscription<interfaces::msg::MotorCommand12>(
        "/motor_command", 10,
        [this](const interfaces::msg::MotorCommand12::SharedPtr msg) {
          this->command_callback(msg);
        });

    set_zero_sub_ = this->create_subscription<std_msgs::msg::Empty>(
        "/motor_set_zero", 10,
        [this](const std_msgs::msg::Empty::SharedPtr) {
          this->request_set_zero();
        });

    RCLCPP_INFO(this->get_logger(),
                "Ready: feedback=/motor_feedback, command=/motor_command, zero=/motor_set_zero");

    worker_thread_ = std::thread(&MotorControlSample::excute_loop, this);
  }

  ~MotorControlSample() {
    {
      std::lock_guard<std::mutex> lock(worker_wait_mutex_);
      running_ = false;
    }
    worker_cv_.notify_all();
    if (worker_thread_.joinable())
      worker_thread_.join();
    std::lock_guard<std::mutex> lock(motors_mutex_);
    for (size_t i = 0; i < motors_.size(); ++i) {
      if (!motor_initialized_[i]) {
        continue;
      }
      try {
        motors_[i]->Disenable_Motor(0);
      } catch (const std::exception &) {
      }
    }
  }

private:
  float clamp_position(size_t motor_index, float position) const {
    return rs00_motor::clamp_position(motor_index, position);
  }

  void command_callback(const interfaces::msg::MotorCommand12::SharedPtr msg) {
    {
      std::lock_guard<std::mutex> lock(command_mutex_);
      latest_command_ = *msg;
    }
    {
      std::lock_guard<std::mutex> lock(worker_wait_mutex_);
      received_first_command_ = true;
    }
    worker_cv_.notify_one();
    RCLCPP_INFO_ONCE(this->get_logger(), "First command received! Starting motor control.");
  }

  void request_set_zero() {
    {
      std::lock_guard<std::mutex> lock(worker_wait_mutex_);
      set_zero_requested_.store(true);
    }
    worker_cv_.notify_one();
    RCLCPP_WARN(this->get_logger(), "Manual motor zero requested");
  }

  void publish_feedback() {
    auto msg = interfaces::msg::MotorFeedback12();
    msg.header.stamp = this->now();
    msg.header.frame_id = "motor_feedback";

    const auto &transforms = rs00_motor::joint_transforms();
    const auto feedback_now = std::chrono::steady_clock::now();
    for (size_t i = 0; i < motors_.size(); ++i) {
      if (!motor_initialized_[i]) {
        continue;
      }
      const auto snapshot = motors_[i]->feedback_snapshot();
      if (received_first_command_ &&
          (snapshot.received_at == std::chrono::steady_clock::time_point{} ||
           feedback_now - snapshot.received_at > FEEDBACK_STALE_TIMEOUT)) {
        RCLCPP_WARN_THROTTLE(
            this->get_logger(), *this->get_clock(), 1000,
            "Motor %zu feedback stale; skipping /motor_feedback publish", i);
        return;
      }

      auto &feedback = msg.*kFeedbackFields[i];
      const auto &transform = transforms[i];
      feedback.torque = snapshot.torque * transform.feedback_torque_scale;
      feedback.position = snapshot.position * transform.feedback_position_scale;
      feedback.velocity = snapshot.velocity * transform.feedback_velocity_scale;
      feedback.temperature = snapshot.temperature;
    }

    feedback_pub_->publish(msg);
  }

  void enable_initialized_motors() {
    std::lock_guard<std::mutex> lock(motors_mutex_);
    for (size_t i = 0; i < motors_.size(); ++i) {
      if (!motor_initialized_[i] || motor_enabled_[i]) {
        continue;
      }
      try {
        motor_enabled_[i] = enable_motor_with_retry(i);
      } catch (const std::exception &e) {
        RCLCPP_WARN(this->get_logger(), "Motor %zu enable failed: %s", i, e.what());
      }
    }
  }

  bool is_enabled_status(uint8_t error_code, uint8_t pattern) const {
    return error_code == 0 && pattern == 2;
  }

  std::tuple<uint8_t, uint8_t, uint8_t> wait_for_enabled_status(size_t motor_index,
                                                                std::chrono::milliseconds timeout) {
    auto status = motors_[motor_index]->return_status();
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
      status = motors_[motor_index]->return_status();
      const auto [error_code, pattern, run_mode] = status;
      (void)run_mode;
      if (is_enabled_status(error_code, pattern)) {
        break;
      }
      std::this_thread::sleep_for(ENABLE_STATUS_POLL_PERIOD);
    }
    return status;
  }

  bool enable_motor_with_retry(size_t motor_index) {
    std::tuple<uint8_t, uint8_t, uint8_t> status{0, 0, 0};
    for (int attempt = 1; attempt <= ENABLE_MAX_ATTEMPTS; ++attempt) {
      const auto [pre_error, pre_pattern, pre_run_mode] =
          motors_[motor_index]->return_status();
      if (attempt > 1 || pre_error != 0) {
        RCLCPP_WARN(this->get_logger(),
                    "Motor %zu enable attempt %d/%d: clearing fault before retry "
                    "(previous error=%u pattern=%u run_mode=%u)",
                    motor_index, attempt, ENABLE_MAX_ATTEMPTS,
                    pre_error, pre_pattern, pre_run_mode);
      }

      motors_[motor_index]->Disenable_Motor(1);
      usleep(2000);
      motors_[motor_index]->Set_RobStrite_Motor_parameter(0X7005, move_control_mode, Set_mode);
      usleep(2000);
      motors_[motor_index]->enable_motor();

      status = wait_for_enabled_status(motor_index, ENABLE_CONFIRM_TIMEOUT);
      const auto [error_code, pattern, run_mode] = status;
      if (is_enabled_status(error_code, pattern)) {
        RCLCPP_INFO(this->get_logger(),
                    "Motor %zu enabled after attempt %d/%d: error=%u pattern=%u run_mode=%u",
                    motor_index, attempt, ENABLE_MAX_ATTEMPTS,
                    error_code, pattern, run_mode);
        return true;
      }

      RCLCPP_WARN(this->get_logger(),
                  "Motor %zu enable attempt %d/%d not confirmed: "
                  "error=%u pattern=%u run_mode=%u",
                  motor_index, attempt, ENABLE_MAX_ATTEMPTS,
                  error_code, pattern, run_mode);
      motors_[motor_index]->Disenable_Motor(1);
      usleep(5000);
    }

    const auto [error_code, pattern, run_mode] = status;
    RCLCPP_ERROR(this->get_logger(),
                 "Motor %zu enable failed after %d attempts; motor will be skipped "
                 "until rs00_motor is restarted. Last status: error=%u pattern=%u run_mode=%u",
                 motor_index, ENABLE_MAX_ATTEMPTS,
                 error_code, pattern, run_mode);
    return false;
  }

  void set_zero_all_motors() {
    RCLCPP_WARN(this->get_logger(), "Setting current position as zero for all initialized motors");
    std::lock_guard<std::mutex> lock(motors_mutex_);
    for (size_t i = 0; i < motors_.size(); ++i) {
      if (!motor_initialized_[i]) {
        continue;
      }
      try {
        motors_[i]->Set_ZeroPos();
        usleep(1000);
        motors_[i]->Disenable_Motor(0);
        usleep(1000);
        motor_enabled_[i] = false;
        RCLCPP_WARN(this->get_logger(), "Motor %zu zeroed and disabled", i);
      } catch (const std::exception &e) {
        RCLCPP_WARN(this->get_logger(), "Motor %zu zero failed: %s", i, e.what());
      }
    }
  }

  void excute_loop() {
    while (rclcpp::ok() && running_) {
      // 等待接收第一个命令，同时允许手柄触发手动定零。
      while (rclcpp::ok() && running_ && !received_first_command_) {
        std::unique_lock<std::mutex> lock(worker_wait_mutex_);
        worker_cv_.wait(lock, [this]() {
          return !rclcpp::ok() || !running_ || received_first_command_ ||
                 set_zero_requested_.load();
        });
        lock.unlock();
        if (set_zero_requested_.exchange(false)) {
          set_zero_all_motors();
        }
      }

      if (!rclcpp::ok() || !running_) {
        return;
      }

      RCLCPP_INFO(this->get_logger(), "Start sending motion commands");
      enable_initialized_motors();

      auto next_tick = std::chrono::steady_clock::now();
      auto last_diag_log = next_tick;
      size_t send_loops = 0;
      auto max_send_duration = std::chrono::steady_clock::duration::zero();

      while (rclcpp::ok() && running_ && received_first_command_) {
        if (set_zero_requested_.exchange(false)) {
          // Clear the old command before zeroing. A command received while the
          // zero operation is running will set this flag again and is retained.
          {
            std::lock_guard<std::mutex> lock(worker_wait_mutex_);
            received_first_command_ = false;
          }
          set_zero_all_motors();
          RCLCPP_WARN(this->get_logger(),
                      "Manual zero finished; waiting for next motor command");
          break;
        }
      interfaces::msg::MotorCommand12 cmd;
      {
        std::lock_guard<std::mutex> lock(command_mutex_);
        cmd = latest_command_;
      }

      auto send_start = std::chrono::steady_clock::now();
      const auto &transforms = rs00_motor::joint_transforms();
      const auto &gains = rs00_motor::joint_gains();
      for (size_t i = 0; i < motors_.size(); ++i) {
        if (!motor_initialized_[i] || !motor_enabled_[i]) {
          continue;
        }

        const auto &command = cmd.*kCommandFields[i];
        const auto &transform = transforms[i];
        const float torque = static_cast<float>(command.torque);
        const float position = clamp_position(
            i, static_cast<float>(command.position) * transform.command_position_scale);
        const auto &gain = gains[i];
        const bool use_default_gains = command.kp == 0.0 && command.kd == 0.0;
        const float kp = use_default_gains ? gain.kp : static_cast<float>(command.kp);
        const float kd = use_default_gains ? gain.kd : static_cast<float>(command.kd);
        motors_[i]->send_motion_command(torque, position, 0.0f, kp, kd);
      }

      auto send_duration = std::chrono::steady_clock::now() - send_start;
      max_send_duration = std::max(max_send_duration, send_duration);
      send_loops++;

      auto now = std::chrono::steady_clock::now();
      if (send_duration > COMMAND_PERIOD) {
        RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                             "Motor send loop overrun: %.2f ms",
                             std::chrono::duration<double, std::milli>(send_duration).count());
      }
      if (now - last_diag_log >= DIAG_LOG_PERIOD) {
        RCLCPP_INFO(this->get_logger(),
                    "Motor send diag: loops=%zu avg_hz=%.1f max_send_ms=%.2f",
                    send_loops,
                    static_cast<double>(send_loops) /
                        std::chrono::duration<double>(now - last_diag_log).count(),
                    std::chrono::duration<double, std::milli>(max_send_duration).count());
        send_loops = 0;
        max_send_duration = std::chrono::steady_clock::duration::zero();
        last_diag_log = now;
      }

      next_tick += COMMAND_PERIOD;
      std::this_thread::sleep_until(next_tick);
      if (std::chrono::steady_clock::now() > next_tick + COMMAND_PERIOD) {
        next_tick = std::chrono::steady_clock::now();
      }
      }
    }
  }

  rclcpp::Publisher<interfaces::msg::MotorFeedback12>::SharedPtr feedback_pub_;
  rclcpp::TimerBase::SharedPtr feedback_timer_;
  rclcpp::Subscription<interfaces::msg::MotorCommand12>::SharedPtr command_sub_;
  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr set_zero_sub_;
  std::thread worker_thread_;
  std::atomic<bool> running_ = true;
  std::atomic<bool> received_first_command_;
  std::atomic<bool> set_zero_requested_{false};
  std::mutex command_mutex_;
  std::mutex motors_mutex_;
  std::mutex worker_wait_mutex_;
  std::condition_variable worker_cv_;
  interfaces::msg::MotorCommand12 latest_command_;
  std::vector<bool> motor_initialized_;
  std::vector<bool> motor_enabled_;
  std::vector<std::unique_ptr<RobStrideMotor>> motors_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto controller = std::make_shared<MotorControlSample>();
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(controller);
  executor.spin();
  rclcpp::shutdown();
  return 0;
}
