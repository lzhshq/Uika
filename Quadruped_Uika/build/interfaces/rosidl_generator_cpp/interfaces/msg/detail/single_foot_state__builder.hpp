// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/SingleFootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/single_foot_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_SingleFootState_force
{
public:
  explicit Init_SingleFootState_force(::interfaces::msg::SingleFootState & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::SingleFootState force(::interfaces::msg::SingleFootState::_force_type arg)
  {
    msg_.force = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::SingleFootState msg_;
};

class Init_SingleFootState_velocity
{
public:
  explicit Init_SingleFootState_velocity(::interfaces::msg::SingleFootState & msg)
  : msg_(msg)
  {}
  Init_SingleFootState_force velocity(::interfaces::msg::SingleFootState::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_SingleFootState_force(msg_);
  }

private:
  ::interfaces::msg::SingleFootState msg_;
};

class Init_SingleFootState_position
{
public:
  Init_SingleFootState_position()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SingleFootState_velocity position(::interfaces::msg::SingleFootState::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_SingleFootState_velocity(msg_);
  }

private:
  ::interfaces::msg::SingleFootState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::SingleFootState>()
{
  return interfaces::msg::builder::Init_SingleFootState_position();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__BUILDER_HPP_
