#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <deque>
#include <functional>
#include <limits>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include <Eigen/Core>
#include <Eigen/Geometry>

#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <pcl/common/transforms.h>
#include <pcl/filters/crop_box.h>
#include <pcl/filters/filter.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/io/pcd_io.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/registration/icp.h>
#include <pcl/registration/ndt.h>
#include <pcl_conversions/pcl_conversions.h>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float64.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <tf2_ros/transform_broadcaster.h>

namespace
{
using PointT = pcl::PointXYZI;
using Cloud = pcl::PointCloud<PointT>;

double normalizeAngle(double angle)
{
  while (angle > M_PI) angle -= 2.0 * M_PI;
  while (angle < -M_PI) angle += 2.0 * M_PI;
  return angle;
}

double stampToSeconds(const builtin_interfaces::msg::Time & stamp)
{
  return static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1e-9;
}

double yawFromRotation(const Eigen::Matrix3d & rotation)
{
  return std::atan2(rotation(1, 0), rotation(0, 0));
}

Eigen::Isometry3d poseToIsometry(const geometry_msgs::msg::Pose & pose)
{
  Eigen::Quaterniond quaternion(
    pose.orientation.w, pose.orientation.x, pose.orientation.y, pose.orientation.z);
  if (quaternion.norm() < 1e-9) quaternion = Eigen::Quaterniond::Identity();
  quaternion.normalize();

  Eigen::Isometry3d transform = Eigen::Isometry3d::Identity();
  transform.linear() = quaternion.toRotationMatrix();
  transform.translation() = Eigen::Vector3d(pose.position.x, pose.position.y, pose.position.z);
  return transform;
}

geometry_msgs::msg::Transform isometryToTransform(const Eigen::Isometry3d & transform)
{
  geometry_msgs::msg::Transform message;
  const Eigen::Quaterniond quaternion(transform.rotation());
  message.translation.x = transform.translation().x();
  message.translation.y = transform.translation().y();
  message.translation.z = transform.translation().z();
  message.rotation.x = quaternion.x();
  message.rotation.y = quaternion.y();
  message.rotation.z = quaternion.z();
  message.rotation.w = quaternion.w();
  return message;
}

geometry_msgs::msg::Pose isometryToPose(const Eigen::Isometry3d & transform)
{
  geometry_msgs::msg::Pose pose;
  const auto converted = isometryToTransform(transform);
  pose.position.x = converted.translation.x;
  pose.position.y = converted.translation.y;
  pose.position.z = converted.translation.z;
  pose.orientation = converted.rotation;
  return pose;
}

Eigen::Isometry3d makeYawTransform(double x, double y, double z, double yaw)
{
  Eigen::Isometry3d transform = Eigen::Isometry3d::Identity();
  transform.translation() = Eigen::Vector3d(x, y, z);
  transform.linear() = Eigen::AngleAxisd(yaw, Eigen::Vector3d::UnitZ()).toRotationMatrix();
  return transform;
}
}  // namespace

class FixedStartRelocalizer : public rclcpp::Node
{
public:
  FixedStartRelocalizer() : Node("fixed_start_relocalizer")
  {
    map_path_ = declare_parameter<std::string>("map_path", "");
    source_topic_ = declare_parameter<std::string>(
      "source_topic", "/cloud_registered_body");
    odom_topic_ = declare_parameter<std::string>("odom_topic", "/aft_mapped_to_init");
    map_frame_ = declare_parameter<std::string>("map_frame", "map");
    odom_frame_ = declare_parameter<std::string>("odom_frame", "odom");
    base_frame_ = declare_parameter<std::string>("base_frame", "base_link");

    source_frames_ = std::max(
      1, static_cast<int>(declare_parameter<int>("source_frames", 10)));
    validation_count_ = std::max(
      1, static_cast<int>(declare_parameter<int>("validation_count", 3)));
    source_voxel_ = declare_parameter<double>("source_voxel", 0.10);
    target_voxel_ = declare_parameter<double>("target_voxel", 0.15);
    local_map_radius_ = declare_parameter<double>("local_map_radius", 6.0);
    local_map_z_radius_ = declare_parameter<double>("local_map_z_radius", 3.0);
    yaw_search_range_ = declare_parameter<double>("yaw_search_range", 0.35);
    yaw_search_step_ = declare_parameter<double>("yaw_search_step", 0.0872664626);
    ndt_resolution_ = declare_parameter<double>("ndt_resolution", 0.50);
    ndt_step_size_ = declare_parameter<double>("ndt_step_size", 0.10);
    ndt_iterations_ = declare_parameter<int>("ndt_iterations", 30);
    icp_max_distance_ = declare_parameter<double>("icp_max_distance", 0.30);
    icp_iterations_ = declare_parameter<int>("icp_iterations", 50);
    metric_max_distance_ = declare_parameter<double>("metric_max_distance", 0.25);
    max_rmse_ = declare_parameter<double>("max_rmse", 0.20);
    min_overlap_ = declare_parameter<double>("min_overlap", 0.40);
    max_prior_xy_ = declare_parameter<double>("max_prior_xy", 0.75);
    max_prior_z_ = declare_parameter<double>("max_prior_z", 0.50);
    max_prior_yaw_ = declare_parameter<double>("max_prior_yaw", 0.436332313);
    consistency_xy_ = declare_parameter<double>("consistency_xy", 0.08);
    consistency_z_ = declare_parameter<double>("consistency_z", 0.10);
    consistency_yaw_ = declare_parameter<double>("consistency_yaw", 0.052359878);

    continuous_shadow_enabled_ = declare_parameter<bool>("continuous_shadow.enabled", false);
    continuous_interval_ = declare_parameter<double>("continuous_shadow.interval", 2.0);
    continuous_source_frames_ = std::max(
      1, static_cast<int>(declare_parameter<int>("continuous_shadow.source_frames", 5)));
    continuous_odom_tolerance_ = declare_parameter<double>(
      "continuous_shadow.odom_tolerance", 0.03);
    continuous_local_map_radius_ = declare_parameter<double>(
      "continuous_shadow.local_map_radius", 5.0);
    continuous_yaw_range_ = declare_parameter<double>(
      "continuous_shadow.yaw_search_range", 0.0872664626);
    continuous_yaw_step_ = declare_parameter<double>(
      "continuous_shadow.yaw_search_step", 0.0872664626);
    continuous_max_rmse_ = declare_parameter<double>("continuous_shadow.max_rmse", 0.15);
    continuous_min_overlap_ = declare_parameter<double>(
      "continuous_shadow.min_overlap", 0.55);
    continuous_max_correction_xy_ = declare_parameter<double>(
      "continuous_shadow.max_correction_xy", 0.20);
    continuous_max_correction_z_ = declare_parameter<double>(
      "continuous_shadow.max_correction_z", 0.10);
    continuous_max_correction_yaw_ = declare_parameter<double>(
      "continuous_shadow.max_correction_yaw", 0.0872664626);
    continuous_consistency_count_ = std::max(
      1, static_cast<int>(declare_parameter<int>("continuous_shadow.consistency_count", 3)));

    const double prior_x = declare_parameter<double>("prior.x", 0.0);
    const double prior_y = declare_parameter<double>("prior.y", 0.0);
    const double prior_z = declare_parameter<double>("prior.z", 0.0);
    const double prior_yaw = declare_parameter<double>("prior.yaw", 0.0);
    prior_map_to_odom_ = makeYawTransform(prior_x, prior_y, prior_z, prior_yaw);

    const double base_body_x = declare_parameter<double>("base_to_body.x", 0.313710623);
    const double base_body_y = declare_parameter<double>("base_to_body.y", 0.02329);
    const double base_body_z = declare_parameter<double>("base_to_body.z", -0.080845726);
    const double base_body_roll = declare_parameter<double>("base_to_body.roll", 0.0);
    const double base_body_pitch = declare_parameter<double>("base_to_body.pitch", 0.7853981634);
    const double base_body_yaw = declare_parameter<double>("base_to_body.yaw", 0.0);
    base_to_body_ = Eigen::Isometry3d::Identity();
    base_to_body_.translation() = Eigen::Vector3d(base_body_x, base_body_y, base_body_z);
    base_to_body_.linear() =
      (Eigen::AngleAxisd(base_body_yaw, Eigen::Vector3d::UnitZ()) *
      Eigen::AngleAxisd(base_body_pitch, Eigen::Vector3d::UnitY()) *
      Eigen::AngleAxisd(base_body_roll, Eigen::Vector3d::UnitX())).toRotationMatrix();

    if (map_path_.empty()) {
      throw std::runtime_error("Parameter map_path must point to a PCD map");
    }
    loadMap();

    const auto transient_qos = rclcpp::QoS(1).reliable().transient_local();
    status_pub_ = create_publisher<std_msgs::msg::String>("relocalization/status", transient_qos);
    success_pub_ = create_publisher<std_msgs::msg::Bool>("relocalization/success", transient_qos);
    rmse_pub_ = create_publisher<std_msgs::msg::Float64>("relocalization/rmse", transient_qos);
    overlap_pub_ = create_publisher<std_msgs::msg::Float64>(
      "relocalization/overlap", transient_qos);
    candidate_pose_pub_ = create_publisher<geometry_msgs::msg::PoseStamped>(
      "relocalization/candidate_map_to_odom", transient_qos);
    pose_pub_ = create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(
      "relocalization/pose", transient_qos);
    aligned_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(
      "relocalization/aligned_cloud", transient_qos);
    local_map_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(
      "relocalization/local_map", transient_qos);

    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      odom_topic_, rclcpp::QoS(20).reliable(),
      std::bind(&FixedStartRelocalizer::odomCallback, this, std::placeholders::_1));
    ensureCloudSubscription();

    retry_service_ = create_service<std_srvs::srv::Trigger>(
      "relocalize",
      std::bind(
        &FixedStartRelocalizer::retryCallback, this, std::placeholders::_1,
        std::placeholders::_2));

    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
    tf_timer_ = create_wall_timer(
      std::chrono::milliseconds(50), std::bind(&FixedStartRelocalizer::publishTransform, this));

    resetState("WAITING_FOR_ODOM");
    RCLCPP_INFO(
      get_logger(), "Loaded %zu map points from %s", map_cloud_->size(), map_path_.c_str());
  }

  ~FixedStartRelocalizer() override
  {
    if (matching_worker_.joinable()) matching_worker_.join();
  }

private:
  void ensureCloudSubscription()
  {
    if (cloud_sub_) return;
    cloud_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
      source_topic_, rclcpp::SensorDataQoS(),
      std::bind(&FixedStartRelocalizer::cloudCallback, this, std::placeholders::_1));
  }

  void loadMap()
  {
    Cloud::Ptr raw(new Cloud());
    if (pcl::io::loadPCDFile<PointT>(map_path_, *raw) != 0 || raw->empty()) {
      throw std::runtime_error("Failed to load non-empty PCD map: " + map_path_);
    }

    std::vector<int> indices;
    pcl::removeNaNFromPointCloud(*raw, *raw, indices);
    pcl::VoxelGrid<PointT> voxel;
    voxel.setLeafSize(target_voxel_, target_voxel_, target_voxel_);
    voxel.setInputCloud(raw);
    map_cloud_.reset(new Cloud());
    voxel.filter(*map_cloud_);
    if (map_cloud_->size() < 100) {
      throw std::runtime_error("PCD map has too few valid points after downsampling");
    }
  }

  void odomCallback(const nav_msgs::msg::Odometry::SharedPtr message)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    latest_odom_to_base_ = poseToIsometry(message->pose.pose);
    latest_odom_stamp_ = message->header.stamp;
    odom_history_.push_back({stampToSeconds(message->header.stamp), latest_odom_to_base_});
    while (odom_history_.size() > 100) odom_history_.pop_front();
    have_odom_ = true;
    if (!localized_ && status_ == "WAITING_FOR_ODOM") {
      setStatusLocked("COLLECTING 0/" + std::to_string(source_frames_));
    }
  }

  void cloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr message)
  {
    std::unique_lock<std::mutex> lock(mutex_);
    if (matching_ || !have_odom_) return;
    if (localized_) {
      handleContinuousCloudLocked(message, lock);
      return;
    }
    if (message->header.frame_id != "body") {
      setStatusLocked("FAILED: expected cloud frame body, got " + message->header.frame_id);
      return;
    }

    Cloud body_cloud;
    pcl::fromROSMsg(*message, body_cloud);
    Cloud base_cloud;
    pcl::transformPointCloud(body_cloud, base_cloud, base_to_body_.matrix().cast<float>());
    *accumulated_source_ += base_cloud;
    accumulated_frames_++;
    setStatusLocked(
      "COLLECTING " + std::to_string(accumulated_frames_) + "/" +
      std::to_string(source_frames_));
    if (accumulated_frames_ < source_frames_) return;

    matching_ = true;
    const auto odom_to_base = latest_odom_to_base_;
    const auto stamp = message->header.stamp;
    Cloud::Ptr source(new Cloud(*accumulated_source_));
    accumulated_source_->clear();
    accumulated_frames_ = 0;
    setStatusLocked("MATCHING");
    lock.unlock();

    MatchResult result = registerCloud(source, odom_to_base, stamp);

    lock.lock();
    matching_ = false;
    handleResultLocked(result, odom_to_base, stamp);
  }

  struct TimedOdom
  {
    double stamp;
    Eigen::Isometry3d odom_to_base;
  };

  struct MatchResult
  {
    bool converged{false};
    bool accepted{false};
    Eigen::Isometry3d map_to_odom{Eigen::Isometry3d::Identity()};
    Eigen::Isometry3d map_to_base{Eigen::Isometry3d::Identity()};
    Cloud::Ptr aligned{new Cloud()};
    Cloud::Ptr local_map{new Cloud()};
    double rmse{std::numeric_limits<double>::infinity()};
    double overlap{0.0};
    double prior_xy{std::numeric_limits<double>::infinity()};
    double prior_z{std::numeric_limits<double>::infinity()};
    double prior_yaw{std::numeric_limits<double>::infinity()};
    std::string reason;
  };

  bool findOdomAtStampLocked(
    const builtin_interfaces::msg::Time & stamp, Eigen::Isometry3d & odom_to_base) const
  {
    if (odom_history_.empty()) return false;
    const double target = stampToSeconds(stamp);
    double best_difference = std::numeric_limits<double>::infinity();
    const TimedOdom * best = nullptr;
    for (auto iterator = odom_history_.rbegin(); iterator != odom_history_.rend(); ++iterator) {
      const double difference = std::abs(iterator->stamp - target);
      if (difference < best_difference) {
        best_difference = difference;
        best = &*iterator;
      }
      if (iterator->stamp < target && difference > best_difference) break;
    }
    if (best == nullptr || best_difference > continuous_odom_tolerance_) return false;
    odom_to_base = best->odom_to_base;
    return true;
  }

  void handleContinuousCloudLocked(
    const sensor_msgs::msg::PointCloud2::SharedPtr & message,
    std::unique_lock<std::mutex> & lock)
  {
    if (!continuous_shadow_enabled_ ||
      std::chrono::steady_clock::now() < next_continuous_attempt_)
    {
      return;
    }
    if (message->header.frame_id != "body") {
      setStatusLocked("SHADOW_REJECTED: expected cloud frame body");
      return;
    }

    Eigen::Isometry3d odom_to_base;
    if (!findOdomAtStampLocked(message->header.stamp, odom_to_base)) {
      setStatusLocked("SHADOW_WAITING_FOR_SYNCED_ODOM");
      return;
    }

    Cloud body_cloud;
    pcl::fromROSMsg(*message, body_cloud);
    Cloud base_cloud;
    Cloud odom_cloud;
    pcl::transformPointCloud(body_cloud, base_cloud, base_to_body_.matrix().cast<float>());
    pcl::transformPointCloud(base_cloud, odom_cloud, odom_to_base.matrix().cast<float>());
    *continuous_source_ += odom_cloud;
    continuous_accumulated_frames_++;
    setStatusLocked(
      "SHADOW_COLLECTING " + std::to_string(continuous_accumulated_frames_) + "/" +
      std::to_string(continuous_source_frames_));
    if (continuous_accumulated_frames_ < continuous_source_frames_) return;

    if (matching_worker_.joinable()) matching_worker_.join();
    Cloud::Ptr source(new Cloud(*continuous_source_));
    continuous_source_->clear();
    continuous_accumulated_frames_ = 0;
    const auto reference_map_to_odom = map_to_odom_;
    const auto current_odom_to_base = odom_to_base;
    const auto stamp = message->header.stamp;
    matching_ = true;
    next_continuous_attempt_ = std::chrono::steady_clock::now() +
      std::chrono::duration_cast<std::chrono::steady_clock::duration>(
      std::chrono::duration<double>(continuous_interval_));
    setStatusLocked("SHADOW_MATCHING");

    matching_worker_ = std::thread(
      [this, source, reference_map_to_odom, current_odom_to_base, stamp]() {
        MatchResult result = registerContinuousCloud(
          source, reference_map_to_odom, current_odom_to_base, stamp);
        std::lock_guard<std::mutex> result_lock(mutex_);
        matching_ = false;
        handleContinuousResultLocked(result, stamp);
      });
    (void)lock;
  }

  MatchResult registerCloud(
    const Cloud::Ptr & accumulated, const Eigen::Isometry3d & odom_to_base,
    const builtin_interfaces::msg::Time & stamp)
  {
    (void)stamp;
    MatchResult result;
    std::vector<int> finite_indices;
    Cloud::Ptr finite(new Cloud());
    pcl::removeNaNFromPointCloud(*accumulated, *finite, finite_indices);

    pcl::VoxelGrid<PointT> source_voxel;
    source_voxel.setLeafSize(source_voxel_, source_voxel_, source_voxel_);
    source_voxel.setInputCloud(finite);
    Cloud::Ptr source(new Cloud());
    source_voxel.filter(*source);
    if (source->size() < 100) {
      result.reason = "too few source points";
      return result;
    }

    const Eigen::Isometry3d initial_map_to_base = prior_map_to_odom_ * odom_to_base;
    pcl::CropBox<PointT> crop;
    crop.setInputCloud(map_cloud_);
    const auto center = initial_map_to_base.translation().cast<float>();
    crop.setMin(Eigen::Vector4f(
      center.x() - local_map_radius_, center.y() - local_map_radius_,
      center.z() - local_map_z_radius_, 1.0f));
    crop.setMax(Eigen::Vector4f(
      center.x() + local_map_radius_, center.y() + local_map_radius_,
      center.z() + local_map_z_radius_, 1.0f));
    crop.filter(*result.local_map);
    if (result.local_map->size() < 200) {
      result.reason = "too few local map points";
      return result;
    }

    pcl::NormalDistributionsTransform<PointT, PointT> ndt;
    ndt.setTransformationEpsilon(0.01);
    ndt.setStepSize(ndt_step_size_);
    ndt.setResolution(ndt_resolution_);
    ndt.setMaximumIterations(ndt_iterations_);
    ndt.setInputSource(source);
    ndt.setInputTarget(result.local_map);

    Eigen::Matrix4f best_transform = initial_map_to_base.matrix().cast<float>();
    double best_score = std::numeric_limits<double>::infinity();
    const int yaw_steps = std::max(0, static_cast<int>(std::ceil(
      yaw_search_range_ / std::max(1e-6, yaw_search_step_))));
    for (int step = -yaw_steps; step <= yaw_steps; ++step) {
      const double yaw_offset = step * yaw_search_step_;
      Eigen::Isometry3d guess = initial_map_to_base;
      guess.linear() =
        Eigen::AngleAxisd(yaw_offset, Eigen::Vector3d::UnitZ()).toRotationMatrix() *
        initial_map_to_base.rotation();
      Cloud output;
      ndt.align(output, guess.matrix().cast<float>());
      if (!ndt.hasConverged()) continue;
      const double score = ndt.getFitnessScore(icp_max_distance_ * 2.0);
      if (std::isfinite(score) && score < best_score) {
        best_score = score;
        best_transform = ndt.getFinalTransformation();
      }
    }
    if (!std::isfinite(best_score)) {
      result.reason = "NDT did not converge";
      return result;
    }

    pcl::IterativeClosestPoint<PointT, PointT> icp;
    icp.setInputSource(source);
    icp.setInputTarget(result.local_map);
    icp.setMaximumIterations(icp_iterations_);
    icp.setMaxCorrespondenceDistance(icp_max_distance_);
    icp.setTransformationEpsilon(1e-8);
    icp.setEuclideanFitnessEpsilon(1e-6);
    Cloud fine_output;
    icp.align(fine_output, best_transform);
    if (!icp.hasConverged()) {
      result.reason = "ICP did not converge";
      return result;
    }
    result.converged = true;

    const Eigen::Matrix4d raw_map_to_base = icp.getFinalTransformation().cast<double>();
    const Eigen::Isometry3d raw_map_to_odom(
      raw_map_to_base * odom_to_base.inverse().matrix());
    result.map_to_odom = makeYawTransform(
      raw_map_to_odom.translation().x(), raw_map_to_odom.translation().y(),
      raw_map_to_odom.translation().z(), yawFromRotation(raw_map_to_odom.rotation()));
    result.map_to_base = result.map_to_odom * odom_to_base;
    pcl::transformPointCloud(
      *source, *result.aligned, result.map_to_base.matrix().cast<float>());

    calculateMetrics(result.aligned, result.local_map, result.rmse, result.overlap);
    const Eigen::Isometry3d prior_delta = prior_map_to_odom_.inverse() * result.map_to_odom;
    result.prior_xy = prior_delta.translation().head<2>().norm();
    result.prior_z = std::abs(prior_delta.translation().z());
    result.prior_yaw = std::abs(yawFromRotation(prior_delta.rotation()));
    result.accepted = result.rmse <= max_rmse_ && result.overlap >= min_overlap_ &&
      result.prior_xy <= max_prior_xy_ && result.prior_z <= max_prior_z_ &&
      result.prior_yaw <= max_prior_yaw_;
    if (!result.accepted) {
      result.reason = "quality or prior gate rejected the match";
    }
    return result;
  }

  MatchResult registerContinuousCloud(
    const Cloud::Ptr & accumulated_odom, const Eigen::Isometry3d & reference_map_to_odom,
    const Eigen::Isometry3d & odom_to_base, const builtin_interfaces::msg::Time & stamp)
  {
    (void)stamp;
    MatchResult result;
    std::vector<int> finite_indices;
    Cloud::Ptr finite(new Cloud());
    pcl::removeNaNFromPointCloud(*accumulated_odom, *finite, finite_indices);

    pcl::VoxelGrid<PointT> source_voxel;
    source_voxel.setLeafSize(source_voxel_, source_voxel_, source_voxel_);
    source_voxel.setInputCloud(finite);
    Cloud::Ptr source(new Cloud());
    source_voxel.filter(*source);
    if (source->size() < 100) {
      result.reason = "too few synchronized source points";
      return result;
    }

    const Eigen::Isometry3d predicted_map_to_base = reference_map_to_odom * odom_to_base;
    pcl::CropBox<PointT> crop;
    crop.setInputCloud(map_cloud_);
    const auto center = predicted_map_to_base.translation().cast<float>();
    crop.setMin(Eigen::Vector4f(
      center.x() - continuous_local_map_radius_,
      center.y() - continuous_local_map_radius_,
      center.z() - local_map_z_radius_, 1.0f));
    crop.setMax(Eigen::Vector4f(
      center.x() + continuous_local_map_radius_,
      center.y() + continuous_local_map_radius_,
      center.z() + local_map_z_radius_, 1.0f));
    crop.filter(*result.local_map);
    if (result.local_map->size() < 200) {
      result.reason = "too few local map points";
      return result;
    }

    pcl::NormalDistributionsTransform<PointT, PointT> ndt;
    ndt.setTransformationEpsilon(0.01);
    ndt.setStepSize(ndt_step_size_);
    ndt.setResolution(ndt_resolution_);
    ndt.setMaximumIterations(ndt_iterations_);
    ndt.setInputSource(source);
    ndt.setInputTarget(result.local_map);

    Eigen::Matrix4f best_transform = reference_map_to_odom.matrix().cast<float>();
    double best_score = std::numeric_limits<double>::infinity();
    const int yaw_steps = std::max(0, static_cast<int>(std::ceil(
      continuous_yaw_range_ / std::max(1e-6, continuous_yaw_step_))));
    for (int step = -yaw_steps; step <= yaw_steps; ++step) {
      const double yaw_offset = step * continuous_yaw_step_;
      Eigen::Isometry3d guess = reference_map_to_odom;
      guess.linear() =
        Eigen::AngleAxisd(yaw_offset, Eigen::Vector3d::UnitZ()).toRotationMatrix() *
        reference_map_to_odom.rotation();
      Cloud output;
      ndt.align(output, guess.matrix().cast<float>());
      if (!ndt.hasConverged()) continue;
      const double score = ndt.getFitnessScore(icp_max_distance_ * 2.0);
      if (std::isfinite(score) && score < best_score) {
        best_score = score;
        best_transform = ndt.getFinalTransformation();
      }
    }
    if (!std::isfinite(best_score)) {
      result.reason = "NDT did not converge";
      return result;
    }

    pcl::IterativeClosestPoint<PointT, PointT> icp;
    icp.setInputSource(source);
    icp.setInputTarget(result.local_map);
    icp.setMaximumIterations(icp_iterations_);
    icp.setMaxCorrespondenceDistance(icp_max_distance_);
    icp.setTransformationEpsilon(1e-8);
    icp.setEuclideanFitnessEpsilon(1e-6);
    Cloud fine_output;
    icp.align(fine_output, best_transform);
    if (!icp.hasConverged()) {
      result.reason = "ICP did not converge";
      return result;
    }
    result.converged = true;

    const Eigen::Matrix4d raw_map_to_odom = icp.getFinalTransformation().cast<double>();
    result.map_to_odom = makeYawTransform(
      raw_map_to_odom(0, 3), raw_map_to_odom(1, 3), raw_map_to_odom(2, 3),
      yawFromRotation(raw_map_to_odom.block<3, 3>(0, 0)));
    result.map_to_base = result.map_to_odom * odom_to_base;
    pcl::transformPointCloud(
      *source, *result.aligned, result.map_to_odom.matrix().cast<float>());

    calculateMetrics(result.aligned, result.local_map, result.rmse, result.overlap);
    const Eigen::Isometry3d correction = reference_map_to_odom.inverse() * result.map_to_odom;
    result.prior_xy = correction.translation().head<2>().norm();
    result.prior_z = std::abs(correction.translation().z());
    result.prior_yaw = std::abs(normalizeAngle(yawFromRotation(correction.rotation())));
    result.accepted = result.rmse <= continuous_max_rmse_ &&
      result.overlap >= continuous_min_overlap_ &&
      result.prior_xy <= continuous_max_correction_xy_ &&
      result.prior_z <= continuous_max_correction_z_ &&
      result.prior_yaw <= continuous_max_correction_yaw_;
    if (!result.accepted) result.reason = "shadow quality or correction gate rejected the match";
    return result;
  }

  void calculateMetrics(
    const Cloud::Ptr & aligned, const Cloud::Ptr & target, double & rmse, double & overlap) const
  {
    pcl::KdTreeFLANN<PointT> tree;
    tree.setInputCloud(target);
    std::vector<int> indices(1);
    std::vector<float> distances(1);
    const double max_distance_squared = metric_max_distance_ * metric_max_distance_;
    std::size_t inliers = 0;
    double squared_error = 0.0;
    for (const auto & point : aligned->points) {
      if (tree.nearestKSearch(point, 1, indices, distances) == 1 &&
        distances[0] <= max_distance_squared)
      {
        inliers++;
        squared_error += distances[0];
      }
    }
    overlap = aligned->empty() ? 0.0 : static_cast<double>(inliers) / aligned->size();
    rmse = inliers == 0 ? std::numeric_limits<double>::infinity() :
      std::sqrt(squared_error / static_cast<double>(inliers));
  }

  void handleResultLocked(
    const MatchResult & result, const Eigen::Isometry3d & odom_to_base,
    const builtin_interfaces::msg::Time & stamp)
  {
    publishMetrics(result, stamp);
    if (!result.accepted) {
      consistency_count_ = 0;
      have_candidate_ = false;
      setStatusLocked(
        "REJECTED: " + result.reason + metricsText(result) + "; retrying");
      return;
    }

    if (have_candidate_ && isConsistent(last_candidate_, result.map_to_odom)) {
      consistency_count_++;
    } else {
      last_candidate_ = result.map_to_odom;
      consistency_count_ = 1;
      have_candidate_ = true;
    }

    if (consistency_count_ < validation_count_) {
      setStatusLocked(
        "VALIDATING " + std::to_string(consistency_count_) + "/" +
        std::to_string(validation_count_) + metricsText(result));
      return;
    }

    map_to_odom_ = result.map_to_odom;
    localized_ = true;
    continuous_stable_count_ = 0;
    continuous_have_candidate_ = false;
    continuous_source_->clear();
    continuous_accumulated_frames_ = 0;
    next_continuous_attempt_ = std::chrono::steady_clock::now() +
      std::chrono::duration_cast<std::chrono::steady_clock::duration>(
      std::chrono::duration<double>(continuous_interval_));
    setStatusLocked("SUCCESS" + metricsText(result));

    geometry_msgs::msg::PoseWithCovarianceStamped pose;
    pose.header.frame_id = map_frame_;
    pose.header.stamp = stamp;
    pose.pose.pose = isometryToPose(map_to_odom_ * odom_to_base);
    pose.pose.covariance[0] = result.rmse * result.rmse;
    pose.pose.covariance[7] = result.rmse * result.rmse;
    pose.pose.covariance[14] = result.rmse * result.rmse;
    pose.pose.covariance[35] = consistency_yaw_ * consistency_yaw_;
    pose_pub_->publish(pose);

    std_msgs::msg::Bool success;
    success.data = true;
    success_pub_->publish(success);
    if (!continuous_shadow_enabled_) {
      cloud_sub_.reset();
      accumulated_source_->clear();
      RCLCPP_INFO(
        get_logger(),
        "Continuous correction is disabled; released the registered-cloud subscription");
    }
    RCLCPP_INFO(
      get_logger(), "Relocalization succeeded: x=%.3f y=%.3f z=%.3f yaw=%.2f deg%s",
      map_to_odom_.translation().x(), map_to_odom_.translation().y(),
      map_to_odom_.translation().z(),
      yawFromRotation(map_to_odom_.rotation()) * 180.0 / M_PI, metricsText(result).c_str());
  }

  void handleContinuousResultLocked(
    const MatchResult & result, const builtin_interfaces::msg::Time & stamp)
  {
    publishMetrics(result, stamp);
    if (!result.accepted) {
      continuous_stable_count_ = 0;
      continuous_have_candidate_ = false;
      setStatusLocked("SHADOW_REJECTED: " + result.reason + metricsText(result));
      return;
    }

    geometry_msgs::msg::PoseStamped candidate;
    candidate.header.frame_id = map_frame_;
    candidate.header.stamp = stamp;
    candidate.pose = isometryToPose(result.map_to_odom);
    candidate_pose_pub_->publish(candidate);

    if (continuous_have_candidate_ &&
      isConsistent(continuous_last_candidate_, result.map_to_odom))
    {
      continuous_stable_count_++;
    } else {
      continuous_last_candidate_ = result.map_to_odom;
      continuous_stable_count_ = 1;
      continuous_have_candidate_ = true;
    }

    const std::string state = continuous_stable_count_ >= continuous_consistency_count_ ?
      "SHADOW_STABLE " : "SHADOW_VALIDATING " + std::to_string(continuous_stable_count_) +
      "/" + std::to_string(continuous_consistency_count_) + " ";
    setStatusLocked(state + metricsText(result));
  }

  bool isConsistent(const Eigen::Isometry3d & first, const Eigen::Isometry3d & second) const
  {
    const Eigen::Isometry3d delta = first.inverse() * second;
    return delta.translation().head<2>().norm() <= consistency_xy_ &&
      std::abs(delta.translation().z()) <= consistency_z_ &&
      std::abs(normalizeAngle(yawFromRotation(delta.rotation()))) <= consistency_yaw_;
  }

  std::string metricsText(const MatchResult & result) const
  {
    char text[256];
    std::snprintf(
      text, sizeof(text), " rmse=%.3f overlap=%.2f prior_xy=%.3f prior_z=%.3f prior_yaw=%.1fdeg",
      result.rmse, result.overlap, result.prior_xy, result.prior_z,
      result.prior_yaw * 180.0 / M_PI);
    return text;
  }

  void publishMetrics(const MatchResult & result, const builtin_interfaces::msg::Time & stamp)
  {
    std_msgs::msg::Float64 rmse;
    rmse.data = result.rmse;
    rmse_pub_->publish(rmse);
    std_msgs::msg::Float64 overlap;
    overlap.data = result.overlap;
    overlap_pub_->publish(overlap);

    if (
      !result.local_map->empty() && local_map_pub_ &&
      local_map_pub_->get_subscription_count() > 0)
    {
      sensor_msgs::msg::PointCloud2 message;
      pcl::toROSMsg(*result.local_map, message);
      message.header.frame_id = map_frame_;
      message.header.stamp = stamp;
      local_map_pub_->publish(message);
    }
    if (
      !result.aligned->empty() && aligned_pub_ &&
      aligned_pub_->get_subscription_count() > 0)
    {
      sensor_msgs::msg::PointCloud2 message;
      pcl::toROSMsg(*result.aligned, message);
      message.header.frame_id = map_frame_;
      message.header.stamp = stamp;
      aligned_pub_->publish(message);
    }
  }

  void retryCallback(
    const std::shared_ptr<std_srvs::srv::Trigger::Request>,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (matching_) {
      response->success = false;
      response->message = "A registration is still running; retry after it completes";
      return;
    }
    ensureCloudSubscription();
    resetState(have_odom_ ? "COLLECTING 0/" + std::to_string(source_frames_) :
      "WAITING_FOR_ODOM");
    response->success = true;
    response->message = "Relocalization state reset";
  }

  void resetState(const std::string & status)
  {
    localized_ = false;
    matching_ = false;
    accumulated_frames_ = 0;
    accumulated_source_.reset(new Cloud());
    consistency_count_ = 0;
    have_candidate_ = false;
    continuous_source_->clear();
    continuous_accumulated_frames_ = 0;
    continuous_stable_count_ = 0;
    continuous_have_candidate_ = false;
    map_to_odom_ = prior_map_to_odom_;
    setStatusLocked(status);
    std_msgs::msg::Bool success;
    success.data = false;
    if (success_pub_) success_pub_->publish(success);
  }

  void setStatusLocked(const std::string & status)
  {
    if (status == status_) return;
    status_ = status;
    std_msgs::msg::String message;
    message.data = status;
    if (status_pub_) status_pub_->publish(message);
    RCLCPP_INFO(get_logger(), "%s", status.c_str());
  }

  void publishTransform()
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!localized_) return;
    geometry_msgs::msg::TransformStamped transform;
    transform.header.stamp = now();
    transform.header.frame_id = map_frame_;
    transform.child_frame_id = odom_frame_;
    transform.transform = isometryToTransform(map_to_odom_);
    tf_broadcaster_->sendTransform(transform);
  }

  std::string map_path_;
  std::string source_topic_;
  std::string odom_topic_;
  std::string map_frame_;
  std::string odom_frame_;
  std::string base_frame_;
  int source_frames_;
  int validation_count_;
  int ndt_iterations_;
  int icp_iterations_;
  int continuous_source_frames_;
  int continuous_consistency_count_;
  double source_voxel_;
  double target_voxel_;
  double local_map_radius_;
  double local_map_z_radius_;
  double yaw_search_range_;
  double yaw_search_step_;
  double ndt_resolution_;
  double ndt_step_size_;
  double icp_max_distance_;
  double metric_max_distance_;
  double max_rmse_;
  double min_overlap_;
  double max_prior_xy_;
  double max_prior_z_;
  double max_prior_yaw_;
  double consistency_xy_;
  double consistency_z_;
  double consistency_yaw_;
  bool continuous_shadow_enabled_;
  double continuous_interval_;
  double continuous_odom_tolerance_;
  double continuous_local_map_radius_;
  double continuous_yaw_range_;
  double continuous_yaw_step_;
  double continuous_max_rmse_;
  double continuous_min_overlap_;
  double continuous_max_correction_xy_;
  double continuous_max_correction_z_;
  double continuous_max_correction_yaw_;

  std::mutex mutex_;
  Cloud::Ptr map_cloud_;
  Cloud::Ptr accumulated_source_{new Cloud()};
  Cloud::Ptr continuous_source_{new Cloud()};
  std::deque<TimedOdom> odom_history_;
  int accumulated_frames_{0};
  int consistency_count_{0};
  int continuous_accumulated_frames_{0};
  int continuous_stable_count_{0};
  bool have_odom_{false};
  bool matching_{false};
  bool localized_{false};
  bool have_candidate_{false};
  bool continuous_have_candidate_{false};
  std::string status_;
  builtin_interfaces::msg::Time latest_odom_stamp_;
  Eigen::Isometry3d base_to_body_{Eigen::Isometry3d::Identity()};
  Eigen::Isometry3d latest_odom_to_base_{Eigen::Isometry3d::Identity()};
  Eigen::Isometry3d prior_map_to_odom_{Eigen::Isometry3d::Identity()};
  Eigen::Isometry3d last_candidate_{Eigen::Isometry3d::Identity()};
  Eigen::Isometry3d continuous_last_candidate_{Eigen::Isometry3d::Identity()};
  Eigen::Isometry3d map_to_odom_{Eigen::Isometry3d::Identity()};
  std::chrono::steady_clock::time_point next_continuous_attempt_{
    std::chrono::steady_clock::now()};
  std::thread matching_worker_;

  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr success_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr rmse_pub_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr overlap_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr candidate_pose_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr pose_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr aligned_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr local_map_pub_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr retry_service_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::TimerBase::SharedPtr tf_timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<FixedStartRelocalizer>());
  } catch (const std::exception & error) {
    RCLCPP_FATAL(rclcpp::get_logger("fixed_start_relocalizer"), "%s", error.what());
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
