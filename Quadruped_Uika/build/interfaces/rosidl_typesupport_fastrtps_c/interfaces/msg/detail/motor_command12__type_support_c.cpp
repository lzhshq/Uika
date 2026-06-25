// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from interfaces:msg/MotorCommand12.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/motor_command12__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "interfaces/msg/detail/motor_command12__struct.h"
#include "interfaces/msg/detail/motor_command12__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "interfaces/msg/detail/motor_command__functions.h"  // fl_calf, fl_hip, fl_thigh, fr_calf, fr_hip, fr_thigh, rl_calf, rl_hip, rl_thigh, rr_calf, rr_hip, rr_thigh
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions
size_t get_serialized_size_interfaces__msg__MotorCommand(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_interfaces__msg__MotorCommand(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand)();
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_interfaces
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_interfaces
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _MotorCommand12__ros_msg_type = interfaces__msg__MotorCommand12;

static bool _MotorCommand12__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _MotorCommand12__ros_msg_type * ros_message = static_cast<const _MotorCommand12__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->header, cdr))
    {
      return false;
    }
  }

  // Field name: fl_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fl_hip, cdr))
    {
      return false;
    }
  }

  // Field name: fl_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fl_thigh, cdr))
    {
      return false;
    }
  }

  // Field name: fl_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fl_calf, cdr))
    {
      return false;
    }
  }

  // Field name: fr_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fr_hip, cdr))
    {
      return false;
    }
  }

  // Field name: fr_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fr_thigh, cdr))
    {
      return false;
    }
  }

  // Field name: fr_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->fr_calf, cdr))
    {
      return false;
    }
  }

  // Field name: rl_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rl_hip, cdr))
    {
      return false;
    }
  }

  // Field name: rl_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rl_thigh, cdr))
    {
      return false;
    }
  }

  // Field name: rl_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rl_calf, cdr))
    {
      return false;
    }
  }

  // Field name: rr_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rr_hip, cdr))
    {
      return false;
    }
  }

  // Field name: rr_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rr_thigh, cdr))
    {
      return false;
    }
  }

  // Field name: rr_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->rr_calf, cdr))
    {
      return false;
    }
  }

  return true;
}

static bool _MotorCommand12__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _MotorCommand12__ros_msg_type * ros_message = static_cast<_MotorCommand12__ros_msg_type *>(untyped_ros_message);
  // Field name: header
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, std_msgs, msg, Header
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->header))
    {
      return false;
    }
  }

  // Field name: fl_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fl_hip))
    {
      return false;
    }
  }

  // Field name: fl_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fl_thigh))
    {
      return false;
    }
  }

  // Field name: fl_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fl_calf))
    {
      return false;
    }
  }

  // Field name: fr_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fr_hip))
    {
      return false;
    }
  }

  // Field name: fr_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fr_thigh))
    {
      return false;
    }
  }

  // Field name: fr_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->fr_calf))
    {
      return false;
    }
  }

  // Field name: rl_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rl_hip))
    {
      return false;
    }
  }

  // Field name: rl_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rl_thigh))
    {
      return false;
    }
  }

  // Field name: rl_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rl_calf))
    {
      return false;
    }
  }

  // Field name: rr_hip
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rr_hip))
    {
      return false;
    }
  }

  // Field name: rr_thigh
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rr_thigh))
    {
      return false;
    }
  }

  // Field name: rr_calf
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->rr_calf))
    {
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_interfaces
size_t get_serialized_size_interfaces__msg__MotorCommand12(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _MotorCommand12__ros_msg_type * ros_message = static_cast<const _MotorCommand12__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name header

  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);
  // field.name fl_hip

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fl_hip), current_alignment);
  // field.name fl_thigh

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fl_thigh), current_alignment);
  // field.name fl_calf

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fl_calf), current_alignment);
  // field.name fr_hip

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fr_hip), current_alignment);
  // field.name fr_thigh

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fr_thigh), current_alignment);
  // field.name fr_calf

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->fr_calf), current_alignment);
  // field.name rl_hip

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rl_hip), current_alignment);
  // field.name rl_thigh

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rl_thigh), current_alignment);
  // field.name rl_calf

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rl_calf), current_alignment);
  // field.name rr_hip

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rr_hip), current_alignment);
  // field.name rr_thigh

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rr_thigh), current_alignment);
  // field.name rr_calf

  current_alignment += get_serialized_size_interfaces__msg__MotorCommand(
    &(ros_message->rr_calf), current_alignment);

  return current_alignment - initial_alignment;
}

static uint32_t _MotorCommand12__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_interfaces__msg__MotorCommand12(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_interfaces
size_t max_serialized_size_interfaces__msg__MotorCommand12(
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

  // member: header
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fl_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fl_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fl_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fr_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fr_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: fr_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rl_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rl_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rl_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rr_hip
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rr_thigh
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }
  // member: rr_calf
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_interfaces__msg__MotorCommand(
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
    using DataType = interfaces__msg__MotorCommand12;
    is_plain =
      (
      offsetof(DataType, rr_calf) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _MotorCommand12__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_interfaces__msg__MotorCommand12(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_MotorCommand12 = {
  "interfaces::msg",
  "MotorCommand12",
  _MotorCommand12__cdr_serialize,
  _MotorCommand12__cdr_deserialize,
  _MotorCommand12__get_serialized_size,
  _MotorCommand12__max_serialized_size
};

static rosidl_message_type_support_t _MotorCommand12__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_MotorCommand12,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, interfaces, msg, MotorCommand12)() {
  return &_MotorCommand12__type_support;
}

#if defined(__cplusplus)
}
#endif
