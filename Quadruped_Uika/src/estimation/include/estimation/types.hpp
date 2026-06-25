/**
 * @file types.hpp
 * @brief 四足机器人腿部参数定义
 *
 * 本文件定义了进行广义动量(GM)触地检测所需的物理参数。
 * 参数值从 SolidWorks URDF 模型提取(单位: SI制)
 *
 * 【GM触地检测原理】
 * 通过广义动量观测器估计外部作用力:
 *   τ_K = τ_measured + C^T·q̇ - g
 * 当 |τ_K| 超过阈值时,判定为触地
 *
 * 【URDF 参数来源】
 * - 几何参数: 从 joint origin 位置计算
 * - 质量参数: 从 <inertial> 标签提取
 * - 惯性矩: 从 <inertia> 标签提取
 *
 * 【标定建议】
 * 1. 静止站立时4条腿都应触地,检查阈值是否足够小
 * 2. 抬一条腿时该腿应检测为不触地,检查阈值是否足够大
 * 3. 行走时摆动相不应误报,支撑相不应漏报
 */

#ifndef ESTIMATION_TYPES_HPP
#define ESTIMATION_TYPES_HPP

#include <cmath>

namespace estimation {

/**
 * @brief 单腿物理参数结构体
 *
 * 包含进行动力学计算(惯性矩阵、Coriolis项、重力项)所需的全部参数。
 * 参数值从 SolidWorks URDF 提取。
 *
 * 【URDF 腿命名对应】
 * - FL: Front-Left  (左前腿)
 * - RL: Rear-Left   (左后腿, URDF中标记为BL)
 * - RR: Rear-Right   (右后腿, URDF中标记为BR)
 * - FR: Front-Right  (右前腿)
 *
 * 腿索引顺序: FL(0), RL(1), RR(2), FR(3)
 */
struct LegConstants {

    //============================================================================
    // 【几何参数】- 腿部长度 (单位: 米)
    // 基于 URDF joint origin 位置计算
    //============================================================================
    /** Hip关节相对于身体中心的偏移距离(横向) */
    static constexpr double L_HIP = 0.153;

    /** 大腿连杆长度(髋关节到膝关节) */
    static constexpr double L_THIGH = 0.14;

    /** 小腿连杆长度(膝关节到踝关节) */
    static constexpr double L_CALF = 0.21;

    //============================================================================
    // 【质量参数】- 连杆质量 (单位: 千克)
    // 从 URDF <mass> 标签提取
    //============================================================================
    /** Hip连杆质量(髋关节侧连杆) */
    static constexpr double M_HIP = 0.933;

    /** 大腿连杆质量 (FL:0.476, FR:0.480, 取平均) */
    static constexpr double M_THIGH = 0.477;

    /** 小腿连杆质量 */
    static constexpr double M_CALF = 0.147;

    //============================================================================
    // 【质心位置】- 相对于近端关节的距离 (单位: 米)
    // 从 URDF <inertial><origin> 标签提取
    //============================================================================
    /** Hip连杆质心到髋关节的距离 */
    static constexpr double HIP_COM = 0.025;

    /** 大腿连杆质心到髋关节的距离 */
    static constexpr double THIGH_COM = 0.065;  // URDF: (-0.054, 0.035, -0.017) -> 0.065m

    /** 小腿连杆质心到膝关节的距离 */
    static constexpr double CALF_COM = 0.070;  // URDF: (0.070, -0.016, -0.002) -> 0.070m

    //============================================================================
    // 【转动惯量】- 绕质心主轴的惯性矩 (单位: kg·m²)
    // 从 URDF <inertia> 标签提取 (URDF采用YXZ欧拉角约定,需注意坐标轴对应)
    //============================================================================
    // Hip连杆惯性矩 (FL/RL相同, FR/RR相同)
    static constexpr double I_HIP_XX = 0.00114;  // ~0.00114
    static constexpr double I_HIP_YY = 0.00108;  // ~0.00108
    static constexpr double I_HIP_ZZ = 0.00110;  // ~0.00110

    // Thigh连杆惯性矩 (FL/RL相同, FR/RR相同)
    // FL_thigh: ixx=0.00108325, iyy=0.00222936, izz=0.00221100
    // FR_thigh: ixx=0.00111780, iyy=0.00231794, izz=0.00230119
    static constexpr double I_THIGH_XX = 0.00110;  // ~0.00110
    static constexpr double I_THIGH_YY = 0.00227;  // ~0.00227
    static constexpr double I_THIGH_ZZ = 0.00226;  // ~0.00226

    // Calf连杆惯性矩 (FL/RL相同, FR/RR相同)
    // FL_calf/FR_calf: ixx=0.00002268, iyy=0.00073677, izz=0.00073626
    static constexpr double I_CALF_XX = 0.0000227;  // ~2.27e-5
    static constexpr double I_CALF_YY = 0.000737;  // ~7.37e-4
    static constexpr double I_CALF_ZZ = 0.000736;  // ~7.36e-4

    //============================================================================
    // 【物理常数】
    //============================================================================
    /** 重力加速度 (单位: m/s²) */
    static constexpr double G = 9.81;

    //============================================================================
    // 【电机参数】
    //============================================================================
    /** ROBSTRIDE_02电机最大扭矩 (单位: Nm) */
    static constexpr double TORQUE_LIMIT = 17.0;

    //============================================================================
    // 【触地检测参数】- 最关键的标定参数!
    //============================================================================
    /**
     * 触地检测默认阈值 (单位: Nm)
     *
     * 【选择依据】
     * - 阈值太小: 会产生误报(空中检测为触地)
     * - 阈值太大: 会产生漏报(触地检测为空中)
     *
     * 【推荐标定范围】
     * - 小型四足(10kg以下): 2-4 Nm
     * - 中型四足(10-30kg): 4-8 Nm
     * - 大型四足(30kg以上): 8-15 Nm
     *
     * 【标定方法】
     * 1. 从较大值开始(如10Nm)
     * 2. 机器人静止站立,逐渐减小阈值直到出现误报
     * 3. 记录当前值,再加0.5Nm作为安全裕度
     */
    static constexpr double CONTACT_THRESHOLD_DEFAULT = 2.0;

    /** 每条腿的关节数量(hip, thigh, calf) */
    static constexpr int JOINTS_PER_LEG = 3;
};

/**
 * @brief 腿部索引枚举
 *
 * 定义4条腿的编号,对应电机在MotorFeedback12消息中的顺序:
 * - FL (Front-Left):  motors 0,1,2   → can0
 * - RL (Rear-Left):   motors 3,4,5   → can1 (URDF中标记为BL)
 * - RR (Rear-Right):  motors 6,7,8   → can2 (URDF中标记为BR)
 * - FR (Front-Right):  motors 9,10,11 → can3
 *
 * 注意: URDF中使用FL/FR/BL/BR命名,这里映射为FL/RL/RR/FR
 */
enum class LegIndex : int {
    FL = 0,  /**< 左前腿 (Front-Left) */
    RL = 1,  /**< 左后腿 (Rear-Left, URDF中为BL) */
    RR = 2,  /**< 右后腿 (Rear-Right, URDF中为BR) */
    FR = 3   /**< 右前腿 (Front-Right) */
};

/**
 * @brief 获取指定腿的第一个电机索引
 * @param leg 腿部索引
 * @return 电机编号(0-11)
 *
 * 例如 FL 返回 0, RL 返回 3, RR 返回 6, FR 返回 9
 */
inline int get_motor_offset(LegIndex leg) {
    return static_cast<int>(leg) * LegConstants::JOINTS_PER_LEG;
}

}  // namespace estimation

#endif  // ESTIMATION_TYPES_HPP
