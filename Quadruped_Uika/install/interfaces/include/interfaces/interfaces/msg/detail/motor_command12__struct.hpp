// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/MotorCommand12.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_HPP_

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
#include "interfaces/msg/detail/motor_command__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interfaces__msg__MotorCommand12 __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__MotorCommand12 __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MotorCommand12_
{
  using Type = MotorCommand12_<ContainerAllocator>;

  explicit MotorCommand12_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    fl_hip(_init),
    fl_thigh(_init),
    fl_calf(_init),
    fr_hip(_init),
    fr_thigh(_init),
    fr_calf(_init),
    rl_hip(_init),
    rl_thigh(_init),
    rl_calf(_init),
    rr_hip(_init),
    rr_thigh(_init),
    rr_calf(_init)
  {
    (void)_init;
  }

  explicit MotorCommand12_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    fl_hip(_alloc, _init),
    fl_thigh(_alloc, _init),
    fl_calf(_alloc, _init),
    fr_hip(_alloc, _init),
    fr_thigh(_alloc, _init),
    fr_calf(_alloc, _init),
    rl_hip(_alloc, _init),
    rl_thigh(_alloc, _init),
    rl_calf(_alloc, _init),
    rr_hip(_alloc, _init),
    rr_thigh(_alloc, _init),
    rr_calf(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _fl_hip_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fl_hip_type fl_hip;
  using _fl_thigh_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fl_thigh_type fl_thigh;
  using _fl_calf_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fl_calf_type fl_calf;
  using _fr_hip_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fr_hip_type fr_hip;
  using _fr_thigh_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fr_thigh_type fr_thigh;
  using _fr_calf_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _fr_calf_type fr_calf;
  using _rl_hip_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rl_hip_type rl_hip;
  using _rl_thigh_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rl_thigh_type rl_thigh;
  using _rl_calf_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rl_calf_type rl_calf;
  using _rr_hip_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rr_hip_type rr_hip;
  using _rr_thigh_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rr_thigh_type rr_thigh;
  using _rr_calf_type =
    interfaces::msg::MotorCommand_<ContainerAllocator>;
  _rr_calf_type rr_calf;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__fl_hip(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fl_hip = _arg;
    return *this;
  }
  Type & set__fl_thigh(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fl_thigh = _arg;
    return *this;
  }
  Type & set__fl_calf(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fl_calf = _arg;
    return *this;
  }
  Type & set__fr_hip(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fr_hip = _arg;
    return *this;
  }
  Type & set__fr_thigh(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fr_thigh = _arg;
    return *this;
  }
  Type & set__fr_calf(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->fr_calf = _arg;
    return *this;
  }
  Type & set__rl_hip(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rl_hip = _arg;
    return *this;
  }
  Type & set__rl_thigh(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rl_thigh = _arg;
    return *this;
  }
  Type & set__rl_calf(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rl_calf = _arg;
    return *this;
  }
  Type & set__rr_hip(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rr_hip = _arg;
    return *this;
  }
  Type & set__rr_thigh(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rr_thigh = _arg;
    return *this;
  }
  Type & set__rr_calf(
    const interfaces::msg::MotorCommand_<ContainerAllocator> & _arg)
  {
    this->rr_calf = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::MotorCommand12_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::MotorCommand12_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotorCommand12_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::MotorCommand12_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__MotorCommand12
    std::shared_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__MotorCommand12
    std::shared_ptr<interfaces::msg::MotorCommand12_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MotorCommand12_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->fl_hip != other.fl_hip) {
      return false;
    }
    if (this->fl_thigh != other.fl_thigh) {
      return false;
    }
    if (this->fl_calf != other.fl_calf) {
      return false;
    }
    if (this->fr_hip != other.fr_hip) {
      return false;
    }
    if (this->fr_thigh != other.fr_thigh) {
      return false;
    }
    if (this->fr_calf != other.fr_calf) {
      return false;
    }
    if (this->rl_hip != other.rl_hip) {
      return false;
    }
    if (this->rl_thigh != other.rl_thigh) {
      return false;
    }
    if (this->rl_calf != other.rl_calf) {
      return false;
    }
    if (this->rr_hip != other.rr_hip) {
      return false;
    }
    if (this->rr_thigh != other.rr_thigh) {
      return false;
    }
    if (this->rr_calf != other.rr_calf) {
      return false;
    }
    return true;
  }
  bool operator!=(const MotorCommand12_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MotorCommand12_

// alias to use template instance with default allocator
using MotorCommand12 =
  interfaces::msg::MotorCommand12_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__MOTOR_COMMAND12__STRUCT_HPP_
