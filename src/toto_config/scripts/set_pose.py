#!/usr/bin/env python3
import sys
import time
import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


POSES = {
    "stand": [
        -0.0567772612, -0.6058225632, 1.2098075151,
         0.0598012805, -0.6071847677, 1.2157436609,
        -0.0645949692, -0.6047599316, 1.2187077999,
         0.0590223074, -0.6046401262, 1.2111896276,
    ],
    "low": [
         0.0349659733,  -0.9889702201, 1.9350168705,
        -0.0395519361,  -0.9709458947, 1.9448159933,
        -0.00448210025, -0.9571959972, 1.9304949045,
        -0.0210403036,  -0.9966241121, 1.9409730434,
    ],
    "sit": [
        -0.3047548532, -1.4912890196, 2.7569868565,
         0.3316514492, -1.4891797304, 2.7532398701,
        -0.2962979674, -1.4862236977, 2.7550015450,
         0.3015590608, -1.5026819710, 2.7604982853,
    ],
}

JOINT_ORDER = [
    "FL_HipX_joint", "FL_HipY_joint", "FL_Knee_joint",
    "FR_HipX_joint", "FR_HipY_joint", "FR_Knee_joint",
    "HL_HipX_joint", "HL_HipY_joint", "HL_Knee_joint",
    "HR_HipX_joint", "HR_HipY_joint", "HR_Knee_joint",
]


def main():
    pose_name = sys.argv[1] if len(sys.argv) > 1 else "sit"
    pose = POSES.get(pose_name)
    if pose is None:
        print("Usage: set_pose.py [sit|stand|low]")
        sys.exit(2)

    rospy.init_node("set_pose", anonymous=True)
    pub = rospy.Publisher(
        "/x30/joint_group_position_controller/command",
        JointTrajectory,
        queue_size=1,
    )

    msg = JointTrajectory()
    msg.joint_names = JOINT_ORDER
    point = JointTrajectoryPoint()
    point.positions = pose
    point.velocities = [0.0] * len(pose)
    point.time_from_start = rospy.Duration(1.0)
    msg.points = [point]

    # Publish a short burst so the controller latches the pose.
    end_time = time.time() + 1.5
    rate = rospy.Rate(10)
    while not rospy.is_shutdown() and time.time() < end_time:
        msg.header.stamp = rospy.Time.now()
        pub.publish(msg)
        rate.sleep()


if __name__ == "__main__":
    main()
