// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/MotorCommand12.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interfaces/msg/detail/motor_command12__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'fl_hip'
// Member 'fl_thigh'
// Member 'fl_calf'
// Member 'fr_hip'
// Member 'fr_thigh'
// Member 'fr_calf'
// Member 'rl_hip'
// Member 'rl_thigh'
// Member 'rl_calf'
// Member 'rr_hip'
// Member 'rr_thigh'
// Member 'rr_calf'
#include "interfaces/msg/detail/motor_command__traits.hpp"

namespace interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MotorCommand12 & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: fl_hip
  {
    out << "fl_hip: ";
    to_flow_style_yaml(msg.fl_hip, out);
    out << ", ";
  }

  // member: fl_thigh
  {
    out << "fl_thigh: ";
    to_flow_style_yaml(msg.fl_thigh, out);
    out << ", ";
  }

  // member: fl_calf
  {
    out << "fl_calf: ";
    to_flow_style_yaml(msg.fl_calf, out);
    out << ", ";
  }

  // member: fr_hip
  {
    out << "fr_hip: ";
    to_flow_style_yaml(msg.fr_hip, out);
    out << ", ";
  }

  // member: fr_thigh
  {
    out << "fr_thigh: ";
    to_flow_style_yaml(msg.fr_thigh, out);
    out << ", ";
  }

  // member: fr_calf
  {
    out << "fr_calf: ";
    to_flow_style_yaml(msg.fr_calf, out);
    out << ", ";
  }

  // member: rl_hip
  {
    out << "rl_hip: ";
    to_flow_style_yaml(msg.rl_hip, out);
    out << ", ";
  }

  // member: rl_thigh
  {
    out << "rl_thigh: ";
    to_flow_style_yaml(msg.rl_thigh, out);
    out << ", ";
  }

  // member: rl_calf
  {
    out << "rl_calf: ";
    to_flow_style_yaml(msg.rl_calf, out);
    out << ", ";
  }

  // member: rr_hip
  {
    out << "rr_hip: ";
    to_flow_style_yaml(msg.rr_hip, out);
    out << ", ";
  }

  // member: rr_thigh
  {
    out << "rr_thigh: ";
    to_flow_style_yaml(msg.rr_thigh, out);
    out << ", ";
  }

  // member: rr_calf
  {
    out << "rr_calf: ";
    to_flow_style_yaml(msg.rr_calf, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MotorCommand12 & msg,
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

  // member: fl_hip
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fl_hip:\n";
    to_block_style_yaml(msg.fl_hip, out, indentation + 2);
  }

  // member: fl_thigh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fl_thigh:\n";
    to_block_style_yaml(msg.fl_thigh, out, indentation + 2);
  }

  // member: fl_calf
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fl_calf:\n";
    to_block_style_yaml(msg.fl_calf, out, indentation + 2);
  }

  // member: fr_hip
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fr_hip:\n";
    to_block_style_yaml(msg.fr_hip, out, indentation + 2);
  }

  // member: fr_thigh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fr_thigh:\n";
    to_block_style_yaml(msg.fr_thigh, out, indentation + 2);
  }

  // member: fr_calf
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fr_calf:\n";
    to_block_style_yaml(msg.fr_calf, out, indentation + 2);
  }

  // member: rl_hip
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rl_hip:\n";
    to_block_style_yaml(msg.rl_hip, out, indentation + 2);
  }

  // member: rl_thigh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rl_thigh:\n";
    to_block_style_yaml(msg.rl_thigh, out, indentation + 2);
  }

  // member: rl_calf
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rl_calf:\n";
    to_block_style_yaml(msg.rl_calf, out, indentation + 2);
  }

  // member: rr_hip
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rr_hip:\n";
    to_block_style_yaml(msg.rr_hip, out, indentation + 2);
  }

  // member: rr_thigh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rr_thigh:\n";
    to_block_style_yaml(msg.rr_thigh, out, indentation + 2);
  }

  // member: rr_calf
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rr_calf:\n";
    to_block_style_yaml(msg.rr_calf, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MotorCommand12 & msg, bool use_flow_style = false)
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
  const interfaces::msg::MotorCommand12 & msg,
  std::ostream & out, size_t indentation = 0)
{
  interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const interfaces::msg::MotorCommand12 & msg)
{
  return interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<interfaces::msg::MotorCommand12>()
{
  return "interfaces::msg::MotorCommand12";
}

template<>
inline const char * name<interfaces::msg::MotorCommand12>()
{
  return "interfaces/msg/MotorCommand12";
}

template<>
struct has_fixed_size<interfaces::msg::MotorCommand12>
  : std::integral_constant<bool, has_fixed_size<interfaces::msg::MotorCommand>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<interfaces::msg::MotorCommand12>
  : std::integral_constant<bool, has_bounded_size<interfaces::msg::MotorCommand>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<interfaces::msg::MotorCommand12>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__TRAITS_HPP_
