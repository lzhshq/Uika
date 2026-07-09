// Copyright (c) 2025.
// IWIN-FINS Lab, Shanghai Jiao Tong University, Shanghai, China.
// All rights reserved.

#ifndef CLOUD_FILTER_BOX_H
#define CLOUD_FILTER_BOX_H

class CloudFilterBox {
public:
  CloudFilterBox() : min_x_(0), max_x_(0), min_y_(0), max_y_(0), min_z_(0), max_z_(0) {}
  CloudFilterBox(double min_x, double max_x, double min_y, double max_y,
                  double min_z, double max_z)
      : min_x_(min_x), max_x_(max_x), min_y_(min_y), max_y_(max_y),
        min_z_(min_z), max_z_(max_z) {}

  bool IsPointValid(const double &pt_x, const double &pt_y, const double &pt_z) const {
    if (pt_x < min_x_ || pt_x > max_x_ || pt_y < min_y_ || pt_y > max_y_ ||
        pt_z < min_z_ || pt_z > max_z_) {
      return true;
        }
    return false;
  }

private:
  double min_x_;
  double max_x_;
  double min_y_;
  double max_y_;
  double min_z_;
  double max_z_;
};

#endif //CLOUD_FILTER_BOX_H
