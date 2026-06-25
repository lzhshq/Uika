std_msgs/Header header                    # 消息头：包含时间戳和坐标系名称

uint8 STANCE=0                            # 支撑相
uint8 SWING=1                             # 摆动相

uint8 fl_phase                            # 左前腿当前相位，取值：STANCE 或 SWING
uint8 fr_phase                            # 右前腿当前相位，取值：STANCE 或 SWING
uint8 rl_phase                            # 左后腿当前相位，取值：STANCE 或 SWING
uint8 rr_phase                            # 右后腿当前相位，取值：STANCE 或 SWING