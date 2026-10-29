import cv2
import numpy as np

video = cv2.VideoCapture(3)



while True:
    grabar, frame = video.read()
    if grabar == False: break
    cv2.imshow('yersonbb', gray)
    
    
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR555)
    cv2.imshow("Frame", frame)
    #cv2.imshow('Gray', gray)
    #cv2.imshow('mascara', mascara)
    #Tecla para cerrar el programa UwU
    if cv2.waitKey(1) & 0xFF == ord ('y'):
        break
video.release()
cv2.imshow('yersonbb', gray)
