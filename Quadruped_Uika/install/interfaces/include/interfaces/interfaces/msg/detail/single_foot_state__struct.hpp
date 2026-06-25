// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/SingleFootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.hpp"
// Member 'velocity'
// Member 'force'
#include "geometry_msgs/msg/detail/vector3__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interfaces__msg__SingleFootState __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__SingleFootState __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SingleFootState_
{
  using Type = SingleFootState_<ContainerAllocator>;

  explicit SingleFootState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : position(_init),
    velocity(_init),
    force(_init)
  {
    (void)_init;
  }

  explicit SingleFootState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : position(_alloc, _init),
    velocity(_alloc, _init),
    force(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _position_type =
    geometry_msgs::msg::Point_<ContainerAllocator>;
  _position_type position;
  using _velocity_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _velocity_type velocity;
  using _force_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _force_type force;

  // setters for named parameter idiom
  Type & set__position(
    const geometry_msgs::msg::Point_<ContainerAllocator> & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__velocity(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__force(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->force = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::SingleFootState_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::SingleFootState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::SingleFootState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::SingleFootState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::SingleFootState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::SingleFootState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::SingleFootState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::SingleFootState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::SingleFootState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::SingleFootState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__SingleFootState
    std::shared_ptr<interfaces::msg::SingleFootState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__SingleFootState
    std::shared_ptr<interfaces::msg::SingleFootState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SingleFootState_ & other) const
  {
    if (this->position != other.position) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->force != other.force) {
      return false;
    }
    return true;
  }
  bool operator!=(const SingleFootState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SingleFootState_

// alias to use template instance with default allocator
using SingleFootState =
  interfaces::msg::SingleFootState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__SINGLE_FOOT_STATE__STRUCT_HPP_
