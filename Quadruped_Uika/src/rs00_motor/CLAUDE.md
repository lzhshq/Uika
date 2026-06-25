# 注意事项

## 二进制文件路径问题

当看到 `ros2 run rs00_motor rs00_motor` 运行时，必须确保使用的是正确路径的二进制文件。

### 问题原因
项目中存在两个可能的 install 路径：
- `~/VMC_Quadruped/install/rs00_motor/` （正确的）
- `~/VMC_Quadruped/src/rs00_motor/install/` （旧的，可能被优先使用）

如果 `ros2 run` 使用了旧版本的二进制文件，代码修改将不会生效。

### 验证方法
```bash
# 查看正在运行的进程
pgrep -f rs00_motor | while read pid; do
  echo "PID $pid:"
  cat /proc/$pid/cmdline | tr '\0' ' '
  echo
done

# 检查二进制文件修改时间
ls -la ~/VMC_Quadruped/install/rs00_motor/lib/rs00_motor/rs00_motor
ls -la ~/VMC_Quadruped/src/rs00_motor/install/rs00_motor/lib/rs00_motor/rs00_motor
```

### 解决方法
如果发现使用了旧路径，删除旧版本：
```bash
rm -rf ~/VMC_Quadruped/src/rs00_motor/install
colcon build --packages-select rs00_motor
```

## ROS2 话题问题排查

当节点运行但话题不显示时：
1. 确认节点正在运行：`ros2 node list`
2. 确认话题已创建：`ros2 topic list`
3. 如果话题不存在，检查是否运行了正确版本的代码（修改时间）
4. 检查进程实际加载的二进制文件路径
