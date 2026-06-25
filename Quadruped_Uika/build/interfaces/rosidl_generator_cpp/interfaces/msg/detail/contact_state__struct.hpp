// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/ContactState.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_HPP_

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
# define DEPRECATED__interfaces__msg__ContactState __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__ContactState __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct ContactState_
{
  using Type = ContactState_<ContainerAllocator>;

  explicit ContactState_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fl_contact = false;
      this->fr_contact = false;
      this->rl_contact = false;
      this->rr_contact = false;
    }
  }

  explicit ContactState_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fl_contact = false;
      this->fr_contact = false;
      this->rl_contact = false;
      this->rr_contact = false;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _fl_contact_type =
    bool;
  _fl_contact_type fl_contact;
  using _fr_contact_type =
    bool;
  _fr_contact_type fr_contact;
  using _rl_contact_type =
    bool;
  _rl_contact_type rl_contact;
  using _rr_contact_type =
    bool;
  _rr_contact_type rr_contact;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__fl_contact(
    const bool & _arg)
  {
    this->fl_contact = _arg;
    return *this;
  }
  Type & set__fr_contact(
    const bool & _arg)
  {
    this->fr_contact = _arg;
    return *this;
  }
  Type & set__rl_contact(
    const bool & _arg)
  {
    this->rl_contact = _arg;
    return *this;
  }
  Type & set__rr_contact(
    const bool & _arg)
  {
    this->rr_contact = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::ContactState_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::ContactState_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::ContactState_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::ContactState_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::ContactState_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::ContactState_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::ContactState_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::ContactState_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::ContactState_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::ContactState_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__ContactState
    std::shared_ptr<interfaces::msg::ContactState_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__ContactState
    std::shared_ptr<interfaces::msg::ContactState_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ContactState_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->fl_contact != other.fl_contact) {
      return false;
    }
    if (this->fr_contact != other.fr_contact) {
      return false;
    }
    if (this->rl_contact != other.rl_contact) {
      return false;
    }
    if (this->rr_contact != other.rr_contact) {
      return false;
    }
    return true;
  }
  bool operator!=(const ContactState_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ContactState_

// alias to use template instance with default allocator
using ContactState =
  interfaces::msg::ContactState_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__CONTACT_STATE__STRUCT_HPP_
