// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/ContactState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_H_
#define INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/ContactState in the package interfaces.
typedef struct interfaces__msg__ContactState
{
  /// 消息头：包含时间戳和坐标系名称
  std_msgs__msg__Header header;
  /// 左前腿是否接触地面，true 表示接触
  bool fl_contact;
  /// 右前腿是否接触地面，true 表示接触
  bool fr_contact;
  /// 左后腿是否接触地面，true 表示接触
  bool rl_contact;
  /// 右后腿是否接触地面，true 表示接触
  bool rr_contact;
} interfaces__msg__ContactState;

// Struct for a sequence of interfaces__msg__ContactState.
typedef struct interfaces__msg__ContactState__Sequence
{
  interfaces__msg__ContactState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__ContactState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_H_
