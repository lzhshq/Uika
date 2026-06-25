// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from interfaces:msg/MotorFeedback12.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "interfaces/msg/detail/motor_feedback12__struct.h"
#include "interfaces/msg/detail/motor_feedback12__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);
bool interfaces__msg__motor_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * interfaces__msg__motor_feedback__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool interfaces__msg__motor_feedback12__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[49];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("interfaces.msg._motor_feedback12.MotorFeedback12", full_classname_dest, 48) == 0);
  }
  interfaces__msg__MotorFeedback12 * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fl_hip
    PyObject * field = PyObject_GetAttrString(_pymsg, "fl_hip");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fl_hip)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fl_thigh
    PyObject * field = PyObject_GetAttrString(_pymsg, "fl_thigh");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fl_thigh)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fl_calf
    PyObject * field = PyObject_GetAttrString(_pymsg, "fl_calf");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fl_calf)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fr_hip
    PyObject * field = PyObject_GetAttrString(_pymsg, "fr_hip");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fr_hip)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fr_thigh
    PyObject * field = PyObject_GetAttrString(_pymsg, "fr_thigh");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fr_thigh)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // fr_calf
    PyObject * field = PyObject_GetAttrString(_pymsg, "fr_calf");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->fr_calf)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rl_hip
    PyObject * field = PyObject_GetAttrString(_pymsg, "rl_hip");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rl_hip)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rl_thigh
    PyObject * field = PyObject_GetAttrString(_pymsg, "rl_thigh");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rl_thigh)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rl_calf
    PyObject * field = PyObject_GetAttrString(_pymsg, "rl_calf");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rl_calf)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rr_hip
    PyObject * field = PyObject_GetAttrString(_pymsg, "rr_hip");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rr_hip)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rr_thigh
    PyObject * field = PyObject_GetAttrString(_pymsg, "rr_thigh");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rr_thigh)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // rr_calf
    PyObject * field = PyObject_GetAttrString(_pymsg, "rr_calf");
    if (!field) {
      return false;
    }
    if (!interfaces__msg__motor_feedback__convert_from_py(field, &ros_message->rr_calf)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * interfaces__msg__motor_feedback12__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of MotorFeedback12 */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("interfaces.msg._motor_feedback12");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "MotorFeedback12");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  interfaces__msg__MotorFeedback12 * ros_message = (interfaces__msg__MotorFeedback12 *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fl_hip
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fl_hip);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fl_hip", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fl_thigh
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fl_thigh);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fl_thigh", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fl_calf
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fl_calf);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fl_calf", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fr_hip
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fr_hip);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fr_hip", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fr_thigh
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fr_thigh);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fr_thigh", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fr_calf
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->fr_calf);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "fr_calf", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rl_hip
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rl_hip);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rl_hip", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rl_thigh
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rl_thigh);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rl_thigh", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rl_calf
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rl_calf);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rl_calf", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rr_hip
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rr_hip);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rr_hip", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rr_thigh
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rr_thigh);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rr_thigh", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rr_calf
    PyObject * field = NULL;
    field = interfaces__msg__motor_feedback__convert_to_py(&ros_message->rr_calf);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rr_calf", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
