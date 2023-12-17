import rospy
from sensor_msgs.msg import LaserScan
import numpy as np
import matplotlib.pyplot as plt
import sys, signal

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


class LidarPointCloudVisualizer:
    def __init__(self):
        self.scan_data = None
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.ax.set_ylim(0, 2)  # Restringe el rango a 2 metros
        self.lidar_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.num_points = 64  # Número de puntos deseados

    def scan_callback(self, msg):
        self.scan_data = msg

    def update_plot(self):
        if self.scan_data is None:
            return

        angles = np.arange(self.scan_data.angle_min, self.scan_data.angle_max + self.scan_data.angle_increment, self.scan_data.angle_increment)
        ranges = np.array(self.scan_data.ranges)

        # Selecciona índices equitativamente espaciados
        indices = np.linspace(0, len(angles) - 1, self.num_points, dtype=int)

        # Filtra los ángulos y rangos utilizando los índices seleccionados
        filtered_angles = angles[indices]
        filtered_ranges = ranges[indices]
        
        print(filtered_ranges[:5])

        # Configura el gráfico polar mostrando solo puntos sin unirlos con líneas
        self.ax.clear()
        self.ax.scatter(filtered_angles, filtered_ranges, s=5, c='b', marker='o')
        self.ax.set_rmax(2)  # Restringe el rango máximo a 2 metros
        self.ax.grid(True)
        self.fig.canvas.draw()
        plt.pause(0.01)

def main():
    rospy.init_node('lidar_pointcloud_visualizer')
    visualizer = LidarPointCloudVisualizer()
    
    rate = rospy.Rate(20)  # Tasa de actualización en Hz
    
    while not rospy.is_shutdown():
        visualizer.update_plot()
        rate.sleep()

if __name__ == '__main__':
    main()

