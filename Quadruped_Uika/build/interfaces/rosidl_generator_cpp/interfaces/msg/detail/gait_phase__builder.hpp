// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/GaitPhase.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__GAIT_PHASE__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__GAIT_PHASE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/gait_phase__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_GaitPhase_rr_phase
{
public:
  explicit Init_GaitPhase_rr_phase(::interfaces::msg::GaitPhase & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::GaitPhase rr_phase(::interfaces::msg::GaitPhase::_rr_phase_type arg)
  {
    msg_.rr_phase = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::GaitPhase msg_;
};

class Init_GaitPhase_rl_phase
{
public:
  explicit Init_GaitPhase_rl_phase(::interfaces::msg::GaitPhase & msg)
  : msg_(msg)
  {}
  Init_GaitPhase_rr_phase rl_phase(::interfaces::msg::GaitPhase::_rl_phase_type arg)
  {
    msg_.rl_phase = std::move(arg);
    return Init_GaitPhase_rr_phase(msg_);
  }

private:
  ::interfaces::msg::GaitPhase msg_;
};

class Init_GaitPhase_fr_phase
{
public:
  explicit Init_GaitPhase_fr_phase(::interfaces::msg::GaitPhase & msg)
  : msg_(msg)
  {}
  Init_GaitPhase_rl_phase fr_phase(::interfaces::msg::GaitPhase::_fr_phase_type arg)
  {
    msg_.fr_phase = std::move(arg);
    return Init_GaitPhase_rl_phase(msg_);
  }

private:
  ::interfaces::msg::GaitPhase msg_;
};

class Init_GaitPhase_fl_phase
{
public:
  explicit Init_GaitPhase_fl_phase(::interfaces::msg::GaitPhase & msg)
  : msg_(msg)
  {}
  Init_GaitPhase_fr_phase fl_phase(::interfaces::msg::GaitPhase::_fl_phase_type arg)
  {
    msg_.fl_phase = std::move(arg);
    return Init_GaitPhase_fr_phase(msg_);
  }

private:
  ::interfaces::msg::GaitPhase msg_;
};

class Init_GaitPhase_header
{
public:
  Init_GaitPhase_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GaitPhase_fl_phase header(::interfaces::msg::GaitPhase::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_GaitPhase_fl_phase(msg_);
  }

private:
  ::interfaces::msg::GaitPhase msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::GaitPhase>()
{
  return interfaces::msg::builder::Init_GaitPhase_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__GAIT_PHASE__BUILDER_HPP_
