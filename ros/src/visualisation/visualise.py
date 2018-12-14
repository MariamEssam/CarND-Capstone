#!/usr/bin/python

import rospy
from geometry_msgs.msg import PoseStamped, Pose, TwistStamped
from styx_msgs.msg import Lane, Waypoint, TrafficLightArray, TrafficLight
from nav_msgs.msg import Path, Odometry
from visualization_msgs.msg import MarkerArray, Marker
from std_msgs.msg import Float32
from dbw_mkz_msgs.msg import BrakeCmd, ThrottleCmd, SteeringCmd

# credits to https://github.com/ericlavigne/CarND-Capstone-Wolf-Pack
class VisualizationHelper(object):
    def __init__(self):
        rospy.init_node("visualization_helper")

        # rospy.Subscriber("/current_pose", PoseStamped, self.current_pose_callback)
        rospy.Subscriber("/base_waypoints", Lane, self.base_waypoints_callback)
        rospy.Subscriber("/final_waypoints", Lane, self.final_waypoints_callback)
        rospy.Subscriber("/vehicle/traffic_lights", TrafficLightArray, self.traffic_light_gt_callback)
        # rospy.Subscriber('/current_velocity', TwistStamped, self.on_current_velocity)
        # rospy.Subscriber('/twist_cmd', TwistStamped, self.on_twist_cmd)
        # rospy.Subscriber("/vehicle/brake_cmd", BrakeCmd, self.on_brake_cmd)
        # rospy.Subscriber("/vehicle/throttle_cmd", ThrottleCmd, self.on_throttle_cmd)
        #rospy.Subscriber("/vehicle/steering_cmd", SteeringCmd, self.on_steering_cmd)

        self.path_pub = rospy.Publisher('/navigation/waypoints', Path, queue_size=1, latch=True)
        self.final_path_pub = rospy.Publisher('/navigation/final_waypoints', Path, queue_size=1)
        self.traffic_light_gt_pub = rospy.Publisher("navigation/traffic_light_gt", MarkerArray, queue_size=1)
        self.accel_decel_pub = rospy.Publisher("visualisation/acceleration", Float32, queue_size=1)
        # self.current_vel_pub = rospy.Publisher("visualisation/current", Float32, queue_size=10)
        # self.goal_vel_pub = rospy.Publisher("visualisation/goal", Float32, queue_size=10)
        self.velocity_diff_pub = rospy.Publisher("visualisation/velocity_diff", Float32, queue_size=10)

        self.current_velocity = 0
        self.goal_velocity = 0

        self.traffic_light_array_gt = None
        self.publish()


    # publish traffic light ground truth
    def publish(self):
        rate = rospy.Rate(5)
        while not rospy.is_shutdown():
            if self.traffic_light_array_gt is not None:
                marker_array = MarkerArray()

                for index, light in enumerate(self.traffic_light_array_gt.lights):
                    marker = self.generate_light_marker(light, index)
                    marker_array.markers.append(marker)

                self.traffic_light_gt_pub.publish(marker_array)

            rate.sleep()

    # used to generate traffic light instance
    def generate_light_marker(self, light, index):
        marker = Marker()
        marker.header.frame_id = "/world"
        marker.ns = "light_gt"
        marker.id = index
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        marker.pose.position = light.pose.pose.position
        marker.pose.orientation = light.pose.pose.orientation
        marker.scale.x = 10.0
        marker.scale.y = 10.0
        marker.scale.z = 10.0

        # light = TrafficLight()
        if light.state == TrafficLight.RED:
            marker.color.r = 1.0
            marker.color.g = 0.0
        elif light.state == TrafficLight.GREEN:
            marker.color.r = 0.0
            marker.color.g = 1.0
        elif light.state == TrafficLight.YELLOW:
            marker.color.r = 1.0
            marker.color.g = 1.0
        elif light.state == TrafficLight.UNKNOWN:
            marker.color.r = 1.0
            marker.color.g = 1.0
            marker.color.b = 1.0

        marker.color.a = 1.0
        return marker


    # On receiving base_waypoints publish a list of paths for Rviz
    def final_waypoints_callback(self, lane):
        # rospy.logwarn(lane)
        path = Path()
        path.header.frame_id = "world"

        for waypoint in lane.waypoints:
            wp_pose = waypoint.pose.pose
            pose = self.generate_pose(wp_pose.position.x, wp_pose.position.y, 0, 0, 0, 0, 0)
            path.poses.append(pose)

        self.final_path_pub.publish(path)

    # On receiving base_waypoints publish a list of paths for Rviz
    def base_waypoints_callback(self, lane):
        path = Path()
        path.header.frame_id = "world"

        for waypoint in lane.waypoints:
            wp_pose = waypoint.pose.pose
            pose = self.generate_pose(wp_pose.position.x, wp_pose.position.y, 0, 0, 0, 0, 0)
            path.poses.append(pose)

        self.path_pub.publish(path)

    # def current_pose_callback(self, pose_stamped):
    #     pass

    def generate_pose(self, px, py, pz, ox, oy, oz, ow):
        pose = PoseStamped()
        pose.header.frame_id = "world"
        pose.pose.position.x = px
        pose.pose.position.y = py
        pose.pose.position.z = pz
        pose.pose.orientation.x = ox
        pose.pose.orientation.y = oy
        pose.pose.orientation.z = oz
        pose.pose.orientation.w = ow
        return pose

    def traffic_light_gt_callback(self, traffic_light_array):
        # rospy.logwarn(traffic_light_array)
        self.traffic_light_array_gt = traffic_light_array



if __name__ == '__main__':
    try:
        VisualizationHelper()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start visualization helper node.')
