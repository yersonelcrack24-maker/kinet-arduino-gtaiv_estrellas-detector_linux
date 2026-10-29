import cv2 as cv
import serial
import numpy as np
import time

print("Iniciando detector")
algo = 1
intervalo = {
    1: 0.1, #no
    2: 2.5,#si
    3: 0.08#parpadeo_led
    }
imagenes = {1:cv.imread('1.png', 0), 2: cv.imread('2.png', 0)}
pantalla = cv.VideoCapture(0)
serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)





while True:
    for _ in range(5):
        pantalla.grab()

    grabar, frame =  pantalla.read()  #pantalla.retrieve()
    if not grabar or frame is None:
        print("Kinect no disponible, reintentando...")
        time.sleep(intervalo[1])
        continue
    time.sleep(intervalo[1])
    if grabar == False: break
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) #cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #cv.imshow('Gray', gray)
    
    

    def idetificador_de_muestras(ejemplo, probabilidad):
        res = cv.matchTemplate(gray, ejemplo, cv.TM_CCOEFF_NORMED)
        candidatos = np.where(res >= probabilidad)
        candidatos = np.column_stack([candidatos[1],candidatos[0]])
        return len(candidatos) > 0   




    policia = (
         idetificador_de_muestras(imagenes[1], 0.64) or 
        idetificador_de_muestras(imagenes[2], 0.7)
        )
    print(policia)
    if policia:
        tiempo_fin = time.time() + intervalo[2]
        
        while time.time() < tiempo_fin:
            serial_port.write(b'l')  
            serial_port.write(b'p')  
            time.sleep(intervalo[3])
            
            serial_port.write(b'k')  
            serial_port.write(b'n')  
            time.sleep(intervalo[3])
            
            serial_port.write(b'k')  
            serial_port.write(b'n')  
            time.sleep(intervalo[3])
            
            if cv.waitKey(1) & 0xFF == ord('y'):
                break
    else:
        serial_port.write(b'k')
        serial_port.write(b'p')
        time.sleep(intervalo[1])

    if cv.waitKey(1) & 0xFF == ord ('y'):
        print("Saliendo del detector")
        serial_port.write(b'k')
        time.sleep(intervalo[1])
        serial_port.write(b'p')
        time.sleep(intervalo[1])
        break
pantalla.release()
