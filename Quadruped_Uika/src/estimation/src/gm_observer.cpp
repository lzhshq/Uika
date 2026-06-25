#include "estimation/gm_observer.hpp"

namespace estimation {

GMObserver::GMObserver(double filter_alpha, double threshold)
    : filter_alpha_(filter_alpha),
      threshold_(threshold),
      initialized_(false) {
    reset();
}

void GMObserver::update(const Eigen::Vector3d& tau_measured,
                         const Eigen::Vector3d& q,
                         const Eigen::Vector3d& q_dot,
                         double dt) {
    // 初始化上一时刻状态
    if (!initialized_) {
        q_ = q;
        q_dot_ = q_dot;
        p_dot_filtered_.setZero();
        tau_external_filtered_.setZero();
        initialized_ = true;
        return;
    }

    // 保存上一时刻状态
    q_ = q;
    q_dot_ = q_dot;

    // 计算惯性矩阵 M(q)
    Eigen::Matrix3d M = leg_dynamics_.computeInertiaMatrix(q);

    // 计算广义动量 p = M(q) * q_dot
    p_ = M * q_dot;

    // 计算 Coriolis 项: C^T(q,q_dot) * q_dot
    Eigen::Vector3d C_transpose_q_dot = leg_dynamics_.computeCoriolisTerm(q, q_dot);

    // 计算重力项 g(q)
    Eigen::Vector3d g = leg_dynamics_.computeGravityTerm(q);

    // 计算动量导数 (关键公式):
    // ṗ = τ + τ_K + C^T·q̇ - g
    // => τ_K = ṗ - τ - C^T·q̇ + g
    //
    // 但我们没有直接测量ṗ,所以用差分近似:
    // ṗ ≈ (p_ - p_prev) / dt
    //
    // 由于数值微分会放大噪声,使用一阶低通滤波:
    // p_dot_filtered = α * p_dot + (1-α) * p_dot_filtered_prev

    // 计算当前动量 (用于差分)
    Eigen::Vector3d p_current = M * q_dot;

    // 动量导数 = τ_measured + C^T·q̇ - g (来自动力学公式 ṗ = τ + τ_K + ...)
    // 这是因为在平衡时(无外部力)应有: τ + C^T·q̇ - g ≈ 0
    // 所以 ṗ ≈ 0, 当有外部力时, τ_K = ṗ - τ - C^T·q̇ + g
    p_dot_ = tau_measured + C_transpose_q_dot - g;

    // 低通滤波
    p_dot_filtered_ = filter_alpha_ * p_dot_ + (1.0 - filter_alpha_) * p_dot_filtered_;

    // 外部扭矩估计 = 滤波后的动量导数
    // 当机器人静止在地面上时, p_dot ≈ 0, 但实际会有微小波动
    // 当脚触地时,地面反作用力导致动量变化
    tau_external_ = p_dot_;
    tau_external_filtered_ = filter_alpha_ * tau_external_ +
                              (1.0 - filter_alpha_) * tau_external_filtered_;
}

bool GMObserver::detectContact() const {
    // 使用滤波后的外部扭矩幅值进行判断
    // 也可以使用 norm() 来综合三个关节
    double torque_magnitude = tau_external_filtered_.norm();

    // 更鲁棒的检测: 检查垂直方向(小腿关节)扭矩
    // 因为触地时主要在pitch方向产生力矩
    double calf_torque = std::abs(tau_external_filtered_(2));

    // 综合判断: 幅值超过阈值 或者 小腿关节扭矩超过阈值
    return (torque_magnitude > threshold_) || (calf_torque > threshold_ * 0.6);
}

void GMObserver::reset() {
    q_.setZero();
    q_dot_.setZero();
    p_.setZero();
    p_dot_.setZero();
    p_dot_filtered_.setZero();
    tau_external_.setZero();
    tau_external_filtered_.setZero();
}

}  // namespace estimation
