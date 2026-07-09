#include <iostream>
#include <fmt/core.h>
#include <rclcpp/rclcpp.hpp>
#include "serial_station.hpp"
#include "msg_types.hpp"
#include "utils/crc.hpp"
#include "utils/data_convert.hpp"

// 带有帧标识符、长度和 CRC 的编码函数
void encode(std::vector<uint8_t>& data, uint8_t frame_identifier) {
    const uint16_t FRAME_HEADER = 0xAA;
    const uint16_t FRAME_TRAILER = 0xBB;
    // 计算 CRC 校验码并插入到帧尾前
    uint8_t crc = calculate_crc(data);
    // 动态计算数据长度，并将其作为长度字段（1 字节）
    uint8_t data_length = static_cast<uint8_t>(data.size());

    // 在 data 的开头插入帧头、帧标识符和标识符长度
    data.insert(data.begin(), data_length);  // 插入标识符长度
    data.insert(data.begin(), frame_identifier);   // 插入帧标识符
    data.insert(data.begin(), FRAME_HEADER);

    data.push_back(crc);
    // 在 data 的末尾添加帧尾
    data.push_back(FRAME_TRAILER);
}

// 解码函数
void decode(std::vector<uint8_t> data) {
        std::string data_str;
        for (const auto& byte : data)
        {
            data_str += fmt::format("{:02X}", byte);
        }
        static int YYY = 0;

        std::cout << "Index: " << YYY <<" Received: " << data_str.c_str() << std::endl;
        YYY++;
}


int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);

    /***************************** 参数处理 ********************************/
    std::string serial_port = "/dev/ttyUSB0";
    uint32_t baudrate = 921600;

    // 输入 serial_port 参数
    if (argc >= 2) {
        serial_port = argv[1];
        std::cout << "Serial port: " << serial_port << std::endl;
    }
    else {
        std::cout << "No serial port input, using default: " << serial_port << std::endl;
    }

    /***************************** 串口配置 ********************************/
    SerialConfig_t config = {
        serial_port, // serial_port
        baudrate, // baudrate
        serial::Timeout(  // 如果只有最长超时，每次read都会超时
                0, // inter_byte_timeout_
                0, // read_timeout_constant_
                0, // read_timeout_multiplier_
                0, // write_timeout_constant_
                0 // write_timeout_multiplier_
        ),
        serial::eightbits, // byte_size
        serial::parity_none, // parity
        serial::stopbits_one, // stopbits
        serial::flowcontrol_none, // flowcontrol
        1, // tx_handle_period, unit: ms
        1, // rx_handle_period, unit: ms
    };
    auto serial_station = std::make_shared<SerialStation>(config);

    serial_station->bindEncodeFunc(encode);
    serial_station->bindDecodeFunc(decode);

    /***************************** uint8数组，用于调试 ********************************/
    auto sub = serial_station->create_subscription<std_msgs::msg::UInt8MultiArray>(
            "/test_topic", 10,
            [serial_station](const std_msgs::msg::UInt8MultiArray::SharedPtr msg) {
                std::vector<uint8_t> debug_data = {};
                // 将接收到的数组数据装填到 std::vector<uint8_t>
                debug_data.assign(msg->data.begin(), msg->data.end());

//                // Debug
//                std::string data_str;
//                for (const auto& byte : debug_data) {
//                    data_str += fmt::format("{:02X} ", byte);  // 转为十六进制格式
//                }
//                RCLCPP_INFO(serial_station->get_logger(), "Transmitting data: [%s]", data_str.c_str());

                // 发送数据到串口
                serial_station->transmit(debug_data, MessageType_e::Debug);
            }
    );

    /***************************** 速度指令 ********************************/
    auto cmd_vel_sub = serial_station->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            [serial_station](const geometry_msgs::msg::Twist::SharedPtr msg) {
                std::vector<uint8_t> data;

                convert_float2bytes(data, msg->linear.x);
                convert_float2bytes(data, msg->linear.y);
                convert_float2bytes(data, msg->linear.z);
                convert_float2bytes(data, msg->angular.x);
                convert_float2bytes(data, msg->angular.y);
                convert_float2bytes(data, msg->angular.z);

                serial_station->transmit(data, MessageType_e::CMD_VEL);
            }
    );

    rclcpp::spin(serial_station);

    rclcpp::shutdown();

    return 0;
}
