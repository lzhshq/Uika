//
// Created by fins on 24-10-12.
//
#include <iostream>
#include <rclcpp/rclcpp.hpp>
#include <queue>

#ifndef FINES_SERIAL_CRC_HPP
#define FINES_SERIAL_CRC_HPP

uint8_t calculate_crc(const std::vector<uint8_t>& data) {
    const uint8_t polynomial = 0x07;  // CRC-8 多项式：x^8 + x^2 + x + 1
    uint8_t crc = 0x00;  // CRC-8 初始值为 0x00

    for (auto byte : data) {
        crc ^= byte;  // 将字节与当前 CRC 值异或
        for (int i = 0; i < 8; ++i) {  // 处理每一位
            if (crc & 0x80) {  // 如果最高位为 1
                crc = (crc << 1) ^ polynomial;  // 左移并异或多项式
            } else {
                crc <<= 1;  // 仅左移
            }
        }
    }

    return crc;  // 返回计算出的 CRC-8 校验值
}
#endif //FINES_SERIAL_CRC_HPP
