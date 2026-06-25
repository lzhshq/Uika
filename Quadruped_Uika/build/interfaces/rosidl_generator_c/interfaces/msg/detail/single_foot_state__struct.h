// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/SingleFootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_H_
#define INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"
// Member 'velocity'
// Member 'force'
#include "geometry_msgs/msg/detail/vector3__struct.h"

/// Struct defined in msg/SingleFootState in the package interfaces.
typedef struct interfaces__msg__SingleFootState
{
  /// 单条腿足端位置，单位 m
  geometry_msgs__msg__Point position;
  /// 单条腿足端速度，单位 m/s
  geometry_msgs__msg__Vector3 velocity;
  /// 单条腿足端受力或期望力，单位 N
  geometry_msgs__msg__Vector3 force;
} interfaces__msg__SingleFootState;

// Struct for a sequence of interfaces__msg__SingleFootState.
typedef struct interfaces__msg__SingleFootState__Sequence
{
  interfaces__msg__SingleFootState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__SingleFootState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_H_
