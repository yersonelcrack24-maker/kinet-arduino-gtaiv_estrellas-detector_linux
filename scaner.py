import freenect
import numpy as np
import open3d as o3d
import cv2 as cv
import time

print("Inicializando Escáner 3D Multi-Perspectiva (Rango Cercano Optimizado)...")

# 1. Configuración de matriz intrínseca calibrada de la Kinect
ANCHO, ALTO = 640, 480
FX, FY = 585.0, 585.0  
CX, CY = 320.0, 240.0
intrinsics = o3d.camera.PinholeCameraIntrinsic(ANCHO, ALTO, FX, FY, CX, CY)

freenect.sync_stop()
time.sleep(0.3)

# Contenedor global para ir acumulando todas las perspectivas
nube_acumulada = o3d.geometry.PointCloud()

def obtener_profundidad_metros():
    try:
        # Traer la profundidad nativa de 11 bits del sensor infrarrojo
        depth, _ = freenect.sync_get_depth(format=freenect.DEPTH_11BIT)
        if depth is None:
            return None
        depth = depth.astype(np.float32)
        depth_metros = 1.0 / (depth * -0.0030711016 + 3.3309495161)
        
        # FILTRO DE HARDWARE MEJORADO: Permitir lecturas ultra-cercanas (35 cm a 90 cm)
        depth_metros[depth >= 2047] = 0.0
        depth_metros[depth_metros < 0.35] = 0.0  # Límite mínimo absoluto de la física del lente
        depth_metros[depth_metros > 0.90] = 0.0  # Recorta el fondo por completo a partir de 90 cm
        
        return depth_metros
    except Exception:
        return None

print("\n[+] Modo Cercano Activo.")
print("-> Coloca la chancla MUY CERCA de la Kinect (entre 40 y 60 cm).")
print("-> Presiona 'S' (Mayúscula) para capturar la perspectiva actual.")
print("-> Presiona 'E' (Mayúscula) para procesar y EXPORTAR el modelo .OBJ sólido.")
print("-> Presiona 'Q' para salir.")

while True:
    depth_map = obtener_profundidad_metros()
    
    if depth_map is not None:
        # Visor de profundidad estable en tiempo real
        vista_provisional = np.uint8(cv.normalize(depth_map, None, 0, 255, cv.NORM_MINMAX))
        vista_provisional = 255 - vista_provisional 
        
        cv.imshow("Visor Infrarrojo - Rango Cercano", vista_provisional)
        tecla = cv.waitKey(1) & 0xFF
        
        # 1. CAPTURAR PERSPECTIVA ACTUAL
        if tecla == ord('s') or tecla == ord('S'):
            depth_o3d = o3d.geometry.Image(depth_map)
            pcd_vane = o3d.geometry.PointCloud.create_from_depth_image(
                depth_o3d, intrinsics, depth_scale=1.0, depth_trunc=0.90
            )
            
            if len(pcd_vane.points) > 50:
                # CAJA DE RECORTE QUIRÚRGICA: Reducida a un cubo de 30x30 cm enfrente de la Kinect
                # Esto aísla por completo la chancla y borra la mesa o el piso de los lados
                caja_limite = o3d.geometry.AxisAlignedBoundingBox(
                    min_bound=(-0.15, -0.15, 0.35),
                    max_bound=(0.15, 0.15, 0.85)
                )
                pcd_vane = pcd_vane.crop(caja_limite)
                
                # Acumular los puntos capturados en el contenedor global
                nube_acumulada += pcd_vane
                print(f"[+] Ángulo cercano capturado. Puntos en la chancla: {len(nube_acumulada.points)}")
            else:
                print("[❌] Error: No se detectaron puntos. Mueve la chancla un poco hacia atrás.")

        # 2. PROCESAR Y EXPORTAR LA CHANCLA EN 3D REAL (.OBJ)
        elif tecla == ord('e') or tecla == ord('E'):
            total_puntos = len(nube_acumulada.points)
            if total_puntos > 200:
                print(f"\n[+] Iniciando procesamiento de {total_puntos} puntos de alta precisión...")
                
                print("[+] Ajustando densidad de puntos en rango corto...")
                nube_acumulada = nube_acumulada.voxel_down_sample(voxel_size=0.002) # Muestreo más fino
                nube_acumulada, _ = nube_acumulada.remove_statistical_outlier(nb_neighbors=30, std_ratio=1.2)
                
                print("[+] Calculando normales óptimas...")
                nube_acumulada.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.02, max_nn=30))
                
                print("[+] Tejiendo la malla compacta de la chancla (Alpha Shapes)...")
                alpha = 0.012  # Radio Alpha más cerrado para capturar detalles finos desde cerca
                mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(nube_acumulada, alpha)
                mesh.compute_vertex_normals()
                
                # Guardar el archivo final sólido en formato .obj
                nombre_obj = f"chancla_cercana_{int(time.time())}.obj"
                o3d.io.write_triangle_mesh(nombre_obj, mesh)
                print(f"\n[⚡ ÉXITO] ¡Chancla de alta resolución guardada como '{nombre_obj}'!")
                
                # Vaciar contenedor para poder iniciar un nuevo escaneo limpio
                nube_acumulada.clear()
            else:
                print("[❌] No has acumulado suficientes perspectivas. Presiona 'S' primero.")
                
        elif tecla == ord('q') or tecla == ord('Q'):
            break
    else:
        time.sleep(0.01)

cv.destroyAllWindows()
freenect.sync_stop()
print("Escáner apagado.")
