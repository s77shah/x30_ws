#!/usr/bin/env python3
import sys
import time
import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from controller_manager_msgs.srv import SwitchController, SwitchControllerRequest, ListControllers
from std_srvs.srv import Empty
from gazebo_msgs.srv import SetModelConfiguration, GetModelProperties


POSES = {
    "stand": [
        -0.056777261197566986, -0.6058225631713867,  1.2098075151443481,
         0.05980128049850464,  -0.6071847677230835,  1.2157436609268188,
        -0.06459496915340424, -0.604759931564331,   1.218707799911499,
         0.05902230739593506, -0.6046401262283325,  1.2111896276474,
    ],
    "low": [
         0.03496597334742546,  -0.9889702200889587,  1.9350168704986572,
        -0.03955193608999252,  -0.9709458947181702,  1.944815993309021,
        -0.004482100252062082, -0.9571959972381592,  1.9304949045181274,
        -0.021040303632616997, -0.9966241121292114,  1.9409730434417725,
    ],
    "sit": [
        -0.3047548532485962,  -1.4912890195846558,  2.7569868564605713,
         0.3316514492034912,  -1.4891797304153442,  2.753239870071411,
        -0.29629796743392944, -1.4862236976623535,  2.7550015449523926,
         0.30155906081199646, -1.5026819705963135,  2.760498285293579,
    ],
}

JOINT_ORDER = [
    "FL_HipX_joint", "FL_HipY_joint", "FL_Knee_joint",
    "FR_HipX_joint", "FR_HipY_joint", "FR_Knee_joint",
    "HL_HipX_joint", "HL_HipY_joint", "HL_Knee_joint",
    "HR_HipX_joint", "HR_HipY_joint", "HR_Knee_joint",
]


def wait_for_controller_running(ns, controller):
    list_srv = rospy.ServiceProxy(f"{ns}/controller_manager/list_controllers", ListControllers)
    switch_srv = rospy.ServiceProxy(f"{ns}/controller_manager/switch_controller", SwitchController)
    rospy.loginfo("Waiting for controller_manager services in %s", ns or "/")
    try:
        list_srv.wait_for_service(timeout=5.0)
        switch_srv.wait_for_service(timeout=5.0)
    except Exception as exc:  # pragma: no cover
        rospy.logwarn("controller_manager services not available: %s", exc)
        return False

    # Try to start the controller if not running.
    for _ in range(20):
        resp = list_srv()
        states = {c.name: c.state for c in resp.controller}
        if states.get(controller) == "running":
            return True
        if controller in states and states[controller] != "running":
            req = SwitchControllerRequest()
            req.start_controllers = [controller]
            req.stop_controllers = []
            req.strictness = SwitchControllerRequest.STRICT
            try:
                switch_srv(req)
            except Exception as exc:  # pragma: no cover
                rospy.logwarn("Switch controller failed: %s", exc)
        time.sleep(0.25)
    return False


def publish_pose(ns, pose_name):
    pose = POSES.get(pose_name)
    if pose is None:
        rospy.logerr("Unknown pose '%s'. Valid: %s", pose_name, list(POSES.keys()))
        return

    pub = rospy.Publisher(f"{ns}/joint_group_position_controller/command", JointTrajectory, queue_size=1, latch=True)
    for _ in range(50):
        if pub.get_num_connections() > 0:
            break
        rospy.sleep(0.05)

    msg = JointTrajectory()
    msg.joint_names = JOINT_ORDER
    point = JointTrajectoryPoint()
    point.positions = pose
    point.velocities = [0.0] * len(pose)
    # Longer duration to reduce aggressive snap when physics starts.
    point.time_from_start = rospy.Duration(2.0)
    msg.points = [point]
    msg.header.stamp = rospy.Time.now()
    pub.publish(msg)
    rospy.loginfo("Published %s pose to %s/joint_group_position_controller/command", pose_name, ns or "/")


def main():
    rospy.init_node("auto_stand_pose")
    pose_name = rospy.get_param("~pose", "stand")
    robot_name = rospy.get_param("~robot_name", "x30")
    set_model_first = rospy.get_param("~set_model_configuration", True)
    hold_with_controller = rospy.get_param("~hold_with_controller", False)

    ns = "" if robot_name in ["", "/"] else f"/{robot_name}"

    # Work around missing /clock while paused: temporarily disable sim time for service calls.
    use_sim_time_param = f"{ns}/use_sim_time" if ns else "/use_sim_time"
    if rospy.has_param(use_sim_time_param):
        rospy.set_param(use_sim_time_param, False)

    # Nudge Gazebo to publish /clock at least once by unpausing briefly.
    try:
        unpause = rospy.ServiceProxy("/gazebo/unpause_physics", Empty)
        pause = rospy.ServiceProxy("/gazebo/pause_physics", Empty)
        unpause.wait_for_service(timeout=3.0)
        pause.wait_for_service(timeout=3.0)
        unpause()
        rospy.sleep(0.2)
        pause()
    except Exception:
        pass

    if set_model_first:
        try:
            get_model = rospy.ServiceProxy("/gazebo/get_model_properties", GetModelProperties)
            get_model.wait_for_service(timeout=5.0)
            set_model = rospy.ServiceProxy("/gazebo/set_model_configuration", SetModelConfiguration)
            set_model.wait_for_service(timeout=5.0)

            pose = POSES.get(pose_name, POSES["stand"])
            applied = False
            for _ in range(60):  # up to ~15s
                try:
                    resp = get_model(robot_name)
                    if resp.success:
                        set_model(model_name=robot_name, urdf_param_name=f"{ns}/robot_description" or "/robot_description",
                                  joint_names=JOINT_ORDER, joint_positions=pose)
                        rospy.loginfo("Applied %s pose via set_model_configuration", pose_name)
                        applied = True
                        break
                except Exception:
                    pass
                rospy.sleep(0.25)
            if not applied:
                rospy.logwarn("set_model_configuration: model %s not found after waiting", robot_name)
        except Exception as exc:  # pragma: no cover
            rospy.logwarn("set_model_configuration failed: %s", exc)

    if hold_with_controller:
        if not wait_for_controller_running(ns, "joint_group_position_controller"):
            rospy.logerr("joint_group_position_controller not running; aborting pose publish")
            if rospy.has_param(use_sim_time_param):
                rospy.set_param(use_sim_time_param, True)
            sys.exit(1)
        publish_pose(ns, pose_name)

    # Restore sim time if we changed it
    if rospy.has_param(use_sim_time_param):
        rospy.set_param(use_sim_time_param, True)


if __name__ == "__main__":
    main()
