// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/FootState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_HPP_

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
// Member 'fl'
// Member 'fr'
// Member 'rl'
// Member 'rr'
#include "interfaces/msg/detail/single_foot_state__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interfaces__msg__FootState __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__FootState __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct FootState_
{
  using Type = FootState_<ContainerAllocator>;

  explicit FootState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    fl(_init),
    fr(_init),
    rl(_init),
    rr(_init)
  {
    (void)_init;
  }

  explicit FootState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    fl(_alloc, _init),
    fr(_alloc, _init),
    rl(_alloc, _init),
    rr(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _fl_type =
    interfaces::msg::SingleFootState_<ContainerAllocator>;
  _fl_type fl;
  using _fr_type =
    interfaces::msg::SingleFootState_<ContainerAllocator>;
  _fr_type fr;
  using _rl_type =
    interfaces::msg::SingleFootState_<ContainerAllocator>;
  _rl_type rl;
  using _rr_type =
    interfaces::msg::SingleFootState_<ContainerAllocator>;
  _rr_type rr;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__fl(
    const interfaces::msg::SingleFootState_<ContainerAllocator> & _arg)
  {
    this->fl = _arg;
    return *this;
  }
  Type & set__fr(
    const interfaces::msg::SingleFootState_<ContainerAllocator> & _arg)
  {
    this->fr = _arg;
    return *this;
  }
  Type & set__rl(
    const interfaces::msg::SingleFootState_<ContainerAllocator> & _arg)
  {
    this->rl = _arg;
    return *this;
  }
  Type & set__rr(
    const interfaces::msg::SingleFootState_<ContainerAllocator> & _arg)
  {
    this->rr = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::FootState_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::FootState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::FootState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::FootState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::FootState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::FootState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::FootState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::FootState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::FootState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::FootState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__FootState
    std::shared_ptr<interfaces::msg::FootState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__FootState
    std::shared_ptr<interfaces::msg::FootState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const FootState_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->fl != other.fl) {
      return false;
    }
    if (this->fr != other.fr) {
      return false;
    }
    if (this->rl != other.rl) {
      return false;
    }
    if (this->rr != other.rr) {
      return false;
    }
    return true;
  }
  bool operator!=(const FootState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct FootState_

// alias to use template instance with default allocator
using FootState =
  interfaces::msg::FootState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__FOOT_STATE__STRUCT_HPP_
