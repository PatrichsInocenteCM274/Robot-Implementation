import rospy
from sensor_msgs.msg import LaserScan
import numpy as np
import matplotlib.pyplot as plt

class LidarPointCloudVisualizer:
    def __init__(self):
        self.scan_data = None
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.ax.set_ylim(0, 2)  # Restrict the range to 2 meters
        self.lidar_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)

    def scan_callback(self, msg):
        self.scan_data = msg

    def update_plot(self):
        if self.scan_data is None:
            return
        
        angles = np.arange(self.scan_data.angle_min, self.scan_data.angle_max + self.scan_data.angle_increment, self.scan_data.angle_increment)
        ranges = np.array(self.scan_data.ranges)
        
        self.ax.clear()
        self.ax.plot(angles, ranges)
        self.ax.set_rmax(2)  # Restrict the maximum range to 2 meters
        self.ax.grid(True)
        self.fig.canvas.draw()
        plt.pause(0.01)

def main():
    rospy.init_node('lidar_pointcloud_visualizer')
    visualizer = LidarPointCloudVisualizer()
    
    rate = rospy.Rate(10)  # Update rate in Hz
    
    while not rospy.is_shutdown():
        visualizer.update_plot()
        rate.sleep()

if __name__ == '__main__':
    main()

