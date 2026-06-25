#ifndef ESTIMATION_GM_OBSERVER_HPP
#define ESTIMATION_GM_OBSERVER_HPP

#include <Eigen/Dense>
#include "leg_dynamics.hpp"

namespace estimation {

/**
 * @brief 广义动量观测器 (Generalized Momentum Observer)
 *
 * 实现MIT Cheetah 3的GM触地检测方法:
 * - 外部扭矩 τ_K = ṗ - τ - Cᵀ·q̇ + g
 * - 当 |τ_K| 超过阈值时,判定触地
 */
class GMObserver {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    /**
     * @brief 构造函数
     * @param filter_alpha 低通滤波器系数 [0,1], 越小越平滑
     * @param threshold 触地检测阈值 (Nm)
     */
    GMObserver(double filter_alpha = 0.3, double threshold = 5.0);

    /**
     * @brief 主更新步
     * @param tau_measured 电机实测扭矩 [hip, thigh, calf] (Nm)
     * @param q 关节角度 (rad)
     * @param q_dot 关节速度 (rad/s)
     * @param dt 时间步长 (s)
     */
    void update(const Eigen::Vector3d& tau_measured,
                const Eigen::Vector3d& q,
                const Eigen::Vector3d& q_dot,
                double dt);

    /**
     * @brief 检测触地
     * @return true if contact detected
     */
    bool detectContact() const;

    /**
     * @brief 设置检测阈值
     */
    void setThreshold(double threshold) { threshold_ = threshold; }

    /**
     * @brief 获取估计的外部扭矩
     */
    const Eigen::Vector3d& getExternalTorque() const { return tau_external_filtered_; }

    /**
     * @brief 重置观测器状态
     */
    void reset();

private:
    LegDynamics leg_dynamics_;

    Eigen::Vector3d q_;
    Eigen::Vector3d q_dot_;
    Eigen::Vector3d p_;                    // 广义动量
    Eigen::Vector3d p_dot_;               // 动量导数(未滤波)
    Eigen::Vector3d p_dot_filtered_;      // 动量导数(滤波后)
    Eigen::Vector3d tau_external_;        // 外部扭矩(未滤波)
    Eigen::Vector3d tau_external_filtered_; // 外部扭矩(滤波后)

    double filter_alpha_;
    double threshold_;
    bool initialized_;
};

}  // namespace estimation

#endif  // ESTIMATION_GM_OBSERVER_HPP
