import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import subprocess, sys, time, serial, math
from collections import deque

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

historial = deque(maxlen=7)

def dedo_preciso(pts, tip, dip, pip, mcp):
    return pts[tip].y < pts[dip].y - 0.01 and pts[dip].y < pts[pip].y - 0.01 and pts[pip].y < pts[mcp].y - 0.01 and math.hypot(pts[tip].x - pts[mcp].x, pts[tip].y - pts[mcp].y) > 0.12

def pulgar_debug(pts):
    # NUEVA LOGICA A PRUEBA DE FLIP: pulgar arriba si esta lejos de la palma y alto
    tip, ip, mcp, palm = pts[4], pts[3], pts[2], pts[0]
    # Distancia tip a base del indice (punto 5)
    dist_tip_indice = math.hypot(tip.x - pts[5].x, tip.y - pts[5].y)
    dist_ip_indice = math.hypot(ip.x - pts[5].x, ip.y - pts[5].y)
    # Si tip esta mas lejos que ip, esta extendido
    extendido = dist_tip_indice > dist_ip_indice + 0.02
    alto = tip.y < mcp.y + 0.08
    print(f"DEBUG PULGAR: dist_tip={dist_tip_indice:.3f} dist_ip={dist_ip_indice:.3f} extendido={extendido} alto={alto}")
    return extendido and alto

opciones = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='/home/yerson24/Documentos/kinet/hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO, num_hands=1,
    min_hand_detection_confidence=0.7, min_hand_presence_confidence=0.7, min_tracking_confidence=0.7
)

serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2) # deja que arduino arranque
detector = HandLandmarker.create_from_options(opciones)

cap = cv2.VideoCapture(3)
if not cap.isOpened(): cap = cv2.VideoCapture(0)
cap.set(3, 640); cap.set(4, 480)

timestamp_ms, ultimo_estado, contador_estable = 0, None, 0
cerrar_app = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    

    frame_para_detectar = frame.copy()
    frame = cv2.flip(frame, 1) 
    
    frame_rgb = cv2.cvtColor(frame_para_detectar, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms += 33
    resultado = detector.detect_for_video(mp_image, timestamp_ms)

    if resultado.hand_landmarks:
        pts = resultado.hand_landmarks[0]
        pulgar = pulgar_debug(pts)
        indice = dedo_preciso(pts, 8,7,6,5)
        corazon = dedo_preciso(pts, 12,11,10,9)
        anular = dedo_preciso(pts, 16,15,14,13)
        menique = dedo_preciso(pts, 20,19,18,17)

        estado_actual = (pulgar, indice, corazon, anular, menique)
        historial.append(estado_actual)
        voto = [sum(x) > len(historial)//2 for x in zip(*historial)]
        pulgar_v, indice_v, corazon_v, anular_v, menique_v = voto

        if estado_actual != ultimo_estado:
            contador_estable = 0
            ultimo_estado = estado_actual
        else:
            contador_estable += 1

        if contador_estable > 3:
            if menique_v and not indice_v and not corazon_v and not anular_v:
                print("GESTO GTA - CERRANDO TODO")
                cerrar_app = True
                break

            if pulgar_v:
                print(">>> PULGAR ARRIBA -> Enviando n (AZUL ON)")
                serial_port.write(b'n')
            else:
                print(">>> PULGAR ABAJO -> Enviando p (AZUL OFF)")
                serial_port.write(b'p')

            if indice_v:
                serial_port.write(b'l')
            else:
                serial_port.write(b'k')

        h,w,_ = frame.shape
        for tip,dip,pip,mcp in [(8,7,6,5),(12,11,10,9),(16,15,14,13),(20,19,18,17)]:
            cx,cy = int(pts[tip].x*w), int(pts[tip].y*h)
            cv2.circle(frame,(w-cx,cy),10,(0,255,0) if dedo_preciso(pts,tip,dip,pip,mcp) else (0,0,255),-1)
        cx,cy = int(pts[4].x*w), int(pts[4].y*h)
        cv2.circle(frame,(w-cx,cy),14,(255,0,0) if pulgar else (0,0,255),-1)

    cv2.imshow('Detector FIX', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# FUERA DEL WHILE - cierre limpio y DEFINITIVO
print("Cerrando...")
try:
    cap.release()
except:
    pass
cv2.destroyAllWindows()
try:
    serial_port.write(b'k')
    time.sleep(0.2)
    serial_port.write(b'p')
    time.sleep(0.2)
    serial_port.close()
except:
    pass

if cerrar_app:
    print("Lanzando GTA IV y matando detector para que no se relance")
    # Crea un archivo lock para que no se relance si tienes un while en bash
    with open("/tmp/no_relaunch_gta", "w") as f:
        f.write("1")
    subprocess.Popen(["lutris", "lutris:rungame/gta-iv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    # Mata el proceso de forma bruta, no deja que vuelva a ejecutarse
    import os
    os._exit(0)
else:
    import os
    os._exit(0)