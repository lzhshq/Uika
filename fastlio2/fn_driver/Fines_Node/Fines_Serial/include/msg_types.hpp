#ifndef FINES_NODE_MSG_TYPES_HPP
#define FINES_NODE_MSG_TYPES_HPP

#include <std_msgs/msg/string.hpp>
#include <std_msgs/msg/u_int8_multi_array.hpp>
#include <geometry_msgs/msg/twist.hpp>

typedef enum {
    Debug = 0x00,
    CMD_VEL = 0x10,
} MessageType_e;


#endif //FINES_NODE_MSG_TYPES_HPP
