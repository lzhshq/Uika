// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/MotionCommand.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_HPP_

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

#ifndef _WIN32
# define DEPRECATED__interfaces__msg__MotionCommand __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__MotionCommand __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MotionCommand_
{
  using Type = MotionCommand_<ContainerAllocator>;

  explicit MotionCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->vy = 0.0;
      this->wz = 0.0;
      this->body_height = 0.0;
    }
  }

  explicit MotionCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->vx = 0.0;
      this->vy = 0.0;
      this->wz = 0.0;
      this->body_height = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _vx_type =
    double;
  _vx_type vx;
  using _vy_type =
    double;
  _vy_type vy;
  using _wz_type =
    double;
  _wz_type wz;
  using _body_height_type =
    double;
  _body_height_type body_height;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__vx(
    const double & _arg)
  {
    this->vx = _arg;
    return *this;
  }
  Type & set__vy(
    const double & _arg)
  {
    this->vy = _arg;
    return *this;
  }
  Type & set__wz(
    const double & _arg)
  {
    this->wz = _arg;
    return *this;
  }
  Type & set__body_height(
    const double & _arg)
  {
    this->body_height = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::MotionCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::MotionCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::MotionCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::MotionCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotionCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotionCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotionCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotionCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::MotionCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::MotionCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__MotionCommand
    std::shared_ptr<interfaces::msg::MotionCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__MotionCommand
    std::shared_ptr<interfaces::msg::MotionCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MotionCommand_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->vx != other.vx) {
      return false;
    }
    if (this->vy != other.vy) {
      return false;
    }
    if (this->wz != other.wz) {
      return false;
    }
    if (this->body_height != other.body_height) {
      return false;
    }
    return true;
  }
  bool operator!=(const MotionCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MotionCommand_

// alias to use template instance with default allocator
using MotionCommand =
  interfaces::msg::MotionCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTION_COMMAND__STRUCT_HPP_
