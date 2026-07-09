#include <memory>
#include <string>

#include "geometry_msgs/msg/point_stamped.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_msgs/action/compute_path_to_pose.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

class RvizPctGoalSelector : public rclcpp::Node
{
public:
  using ComputePathToPose = nav2_msgs::action::ComputePathToPose;
  using GoalHandle = rclcpp_action::ClientGoalHandle<ComputePathToPose>;

  RvizPctGoalSelector()
  : Node("rviz_pct_goal_selector"), expect_start_(true)
  {
    declare_parameter<std::string>("clicked_topic", "/clicked_point");
    declare_parameter<std::string>("marker_topic", "/selection_markers");
    declare_parameter<std::string>("start_topic", "/pct_start_point");
    declare_parameter<std::string>("goal_topic", "/pct_goal_point");
    declare_parameter<std::string>("action_name", "/compute_path_to_pose");
    declare_parameter<std::string>("default_frame", "map");
    declare_parameter<double>("arrow_height", 0.6);
    declare_parameter<double>("arrow_length", 0.7);
    declare_parameter<double>("shaft_diameter", 0.12);
    declare_parameter<double>("head_diameter", 0.26);
    declare_parameter<double>("head_length", 0.36);
    declare_parameter<double>("cube_size", 0.18);

    const auto clicked_topic = get_parameter("clicked_topic").as_string();
    const auto marker_topic = get_parameter("marker_topic").as_string();
    const auto start_topic = get_parameter("start_topic").as_string();
    const auto goal_topic = get_parameter("goal_topic").as_string();
    const auto action_name = get_parameter("action_name").as_string();

    marker_pub_ = create_publisher<visualization_msgs::msg::MarkerArray>(
      marker_topic, rclcpp::QoS(1).transient_local().reliable());
    start_pub_ = create_publisher<geometry_msgs::msg::PointStamped>(
      start_topic, rclcpp::QoS(1).transient_local().reliable());
    goal_pub_ = create_publisher<geometry_msgs::msg::PointStamped>(
      goal_topic, rclcpp::QoS(1).transient_local().reliable());
    clicked_sub_ = create_subscription<geometry_msgs::msg::PointStamped>(
      clicked_topic, 10, std::bind(&RvizPctGoalSelector::onClickedPoint, this, std::placeholders::_1));
    action_client_ = rclcpp_action::create_client<ComputePathToPose>(this, action_name);

    RCLCPP_INFO(
      get_logger(),
      "rviz_pct_goal_selector started. First RViz Publish Point click sets START, second sets GOAL.");
  }

private:
  void onClickedPoint(const geometry_msgs::msg::PointStamped::SharedPtr msg)
  {
    auto clicked = *msg;
    if (clicked.header.frame_id.empty()) {
      clicked.header.frame_id = get_parameter("default_frame").as_string();
    }
    clicked.header.stamp = now();

    if (expect_start_) {
      start_point_ = clicked;
      has_start_ = true;
      start_pub_->publish(start_point_);
      RCLCPP_INFO(
        get_logger(), "Set START point: [%.3f, %.3f, %.3f] in %s",
        clicked.point.x, clicked.point.y, clicked.point.z, clicked.header.frame_id.c_str());
    } else {
      goal_point_ = clicked;
      has_goal_ = true;
      goal_pub_->publish(goal_point_);
      RCLCPP_INFO(
        get_logger(), "Set GOAL point: [%.3f, %.3f, %.3f] in %s",
        clicked.point.x, clicked.point.y, clicked.point.z, clicked.header.frame_id.c_str());
      sendPlanRequest();
    }

    expect_start_ = !expect_start_;
    publishMarkers();
  }

  void sendPlanRequest()
  {
    if (!has_start_ || !has_goal_) {
      return;
    }

    if (!action_client_->wait_for_action_server(std::chrono::seconds(1))) {
      RCLCPP_WARN(get_logger(), "PCT action server is not available yet.");
      return;
    }

    ComputePathToPose::Goal goal;
    goal.use_start = true;
    goal.start = pointToPose(start_point_);
    goal.goal = pointToPose(goal_point_);

    rclcpp_action::Client<ComputePathToPose>::SendGoalOptions options;
    options.goal_response_callback =
      [this](const GoalHandle::SharedPtr & handle) {
        if (!handle) {
          RCLCPP_WARN(get_logger(), "PCT rejected the selected start/goal.");
          return;
        }
        RCLCPP_INFO(get_logger(), "PCT accepted selected start/goal.");
      };
    options.result_callback =
      [this](const GoalHandle::WrappedResult & result) {
        if (result.code == rclcpp_action::ResultCode::SUCCEEDED) {
          RCLCPP_INFO(
            get_logger(), "PCT planned path from RViz clicks. poses=%zu",
            result.result->path.poses.size());
        } else {
          RCLCPP_WARN(get_logger(), "PCT planning from RViz clicks failed. result_code=%d", static_cast<int>(result.code));
        }
      };

    action_client_->async_send_goal(goal, options);
  }

  geometry_msgs::msg::PoseStamped pointToPose(const geometry_msgs::msg::PointStamped & point) const
  {
    geometry_msgs::msg::PoseStamped pose;
    pose.header = point.header;
    pose.pose.position = point.point;
    pose.pose.orientation.w = 1.0;
    return pose;
  }

  visualization_msgs::msg::Marker makeArrow(
    int id, const geometry_msgs::msg::PointStamped & point, float r, float g, float b) const
  {
    const double arrow_height = get_parameter("arrow_height").as_double();
    const double arrow_length = get_parameter("arrow_length").as_double();

    visualization_msgs::msg::Marker marker;
    marker.header = point.header;
    marker.ns = "rviz_pct_selector";
    marker.id = id;
    marker.type = visualization_msgs::msg::Marker::ARROW;
    marker.action = visualization_msgs::msg::Marker::ADD;
    marker.scale.x = get_parameter("shaft_diameter").as_double();
    marker.scale.y = get_parameter("head_diameter").as_double();
    marker.scale.z = get_parameter("head_length").as_double();
    marker.color.r = r;
    marker.color.g = g;
    marker.color.b = b;
    marker.color.a = 1.0F;
    marker.pose.orientation.w = 1.0;

    geometry_msgs::msg::Point base = point.point;
    base.z += arrow_height;
    geometry_msgs::msg::Point tip = base;
    tip.z -= arrow_length;
    marker.points.push_back(base);
    marker.points.push_back(tip);
    return marker;
  }

  visualization_msgs::msg::Marker makeCube(
    int id, const geometry_msgs::msg::PointStamped & point, float r, float g, float b) const
  {
    visualization_msgs::msg::Marker marker;
    marker.header = point.header;
    marker.ns = "rviz_pct_selector";
    marker.id = id;
    marker.type = visualization_msgs::msg::Marker::CUBE;
    marker.action = visualization_msgs::msg::Marker::ADD;
    marker.pose.position = point.point;
    marker.pose.orientation.w = 1.0;
    const double cube_size = get_parameter("cube_size").as_double();
    marker.scale.x = cube_size;
    marker.scale.y = cube_size;
    marker.scale.z = cube_size;
    marker.color.r = r;
    marker.color.g = g;
    marker.color.b = b;
    marker.color.a = 0.95F;
    return marker;
  }

  void publishMarkers()
  {
    visualization_msgs::msg::MarkerArray markers;

    visualization_msgs::msg::Marker clear_marker;
    clear_marker.header.frame_id = get_parameter("default_frame").as_string();
    clear_marker.header.stamp = now();
    clear_marker.action = visualization_msgs::msg::Marker::DELETEALL;
    markers.markers.push_back(clear_marker);

    if (has_start_) {
      markers.markers.push_back(makeArrow(0, start_point_, 0.1F, 0.95F, 0.1F));
      markers.markers.push_back(makeCube(2, start_point_, 0.1F, 0.95F, 0.1F));
    }
    if (has_goal_) {
      markers.markers.push_back(makeArrow(1, goal_point_, 0.95F, 0.1F, 0.1F));
      markers.markers.push_back(makeCube(3, goal_point_, 0.95F, 0.1F, 0.1F));
    }
    marker_pub_->publish(markers);
  }

  bool expect_start_;
  bool has_start_{false};
  bool has_goal_{false};
  geometry_msgs::msg::PointStamped start_point_;
  geometry_msgs::msg::PointStamped goal_point_;

  rclcpp::Subscription<geometry_msgs::msg::PointStamped>::SharedPtr clicked_sub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PointStamped>::SharedPtr start_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PointStamped>::SharedPtr goal_pub_;
  rclcpp_action::Client<ComputePathToPose>::SharedPtr action_client_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RvizPctGoalSelector>());
  rclcpp::shutdown();
  return 0;
}
