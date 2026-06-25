// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/ContactState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__CONTACT_STATE__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__CONTACT_STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interfaces/msg/detail/contact_state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_ContactState_rr_contact
{
public:
  explicit Init_ContactState_rr_contact(::interfaces::msg::ContactState & msg)
  : msg_(msg)
  {}
  ::interfaces::msg::ContactState rr_contact(::interfaces::msg::ContactState::_rr_contact_type arg)
  {
    msg_.rr_contact = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::ContactState msg_;
};

class Init_ContactState_rl_contact
{
public:
  explicit Init_ContactState_rl_contact(::interfaces::msg::ContactState & msg)
  : msg_(msg)
  {}
  Init_ContactState_rr_contact rl_contact(::interfaces::msg::ContactState::_rl_contact_type arg)
  {
    msg_.rl_contact = std::move(arg);
    return Init_ContactState_rr_contact(msg_);
  }

private:
  ::interfaces::msg::ContactState msg_;
};

class Init_ContactState_fr_contact
{
public:
  explicit Init_ContactState_fr_contact(::interfaces::msg::ContactState & msg)
  : msg_(msg)
  {}
  Init_ContactState_rl_contact fr_contact(::interfaces::msg::ContactState::_fr_contact_type arg)
  {
    msg_.fr_contact = std::move(arg);
    return Init_ContactState_rl_contact(msg_);
  }

private:
  ::interfaces::msg::ContactState msg_;
};

class Init_ContactState_fl_contact
{
public:
  explicit Init_ContactState_fl_contact(::interfaces::msg::ContactState & msg)
  : msg_(msg)
  {}
  Init_ContactState_fr_contact fl_contact(::interfaces::msg::ContactState::_fl_contact_type arg)
  {
    msg_.fl_contact = std::move(arg);
    return Init_ContactState_fr_contact(msg_);
  }

private:
  ::interfaces::msg::ContactState msg_;
};

class Init_ContactState_header
{
public:
  Init_ContactState_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ContactState_fl_contact header(::interfaces::msg::ContactState::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ContactState_fl_contact(msg_);
  }

private:
  ::interfaces::msg::ContactState msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::ContactState>()
{
  return interfaces::msg::builder::Init_ContactState_header();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__CONTACT_STATE__BUILDER_HPP_
