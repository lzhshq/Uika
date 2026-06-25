// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotorCommand12.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_H_

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
#include "interfaces/msg/detail/motor_command__struct.h"

/// Struct defined in msg/MotorCommand12 in the package interfaces.
typedef struct interfaces__msg__MotorCommand12
{
  /// 消息头：包含时间戳
  std_msgs__msg__Header header;
  /// 左前髋关节电机命令
  interfaces__msg__MotorCommand fl_hip;
  /// 左前大腿关节电机命令
  interfaces__msg__MotorCommand fl_thigh;
  /// 左前小腿关节电机命令
  interfaces__msg__MotorCommand fl_calf;
  /// 右前髋关节电机命令
  interfaces__msg__MotorCommand fr_hip;
  /// 右前大腿关节电机命令
  interfaces__msg__MotorCommand fr_thigh;
  /// 右前小腿关节电机命令
  interfaces__msg__MotorCommand fr_calf;
  /// 左后髋关节电机命令
  interfaces__msg__MotorCommand rl_hip;
  /// 左后大腿关节电机命令
  interfaces__msg__MotorCommand rl_thigh;
  /// 左后小腿关节电机命令
  interfaces__msg__MotorCommand rl_calf;
  /// 右后髋关节电机命令
  interfaces__msg__MotorCommand rr_hip;
  /// 右后大腿关节电机命令
  interfaces__msg__MotorCommand rr_thigh;
  /// 右后小腿关节电机命令
  interfaces__msg__MotorCommand rr_calf;
} interfaces__msg__MotorCommand12;

// Struct for a sequence of interfaces__msg__MotorCommand12.
typedef struct interfaces__msg__MotorCommand12__Sequence
{
  interfaces__msg__MotorCommand12 * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotorCommand12__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_H_
