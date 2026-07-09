#include "serial_station.hpp"
#include <fmt/core.h>

SerialStation::SerialStation(SerialConfig_t &config) : Node("serial_station") {
    // Set up the serial port
    serial_.setPort(config.port);
    serial_.setBaudrate(config.baudrate);
    serial_.setTimeout(config.timeout);
    serial_.setBytesize(config.bytesize);
    serial_.setParity(config.parity);
    serial_.setStopbits(config.stopbits);
    serial_.setFlowcontrol(config.flowcontrol);

    // Open the serial port
    try {
        serial_.open();
    } catch (serial::IOException &e) {
        RCLCPP_ERROR(this->get_logger(), "Cannot open serial port %s", config.port.c_str());
    }
    if (serial_.isOpen()) {
        RCLCPP_INFO(this->get_logger(), "Serial port %s is open", config.port.c_str());
    } else {
        RCLCPP_ERROR(this->get_logger(), "Serial port %s is not open", config.port.c_str());
    }

    serial_.flush();

    // TODO： 应当得改为用多线程实现，使用wall_timer，本质上只有一个线程
    tx_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(config.tx_handle_period),
            [this]() { this->loadTx(); }
    );

    rx_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(config.rx_handle_period),
            [this]() { this->rxCallback(); }
    );
}

SerialStation::~SerialStation() {
    serial_.close();
}

void SerialStation::transmit(std::vector<uint8_t> &data, MessageType_e dataID) {
    // 先将发送数据存入队列，防止外部数据更新过快
    tx_queue_.push(std::move(data));
    if (encode_func_) {
        encode_func_(tx_queue_.back(), dataID);
    }
}

void SerialStation::loadTx() {
    if (!tx_queue_.empty()) {
        serial_.write(tx_queue_.front());
        // TODO: 存在风险，serial_尚未将数据放入串口发送缓冲区，而数据已经pop，此时将跳出内存错误
        //  需要一套生命周期管理机制

//        // Debug
//        std::string data_str;
//        for (const auto& byte : tx_queue_.front())
//        {
//            data_str += fmt::format("{:02X}", byte);
//        }
//        RCLCPP_INFO(this->get_logger(), "Data:[%s], TX Queue size: %zu",
//                    data_str.c_str(), tx_queue_.size());

        tx_queue_.pop();
    }
}

void SerialStation::rxCallback() {
    rx_buffer_.clear(); // 清空缓冲区

    auto bytes_read = serial_.read(rx_buffer_, 200);
    if (bytes_read > 0) {
        if (decode_func_) {    // 复制一份缓冲区数据
            std::vector<uint8_t> data(rx_buffer_.begin(), rx_buffer_.begin() + bytes_read);

            // Debug
//            std::string data_str;
//            for (const auto& byte : data)
//            {
//                data_str += fmt::format("{:02X}", byte);
//            }
//            RCLCPP_INFO(this->get_logger(), "Data: [%s]", data_str.c_str());

            decode_func_(std::move(data));
        }
    }
}

