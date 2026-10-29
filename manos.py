import subprocess
import cv2
import os
import time
import sys
import face_recognition as fr


#codificar los rostros
imagenes = "/home/yerson24/Documentos/kinet/rostros"
rostros_codificados = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
clasificador = cv2.CascadeClassifier(os.path.join(BASE_DIR, 'haarcascade_frontalface_alt.xml'))
rostros_nombres = []
for imagenesnombres in os.listdir(imagenes):
    print(imagenesnombres)
    imagen = cv2.imread(imagenes + "/" + imagenesnombres)
    imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    codificacion = fr.face_encodings(imagen, known_face_locations=[(0, 0, imagen.shape[0], imagen.shape[1])])[0]
    rostros_codificados.append(codificacion)
    rostros_nombres.append(imagenesnombres.split(".")[0])
   # cv2.imshow("Imagen", imagen)
    #cv2.waitKey(0)
cv2.destroyAllWindows()
print(rostros_nombres)
print(rostros_codificados)

#leer video
video = cv2.VideoCapture(4)
video.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
video. set(cv2.CAP_PROP_EXPOSURE, -7)
video.set(cv2.CAP_PROP_GAIN, 100)
video.set(cv2.CAP_PROP_BRIGHTNESS, 80)

while True:
    ret, frame = video.read()
    if ret == False:
        break
    frame = cv2.flip(frame, 1)
    original = frame.copy()
    rostros = clasificador.detectMultiScale(frame, 1.1, 5)
    for (x, y, w, h) in rostros:
        rostro = original[y:y+h, x:x+w]
        rostro = cv2.cvtColor(rostro, cv2.COLOR_BGR2RGB)
        actual_codificacion = fr.face_encodings(rostro, known_face_locations=[(0, 0, rostro.shape[0], rostro.shape[1])])[0]
        resultados = rostros_reconocidos = fr.compare_faces(rostros_codificados, actual_codificacion)
        print(resultados)

        distancias = fr.face_distance(rostros_codificados, actual_codificacion)
        
        # 2. Encuentra la distancia más pequeña (el rostro más parecido)
        import numpy as np
        indice_mejor_coincidencia = np.argmin(distancias)
        menor_distancia = distancias[indice_mejor_coincidencia]
        
        # 3. Convierte la distancia a porcentaje de probabilidad
        probabilidad = (1 - menor_distancia) * 100
        print(f"Distancia: {menor_distancia:.2f} -> Probabilidad: {probabilidad:.2f}%")

        if probabilidad >= 65:
            nombre = f"{rostros_nombres[indice_mejor_coincidencia]} ({probabilidad:.0f}%)"
            color = (125, 250, 0) # Verde
            time.sleep(0.5)
            comando = ["lutris", f"lutris:rungame/{"gta-iv"}"]   
            subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.exit(0)
        
        else:
            nombre = "Desconocido"
            color = (50, 50, 255) # Rojo
            
        cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, nombre, (x, y + h + 25), 2, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow("Video", frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27: 
        break
