#include <ros/ros.h>
#include <nav_msgs/OccupancyGrid.h>
#include <geometry_msgs/TransformStamped.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>

class FrontierChecker {
public:
    FrontierChecker()
        : tf_listener(tf_buffer) {
        map_sub = nh.subscribe("/move_base/global_costmap/costmap", 1, &FrontierChecker::mapCallback, this);
    }

private:
    ros::NodeHandle nh;
    ros::Subscriber map_sub;
    tf2_ros::Buffer tf_buffer;
    tf2_ros::TransformListener tf_listener;

    void mapCallback(const nav_msgs::OccupancyGrid::ConstPtr& msg) {
        geometry_msgs::TransformStamped tfStamped;
        try {
            tfStamped = tf_buffer.lookupTransform(msg->header.frame_id, "base_link", ros::Time(0), ros::Duration(0.5));
        } catch (tf2::TransformException &ex) {
            ROS_WARN("TF Error: %s", ex.what());
            return;
        }

        double robot_x = tfStamped.transform.translation.x;
        double robot_y = tfStamped.transform.translation.y;

        double res = msg->info.resolution;
        int width = msg->info.width;
        int height = msg->info.height;
        double origin_x = msg->info.origin.position.x;
        double origin_y = msg->info.origin.position.y;

        int cell_x = (int)((robot_x - origin_x) / res);
        int cell_y = (int)((robot_y - origin_y) / res);

        int window = 3; // Check 3x3 neighborhood

        bool found_unknown = false;
        for (int dx = -window; dx <= window; ++dx) {
            for (int dy = -window; dy <= window; ++dy) {
                int nx = cell_x + dx;
                int ny = cell_y + dy;
                if (nx >= 0 && ny >= 0 && nx < width && ny < height) {
                    int index = ny * width + nx;
                    if (msg->data[index] == -1) {
                        found_unknown = true;
                        break;
                    }
                }
            }
            if (found_unknown) break;
        }

        if (found_unknown) {
            ROS_INFO("Unknown space detected near the robot.");
        } else {
            ROS_INFO("All nearby cells are known.");
        }
    }
};

int main(int argc, char** argv) {
    ros::init(argc, argv, "frontier_checker_node");
    FrontierChecker fc;
    ros::spin();
    return 0;
}
