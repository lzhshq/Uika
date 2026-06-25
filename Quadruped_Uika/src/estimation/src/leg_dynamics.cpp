#include "estimation/leg_dynamics.hpp"

namespace estimation {

LegDynamics::LegDynamics() {}

Eigen::Matrix3d LegDynamics::computeInertiaMatrix(const Eigen::Vector3d& q) const {
    double l1 = LegConstants::L_THIGH;
    double l2 = LegConstants::L_CALF;
    double m1 = LegConstants::M_THIGH;
    double m2 = LegConstants::M_CALF;
    double l1c = LegConstants::THIGH_COM;  // 0.5 * L_THIGH
    double l2c = LegConstants::CALF_COM;    // 0.5 * L_CALF

    double s2 = std::sin(q(1));      // sin(thigh)
    double s12 = std::sin(q(1) + q(2));  // sin(thigh + calf)

    double I1_xx = LegConstants::I_THIGH_XX;
    double I1_zz = LegConstants::I_THIGH_ZZ;
    double I2_xx = LegConstants::I_CALF_XX;
    double I2_zz = LegConstants::I_CALF_ZZ;

    Eigen::Matrix3d M;
    M.setZero();

    // M(0,0) - Hip inertia
    M(0, 0) = (m1 + m2) * l1c * l1c + m2 * l2c * l2c + 2 * m2 * l1c * l2c * s2 +
              I1_xx + I2_xx;

    // M(1,1) - Thigh inertia
    M(1, 1) = (m1 + m2) * l1c * l1c + m2 * l2c * l2c + 2 * m2 * l1c * l2c * s2 +
              I1_zz + I2_zz;

    // M(1,2) and M(2,1)
    M(1, 2) = m2 * l2c * l2c + m2 * l1c * l2c * s2;
    M(2, 1) = M(1, 2);

    // M(2,2) - Calf inertia
    M(2, 2) = m2 * l2c * l2c + I2_zz;

    return M;
}

Eigen::Vector3d LegDynamics::computeCoriolisTerm(const Eigen::Vector3d& q,
                                                     const Eigen::Vector3d& q_dot) const {
    double l1c = LegConstants::THIGH_COM;
    double l2c = LegConstants::CALF_COM;
    double m2 = LegConstants::M_CALF;

    double s2 = std::sin(q(1));
    double c2 = std::cos(q(1));
    double q1_dot = q_dot(1);
    double q2_dot = q_dot(2);

    Eigen::Vector3d C_q_dot;
    C_q_dot.setZero();

    // C_1: Hip Coriolis (simplified)
    C_q_dot(0) = -m2 * l1c * l2c * s2 * (2 * q1_dot * q2_dot + q2_dot * q2_dot);

    // C_2: Thigh Coriolis
    C_q_dot(1) = m2 * l1c * l2c * s2 * q2_dot * q2_dot;

    // C_3: Calf Coriolis
    C_q_dot(2) = 0.0;

    return C_q_dot;
}

Eigen::Vector3d LegDynamics::computeGravityTerm(const Eigen::Vector3d& q) const {
    double m1 = LegConstants::M_THIGH;
    double m2 = LegConstants::M_CALF;
    double l1c = LegConstants::THIGH_COM;
    double l2c = LegConstants::CALF_COM;
    double g = LegConstants::G;

    double s1 = std::sin(q(1));       // sin(thigh)
    double s12 = std::sin(q(1) + q(2));  // sin(thigh + calf)

    Eigen::Vector3d g_vec;
    g_vec.setZero();

    // Hip doesn't see gravity directly (axis is vertical)
    g_vec(0) = 0.0;

    // Thigh gravity term
    g_vec(1) = -(m1 * l1c + m2 * l1c) * g * s1 - m2 * l2c * g * s12;

    // Calf gravity term
    g_vec(2) = -m2 * l2c * g * s12;

    return g_vec;
}

}  // namespace estimation
