// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/MotorFeedback12.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__STRUCT_H_
#define INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__STRUCT_H_

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
#include "interfaces/msg/detail/motor_feedback__struct.h"

/// Struct defined in msg/MotorFeedback12 in the package interfaces.
typedef struct interfaces__msg__MotorFeedback12
{
  std_msgs__msg__Header header;
  interfaces__msg__MotorFeedback fl_hip;
  interfaces__msg__MotorFeedback fl_thigh;
  interfaces__msg__MotorFeedback fl_calf;
  interfaces__msg__MotorFeedback fr_hip;
  interfaces__msg__MotorFeedback fr_thigh;
  interfaces__msg__MotorFeedback fr_calf;
  interfaces__msg__MotorFeedback rl_hip;
  interfaces__msg__MotorFeedback rl_thigh;
  interfaces__msg__MotorFeedback rl_calf;
  interfaces__msg__MotorFeedback rr_hip;
  interfaces__msg__MotorFeedback rr_thigh;
  interfaces__msg__MotorFeedback rr_calf;
} interfaces__msg__MotorFeedback12;

// Struct for a sequence of interfaces__msg__MotorFeedback12.
typedef struct interfaces__msg__MotorFeedback12__Sequence
{
  interfaces__msg__MotorFeedback12 * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__MotorFeedback12__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__MOTOR_FEEDBACK12__STRUCT_H_
