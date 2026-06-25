// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from interfaces:msg/MotorCommand12.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/motor_command12__rosidl_typesupport_fastrtps_cpp.hpp"
#include "interfaces/msg/detail/motor_command12__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions
namespace std_msgs
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const std_msgs::msg::Header &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  std_msgs::msg::Header &);
size_t get_serialized_size(
  const std_msgs::msg::Header &,
  size_t current_alignment);
size_t
max_serialized_size_Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace std_msgs

namespace interfaces
{
namespace msg
{
namespace typesupport_fastrtps_cpp
{
bool cdr_serialize(
  const interfaces::msg::MotorCommand &,
  eprosima::fastcdr::Cdr &);
bool cdr_deserialize(
  eprosima::fastcdr::Cdr &,
  interfaces::msg::MotorCommand &);
size_t get_serialized_size(
  const interfaces::msg::MotorCommand &,
  size_t current_alignment);
size_t
max_serialized_size_MotorCommand(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);
}  // namespace typesupport_fastrtps_cpp
}  // namespace msg
}  // namespace interfaces

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above

// functions for interfaces::msg::MotorCommand already declared above


namespace interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_interfaces
cdr_serialize(
  const interfaces::msg::MotorCommand12 & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.header,
    cdr);
  // Member: fl_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fl_hip,
    cdr);
  // Member: fl_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fl_thigh,
    cdr);
  // Member: fl_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fl_calf,
    cdr);
  // Member: fr_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fr_hip,
    cdr);
  // Member: fr_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fr_thigh,
    cdr);
  // Member: fr_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.fr_calf,
    cdr);
  // Member: rl_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rl_hip,
    cdr);
  // Member: rl_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rl_thigh,
    cdr);
  // Member: rl_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rl_calf,
    cdr);
  // Member: rr_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rr_hip,
    cdr);
  // Member: rr_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rr_thigh,
    cdr);
  // Member: rr_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_serialize(
    ros_message.rr_calf,
    cdr);
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  interfaces::msg::MotorCommand12 & ros_message)
{
  // Member: header
  std_msgs::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.header);

  // Member: fl_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fl_hip);

  // Member: fl_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fl_thigh);

  // Member: fl_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fl_calf);

  // Member: fr_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fr_hip);

  // Member: fr_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fr_thigh);

  // Member: fr_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.fr_calf);

  // Member: rl_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rl_hip);

  // Member: rl_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rl_thigh);

  // Member: rl_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rl_calf);

  // Member: rr_hip
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rr_hip);

  // Member: rr_thigh
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rr_thigh);

  // Member: rr_calf
  interfaces::msg::typesupport_fastrtps_cpp::cdr_deserialize(
    cdr, ros_message.rr_calf);

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_interfaces
get_serialized_size(
  const interfaces::msg::MotorCommand12 & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: header

  current_alignment +=
    std_msgs::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.header, current_alignment);
  // Member: fl_hip

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fl_hip, current_alignment);
  // Member: fl_thigh

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fl_thigh, current_alignment);
  // Member: fl_calf

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fl_calf, current_alignment);
  // Member: fr_hip

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fr_hip, current_alignment);
  // Member: fr_thigh

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fr_thigh, current_alignment);
  // Member: fr_calf

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.fr_calf, current_alignment);
  // Member: rl_hip

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rl_hip, current_alignment);
  // Member: rl_thigh

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rl_thigh, current_alignment);
  // Member: rl_calf

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rl_calf, current_alignment);
  // Member: rr_hip

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rr_hip, current_alignment);
  // Member: rr_thigh

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rr_thigh, current_alignment);
  // Member: rr_calf

  current_alignment +=
    interfaces::msg::typesupport_fastrtps_cpp::get_serialized_size(
    ros_message.rr_calf, current_alignment);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_interfaces
max_serialized_size_MotorCommand12(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: header
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        std_msgs::msg::typesupport_fastrtps_cpp::max_serialized_size_Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fl_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fl_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fl_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fr_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fr_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: fr_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rl_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rl_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rl_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rr_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rr_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Member: rr_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size =
        interfaces::msg::typesupport_fastrtps_cpp::max_serialized_size_MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = interfaces::msg::MotorCommand12;
    is_plain =
      (
      offsetof(DataType, rr_calf) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _MotorCommand12__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const interfaces::msg::MotorCommand12 *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _MotorCommand12__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<interfaces::msg::MotorCommand12 *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _MotorCommand12__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const interfaces::msg::MotorCommand12 *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _MotorCommand12__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_MotorCommand12(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _MotorCommand12__callbacks = {
  "interfaces::msg",
  "MotorCommand12",
  _MotorCommand12__cdr_serialize,
  _MotorCommand12__cdr_deserialize,
  _MotorCommand12__get_serialized_size,
  _MotorCommand12__max_serialized_size
};

static rosidl_message_type_support_t _MotorCommand12__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_MotorCommand12__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace interfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_interfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<interfaces::msg::MotorCommand12>()
{
  return &interfaces::msg::typesupport_fastrtps_cpp::_MotorCommand12__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, interfaces, msg, MotorCommand12)() {
  return &interfaces::msg::typesupport_fastrtps_cpp::_MotorCommand12__handle;
}

#ifdef __cplusplus
}
#endif
