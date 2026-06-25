// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interfaces:msg/FootState.idl
// generated code does not contain a copyright notice
#include "interfaces/msg/detail/foot_state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `fl`
// Member `fr`
// Member `rl`
// Member `rr`
#include "interfaces/msg/detail/single_foot_state__functions.h"

bool
interfaces__msg__FootState__init(interfaces__msg__FootState * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    interfaces__msg__FootState__fini(msg);
    return false;
  }
  // fl
  if (!interfaces__msg__SingleFootState__init(&msg->fl)) {
    interfaces__msg__FootState__fini(msg);
    return false;
  }
  // fr
  if (!interfaces__msg__SingleFootState__init(&msg->fr)) {
    interfaces__msg__FootState__fini(msg);
    return false;
  }
  // rl
  if (!interfaces__msg__SingleFootState__init(&msg->rl)) {
    interfaces__msg__FootState__fini(msg);
    return false;
  }
  // rr
  if (!interfaces__msg__SingleFootState__init(&msg->rr)) {
    interfaces__msg__FootState__fini(msg);
    return false;
  }
  return true;
}

void
interfaces__msg__FootState__fini(interfaces__msg__FootState * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // fl
  interfaces__msg__SingleFootState__fini(&msg->fl);
  // fr
  interfaces__msg__SingleFootState__fini(&msg->fr);
  // rl
  interfaces__msg__SingleFootState__fini(&msg->rl);
  // rr
  interfaces__msg__SingleFootState__fini(&msg->rr);
}

bool
interfaces__msg__FootState__are_equal(const interfaces__msg__FootState * lhs, const interfaces__msg__FootState * rhs)
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
  // fl
  if (!interfaces__msg__SingleFootState__are_equal(
      &(lhs->fl), &(rhs->fl)))
  {
    return false;
  }
  // fr
  if (!interfaces__msg__SingleFootState__are_equal(
      &(lhs->fr), &(rhs->fr)))
  {
    return false;
  }
  // rl
  if (!interfaces__msg__SingleFootState__are_equal(
      &(lhs->rl), &(rhs->rl)))
  {
    return false;
  }
  // rr
  if (!interfaces__msg__SingleFootState__are_equal(
      &(lhs->rr), &(rhs->rr)))
  {
    return false;
  }
  return true;
}

bool
interfaces__msg__FootState__copy(
  const interfaces__msg__FootState * input,
  interfaces__msg__FootState * output)
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
  // fl
  if (!interfaces__msg__SingleFootState__copy(
      &(input->fl), &(output->fl)))
  {
    return false;
  }
  // fr
  if (!interfaces__msg__SingleFootState__copy(
      &(input->fr), &(output->fr)))
  {
    return false;
  }
  // rl
  if (!interfaces__msg__SingleFootState__copy(
      &(input->rl), &(output->rl)))
  {
    return false;
  }
  // rr
  if (!interfaces__msg__SingleFootState__copy(
      &(input->rr), &(output->rr)))
  {
    return false;
  }
  return true;
}

interfaces__msg__FootState *
interfaces__msg__FootState__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__FootState * msg = (interfaces__msg__FootState *)allocator.allocate(sizeof(interfaces__msg__FootState), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interfaces__msg__FootState));
  bool success = interfaces__msg__FootState__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interfaces__msg__FootState__destroy(interfaces__msg__FootState * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interfaces__msg__FootState__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interfaces__msg__FootState__Sequence__init(interfaces__msg__FootState__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__FootState * data = NULL;

  if (size) {
    data = (interfaces__msg__FootState *)allocator.zero_allocate(size, sizeof(interfaces__msg__FootState), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interfaces__msg__FootState__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interfaces__msg__FootState__fini(&data[i - 1]);
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
interfaces__msg__FootState__Sequence__fini(interfaces__msg__FootState__Sequence * array)
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
      interfaces__msg__FootState__fini(&array->data[i]);
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

interfaces__msg__FootState__Sequence *
interfaces__msg__FootState__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interfaces__msg__FootState__Sequence * array = (interfaces__msg__FootState__Sequence *)allocator.allocate(sizeof(interfaces__msg__FootState__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interfaces__msg__FootState__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interfaces__msg__FootState__Sequence__destroy(interfaces__msg__FootState__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interfaces__msg__FootState__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interfaces__msg__FootState__Sequence__are_equal(const interfaces__msg__FootState__Sequence * lhs, const interfaces__msg__FootState__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interfaces__msg__FootState__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interfaces__msg__FootState__Sequence__copy(
  const interfaces__msg__FootState__Sequence * input,
  interfaces__msg__FootState__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interfaces__msg__FootState);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interfaces__msg__FootState * data =
      (interfaces__msg__FootState *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interfaces__msg__FootState__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interfaces__msg__FootState__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interfaces__msg__FootState__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
