std_msgs/Header header                    # 消息头：包含时间戳和坐标系名称

geometry_msgs/Point position              # 机身位置，单位 m，建议在 world 坐标系下表达
geometry_msgs/Quaternion orientation      # 机身姿态，四元数表示

geometry_msgs/Vector3 linear_velocity     # 机身线速度，单位 m/s
geometry_msgs/Vector3 angular_velocity    # 机身角速度，单位 rad/s