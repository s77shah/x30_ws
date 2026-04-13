#!/usr/bin/env python3
# ...existing code...
import rospy
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

rospy.init_node('hold_joints')
pub = rospy.Publisher('/joint_group_position_controller/command', JointTrajectory, queue_size=1)
latest = None

def js_cb(msg):
    global latest
    latest = msg

rospy.Subscriber('/joint_states', JointState, js_cb)
rate = rospy.Rate(10.0)

while not rospy.is_shutdown():
    if latest and latest.name and latest.position:
        traj = JointTrajectory()
        traj.joint_names = list(latest.name)
        p = JointTrajectoryPoint()
        p.positions = list(latest.position)
        # give controllers time to reach pose smoothly
        p.time_from_start = rospy.Duration(0.6)
        traj.points = [p]
        pub.publish(traj)
    rate.sleep()
# ...existing code...