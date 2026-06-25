// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotorFeedback.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/MotorFeedback in the package interfaces.
typedef struct interfaces__msg__MotorFeedback
{
  /// 反馈力矩 (N·m)
  double torque;
  /// 反馈位置 (rad)
  double position;
  /// 反馈速度 (rad/s)
  double velocity;
  /// 电机温度 (°C)
  double temperature;
} interfaces__msg__MotorFeedback;

// Struct for a sequence of interfaces__msg__MotorFeedback.
typedef struct interfaces__msg__MotorFeedback__Sequence
{
  interfaces__msg__MotorFeedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotorFeedback__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK__STRUCT_H_
