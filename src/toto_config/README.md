# TOTO — Autonomous Damage Surveying Robot

**Technological Optimization for Tornado Observation**
Quadrupedal robot simulation for autonomous post-tornado damage surveying.
Built on the Unitree X30 platform with CHAMP gait controller.

---

## Repository Structure

```
src/
├── toto_config/          # Main config: launch files, scripts, worlds, maps
├── x30_urdf/             # Robot URDF with 4x Livox Mid-360 LiDARs + camera
├── champ/                # Quadruped gait controller (external)
├── champ_teleop/         # Keyboard/joystick teleoperation (external)
├── explore_lite/         # Autonomous frontier exploration (external)
├── rtabmap_ros/          # LiDAR SLAM (external)
├── costmap_converter/    # Costmap utilities for local planner (external)
├── robot_state_plugin/   # RViz visualization plugin (external)
└── yocs_velocity_smoother/ # Velocity command smoother (external)
foxglove/
└── toto.json             # Foxglove Studio layout
STARTUP_GUIDE.md          # Known-good startup sequence
```

---

## Sensor Suite (Simulated)

Matches the real Unitree X30 Pro sensor layout:

| Sensor | ROS Topic | Rate |
|---|---|---|
| LiDAR front-up (Livox Mid-360) | `/x30/lidar_front_up/points` | 10 Hz |
| LiDAR front-down (Livox Mid-360) | `/x30/lidar_front_down/points` | 10 Hz |
| LiDAR rear-up (Livox Mid-360) | `/x30/lidar_rear_up/points` | 10 Hz |
| LiDAR rear-down (Livox Mid-360) | `/x30/lidar_rear_down/points` | 10 Hz |
| 2D scan slice (nav stack) | `/x30/scan` | 20 Hz |
| Wide-angle camera (90° FOV) | `/x30/camera/image_raw` | 30 Hz |

---

## Quick Start

### Build

```bash
cd ~/x30_ws
catkin_make
source devel/setup.bash
```

### 1. Simulation — default world

```bash
roslaunch toto_config gazebo.launch robot_name:=x30 paused:=true stand_pose:=sit
```

Then in a new terminal — unpause and stand up:
```bash
rosrun toto_config set_pose.py stand
rosservice call /gazebo/unpause_physics
```

### 2. Simulation — tornado damage world

```bash
roslaunch toto_config gazebo.launch robot_name:=x30 paused:=true stand_pose:=sit \
  gazebo_world:=$(rospack find toto_config)/worlds/tornado_damage.world
```

### 3. Teleop

```bash
roslaunch champ_teleop teleop.launch
```

### 4. SLAM (build a map)

```bash
roslaunch toto_config slam.launch rviz:=true
```

Save the map:
```bash
roscd toto_config/maps
rosrun map_server map_saver
```

### 5. Autonomous Navigation (requires existing map)

```bash
roslaunch toto_config navigate.launch robot_name:=x30 rviz:=true
```

Click **2D Nav Goal** in RViz to send the robot to a position.

### 6. Foxglove Visualization

Install `foxglove_bridge`:
```bash
sudo apt install ros-noetic-foxglove-bridge
roslaunch foxglove_bridge foxglove_bridge.launch
```

Open [Foxglove Studio](https://foxglove.dev/studio) → **File → Import Layout** → select `foxglove/toto.json`.

---

## Pose Commands

```bash
rosrun toto_config set_pose.py sit
rosrun toto_config set_pose.py stand
rosrun toto_config set_pose.py low
```

See `STARTUP_GUIDE.md` for the full known-good startup sequence including reset workflow.

---

## Worlds

| World | Description |
|---|---|
| `outdoor.world` | Default outdoor terrain |
| `tornado_damage.world` | Scientifically accurate EF2-3 tornado aftermath — fallen trees (radial blowdown pattern), collapsed house, scattered debris |

---

*Built on [CHAMP](https://github.com/chvmp/champ) by Marko Bjelonic.*
