//
// Created by fins on 24-10-28.
//

#ifndef FINES_SERIAL_DATA_CONVERT_HPP
#define FINES_SERIAL_DATA_CONVERT_HPP

#include <vector>
#include <cstdint>

void convert_float2bytes(std::vector<uint8_t>& bytes, float value) {
    uint32_t as_int = *reinterpret_cast<uint32_t*>(&value);
    bytes.push_back(static_cast<uint8_t>(as_int & 0xFF));
    bytes.push_back(static_cast<uint8_t>((as_int >> 8) & 0xFF));
    bytes.push_back(static_cast<uint8_t>((as_int >> 16) & 0xFF));
    bytes.push_back(static_cast<uint8_t>((as_int >> 24) & 0xFF));
}

#endif //FINES_SERIAL_DATA_CONVERT_HPP
