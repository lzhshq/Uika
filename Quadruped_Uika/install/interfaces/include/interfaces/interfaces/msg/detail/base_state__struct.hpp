// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/BaseState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.hpp"
// Member 'orientation'
#include "geometry_msgs/msg/detail/quaternion__struct.hpp"
// Member 'linear_velocity'
// Member 'angular_velocity'
#include "geometry_msgs/msg/detail/vector3__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interfaces__msg__BaseState __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__BaseState __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct BaseState_
{
  using Type = BaseState_<ContainerAllocator>;

  explicit BaseState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    position(_init),
    orientation(_init),
    linear_velocity(_init),
    angular_velocity(_init)
  {
    (void)_init;
  }

  explicit BaseState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    position(_alloc, _init),
    orientation(_alloc, _init),
    linear_velocity(_alloc, _init),
    angular_velocity(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _position_type =
    geometry_msgs::msg::Point_<ContainerAllocator>;
  _position_type position;
  using _orientation_type =
    geometry_msgs::msg::Quaternion_<ContainerAllocator>;
  _orientation_type orientation;
  using _linear_velocity_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _linear_velocity_type linear_velocity;
  using _angular_velocity_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _angular_velocity_type angular_velocity;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__position(
    const geometry_msgs::msg::Point_<ContainerAllocator> & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__orientation(
    const geometry_msgs::msg::Quaternion_<ContainerAllocator> & _arg)
  {
    this->orientation = _arg;
    return *this;
  }
  Type & set__linear_velocity(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->linear_velocity = _arg;
    return *this;
  }
  Type & set__angular_velocity(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->angular_velocity = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::BaseState_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::BaseState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::BaseState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::BaseState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::BaseState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::BaseState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::BaseState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::BaseState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::BaseState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::BaseState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__BaseState
    std::shared_ptr<interfaces::msg::BaseState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__BaseState
    std::shared_ptr<interfaces::msg::BaseState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const BaseState_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    if (this->orientation != other.orientation) {
      return false;
    }
    if (this->linear_velocity != other.linear_velocity) {
      return false;
    }
    if (this->angular_velocity != other.angular_velocity) {
      return false;
    }
    return true;
  }
  bool operator!=(const BaseState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct BaseState_

// alias to use template instance with default allocator
using BaseState =
  interfaces::msg::BaseState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__BASE_STATE__STRUCT_HPP_
