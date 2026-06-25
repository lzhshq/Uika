// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/FootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_H_
#define INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_H_

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
// Member 'fl'
// Member 'fr'
// Member 'rl'
// Member 'rr'
#include "interfaces/msg/detail/single_foot_state__struct.h"

/// Struct defined in msg/FootState in the package interfaces.
typedef struct interfaces__msg__FootState
{
  /// 消息头：包含时间戳和坐标系名称
  std_msgs__msg__Header header;
  /// 左前腿足端状态
  interfaces__msg__SingleFootState fl;
  /// 右前腿足端状态
  interfaces__msg__SingleFootState fr;
  /// 左后腿足端状态
  interfaces__msg__SingleFootState rl;
  /// 右后腿足端状态
  interfaces__msg__SingleFootState rr;
} interfaces__msg__FootState;

// Struct for a sequence of interfaces__msg__FootState.
typedef struct interfaces__msg__FootState__Sequence
{
  interfaces__msg__FootState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__FootState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_H_
