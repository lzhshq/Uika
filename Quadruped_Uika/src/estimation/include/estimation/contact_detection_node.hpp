#ifndef ESTIMATION_CONTACT_DETECTION_NODE_HPP
#define ESTIMATION_CONTACT_DETECTION_NODE_HPP

#include <memory>
#include <array>
#include <mutex>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/header.hpp>
#include <geometry_msgs/msg/vector3.hpp>

#include "interfaces/msg/motor_feedback12.hpp"
#include "interfaces/msg/contact_state.hpp"
#include "interfaces/msg/gait_phase.hpp"

#include "gm_observer.hpp"
#include "types.hpp"

namespace estimation {

/**
 * @brief 触地检测节点
 *
 * 订阅电机反馈,使用GM观测器检测触地状态并发布
 */
class ContactDetectionNode : public rclcpp::Node {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    ContactDetectionNode();

private:
    // 回调函数
    void on_motor_feedback(const interfaces::msg::MotorFeedback12::SharedPtr msg);
    void on_gait_phase(const interfaces::msg::GaitPhase::SharedPtr msg);

    // 发布触地状态
    void publish_contact_state();

    // GM观测器 (每条腿一个)
    std::array<std::unique_ptr<GMObserver>, 4> gm_observers_;

    // 步态相位 (可选,用于辅助判断)
    std::optional<interfaces::msg::GaitPhase> gait_phase_;
    std::mutex gait_phase_mutex_;

    // ROS2 接口
    rclcpp::Subscription<interfaces::msg::MotorFeedback12>::SharedPtr motor_feedback_sub_;
    rclcpp::Subscription<interfaces::msg::GaitPhase>::SharedPtr gait_phase_sub_;
    rclcpp::Publisher<interfaces::msg::ContactState>::SharedPtr contact_state_pub_;

    // 时间跟踪
    rclcpp::Time prev_time_;
    bool first_callback_;

    // 触地阈值 (可配置)
    double contact_threshold_;
};

}  // namespace estimation

#endif  // ESTIMATION_CONTACT_DETECTION_NODE_HPP
