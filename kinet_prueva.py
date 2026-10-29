import cv2 as cv
import serial
import numpy as np
import time

print('Iniciando detector con reescalado de Video')

intervalo = 0.1

# 1. CARGAR LAS IMÁGENES ORIGINALES A COLOR (Sin tocar su tamaño gigante)
uno = cv.imread('1.png', 1)
dos = cv.imread('2.png', 1)

# Validar que los archivos de imagen existan antes de continuar
if uno is None or dos is None:
    print("Error: No se pudo cargar '1.png' o '2.png'. Verifica que estén en la misma carpeta.")
    exit()

# 2. Inicializar hardware (Kinect en índice 3 y puerto Serial)
pantalla = cv.VideoCapture(3) 
serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

def idetificador_de_muestras(ejemplo, probabilidad):
    global frame_gigante
    
    # Validar que la variable de la cámara exista y tenga datos
    if 'frame_gigante' not in globals() or frame_gigante is None:
        return False
        
    # Escudo de dimensiones: El video reescalado TIENE que ser más grande que la plantilla
    if frame_gigante.shape[0] <= ejemplo.shape[0] or frame_gigante.shape[1] <= ejemplo.shape[1]:
        return False
    
    # Procesar coincidencia de plantilla a COLOR de forma segura
    res = cv.matchTemplate(frame_gigante, ejemplo, cv.TM_CCOEFF_NORMED)
    candidatos = np.where(res >= probabilidad)
    candidatos = np.column_stack((candidatos[1], candidatos[0]))
    return len(candidatos) > 0


while True:
    # Capturar el frame nativo (640x480) de la Kinect
    grabar, frame = pantalla.read()
    
    # Escudo de protección de hardware: Si la cámara falla, reintenta sin romper el bucle
    if not grabar or frame is None:
        print("Esperando señal válida de la Kinect...")
        time.sleep(intervalo)
        continue
        
    # 3. REESCALAR EL VIDEO DE LA KINECT
    # Duplicamos su tamaño a 1280x960 para que tus plantillas quepan sobradas
    frame_gigante = cv.resize(frame, (1280, 960), interpolation=cv.INTER_CUBIC)
    
    # Mostrar el video reescalado en una ventana
    cv.imshow('yersonbb', frame_gigante)
    
    # Refrescar la ventana (Obligatorio en OpenCV). Si presionas 'q' se cierra el script
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
        
    # Procesamiento y detección de muestras sobre el video agrandado
    policia = (
        idetificador_de_muestras(uno, 0.64) or
        idetificador_de_muestras(dos, 0.7)
    )
    
    # Acción según el resultado de la detección enviada por Serial
    if policia == True:
        serial_port.write(b'l')
        time.sleep(2.5)
    else:
        time.sleep(intervalo)
        serial_port.write(b'p')
        
    print(policia)

# Liberar la cámara y cerrar ventanas limpiamente al salir
pantalla.release()
cv.destroyAllWindows()
