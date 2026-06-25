#include "estimation/contact_detection_node.hpp"

namespace estimation {

ContactDetectionNode::ContactDetectionNode()
    : Node("contact_detection_node"),
      first_callback_(true),
      contact_threshold_(1.3)  // 5Nm 默认阈值,需要标定
{
    // 声明参数
    this->declare_parameter<double>("contact_threshold", contact_threshold_);
    this->get_parameter("contact_threshold", contact_threshold_);

    // 初始化GM观测器
    double alpha = 0.3;  // 滤波系数
    for (int i = 0; i < 4; ++i) {
        gm_observers_[i] = std::make_unique<GMObserver>(alpha, contact_threshold_);
    }

    // 订阅电机反馈
    motor_feedback_sub_ = this->create_subscription<interfaces::msg::MotorFeedback12>(
        "/motor_feedback",
        100,  // QoS history depth
        [this](const interfaces::msg::MotorFeedback12::SharedPtr msg) {
            this->on_motor_feedback(msg);
        });

    // 订阅步态相位 (可选)
    gait_phase_sub_ = this->create_subscription<interfaces::msg::GaitPhase>(
        "/gait_phase",
        10,
        [this](const interfaces::msg::GaitPhase::SharedPtr msg) {
            this->on_gait_phase(msg);
        });

    // 发布触地状态
    contact_state_pub_ = this->create_publisher<interfaces::msg::ContactState>(
        "/contact_state",
        10);

    RCLCPP_INFO(this->get_logger(), "ContactDetectionNode initialized, threshold=%.2f Nm",
                contact_threshold_);
}

void ContactDetectionNode::on_motor_feedback(
    const interfaces::msg::MotorFeedback12::SharedPtr msg) {
    // 计算时间步长
    rclcpp::Time now = msg->header.stamp;
    double dt = 0.01;  // 默认10ms

    if (!first_callback_) {
        rclcpp::Duration duration = now - prev_time_;
        dt = duration.seconds();
        if (dt <= 0 || dt > 0.1) {
            dt = 0.01;  // 防止异常值
        }
    }
    prev_time_ = now;
    first_callback_ = false;

    // 处理每条腿
    for (int leg_idx = 0; leg_idx < 4; ++leg_idx) {
        int offset = static_cast<int>(leg_idx) * LegConstants::JOINTS_PER_LEG;

        // 提取关节数据
        Eigen::Vector3d q, q_dot, tau;

        // MotorFeedback12 的顺序: fl_hip, fl_thigh, fl_calf, fr_hip, ...
        switch (leg_idx) {
            case 0:  // FL
                q << msg->fl_hip.position, msg->fl_thigh.position, msg->fl_calf.position;
                q_dot << msg->fl_hip.velocity, msg->fl_thigh.velocity, msg->fl_calf.velocity;
                tau << msg->fl_hip.torque, msg->fl_thigh.torque, msg->fl_calf.torque;
                break;
            case 1:  // FR
                q << msg->fr_hip.position, msg->fr_thigh.position, msg->fr_calf.position;
                q_dot << msg->fr_hip.velocity, msg->fr_thigh.velocity, msg->fr_calf.velocity;
                tau << msg->fr_hip.torque, msg->fr_thigh.torque, msg->fr_calf.torque;
                break;
            case 2:  // RL
                q << msg->rl_hip.position, msg->rl_thigh.position, msg->rl_calf.position;
                q_dot << msg->rl_hip.velocity, msg->rl_thigh.velocity, msg->rl_calf.velocity;
                tau << msg->rl_hip.torque, msg->rl_thigh.torque, msg->rl_calf.torque;
                break;
            case 3:  // RR
                q << msg->rr_hip.position, msg->rr_thigh.position, msg->rr_calf.position;
                q_dot << msg->rr_hip.velocity, msg->rr_thigh.velocity, msg->rr_calf.velocity;
                tau << msg->rr_hip.torque, msg->rr_thigh.torque, msg->rr_calf.torque;
                break;
        }

        // 更新GM观测器
        gm_observers_[leg_idx]->update(tau, q, q_dot, dt);
    }

    // 发布触地状态
    publish_contact_state();
}

void ContactDetectionNode::on_gait_phase(
    const interfaces::msg::GaitPhase::SharedPtr msg) {
    std::lock_guard<std::mutex> lock(gait_phase_mutex_);
    gait_phase_ = *msg;
}

void ContactDetectionNode::publish_contact_state() {
    auto msg = interfaces::msg::ContactState();
    msg.header.stamp = this->now();
    msg.header.frame_id = "base_link";

    // 使用GM观测器检测触地
    bool fl_contact = gm_observers_[0]->detectContact();
    bool fr_contact = gm_observers_[1]->detectContact();
    bool rl_contact = gm_observers_[2]->detectContact();
    bool rr_contact = gm_observers_[3]->detectContact();

    // 可选: 如果有步态相位信息,用SWING相辅助判断
    // SWING相的腿不应该触地
    {
        std::lock_guard<std::mutex> lock(gait_phase_mutex_);
        if (gait_phase_.has_value()) {
            if (gait_phase_->fl_phase == interfaces::msg::GaitPhase::SWING) {
                fl_contact = false;
            }
            if (gait_phase_->fr_phase == interfaces::msg::GaitPhase::SWING) {
                fr_contact = false;
            }
            if (gait_phase_->rl_phase == interfaces::msg::GaitPhase::SWING) {
                rl_contact = false;
            }
            if (gait_phase_->rr_phase == interfaces::msg::GaitPhase::SWING) {
                rr_contact = false;
            }
        }
    }

    msg.fl_contact = fl_contact;
    msg.fr_contact = fr_contact;
    msg.rl_contact = rl_contact;
    msg.rr_contact = rr_contact;

    contact_state_pub_->publish(msg);
}

}  // namespace estimation
