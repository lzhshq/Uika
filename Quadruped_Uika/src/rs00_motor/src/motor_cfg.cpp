#include "motor_ros2/motor_cfg.h"

#include <array>
#include <map>
#include <memory>

class CanRxDispatcher {
public:
  explicit CanRxDispatcher(const std::string &iface) : iface_(iface) {
    init_socket();
    rx_thread_ = std::thread(&CanRxDispatcher::rx_loop, this);
  }

  ~CanRxDispatcher() {
    running_ = false;
    if (rx_thread_.joinable()) {
      rx_thread_.join();
    }
    if (socket_fd_ >= 0) {
      close(socket_fd_);
    }
  }

  void register_motor(uint8_t motor_id, RobStrideMotor *motor) {
    std::lock_guard<std::mutex> lock(motors_mutex_);
    motors_[motor_id] = motor;
  }

  void unregister_motor(uint8_t motor_id, RobStrideMotor *motor) {
    std::lock_guard<std::mutex> lock(motors_mutex_);
    if (motors_[motor_id] == motor) {
      motors_[motor_id] = nullptr;
    }
  }

  ssize_t send(const struct can_frame &frame) {
    std::lock_guard<std::mutex> lock(tx_mutex_);
    return write(socket_fd_, &frame, sizeof(frame));
  }

private:
  void init_socket() {
    socket_fd_ = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (socket_fd_ < 0) {
      perror("rx socket");
      exit(1);
    }

    struct ifreq ifr{};
    std::strncpy(ifr.ifr_name, iface_.c_str(), IFNAMSIZ);
    if (ioctl(socket_fd_, SIOCGIFINDEX, &ifr) < 0) {
      perror("rx ioctl");
      exit(1);
    }

    struct sockaddr_can addr{};
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(socket_fd_, reinterpret_cast<struct sockaddr *>(&addr),
             sizeof(addr)) < 0) {
      perror("rx bind");
      exit(1);
    }

    struct timeval timeout{};
    timeout.tv_sec = 0;
    timeout.tv_usec = 5000;
    if (setsockopt(socket_fd_, SOL_SOCKET, SO_RCVTIMEO, &timeout,
                   sizeof(timeout)) < 0) {
      perror("rx setsockopt timeout");
      exit(1);
    }
  }

  void rx_loop() {
    while (running_) {
      struct can_frame frame{};
      const ssize_t nbytes = recv(socket_fd_, &frame, sizeof(frame), 0);
      if (nbytes <= 0) {
        continue;
      }
      if (!(frame.can_id & CAN_EFF_FLAG)) {
        continue;
      }

      const uint32_t can_id = frame.can_id & CAN_EFF_MASK;
      const uint8_t communication_type = (can_id >> 24) & 0x1F;
      const uint16_t extra_data = (can_id >> 8) & 0xFFFF;
      const uint8_t host_id = can_id & 0xFF;
      const uint8_t motor_id = extra_data & 0xFF;
      std::lock_guard<std::mutex> lock(motors_mutex_);
      RobStrideMotor *motor = motors_[motor_id];
      if (motor == nullptr) {
        continue;
      }
      motor->handle_received_frame(communication_type, extra_data, host_id,
                                   frame.data, frame.can_dlc);
      motor->rx_count_.fetch_add(1, std::memory_order_relaxed);
    }
  }

  std::string iface_;
  int socket_fd_ = -1;
  std::atomic<bool> running_{true};
  std::thread rx_thread_;
  std::mutex motors_mutex_;
  std::mutex tx_mutex_;
  std::array<RobStrideMotor *, 256> motors_{};
};

std::shared_ptr<CanRxDispatcher> get_can_rx_dispatcher(
    const std::string &iface) {
  static std::mutex dispatchers_mutex;
  static std::map<std::string, std::weak_ptr<CanRxDispatcher>> dispatchers;

  std::lock_guard<std::mutex> lock(dispatchers_mutex);
  auto existing = dispatchers[iface].lock();
  if (existing) {
    return existing;
  }

  auto created = std::make_shared<CanRxDispatcher>(iface);
  dispatchers[iface] = created;
  return created;
}

RobStrideMotor::RobStrideMotor(const std::string &can_interface,
                               uint8_t master_id, uint8_t motor_id,
                               int actuator_type)
    : iface(can_interface), master_id(master_id), motor_id(motor_id),
      actuator_type(actuator_type),
      actuator_operation_(ACTUATOR_OPERATION_MAPPING.at(
          static_cast<ActuatorType>(actuator_type))) {
  rx_dispatcher_ = get_can_rx_dispatcher(iface);
  rx_dispatcher_->register_motor(motor_id, this);
}

RobStrideMotor::~RobStrideMotor() {
  if (rx_dispatcher_) {
    rx_dispatcher_->unregister_motor(motor_id, this);
  }
}

void RobStrideMotor::handle_received_frame(uint8_t communication_type,
                                           uint16_t extra_data,
                                           uint8_t host_id,
                                           const uint8_t *data,
                                           std::size_t data_size) {
  (void)host_id;
  if (data_size < 8) {
    return;
  }

  std::lock_guard<std::mutex> lock(state_mutex_);
  error_code = uint8_t((extra_data >> 8) & 0x3F);
  pattern = uint8_t((extra_data >> 14) & 0x03);

  if (communication_type == Communication_Type_MotorRequest) {
    uint16_t position_u16 = (data[0] << 8) | data[1];
    uint16_t velocity_u16 = (data[2] << 8) | data[3];
    uint16_t torque_i16 = (data[4] << 8) | data[5];
    uint16_t temperature_u16 = (data[6] << 8) | data[7];

    position_ =
        ((static_cast<float>(position_u16) / 32767.0f) - 1.0f) *
        actuator_operation_.position;
    velocity_ =
        ((static_cast<float>(velocity_u16) / 32767.0f) - 1.0f) *
        actuator_operation_.velocity;
    torque_ =
        ((static_cast<float>(torque_i16) / 32767.0f) - 1.0f) *
        actuator_operation_.torque;
    temperature_ = static_cast<float>(temperature_u16) * 0.1f;
    last_motion_feedback_time_ = std::chrono::steady_clock::now();
  } else if (communication_type == 17) {
    params.data = uint8_t(data[4]);
    params.index = 0X7005;
    for (int index_num = 0; index_num <= 13; index_num++) {
      if ((data[1] << 8 | data[0]) == Index_List[index_num]) {
        switch (index_num) {
        case 0:
          drw.run_mode.data = uint8_t(data[4]);
          break;
        case 1:
          drw.iq_ref.data = Byte_to_float(data, data_size);
          break;
        case 2:
          drw.spd_ref.data = Byte_to_float(data, data_size);
          break;
        case 3:
          drw.imit_torque.data = Byte_to_float(data, data_size);
          break;
        case 4:
          drw.cur_kp.data = Byte_to_float(data, data_size);
          break;
        case 5:
          drw.cur_ki.data = Byte_to_float(data, data_size);
          break;
        case 6:
          drw.cur_filt_gain.data = Byte_to_float(data, data_size);
          break;
        case 7:
          drw.loc_ref.data = Byte_to_float(data, data_size);
          break;
        case 8:
          drw.limit_spd.data = Byte_to_float(data, data_size);
          break;
        case 9:
          drw.limit_cur.data = Byte_to_float(data, data_size);
          break;
        case 10:
          drw.mechPos.data = Byte_to_float(data, data_size);
          break;
        case 11:
          drw.iqf.data = Byte_to_float(data, data_size);
          break;
        case 12:
          drw.mechVel.data = Byte_to_float(data, data_size);
          break;
        case 13:
          drw.VBUS.data = Byte_to_float(data, data_size);
          break;
        }
      }
    }
  }
}

bool RobStrideMotor::wait_for_rx_update(uint64_t previous_rx_count,
                                        std::chrono::milliseconds timeout) {
  auto deadline = std::chrono::steady_clock::now() + timeout;
  while (std::chrono::steady_clock::now() < deadline) {
    if (rx_count_.load(std::memory_order_relaxed) > previous_rx_count) {
      return true;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  return rx_count_.load(std::memory_order_relaxed) > previous_rx_count;
}

void RobStrideMotor::Set_RobStrite_Motor_parameter(uint16_t Index, float Value,
                                                   char Value_mode) {
  struct can_frame frame{};

  frame.can_id =
      Communication_Type_SetSingleParameter << 24 | master_id << 8 | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 0x08;

  frame.data[0] = Index;
  frame.data[1] = Index >> 8;
  frame.data[2] = 0x00;
  frame.data[3] = 0x00;

  if (Value_mode == 'p') {
    memcpy(&frame.data[4], &Value, 4);
  } else if (Value_mode == 'j') {
    // Motor_Set_All.set_motor_mode = int(Value);
    frame.data[4] = (uint8_t)Value;
    frame.data[5] = 0x00;
    frame.data[6] = 0x00;
    frame.data[7] = 0x00;
  }

  uint64_t previous_rx_count = rx_count_.load();
  int n = rx_dispatcher_->send(frame);
  if (n != sizeof(frame)) {
    perror("set mode failed");
  }
  wait_for_rx_update(previous_rx_count, std::chrono::milliseconds(20));
}

// 发送使能指令（通信类型3）
std::tuple<float, float, float, float> RobStrideMotor::enable_motor() {
  struct can_frame frame{};
  frame.can_id =
      (Communication_Type_MotorEnable << 24) | (master_id << 8) | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 8;
  memset(frame.data, 0, 8);

  uint64_t previous_rx_count = rx_count_.load();
  int n = rx_dispatcher_->send(frame);
  if (n != sizeof(frame)) {
    perror("enable_motor failed");
  } else {
    std::cout << "[✓] Motor enable command sent." << std::endl;
  }
  wait_for_rx_update(previous_rx_count, std::chrono::milliseconds(20));

  return std::make_tuple(position_, velocity_, torque_, temperature_);
}

uint16_t RobStrideMotor::float_to_uint(float x, float x_min, float x_max,
                                       int bits) {
  if (x < x_min)
    x = x_min;
  if (x > x_max)
    x = x_max;
  float span = x_max - x_min;
  float offset = x - x_min;
  return static_cast<uint16_t>((offset * ((1 << bits) - 1)) / span);
}

// 发送运控模式（控制角度 + 速度 + KP + KD）
void RobStrideMotor::send_motion_command(float torque, float position_rad,
                                         float velocity_rad_s, float kp,
                                         float kd) {
  uint8_t run_mode_snapshot;
  uint8_t pattern_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
    pattern_snapshot = pattern;
  }
  if (run_mode_snapshot != 0 && pattern_snapshot == 2) {
    Disenable_Motor(0);
    usleep(1000);

    Set_RobStrite_Motor_parameter(0X7005, move_control_mode, Set_mode);
    usleep(1000);

    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);

    enable_motor();
    usleep(1000);
  }
  struct can_frame frame{};
  frame.can_id =
      (Communication_Type_MotionControl << 24) |
      (float_to_uint(torque, -actuator_operation_.torque,
                     actuator_operation_.torque, 16)
       << 8) |
      motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  // frame.can_id = 0x1200fd01;
  frame.can_dlc = 8;

  uint16_t pos = float_to_uint(
      position_rad,
      -actuator_operation_.position, actuator_operation_.position,
      16);
  uint16_t vel = float_to_uint(
      velocity_rad_s,
      -actuator_operation_.velocity, actuator_operation_.velocity,
      16);
  uint16_t kp_u = float_to_uint(
      kp, 0.0f, actuator_operation_.kp, 16);
  uint16_t kd_u = float_to_uint(
      kd, 0.0f, actuator_operation_.kd, 16);

  frame.data[0] = (pos >> 8);
  frame.data[1] = pos;
  frame.data[2] = (vel >> 8);
  frame.data[3] = vel;
  frame.data[4] = (kp_u >> 8);
  frame.data[5] = kp_u;
  frame.data[6] = (kd_u >> 8);
  frame.data[7] = kd_u;
  // 05 70 00 00 07 01 82 F9

  int n = rx_dispatcher_->send(frame);

  if (n != sizeof(frame)) {
    perror("send_motion_command failed");
  }
}

std::tuple<float, float, float, float>
RobStrideMotor::send_velocity_mode_command(float velocity_rad_s) {
  uint8_t run_mode_snapshot;
  uint8_t pattern_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
    pattern_snapshot = pattern;
  }
  if (run_mode_snapshot != 2 && pattern_snapshot == 2) {
    Disenable_Motor(0);
    std::cout << "disable motor " << std::endl;
    usleep(1000);
    Set_RobStrite_Motor_parameter(0X7005, Speed_control_mode, Set_mode);
    usleep(1000);
    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);
    enable_motor();
    Set_RobStrite_Motor_parameter(0X7018, 27.0f, Set_parameter);
    usleep(1000);
    Set_RobStrite_Motor_parameter(0X7026, Motor_Set_All.set_acc, Set_parameter);
    usleep(1000);
  }
  std::cout << "excute vel_mode" << std::endl;
  Set_RobStrite_Motor_parameter(0X700A, velocity_rad_s, Set_parameter);
  std::cout << "finish" << std::endl;
  return std::make_tuple(position_, velocity_, torque_, temperature_);
}

float RobStrideMotor::read_initial_position() {
  const uint64_t previous_rx_count = rx_count_.load();
  if (!wait_for_rx_update(previous_rx_count, std::chrono::seconds(10))) {
    std::cerr << "[!] Timeout waiting for motor feedback." << std::endl;
    return 0.0f;
  }

  std::lock_guard<std::mutex> lock(state_mutex_);
  std::cout << "[✓] Initial position read: " << position_ << " rad"
            << std::endl;
  return position_;
}

void RobStrideMotor::Get_RobStrite_Motor_parameter(uint16_t Index) {
  struct can_frame frame{};
  frame.can_id = (Communication_Type_GetSingleParameter << 24) |
                 (master_id << 8) | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 8;

  frame.data[0] = Index;
  frame.data[1] = Index >> 8;
  frame.data[2] = 0x00;
  frame.data[3] = 0x00;
  frame.data[4] = 0x00;
  frame.data[5] = 0x00;
  frame.data[6] = 0x00;
  frame.data[7] = 0x00;
  uint64_t previous_rx_count = rx_count_.load();
  int n = rx_dispatcher_->send(frame);

  if (n != sizeof(frame)) {
    perror("get_motor_parameter failed");
  }
  wait_for_rx_update(previous_rx_count, std::chrono::milliseconds(20));
}

// 位置模式（PP）
std::tuple<float, float, float, float>
RobStrideMotor::RobStrite_Motor_PosPP_control(float Speed, float Acceleration,
                                              float Angle) {
  uint8_t run_mode_snapshot;
  uint8_t pattern_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
    pattern_snapshot = pattern;
  }
  if (run_mode_snapshot != 1 && pattern_snapshot == 2) {
    Disenable_Motor(0);
    usleep(1000);
    Set_RobStrite_Motor_parameter(0X7005, PosPP_control_mode, Set_mode);
    usleep(1000);
    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);
    enable_motor();
    usleep(1000);
  }

  Motor_Set_All.set_speed = Speed;
  Motor_Set_All.set_acc = Acceleration;
  Motor_Set_All.set_angle = Angle;

  Set_RobStrite_Motor_parameter(0X7024, Motor_Set_All.set_speed, Set_parameter);
  usleep(1000);

  Set_RobStrite_Motor_parameter(0X7025, Motor_Set_All.set_acc, Set_parameter);
  usleep(1000);

  Set_RobStrite_Motor_parameter(0X7016, Motor_Set_All.set_angle, Set_parameter);
  usleep(1000);

  return std::make_tuple(position_, velocity_, torque_, temperature_);
}

// 电流模式
std::tuple<float, float, float, float>
RobStrideMotor::RobStrite_Motor_Current_control(float IqCommand) {
  uint8_t run_mode_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
  }
  if (run_mode_snapshot != 3) {
    Disenable_Motor(0);
    usleep(1000);
    Set_RobStrite_Motor_parameter(0X7005, Elect_control_mode, Set_mode);
    usleep(1000);
    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);
    enable_motor();
    usleep(1000);
  }

  // Store the target values
  Motor_Set_All.set_iq = IqCommand;

  Motor_Set_All.set_iq =
      float_to_uint(Motor_Set_All.set_iq, SCIQ_MIN, SC_MAX, 16);
  Set_RobStrite_Motor_parameter(0X7006, Motor_Set_All.set_iq, Set_parameter);
  usleep(1000);

  return std::make_tuple(position_, velocity_, torque_, temperature_);
}

void RobStrideMotor::RobStrite_Motor_Set_Zero_control() {
  Set_RobStrite_Motor_parameter(0X7005, Set_Zero_mode,
                                Set_mode); // 设置电机模式
}

void RobStrideMotor::Disenable_Motor(uint8_t clear_error) {
  struct can_frame frame{};
  frame.can_id =
      (Communication_Type_MotorStop << 24) | (master_id << 8) | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 8;
  memset(frame.data, 0, 8);

  frame.data[0] = clear_error;
  frame.data[1] = 0x00;
  frame.data[2] = 0x00;
  frame.data[3] = 0x00;
  frame.data[4] = 0x00;
  frame.data[5] = 0x00;
  frame.data[6] = 0x00;
  frame.data[7] = 0x00;

  uint64_t previous_rx_count = rx_count_.load();
  int n = rx_dispatcher_->send(frame);

  if (n != sizeof(frame)) {
    perror("disable_motor failed");
  }
  wait_for_rx_update(previous_rx_count, std::chrono::milliseconds(20));
}

void RobStrideMotor::Set_CAN_ID(uint8_t Set_CAN_ID) {
  Disenable_Motor(0);

  struct can_frame frame{};
  frame.can_id = (Communication_Type_Can_ID << 24) | (Set_CAN_ID << 16) |
                 (master_id << 8) | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 8;
  memset(frame.data, 0, 8);

  frame.data[0] = 0x00;
  frame.data[1] = 0x00;
  frame.data[2] = 0x00;
  frame.data[3] = 0x00;
  frame.data[4] = 0x00;
  frame.data[5] = 0x00;
  frame.data[6] = 0x00;
  frame.data[7] = 0x00;

  int n = rx_dispatcher_->send(frame);

  if (n != sizeof(frame)) {
    perror("Set_ZeroPos failed");
  } else {
    std::cout << "[✓] Motor Set_ZeroPos command sent." << std::endl;
  }
}
// 5.位置模式（CSP）
std::tuple<float, float, float, float>
RobStrideMotor::RobStrite_Motor_PosCSP_control(float Speed, float Angle) {
  Motor_Set_All.set_speed = Speed;
  Motor_Set_All.set_angle = Angle;
  std::cout << "speed: " << Motor_Set_All.set_speed << std::endl;
  std::cout << "angle: " << Motor_Set_All.set_angle << std::endl;

  uint8_t run_mode_snapshot;
  uint8_t pattern_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
    pattern_snapshot = pattern;
  }
  if (run_mode_snapshot != 5 && pattern_snapshot == 2) {
    Disenable_Motor(0);
    usleep(1000);
    Set_RobStrite_Motor_parameter(0X7005, PosCSP_control_mode,
                                  Set_mode); // 设置电机模式
    usleep(1000);

    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);

    enable_motor();
    usleep(1000);

    Motor_Set_All.set_motor_mode = PosCSP_control_mode;
  }
  Set_RobStrite_Motor_parameter(0X7017, Motor_Set_All.set_speed, Set_parameter);
  Set_RobStrite_Motor_parameter(0X7016, Motor_Set_All.set_angle, Set_parameter);
  usleep(1000);

  return std::make_tuple(position_, velocity_, torque_, temperature_);
}

void RobStrideMotor::Set_ZeroPos() {
  Disenable_Motor(0);

  uint8_t run_mode_snapshot;
  {
    std::lock_guard<std::mutex> lock(state_mutex_);
    run_mode_snapshot = drw.run_mode.data;
  }
  if (run_mode_snapshot != 4) {
    Set_RobStrite_Motor_parameter(0X7005, Speed_control_mode, Set_mode);
    usleep(1000);

    Get_RobStrite_Motor_parameter(0x7005);
    usleep(1000);
  }

  struct can_frame frame{};
  frame.can_id =
      (Communication_Type_SetPosZero << 24) | (master_id << 8) | motor_id;
  frame.can_id |= CAN_EFF_FLAG; // 扩展帧
  frame.can_dlc = 8;
  memset(frame.data, 0, 8);

  frame.data[0] = 1;
  frame.data[1] = 0x00;
  frame.data[2] = 0x00;
  frame.data[3] = 0x00;
  frame.data[4] = 0x00;
  frame.data[5] = 0x00;
  frame.data[6] = 0x00;
  frame.data[7] = 0x00;

  int n = rx_dispatcher_->send(frame);

  if (n != sizeof(frame)) {
    perror("Set_ZeroPos failed");
  } else {
    std::cout << "[✓] Motor Set_ZeroPos command sent." << std::endl;
  }

  enable_motor();
}
