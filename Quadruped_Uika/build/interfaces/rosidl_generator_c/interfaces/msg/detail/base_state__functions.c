// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interfaces:msg/BaseState.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/base_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `position`
#include "geometry_msgs/msg/detail/point__functions.h"
// Member `orientation`
#include "geometry_msgs/msg/detail/quaternion__functions.h"
// Member `linear_velocity`
// Member `angular_velocity`
#include "geometry_msgs/msg/detail/vector3__functions.h"

bool
interfaces__msg__BaseState__init(interfaces__msg__BaseState * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    interfaces__msg__BaseState__fini(msg);
    return false;
  }
  // position
  if (!geometry_msgs__msg__Point__init(&msg->position)) {
    interfaces__msg__BaseState__fini(msg);
    return false;
  }
  // orientation
  if (!geometry_msgs__msg__Quaternion__init(&msg->orientation)) {
    interfaces__msg__BaseState__fini(msg);
    return false;
  }
  // linear_velocity
  if (!geometry_msgs__msg__Vector3__init(&msg->linear_velocity)) {
    interfaces__msg__BaseState__fini(msg);
    return false;
  }
  // angular_velocity
  if (!geometry_msgs__msg__Vector3__init(&msg->angular_velocity)) {
    interfaces__msg__BaseState__fini(msg);
    return false;
  }
  return true;
}

void
interfaces__msg__BaseState__fini(interfaces__msg__BaseState * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // position
  geometry_msgs__msg__Point__fini(&msg->position);
  // orientation
  geometry_msgs__msg__Quaternion__fini(&msg->orientation);
  // linear_velocity
  geometry_msgs__msg__Vector3__fini(&msg->linear_velocity);
  // angular_velocity
  geometry_msgs__msg__Vector3__fini(&msg->angular_velocity);
}

bool
interfaces__msg__BaseState__are_equal(const interfaces__msg__BaseState * lhs, const interfaces__msg__BaseState * rhs)
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
  // position
  if (!geometry_msgs__msg__Point__are_equal(
      &(lhs->position), &(rhs->position)))
  {
    return false;
  }
  // orientation
  if (!geometry_msgs__msg__Quaternion__are_equal(
      &(lhs->orientation), &(rhs->orientation)))
  {
    return false;
  }
  // linear_velocity
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->linear_velocity), &(rhs->linear_velocity)))
  {
    return false;
  }
  // angular_velocity
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->angular_velocity), &(rhs->angular_velocity)))
  {
    return false;
  }
  return true;
}

bool
interfaces__msg__BaseState__copy(
  const interfaces__msg__BaseState * input,
  interfaces__msg__BaseState * output)
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
  // position
  if (!geometry_msgs__msg__Point__copy(
      &(input->position), &(output->position)))
  {
    return false;
  }
  // orientation
  if (!geometry_msgs__msg__Quaternion__copy(
      &(input->orientation), &(output->orientation)))
  {
    return false;
  }
  // linear_velocity
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->linear_velocity), &(output->linear_velocity)))
  {
    return false;
  }
  // angular_velocity
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->angular_velocity), &(output->angular_velocity)))
  {
    return false;
  }
  return true;
}

interfaces__msg__BaseState *
interfaces__msg__BaseState__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__BaseState * msg = (interfaces__msg__BaseState *)allocator.allocate(sizeof(interfaces__msg__BaseState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interfaces__msg__BaseState));
  bool success = interfaces__msg__BaseState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interfaces__msg__BaseState__destroy(interfaces__msg__BaseState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interfaces__msg__BaseState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interfaces__msg__BaseState__Sequence__init(interfaces__msg__BaseState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__BaseState * data = NULL;

  if (size) {
    data = (interfaces__msg__BaseState *)allocator.zero_allocate(size, sizeof(interfaces__msg__BaseState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interfaces__msg__BaseState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interfaces__msg__BaseState__fini(&data[i - 1]);
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
interfaces__msg__BaseState__Sequence__fini(interfaces__msg__BaseState__Sequence * array)
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
      interfaces__msg__BaseState__fini(&array->data[i]);
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

interfaces__msg__BaseState__Sequence *
interfaces__msg__BaseState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__BaseState__Sequence * array = (interfaces__msg__BaseState__Sequence *)allocator.allocate(sizeof(interfaces__msg__BaseState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interfaces__msg__BaseState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interfaces__msg__BaseState__Sequence__destroy(interfaces__msg__BaseState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interfaces__msg__BaseState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interfaces__msg__BaseState__Sequence__are_equal(const interfaces__msg__BaseState__Sequence * lhs, const interfaces__msg__BaseState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interfaces__msg__BaseState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interfaces__msg__BaseState__Sequence__copy(
  const interfaces__msg__BaseState__Sequence * input,
  interfaces__msg__BaseState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interfaces__msg__BaseState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interfaces__msg__BaseState * data =
      (interfaces__msg__BaseState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interfaces__msg__BaseState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interfaces__msg__BaseState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interfaces__msg__BaseState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
