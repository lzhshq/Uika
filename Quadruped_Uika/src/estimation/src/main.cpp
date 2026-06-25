#include <rclcpp/rclcpp.hpp>
#include "estimation/contact_detection_node.hpp"

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<estimation::ContactDetectionNode>();

    // 使用多线程执行器以支持异步回调
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);

    RCLCPP_INFO(node->get_logger(), "Starting contact detection node...");

    executor.spin();

    rclcpp::shutdown();
    return 0;
}
