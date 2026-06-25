// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/MotorFeedback12.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/motor_feedback12__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_MotorFeedback12_rr_calf
{
public:
  explicit Init_MotorFeedback12_rr_calf(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::MotorFeedback12 rr_calf(::interfaces::msg::MotorFeedback12::_rr_calf_type arg)
  {
    msg_.rr_calf = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_rr_thigh
{
public:
  explicit Init_MotorFeedback12_rr_thigh(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rr_calf rr_thigh(::interfaces::msg::MotorFeedback12::_rr_thigh_type arg)
  {
    msg_.rr_thigh = std::move(arg);
    return Init_MotorFeedback12_rr_calf(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_rr_hip
{
public:
  explicit Init_MotorFeedback12_rr_hip(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rr_thigh rr_hip(::interfaces::msg::MotorFeedback12::_rr_hip_type arg)
  {
    msg_.rr_hip = std::move(arg);
    return Init_MotorFeedback12_rr_thigh(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_rl_calf
{
public:
  explicit Init_MotorFeedback12_rl_calf(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rr_hip rl_calf(::interfaces::msg::MotorFeedback12::_rl_calf_type arg)
  {
    msg_.rl_calf = std::move(arg);
    return Init_MotorFeedback12_rr_hip(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_rl_thigh
{
public:
  explicit Init_MotorFeedback12_rl_thigh(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rl_calf rl_thigh(::interfaces::msg::MotorFeedback12::_rl_thigh_type arg)
  {
    msg_.rl_thigh = std::move(arg);
    return Init_MotorFeedback12_rl_calf(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_rl_hip
{
public:
  explicit Init_MotorFeedback12_rl_hip(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rl_thigh rl_hip(::interfaces::msg::MotorFeedback12::_rl_hip_type arg)
  {
    msg_.rl_hip = std::move(arg);
    return Init_MotorFeedback12_rl_thigh(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fr_calf
{
public:
  explicit Init_MotorFeedback12_fr_calf(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_rl_hip fr_calf(::interfaces::msg::MotorFeedback12::_fr_calf_type arg)
  {
    msg_.fr_calf = std::move(arg);
    return Init_MotorFeedback12_rl_hip(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fr_thigh
{
public:
  explicit Init_MotorFeedback12_fr_thigh(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_fr_calf fr_thigh(::interfaces::msg::MotorFeedback12::_fr_thigh_type arg)
  {
    msg_.fr_thigh = std::move(arg);
    return Init_MotorFeedback12_fr_calf(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fr_hip
{
public:
  explicit Init_MotorFeedback12_fr_hip(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_fr_thigh fr_hip(::interfaces::msg::MotorFeedback12::_fr_hip_type arg)
  {
    msg_.fr_hip = std::move(arg);
    return Init_MotorFeedback12_fr_thigh(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fl_calf
{
public:
  explicit Init_MotorFeedback12_fl_calf(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_fr_hip fl_calf(::interfaces::msg::MotorFeedback12::_fl_calf_type arg)
  {
    msg_.fl_calf = std::move(arg);
    return Init_MotorFeedback12_fr_hip(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fl_thigh
{
public:
  explicit Init_MotorFeedback12_fl_thigh(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_fl_calf fl_thigh(::interfaces::msg::MotorFeedback12::_fl_thigh_type arg)
  {
    msg_.fl_thigh = std::move(arg);
    return Init_MotorFeedback12_fl_calf(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_fl_hip
{
public:
  explicit Init_MotorFeedback12_fl_hip(::interfaces::msg::MotorFeedback12 & msg)
  : msg_(msg)
  {}
  Init_MotorFeedback12_fl_thigh fl_hip(::interfaces::msg::MotorFeedback12::_fl_hip_type arg)
  {
    msg_.fl_hip = std::move(arg);
    return Init_MotorFeedback12_fl_thigh(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

class Init_MotorFeedback12_header
{
public:
  Init_MotorFeedback12_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MotorFeedback12_fl_hip header(::interfaces::msg::MotorFeedback12::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_MotorFeedback12_fl_hip(msg_);
  }

private:
  ::interfaces::msg::MotorFeedback12 msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::MotorFeedback12>()
{
  return interfaces::msg::builder::Init_MotorFeedback12_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__BUILDER_HPP_
