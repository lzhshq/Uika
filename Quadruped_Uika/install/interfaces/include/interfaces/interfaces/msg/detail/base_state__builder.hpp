// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/BaseState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__BASE_STATE__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__BASE_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/base_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_BaseState_angular_velocity
{
public:
  explicit Init_BaseState_angular_velocity(::interfaces::msg::BaseState & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::BaseState angular_velocity(::interfaces::msg::BaseState::_angular_velocity_type arg)
  {
    msg_.angular_velocity = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::BaseState msg_;
};

class Init_BaseState_linear_velocity
{
public:
  explicit Init_BaseState_linear_velocity(::interfaces::msg::BaseState & msg)
  : msg_(msg)
  {}
  Init_BaseState_angular_velocity linear_velocity(::interfaces::msg::BaseState::_linear_velocity_type arg)
  {
    msg_.linear_velocity = std::move(arg);
    return Init_BaseState_angular_velocity(msg_);
  }

private:
  ::interfaces::msg::BaseState msg_;
};

class Init_BaseState_orientation
{
public:
  explicit Init_BaseState_orientation(::interfaces::msg::BaseState & msg)
  : msg_(msg)
  {}
  Init_BaseState_linear_velocity orientation(::interfaces::msg::BaseState::_orientation_type arg)
  {
    msg_.orientation = std::move(arg);
    return Init_BaseState_linear_velocity(msg_);
  }

private:
  ::interfaces::msg::BaseState msg_;
};

class Init_BaseState_position
{
public:
  explicit Init_BaseState_position(::interfaces::msg::BaseState & msg)
  : msg_(msg)
  {}
  Init_BaseState_orientation position(::interfaces::msg::BaseState::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_BaseState_orientation(msg_);
  }

private:
  ::interfaces::msg::BaseState msg_;
};

class Init_BaseState_header
{
public:
  Init_BaseState_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_BaseState_position header(::interfaces::msg::BaseState::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_BaseState_position(msg_);
  }

private:
  ::interfaces::msg::BaseState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::BaseState>()
{
  return interfaces::msg::builder::Init_BaseState_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__BASE_STATE__BUILDER_HPP_
