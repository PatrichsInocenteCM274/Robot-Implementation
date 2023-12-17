# this code is a modification of OMES' code, the original code is provided in https://omes-va.com/deteccion-de-colores2/

import cv2
import numpy as np
import math
import rospy
from std_msgs.msg import Int16
import sys, signal

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

def dibujar(mask,color):
  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
  indice = 0  
  x=[0,0]
  y=[0,0]    
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 1000 and indice<1:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x[indice] = int(M["m10"]/M["m00"])
      y[indice] = int(M['m01']/M['m00'])
      nuevoContorno = cv2.convexHull(c)
      if x[indice] > 380.0:
      	mensaje.data = 20;
      	pub_giro.publish(mensaje);
      if x[indice] < 280.0:
      	mensaje.data = -20;
      	pub_giro.publish(mensaje);
      if x[indice] > 280.0 and x[indice] < 380:
      	mensaje.data = 0;
      	pub_giro.publish(mensaje);
      cv2.circle(frame,(x[indice],y[indice]),7,(0,255,0),-1)
      cv2.putText(frame,'{},{}'.format(x[indice],y[indice]),(x[indice]+10,y[indice]), font, 0.75,(0,255,0),1,cv2.LINE_AA)
      cv2.drawContours(frame, [nuevoContorno], 0, color, 3)
      indice = indice+1
      

rospy.init_node('camera_control_from_python')
pub_giro = rospy.Publisher('/set_angle_camera', Int16, queue_size=10)
mensaje = Int16() 
cap = cv2.VideoCapture('http://192.168.12.186:8080/video')

ColorBajo = np.array([40, 40, 40], np.uint8)
ColorAlto = np.array([80, 255, 255], np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX
while True:

  ret,frame = cap.read()

  if ret == True:
    frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maskColor = cv2.inRange(frameHSV,ColorBajo,ColorAlto)
    dibujar(maskColor,(255,0,0))
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
      break

