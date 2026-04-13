# X30 Simulation Startup (Known Good)

This is a minimal, repeatable sequence that matches the working setup.

## 0) Build and source
```
cd /home/toto/x30_ws
catkin_make
source devel/setup.bash
```

## 1) Launch Gazebo (paused, sitting)
```
roslaunch toto_v2_config gazebo.launch robot_name:=x30 paused:=true world_init_z:=0.6 stand_pose:=sit
```

Reapply sit pose **before** unpausing (prevents the jump):
```
rosservice call /gazebo/set_model_configuration "model_name: x30
urdf_param_name: /x30/robot_description
joint_names: [FL_HipX_joint, FL_HipY_joint, FL_Knee_joint, FR_HipX_joint, FR_HipY_joint, FR_Knee_joint, HL_HipX_joint, HL_HipY_joint, HL_Knee_joint, HR_HipX_joint, HR_HipY_joint, HR_Knee_joint]
joint_positions: [-0.3047548532, -1.4912890196, 2.7569868565, 0.3316514492, -1.4891797304, 2.7532398701, -0.2962979674, -1.4862236977, 2.7550015450, 0.3015590608, -1.502681971, 2.7604982853]"
```

Unpause to settle:
```
rosservice call /gazebo/unpause_physics
```

Start controllers once (after it settles):
```
rosrun controller_manager spawner joint_states_controller joint_group_position_controller __ns:=/x30
```

## 2) Pose commands
Fast pose scripts (recommended):
```
rosrun toto_v2_config set_pose.py sit
rosrun toto_v2_config set_pose.py stand
rosrun toto_v2_config set_pose.py low
```

Reapply sitting pose (use when paused or after reset):
```
rosservice call /gazebo/set_model_configuration "model_name: x30
urdf_param_name: /x30/robot_description
joint_names: [FL_HipX_joint, FL_HipY_joint, FL_Knee_joint, FR_HipX_joint, FR_HipY_joint, FR_Knee_joint, HL_HipX_joint, HL_HipY_joint, HL_Knee_joint, HR_HipX_joint, HR_HipY_joint, HR_Knee_joint]
joint_positions: [-0.3047548532, -1.4912890196, 2.7569868565, 0.3316514492, -1.4891797304, 2.7532398701, -0.2962979674, -1.4862236977, 2.7550015450, 0.3015590608, -1.502681971, 2.7604982853]"
```

Standing:
```
rostopic pub -r 10 /x30/joint_group_position_controller/command trajectory_msgs/JointTrajectory "
joint_names: [FL_HipX_joint, FL_HipY_joint, FL_Knee_joint, FR_HipX_joint, FR_HipY_joint, FR_Knee_joint, HL_HipX_joint, HL_HipY_joint, HL_Knee_joint, HR_HipX_joint, HR_HipY_joint, HR_Knee_joint]
points:
- positions: [-0.0567772612, -0.6058225632, 1.2098075151,  0.0598012805, -0.6071847677, 1.2157436609,  -0.0645949692, -0.6047599316, 1.2187077999,  0.0590223074, -0.6046401262, 1.2111896276]
  velocities: [0,0,0,0,0,0,0,0,0,0,0,0]
  time_from_start: {secs: 1, nsecs: 0}
"
```

Low stand:
```
rostopic pub -r 10 /x30/joint_group_position_controller/command trajectory_msgs/JointTrajectory "
joint_names: [FL_HipX_joint, FL_HipY_joint, FL_Knee_joint, FR_HipX_joint, FR_HipY_joint, FR_Knee_joint, HL_HipX_joint, HL_HipY_joint, HL_Knee_joint, HR_HipX_joint, HR_HipY_joint, HR_Knee_joint]
points:
- positions: [0.0349659733, -0.9889702201, 1.9350168705,  -0.0395519361, -0.9709458947, 1.9448159933,  -0.00448210025, -0.9571959972, 1.9304949045,  -0.0210403036, -0.9966241121, 1.9409730434]
  velocities: [0,0,0,0,0,0,0,0,0,0,0,0]
  time_from_start: {secs: 1, nsecs: 0}
"
```

Sitting:
```
rostopic pub -r 10 /x30/joint_group_position_controller/command trajectory_msgs/JointTrajectory "
joint_names: [FL_HipX_joint, FL_HipY_joint, FL_Knee_joint, FR_HipX_joint, FR_HipY_joint, FR_Knee_joint, HL_HipX_joint, HL_HipY_joint, HL_Knee_joint, HR_HipX_joint, HR_HipY_joint, HR_Knee_joint]
points:
- positions: [-0.3047548532, -1.4912890196, 2.7569868565,  0.3316514492, -1.4891797304, 2.7532398701,  -0.2962979674, -1.4862236977, 2.7550015450,  0.3015590608, -1.502681971, 2.7604982853]
  velocities: [0,0,0,0,0,0,0,0,0,0,0,0]
  time_from_start: {secs: 1, nsecs: 0}
"
```

Note: `-r 10` publishes continuously. Stop it with Ctrl+C before sending the next pose.

## 3) Reset without flipping
```
rosservice call /gazebo/pause_physics
rosservice call /gazebo/reset_world
# Reapply sitting pose (command above)
rosservice call /gazebo/unpause_physics
```

## 4) Navigation stack
```
roslaunch toto_v2_config navigate.launch robot_name:=x30 rviz:=true
```

RViz settings:
- Fixed Frame: `x30/odom` first, then `x30/map` after AMCL starts.
- RobotModel: Description `/x30/robot_description`, TF Prefix `x30`.

Quick checks:
```
rostopic echo -n1 /x30/scan
rosrun tf tf_echo x30/odom x30/base_footprint
rosrun tf tf_echo x30/map x30/base_footprint   # after AMCL gets scans + initial pose
```
