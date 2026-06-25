// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interfaces:msg/MotorFeedback12.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/motor_feedback12__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `fl_hip`
// Member `fl_thigh`
// Member `fl_calf`
// Member `fr_hip`
// Member `fr_thigh`
// Member `fr_calf`
// Member `rl_hip`
// Member `rl_thigh`
// Member `rl_calf`
// Member `rr_hip`
// Member `rr_thigh`
// Member `rr_calf`
#include "interfaces/msg/detail/motor_feedback__functions.h"

bool
interfaces__msg__MotorFeedback12__init(interfaces__msg__MotorFeedback12 * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fl_hip
  if (!interfaces__msg__MotorFeedback__init(&msg->fl_hip)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fl_thigh
  if (!interfaces__msg__MotorFeedback__init(&msg->fl_thigh)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fl_calf
  if (!interfaces__msg__MotorFeedback__init(&msg->fl_calf)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fr_hip
  if (!interfaces__msg__MotorFeedback__init(&msg->fr_hip)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fr_thigh
  if (!interfaces__msg__MotorFeedback__init(&msg->fr_thigh)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // fr_calf
  if (!interfaces__msg__MotorFeedback__init(&msg->fr_calf)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rl_hip
  if (!interfaces__msg__MotorFeedback__init(&msg->rl_hip)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rl_thigh
  if (!interfaces__msg__MotorFeedback__init(&msg->rl_thigh)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rl_calf
  if (!interfaces__msg__MotorFeedback__init(&msg->rl_calf)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rr_hip
  if (!interfaces__msg__MotorFeedback__init(&msg->rr_hip)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rr_thigh
  if (!interfaces__msg__MotorFeedback__init(&msg->rr_thigh)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  // rr_calf
  if (!interfaces__msg__MotorFeedback__init(&msg->rr_calf)) {
    interfaces__msg__MotorFeedback12__fini(msg);
    return false;
  }
  return true;
}

void
interfaces__msg__MotorFeedback12__fini(interfaces__msg__MotorFeedback12 * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // fl_hip
  interfaces__msg__MotorFeedback__fini(&msg->fl_hip);
  // fl_thigh
  interfaces__msg__MotorFeedback__fini(&msg->fl_thigh);
  // fl_calf
  interfaces__msg__MotorFeedback__fini(&msg->fl_calf);
  // fr_hip
  interfaces__msg__MotorFeedback__fini(&msg->fr_hip);
  // fr_thigh
  interfaces__msg__MotorFeedback__fini(&msg->fr_thigh);
  // fr_calf
  interfaces__msg__MotorFeedback__fini(&msg->fr_calf);
  // rl_hip
  interfaces__msg__MotorFeedback__fini(&msg->rl_hip);
  // rl_thigh
  interfaces__msg__MotorFeedback__fini(&msg->rl_thigh);
  // rl_calf
  interfaces__msg__MotorFeedback__fini(&msg->rl_calf);
  // rr_hip
  interfaces__msg__MotorFeedback__fini(&msg->rr_hip);
  // rr_thigh
  interfaces__msg__MotorFeedback__fini(&msg->rr_thigh);
  // rr_calf
  interfaces__msg__MotorFeedback__fini(&msg->rr_calf);
}

bool
interfaces__msg__MotorFeedback12__are_equal(const interfaces__msg__MotorFeedback12 * lhs, const interfaces__msg__MotorFeedback12 * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // fl_hip
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fl_hip), &(rhs->fl_hip)))
  {
    return false;
  }
  // fl_thigh
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fl_thigh), &(rhs->fl_thigh)))
  {
    return false;
  }
  // fl_calf
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fl_calf), &(rhs->fl_calf)))
  {
    return false;
  }
  // fr_hip
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fr_hip), &(rhs->fr_hip)))
  {
    return false;
  }
  // fr_thigh
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fr_thigh), &(rhs->fr_thigh)))
  {
    return false;
  }
  // fr_calf
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->fr_calf), &(rhs->fr_calf)))
  {
    return false;
  }
  // rl_hip
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rl_hip), &(rhs->rl_hip)))
  {
    return false;
  }
  // rl_thigh
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rl_thigh), &(rhs->rl_thigh)))
  {
    return false;
  }
  // rl_calf
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rl_calf), &(rhs->rl_calf)))
  {
    return false;
  }
  // rr_hip
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rr_hip), &(rhs->rr_hip)))
  {
    return false;
  }
  // rr_thigh
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rr_thigh), &(rhs->rr_thigh)))
  {
    return false;
  }
  // rr_calf
  if (!interfaces__msg__MotorFeedback__are_equal(
      &(lhs->rr_calf), &(rhs->rr_calf)))
  {
    return false;
  }
  return true;
}

bool
interfaces__msg__MotorFeedback12__copy(
  const interfaces__msg__MotorFeedback12 * input,
  interfaces__msg__MotorFeedback12 * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // fl_hip
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fl_hip), &(output->fl_hip)))
  {
    return false;
  }
  // fl_thigh
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fl_thigh), &(output->fl_thigh)))
  {
    return false;
  }
  // fl_calf
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fl_calf), &(output->fl_calf)))
  {
    return false;
  }
  // fr_hip
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fr_hip), &(output->fr_hip)))
  {
    return false;
  }
  // fr_thigh
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fr_thigh), &(output->fr_thigh)))
  {
    return false;
  }
  // fr_calf
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->fr_calf), &(output->fr_calf)))
  {
    return false;
  }
  // rl_hip
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rl_hip), &(output->rl_hip)))
  {
    return false;
  }
  // rl_thigh
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rl_thigh), &(output->rl_thigh)))
  {
    return false;
  }
  // rl_calf
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rl_calf), &(output->rl_calf)))
  {
    return false;
  }
  // rr_hip
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rr_hip), &(output->rr_hip)))
  {
    return false;
  }
  // rr_thigh
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rr_thigh), &(output->rr_thigh)))
  {
    return false;
  }
  // rr_calf
  if (!interfaces__msg__MotorFeedback__copy(
      &(input->rr_calf), &(output->rr_calf)))
  {
    return false;
  }
  return true;
}

interfaces__msg__MotorFeedback12 *
interfaces__msg__MotorFeedback12__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorFeedback12 * msg = (interfaces__msg__MotorFeedback12 *)allocator.allocate(sizeof(interfaces__msg__MotorFeedback12), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interfaces__msg__MotorFeedback12));
  bool success = interfaces__msg__MotorFeedback12__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interfaces__msg__MotorFeedback12__destroy(interfaces__msg__MotorFeedback12 * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interfaces__msg__MotorFeedback12__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interfaces__msg__MotorFeedback12__Sequence__init(interfaces__msg__MotorFeedback12__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorFeedback12 * data = NULL;

  if (size) {
    data = (interfaces__msg__MotorFeedback12 *)allocator.zero_allocate(size, sizeof(interfaces__msg__MotorFeedback12), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interfaces__msg__MotorFeedback12__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interfaces__msg__MotorFeedback12__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
interfaces__msg__MotorFeedback12__Sequence__fini(interfaces__msg__MotorFeedback12__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      interfaces__msg__MotorFeedback12__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

interfaces__msg__MotorFeedback12__Sequence *
interfaces__msg__MotorFeedback12__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__MotorFeedback12__Sequence * array = (interfaces__msg__MotorFeedback12__Sequence *)allocator.allocate(sizeof(interfaces__msg__MotorFeedback12__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interfaces__msg__MotorFeedback12__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interfaces__msg__MotorFeedback12__Sequence__destroy(interfaces__msg__MotorFeedback12__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interfaces__msg__MotorFeedback12__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interfaces__msg__MotorFeedback12__Sequence__are_equal(const interfaces__msg__MotorFeedback12__Sequence * lhs, const interfaces__msg__MotorFeedback12__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interfaces__msg__MotorFeedback12__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interfaces__msg__MotorFeedback12__Sequence__copy(
  const interfaces__msg__MotorFeedback12__Sequence * input,
  interfaces__msg__MotorFeedback12__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interfaces__msg__MotorFeedback12);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interfaces__msg__MotorFeedback12 * data =
      (interfaces__msg__MotorFeedback12 *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interfaces__msg__MotorFeedback12__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interfaces__msg__MotorFeedback12__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interfaces__msg__MotorFeedback12__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
