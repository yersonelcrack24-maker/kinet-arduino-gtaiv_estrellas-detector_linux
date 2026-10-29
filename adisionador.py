import subprocess
import cv2
import os
juego_a_lanzar = False #"gta-iv"
imagenes = "/home/yerson24/Documentos/kinet/imagenes"
clasificador = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

if juego_a_lanzar == "gta-iv":
    print("Iniciando Grand Theft Auto IV directamente...")
    
    # Usamos --run-game para saltarnos la ventana de confirmación de Lutris
    comando = ["lutris", f"lutris:rungame/{"gta-iv"}"]
    
    # Ejecutamos de fondo de manera limpia
    subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



if not os.path.exists("rostros"):
    os.makedirs("rostros")
    print("Carpeta de rostros creada :)")
contador = 0
for imagenesnombres in os.listdir(imagenes):
    print(imagenesnombres)
    imagen = cv2.imread(imagenes + "/" + imagenesnombres)
    rostros = clasificador.detectMultiScale(imagen,1.1, 5)
    for (x, y, w, h) in rostros:
        #cv2.rectangle(imagen, (x, y), (x + w, y + h), (0, 255, 0), 2)
        rostro = imagen[y:y+h, x:x+w]
        rostro = cv2.resize(rostro, (150, 150))#, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite("rostros/" + str(contador) + ".png", rostro)
        contador += 1
        #cv2.imwrite("rostros/rostro_" + imagenesnombres, rostro)
    #cv2.imshow("Rostro", rostro)    
    #cv2.imshow("Imagen", imagen)
    #cv2.waitKey(0)
#cv2.destroyAllWindows()