// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/ContactState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__CONTACT_STATE__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__CONTACT_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interfaces/msg/detail/contact_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const ContactState & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: fl_contact
  {
    out << "fl_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.fl_contact, out);
    out << ", ";
  }

  // member: fr_contact
  {
    out << "fr_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.fr_contact, out);
    out << ", ";
  }

  // member: rl_contact
  {
    out << "rl_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.rl_contact, out);
    out << ", ";
  }

  // member: rr_contact
  {
    out << "rr_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.rr_contact, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ContactState & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: fl_contact
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fl_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.fl_contact, out);
    out << "\n";
  }

  // member: fr_contact
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fr_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.fr_contact, out);
    out << "\n";
  }

  // member: rl_contact
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rl_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.rl_contact, out);
    out << "\n";
  }

  // member: rr_contact
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rr_contact: ";
    rosidl_generator_traits::value_to_yaml(msg.rr_contact, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ContactState & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace interfaces

namespace rosidl_generator_traits
{

[[deprecated("use interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const interfaces::msg::ContactState & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::msg::ContactState & msg)
{
  return interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::msg::ContactState>()
{
  return "interfaces::msg::ContactState";
}

template<>
inline const char * name<interfaces::msg::ContactState>()
{
  return "interfaces/msg/ContactState";
}

template<>
struct has_fixed_size<interfaces::msg::ContactState>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<interfaces::msg::ContactState>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<interfaces::msg::ContactState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__CONTACT_STATE__TRAITS_HPP_
