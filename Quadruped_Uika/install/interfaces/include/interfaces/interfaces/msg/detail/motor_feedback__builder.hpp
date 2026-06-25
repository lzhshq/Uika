// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/MotorFeedback.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/motor_feedback__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_MotorFeedback_temperature
{
public:
  explicit Init_MotorFeedback_temperature(::interfaces::msg::MotorFeedback & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::MotorFeedback temperature(::interfaces::msg::MotorFeedback::_temperature_type arg)
  {
    msg_.temperature = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback msg_;
};

class Init_MotorFeedback_velocity
{
public:
  explicit Init_MotorFeedback_velocity(::interfaces::msg::MotorFeedback & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback_temperature velocity(::interfaces::msg::MotorFeedback::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_MotorFeedback_temperature(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback msg_;
};

class Init_MotorFeedback_position
{
public:
  explicit Init_MotorFeedback_position(::interfaces::msg::MotorFeedback & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback_velocity position(::interfaces::msg::MotorFeedback::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_MotorFeedback_velocity(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback msg_;
};

class Init_MotorFeedback_torque
{
public:
  Init_MotorFeedback_torque()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorFeedback_position torque(::interfaces::msg::MotorFeedback::_torque_type arg)
  {
    msg_.torque = std::move(arg);
    return Init_MotorFeedback_position(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::MotorFeedback>()
{
  return interfaces::msg::builder::Init_MotorFeedback_torque();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__BUILDER_HPP_
