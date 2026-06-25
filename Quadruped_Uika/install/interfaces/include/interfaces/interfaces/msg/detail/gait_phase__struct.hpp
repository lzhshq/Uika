// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/GaitPhase.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_HPP_

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
# define DEPRECATED__interfaces__msg__GaitPhase __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__GaitPhase __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct GaitPhase_
{
  using Type = GaitPhase_<ContainerAllocator>;

  explicit GaitPhase_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fl_phase = 0;
      this->fr_phase = 0;
      this->rl_phase = 0;
      this->rr_phase = 0;
    }
  }

  explicit GaitPhase_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fl_phase = 0;
      this->fr_phase = 0;
      this->rl_phase = 0;
      this->rr_phase = 0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _fl_phase_type =
    uint8_t;
  _fl_phase_type fl_phase;
  using _fr_phase_type =
    uint8_t;
  _fr_phase_type fr_phase;
  using _rl_phase_type =
    uint8_t;
  _rl_phase_type rl_phase;
  using _rr_phase_type =
    uint8_t;
  _rr_phase_type rr_phase;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__fl_phase(
    const uint8_t & _arg)
  {
    this->fl_phase = _arg;
    return *this;
  }
  Type & set__fr_phase(
    const uint8_t & _arg)
  {
    this->fr_phase = _arg;
    return *this;
  }
  Type & set__rl_phase(
    const uint8_t & _arg)
  {
    this->rl_phase = _arg;
    return *this;
  }
  Type & set__rr_phase(
    const uint8_t & _arg)
  {
    this->rr_phase = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t STANCE =
    0u;
  static constexpr uint8_t SWING =
    1u;

  // pointer types
  using RawPtr =
    interfaces::msg::GaitPhase_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::GaitPhase_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::GaitPhase_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::GaitPhase_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::GaitPhase_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::GaitPhase_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::GaitPhase_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::GaitPhase_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::GaitPhase_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::GaitPhase_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__GaitPhase
    std::shared_ptr<interfaces::msg::GaitPhase_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__GaitPhase
    std::shared_ptr<interfaces::msg::GaitPhase_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GaitPhase_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->fl_phase != other.fl_phase) {
      return false;
    }
    if (this->fr_phase != other.fr_phase) {
      return false;
    }
    if (this->rl_phase != other.rl_phase) {
      return false;
    }
    if (this->rr_phase != other.rr_phase) {
      return false;
    }
    return true;
  }
  bool operator!=(const GaitPhase_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GaitPhase_

// alias to use template instance with default allocator
using GaitPhase =
  interfaces::msg::GaitPhase_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GaitPhase_<ContainerAllocator>::STANCE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t GaitPhase_<ContainerAllocator>::SWING;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__GAIT_PHASE__STRUCT_HPP_
