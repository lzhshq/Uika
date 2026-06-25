// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/GaitPhase.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_H_
#define INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'STANCE'.
/**
  * 支撑相
 */
enum
{
  interfaces__msg__GaitPhase__STANCE = 0
};

/// Constant 'SWING'.
/**
  * 摆动相
 */
enum
{
  interfaces__msg__GaitPhase__SWING = 1
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/GaitPhase in the package interfaces.
typedef struct interfaces__msg__GaitPhase
{
  /// 消息头：包含时间戳和坐标系名称
  std_msgs__msg__Header header;
  /// 左前腿当前相位，取值：STANCE 或 SWING
  uint8_t fl_phase;
  /// 右前腿当前相位，取值：STANCE 或 SWING
  uint8_t fr_phase;
  /// 左后腿当前相位，取值：STANCE 或 SWING
  uint8_t rl_phase;
  /// 右后腿当前相位，取值：STANCE 或 SWING
  uint8_t rr_phase;
} interfaces__msg__GaitPhase;

// Struct for a sequence of interfaces__msg__GaitPhase.
typedef struct interfaces__msg__GaitPhase__Sequence
{
  interfaces__msg__GaitPhase * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__GaitPhase__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_H_
