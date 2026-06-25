// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/BaseState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_H_
#define INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_H_

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
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"
// Member 'orientation'
#include "geometry_msgs/msg/detail/quaternion__struct.h"
// Member 'linear_velocity'
// Member 'angular_velocity'
#include "geometry_msgs/msg/detail/vector3__struct.h"

/// Struct defined in msg/BaseState in the package interfaces.
typedef struct interfaces__msg__BaseState
{
  /// 消息头：包含时间戳和坐标系名称
  std_msgs__msg__Header header;
  /// 机身位置，单位 m，建议在 world 坐标系下表达
  geometry_msgs__msg__Point position;
  /// 机身姿态，四元数表示
  geometry_msgs__msg__Quaternion orientation;
  /// 机身线速度，单位 m/s
  geometry_msgs__msg__Vector3 linear_velocity;
  /// 机身角速度，单位 rad/s
  geometry_msgs__msg__Vector3 angular_velocity;
} interfaces__msg__BaseState;

// Struct for a sequence of interfaces__msg__BaseState.
typedef struct interfaces__msg__BaseState__Sequence
{
  interfaces__msg__BaseState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__BaseState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_H_
