import subprocess
import sys

# Diccionario mapeado exactamente con los IDs reales de tu terminal
JUEGOS = {
    "1": ("GTA IV", "gta-iv"),
    "2": ("Gta V", "gta-v"),
    "3": ("Deltarune", "deltarune"),
    "4": ("Undertale", "undertale"),
    "5": ("Call of Duty Modern Warfare 4", "call-of-duty-moder-warfare-4"),
    "6": ("Resident Evil", "resident-evil"),
    "7": ("Flatout 2 (Instalador)", "flatout2")
}

def mostrar_menu():
    print("\n=== MI LANZADOR DE JUEGOS EN PYTHON ===")
    for opcion, (nombre, _) in JUEGOS.items():
        print(f"[{opcion}] - {nombre}")
    print("[0] - Salir")

def arrancar_juego(id_lutris):
    print(f"\n[+] Enviando orden a Lutris para arrancar: {id_lutris}...")
    
    # Comando nativo directo de Bazzite
    comando = ["lutris", f"lutris:{id_lutris}"]
    
    # Popen inicia el proceso de fondo de forma independiente
    subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[✓] Proceso enviado. El juego debería abrirse en unos segundos.")

def principal():
    while True:
        mostrar_menu()
        seleccion = input("\nSelecciona el número del juego que quieres iniciar: ").strip()
        
        if seleccion == "0":
            print("Cerrando el lanzador de Python. ¡Buen juego!")
            sys.exit()
        elif seleccion in JUEGOS:
            nombre_juego, id_lutris = JUEGOS[seleccion]
            arrancar_juego(id_lutris)
            break
        else:
            print("[!] Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    principal()
