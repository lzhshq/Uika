// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/MotorCommand.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/motor_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_MotorCommand_kd
{
public:
  explicit Init_MotorCommand_kd(::interfaces::msg::MotorCommand & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::MotorCommand kd(::interfaces::msg::MotorCommand::_kd_type arg)
  {
    msg_.kd = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::MotorCommand msg_;
};

class Init_MotorCommand_kp
{
public:
  explicit Init_MotorCommand_kp(::interfaces::msg::MotorCommand & msg)
  : msg_(msg)
  {}
  Init_MotorCommand_kd kp(::interfaces::msg::MotorCommand::_kp_type arg)
  {
    msg_.kp = std::move(arg);
    return Init_MotorCommand_kd(msg_);
  }

private:
  ::interfaces::msg::MotorCommand msg_;
};

class Init_MotorCommand_velocity
{
public:
  explicit Init_MotorCommand_velocity(::interfaces::msg::MotorCommand & msg)
  : msg_(msg)
  {}
  Init_MotorCommand_kp velocity(::interfaces::msg::MotorCommand::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_MotorCommand_kp(msg_);
  }

private:
  ::interfaces::msg::MotorCommand msg_;
};

class Init_MotorCommand_position
{
public:
  explicit Init_MotorCommand_position(::interfaces::msg::MotorCommand & msg)
  : msg_(msg)
  {}
  Init_MotorCommand_velocity position(::interfaces::msg::MotorCommand::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_MotorCommand_velocity(msg_);
  }

private:
  ::interfaces::msg::MotorCommand msg_;
};

class Init_MotorCommand_torque
{
public:
  Init_MotorCommand_torque()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorCommand_position torque(::interfaces::msg::MotorCommand::_torque_type arg)
  {
    msg_.torque = std::move(arg);
    return Init_MotorCommand_position(msg_);
  }

private:
  ::interfaces::msg::MotorCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::MotorCommand>()
{
  return interfaces::msg::builder::Init_MotorCommand_torque();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_COMMAND__BUILDER_HPP_
