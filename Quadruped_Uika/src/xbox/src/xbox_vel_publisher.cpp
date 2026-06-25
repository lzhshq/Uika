// Copyright 2026 lzh
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/joy.hpp>

#include <memory>
#include <chrono>

using namespace std::chrono_literals;

/**
 * @brief Xbox velocity publisher node
 *
 * Subscribes to /joy topic (Xbox controller data) and publishes
 * velocity commands to /xbox_vel topic.
 */
class XboxVelPublisher : public rclcpp::Node
{
public:
  XboxVelPublisher()
  : Node("xbox_vel_publisher")
  {
    // Declare parameters with default values
    this->declare_parameter<double>("max_linear_speed", 1.0);
    this->declare_parameter<double>("max_angular_speed", 2.0);
    this->declare_parameter<double>("deadzone", 0.1);

    // Get parameter values
    this->get_parameter("max_linear_speed", max_linear_speed_);
    this->get_parameter("max_angular_speed", max_angular_speed_);
    this->get_parameter("deadzone", deadzone_);

    RCLCPP_INFO(this->get_logger(), "Xbox Vel Publisher started");
    RCLCPP_INFO(this->get_logger(), "max_linear_speed: %.2f", max_linear_speed_);
    RCLCPP_INFO(this->get_logger(), "max_angular_speed: %.2f", max_angular_speed_);
    RCLCPP_INFO(this->get_logger(), "deadzone: %.2f", deadzone_);

    // Create publisher for velocity commands
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("xbox_vel", 10);

    // Create subscriber for joy messages
    subscriber_ = this->create_subscription<sensor_msgs::msg::Joy>(
      "joy",
      10,
      std::bind(&XboxVelPublisher::joy_callback, this, std::placeholders::_1)
    );

    // Create timer for publishing at 50Hz
    timer_ = this->create_wall_timer(
      20ms,
      std::bind(&XboxVelPublisher::timer_callback, this)
    );
  }

private:
  /**
   * @brief Apply deadzone to joystick input
   * @param value Raw joystick input [-1.0, 1.0]
   * @return Processed value with deadzone applied
   */
  double apply_deadzone(double value)
  {
    if (std::abs(value) < deadzone_) {
      return 0.0;
    }
    // Rescale the value to maintain full range
    double sign = (value > 0) ? 1.0 : -1.0;
    return sign * ((std::abs(value) - deadzone_) / (1.0 - deadzone_));
  }

  /**
   * @brief Joystick callback - stores latest joystick data
   */
  void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg)
  {
    latest_joy_ = msg;
  }

  /**
   * @brief Timer callback - publishes velocity commands
   */
  void timer_callback()
  {
    // Check if we have received joy messages
    if (!latest_joy_) {
      return;
    }

    auto joy = latest_joy_;

    // Create twist message
    geometry_msgs::msg::Twist twist;

    // Xbox controller mapping:
    // axes[0]: Left stick X (left/right)  -> linear.y (sideways)
    // axes[1]: Left stick Y (up/down)     -> linear.x (forward/backward, inverted)
    // axes[2]: Right stick X (left/right) -> angular.z (turning)
    // axes[3]: Right stick Y (up/down)    -> not used

    // Apply deadzone and scaling
    double left_stick_y = apply_deadzone(joy->axes[1]);   // Forward positive
    double left_stick_x = apply_deadzone(joy->axes[0]);   // Right positive
    double right_stick_x = apply_deadzone(joy->axes[3]);  // Right positive

    // Map to velocity commands
    twist.linear.x = left_stick_y * max_linear_speed_;    // Forward/backward
    twist.linear.y = left_stick_x * max_linear_speed_;   // Left/right strafe
    twist.linear.z = 0.0;
    twist.angular.x = 0.0;
    twist.angular.y = 0.0;
    twist.angular.z = right_stick_x * max_angular_speed_; // Turning

    // Publish velocity command
    publisher_->publish(twist);
  }

  // Parameters
  double max_linear_speed_;
  double max_angular_speed_;
  double deadzone_;

  // ROS interfaces
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr subscriber_;
  rclcpp::TimerBase::SharedPtr timer_;

  // Store latest joy message
  sensor_msgs::msg::Joy::SharedPtr latest_joy_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<XboxVelPublisher>());
  rclcpp::shutdown();
  return 0;
}
