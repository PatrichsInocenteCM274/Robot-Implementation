from imageai.Detection.Custom import CustomObjectDetection
import os
import cv2
import numpy as np
import threading

execution_path = os.getcwd()

video_detector = CustomObjectDetection()
video_detector.setModelTypeAsTinyYOLOv3()
video_detector.setModelPath("tiny-yolov3_person_mAP-0.72476_epoch-101.pt")
video_detector.setJsonPath("person_tiny-yolov3_detection_config.json")
video_detector.loadModel()

camera = cv2.VideoCapture('http://192.168.43.1:8080/video')

# Variables compartidas para almacenar la detección actual y el último fotograma
lock = threading.Lock()
detection_result = None
latest_frame = None
box_detect = None

# Función para capturar fotogramas en un hilo separado
def capture_frames():
    global latest_frame
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        with lock:
            latest_frame = frame

# Función para realizar la detección en un hilo separado
def detect_objects():
    global detection_result, box_detect
    while True:
        with lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
            else:
                frame = None
        if frame is not None:
            detections = video_detector.detectObjectsFromImage(input_image=frame, minimum_percentage_probability=30)
            max_percentage = 0.0
            for Object in detections:    
                if Object["percentage_probability"] > max_percentage:
                    box_detect = Object["box_points"]
                    max_percentage = Object["percentage_probability"]
            print("percentage max: ",max_percentage)
            with lock:
                detection_result = (frame, max_percentage, box_detect)

# Inicia los hilos para captura y detección
capture_thread = threading.Thread(target=capture_frames)
detect_thread = threading.Thread(target=detect_objects)

capture_thread.start()
detect_thread.start()

# Espera a que los hilos finalicen
capture_thread.join()
detect_thread.join()

# Libera los recursos
camera.release()

