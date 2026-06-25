// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotionCommand.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_H_

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

/// Struct defined in msg/MotionCommand in the package interfaces.
typedef struct interfaces__msg__MotionCommand
{
  /// 消息头：主要用于时间戳
  std_msgs__msg__Header header;
  /// 机器人期望前向速度，单位 m/s
  double vx;
  /// 机器人期望侧向速度，单位 m/s
  double vy;
  /// 机器人期望偏航角速度，单位 rad/s
  double wz;
  /// 机器人期望机身高度，单位 m
  double body_height;
} interfaces__msg__MotionCommand;

// Struct for a sequence of interfaces__msg__MotionCommand.
typedef struct interfaces__msg__MotionCommand__Sequence
{
  interfaces__msg__MotionCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotionCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_H_
