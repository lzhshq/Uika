// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotorCommand.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/MotorCommand in the package interfaces.
typedef struct interfaces__msg__MotorCommand
{
  /// 电机前馈力矩，单位 N·m
  double torque;
  /// 电机目标位置，单位 rad
  double position;
  /// 电机目标速度，单位 rad/s
  double velocity;
  /// 位置环增益
  double kp;
  /// 速度环增益
  double kd;
} interfaces__msg__MotorCommand;

// Struct for a sequence of interfaces__msg__MotorCommand.
typedef struct interfaces__msg__MotorCommand__Sequence
{
  interfaces__msg__MotorCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotorCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTOR_COMMAND__STRUCT_H_
