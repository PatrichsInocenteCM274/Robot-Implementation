from gym.spaces import Box, Discrete
import numpy as np
import rospy
import math
from utilities import normalize_to_range
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from std_msgs.msg import Int8
import matplotlib.pyplot as plt


class HumanFollowingRobot:
    def __init__(self):
        rospy.init_node('robot_control_from_python')
        rate = rospy.Rate(20)
        self.angular_velocity_right = 0.0
        self.angular_velocity_left = 0.0
        self.last_orientations = [0.0] * 5
        self.lidar_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.orientation_sub = rospy.Subscriber('/angle_orientation_robot', Float32, self.orientation_callback)
        self.angle_camera_sub = rospy.Subscriber('/get_angle_camera', Float32, self.angle_camera_callback)
        self.pub_left = rospy.Publisher('/pwm_wheel_L', Int8, queue_size=10)
        self.pub_right = rospy.Publisher('/pwm_wheel_R', Int8, queue_size=10)
        self.lidar_resolution = 64
        self.lidar_radius = 3.0
        self.radio_wheel = 0.35
        self.observation_space = Box(low= np.concatenate([np.array([-np.inf, -np.inf, -1.0, -1.0, 0.0]),np.array([0.0]*self.lidar_resolution)]),
                                     high= np.concatenate([np.array([np.inf, np.inf, 1.0, 1.0, 6.28]),np.array([np.inf]*self.lidar_resolution)]),
                                     dtype=np.float64)
        self.action_space = Box(low=np.array([-1.0 , -1.0]), high=np.array([1.0 , 1.0]), dtype=np.float64)
        
    def scan_callback(self, msg):
        self.scan_data = msg
        
    def orientation_callback(self, msg):
        #self.orientation_data = msg
        self.last_orientations.pop(0)
        self.last_orientations.append(msg.data)
        
    def angle_camera_callback(self, msg):
    	self.angle_camera_data = msg

    def laser_observation(self):
        angles = np.arange(self.scan_data.angle_min, self.scan_data.angle_max + self.scan_data.angle_increment, self.scan_data.angle_increment)
        ranges = np.array(self.scan_data.ranges)

        # Selecciona índices equitativamente espaciados
        indices = np.linspace(0, len(angles) - 1, self.lidar_resolution, dtype=int)

        # Filtra los ángulos y rangos utilizando los índices seleccionados
        filtered_angles = angles[indices]
        filtered_ranges = ranges[indices]
        
        return filtered_ranges
    
    def apply_action(self, action):
        """
        Aplica una acción al robot.
        """
        self.angular_velocity_right = action[0]
        self.angular_velocity_left = action[1]

        
        if self.angular_velocity_right>=0:
                if self.angular_velocity_right==0:
                	self.pub_right.publish(0)
                else:
                	self.pub_right.publish(int(self.angular_velocity_right*80+40))
        else:
                self.pub_right.publish(int(self.angular_velocity_right*80-40))
        	
        if self.angular_velocity_left>=0:
                if self.angular_velocity_left==0:
                	self.pub_left.publish(0)
                else:
                	self.pub_left.publish(int(self.angular_velocity_left*80+40))
        else:
                self.pub_left.publish(int(self.angular_velocity_left*80-40))

    def get_observation(self):
        robot_orientation_x = math.cos(math.radians( np.mean(self.last_orientations) ))
        robot_orientation_y = math.sin(math.radians( np.mean(self.last_orientations) ))
        robot_velocity_x = (self.angular_velocity_right/2.0 + self.angular_velocity_left/2.0)*self.radio_wheel*robot_orientation_x
        robot_velocity_y = (self.angular_velocity_right/2.0 + self.angular_velocity_left/2.0)*self.radio_wheel*robot_orientation_y
        #print(robot_velocity_x,robot_velocity_y)
        robot_velocity_x = normalize_to_range(robot_velocity_x, -6.0, 6.0, -1.0, 1.0, clip=True)
        robot_velocity_y = normalize_to_range(robot_velocity_y, -6.0, 6.0, -1.0, 1.0, clip=True)
        angle_camera = self.angle_camera_data
        angle_camera = normalize_to_range(self.angle_camera_data.data, 0.0, 512, -1.0, 1.0, clip=True)
        range_image = self.laser_observation()
        range_image = np.clip(range_image, 0, 0.85)
        range_image = np.interp(range_image, (0, 0.85), (0.0, 1.0))
        print(range_image)
        range_image = range_image.tolist()
        
        #print(np.mean(self.last_orientations))
        return [robot_velocity_x, robot_velocity_y, robot_orientation_x, robot_orientation_y, angle_camera] + range_image
        #return np.concatenate([np.array([0.0,0.0,1.0,0.0,0.0]),np.array([1.0]*self.lidar_resolution)])
        
        
           
        
