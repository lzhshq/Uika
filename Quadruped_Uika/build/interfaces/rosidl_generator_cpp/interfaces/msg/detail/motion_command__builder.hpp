// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/MotionCommand.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTION_COMMAND__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__MOTION_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/motion_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_MotionCommand_body_height
{
public:
  explicit Init_MotionCommand_body_height(::interfaces::msg::MotionCommand & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::MotionCommand body_height(::interfaces::msg::MotionCommand::_body_height_type arg)
  {
    msg_.body_height = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::MotionCommand msg_;
};

class Init_MotionCommand_wz
{
public:
  explicit Init_MotionCommand_wz(::interfaces::msg::MotionCommand & msg)
  : msg_(msg)
  {}
  Init_MotionCommand_body_height wz(::interfaces::msg::MotionCommand::_wz_type arg)
  {
    msg_.wz = std::move(arg);
    return Init_MotionCommand_body_height(msg_);
  }

private:
  ::interfaces::msg::MotionCommand msg_;
};

class Init_MotionCommand_vy
{
public:
  explicit Init_MotionCommand_vy(::interfaces::msg::MotionCommand & msg)
  : msg_(msg)
  {}
  Init_MotionCommand_wz vy(::interfaces::msg::MotionCommand::_vy_type arg)
  {
    msg_.vy = std::move(arg);
    return Init_MotionCommand_wz(msg_);
  }

private:
  ::interfaces::msg::MotionCommand msg_;
};

class Init_MotionCommand_vx
{
public:
  explicit Init_MotionCommand_vx(::interfaces::msg::MotionCommand & msg)
  : msg_(msg)
  {}
  Init_MotionCommand_vy vx(::interfaces::msg::MotionCommand::_vx_type arg)
  {
    msg_.vx = std::move(arg);
    return Init_MotionCommand_vy(msg_);
  }

private:
  ::interfaces::msg::MotionCommand msg_;
};

class Init_MotionCommand_header
{
public:
  Init_MotionCommand_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotionCommand_vx header(::interfaces::msg::MotionCommand::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MotionCommand_vx(msg_);
  }

private:
  ::interfaces::msg::MotionCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::MotionCommand>()
{
  return interfaces::msg::builder::Init_MotionCommand_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTION_COMMAND__BUILDER_HPP_
