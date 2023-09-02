# this code is a modification of OMES' code, the original code is provided in https://omes-va.com/deteccion-de-colores2/

import cv2
import numpy as np
import math

def dibujar(mask,color):
  contornos,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)
  indice = 0  
  x=[0,0]
  y=[0,0]    
  for c in contornos:
    area = cv2.contourArea(c)
    if area > 3000 and indice<2:
      M = cv2.moments(c)
      if (M["m00"]==0): M["m00"]=1
      x[indice] = int(M["m10"]/M["m00"])
      y[indice] = int(M['m01']/M['m00'])
      nuevoContorno = cv2.convexHull(c)
      cv2.circle(frame,(x[indice],y[indice]),7,(0,255,0),-1)
      cv2.putText(frame,'{},{}'.format(x[indice],y[indice]),(x[indice]+10,y[indice]), font, 0.75,(0,255,0),1,cv2.LINE_AA)
      cv2.drawContours(frame, [nuevoContorno], 0, color, 3)
      indice = indice+1
  if indice ==1:
      cv2.putText(frame,'Distance: {}'.format(0.0),(0,20), font, 0.75,(0,255,0),1,cv2.LINE_AA)
  else:
      cv2.putText(frame,'Distance: {}'.format(math.sqrt(pow(x[1]-x[0],2)+pow(y[1]-y[0],2))),(0,20), font, 0.75,(0,255,0),1,cv2.LINE_AA)

cap = cv2.VideoCapture('http://192.168.43.1:8080/video')

azulBajo = np.array([100,100,20],np.uint8)
azulAlto = np.array([125,255,255],np.uint8)

font = cv2.FONT_HERSHEY_SIMPLEX
while True:

  ret,frame = cap.read()

  if ret == True:
    frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    maskAzul = cv2.inRange(frameHSV,azulBajo,azulAlto)
    dibujar(maskAzul,(255,0,0))
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('s'):
      break
cap.release()
cv2.destroyAllWindows()
