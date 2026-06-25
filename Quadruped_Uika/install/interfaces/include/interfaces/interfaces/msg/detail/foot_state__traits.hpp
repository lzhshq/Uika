// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/FootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__FOOT_STATE__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__FOOT_STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interfaces/msg/detail/foot_state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'fl'
// Member 'fr'
// Member 'rl'
// Member 'rr'
#include "interfaces/msg/detail/single_foot_state__traits.hpp"

namespace interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const FootState & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: fl
  {
    out << "fl: ";
    to_flow_style_yaml(msg.fl, out);
    out << ", ";
  }

  // member: fr
  {
    out << "fr: ";
    to_flow_style_yaml(msg.fr, out);
    out << ", ";
  }

  // member: rl
  {
    out << "rl: ";
    to_flow_style_yaml(msg.rl, out);
    out << ", ";
  }

  // member: rr
  {
    out << "rr: ";
    to_flow_style_yaml(msg.rr, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const FootState & msg,
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

  // member: fl
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fl:\n";
    to_block_style_yaml(msg.fl, out, indentation + 2);
  }

  // member: fr
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fr:\n";
    to_block_style_yaml(msg.fr, out, indentation + 2);
  }

  // member: rl
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rl:\n";
    to_block_style_yaml(msg.rl, out, indentation + 2);
  }

  // member: rr
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rr:\n";
    to_block_style_yaml(msg.rr, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const FootState & msg, bool use_flow_style = false)
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
  const interfaces::msg::FootState & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::msg::FootState & msg)
{
  return interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::msg::FootState>()
{
  return "interfaces::msg::FootState";
}

template<>
inline const char * name<interfaces::msg::FootState>()
{
  return "interfaces/msg/FootState";
}

template<>
struct has_fixed_size<interfaces::msg::FootState>
  : std::integral_constant<bool, has_fixed_size<interfaces::msg::SingleFootState>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<interfaces::msg::FootState>
  : std::integral_constant<bool, has_bounded_size<interfaces::msg::SingleFootState>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<interfaces::msg::FootState>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__FOOT_STATE__TRAITS_HPP_
