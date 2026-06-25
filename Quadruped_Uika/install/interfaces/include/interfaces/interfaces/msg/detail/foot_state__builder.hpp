// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/FootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__FOOT_STATE__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__FOOT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/foot_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_FootState_rr
{
public:
  explicit Init_FootState_rr(::interfaces::msg::FootState & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::FootState rr(::interfaces::msg::FootState::_rr_type arg)
  {
    msg_.rr = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::FootState msg_;
};

class Init_FootState_rl
{
public:
  explicit Init_FootState_rl(::interfaces::msg::FootState & msg)
  : msg_(msg)
  {}
  Init_FootState_rr rl(::interfaces::msg::FootState::_rl_type arg)
  {
    msg_.rl = std::move(arg);
    return Init_FootState_rr(msg_);
  }

private:
  ::interfaces::msg::FootState msg_;
};

class Init_FootState_fr
{
public:
  explicit Init_FootState_fr(::interfaces::msg::FootState & msg)
  : msg_(msg)
  {}
  Init_FootState_rl fr(::interfaces::msg::FootState::_fr_type arg)
  {
    msg_.fr = std::move(arg);
    return Init_FootState_rl(msg_);
  }

private:
  ::interfaces::msg::FootState msg_;
};

class Init_FootState_fl
{
public:
  explicit Init_FootState_fl(::interfaces::msg::FootState & msg)
  : msg_(msg)
  {}
  Init_FootState_fr fl(::interfaces::msg::FootState::_fl_type arg)
  {
    msg_.fl = std::move(arg);
    return Init_FootState_fr(msg_);
  }

private:
  ::interfaces::msg::FootState msg_;
};

class Init_FootState_header
{
public:
  Init_FootState_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_FootState_fl header(::interfaces::msg::FootState::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_FootState_fl(msg_);
  }

private:
  ::interfaces::msg::FootState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::FootState>()
{
  return interfaces::msg::builder::Init_FootState_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__FOOT_STATE__BUILDER_HPP_
