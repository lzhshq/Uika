# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_xbox_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED xbox_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(xbox_FOUND FALSE)
  elseif(NOT xbox_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(xbox_FOUND FALSE)
  endif()
  return()
endif()
set(_xbox_CONFIG_INCLUDED TRUE)

# output package information
if(NOT xbox_FIND_QUIETLY)
  message(STATUS "Found xbox: 1.0.0 (${xbox_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'xbox' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${xbox_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(xbox_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${xbox_DIR}/${_extra}")
endforeach()
