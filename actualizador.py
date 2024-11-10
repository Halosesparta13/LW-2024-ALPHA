import os
import sys
import time

# Ruta del archivo descargado y la ruta de destino
temp_file = os.path.join(os.getcwd(), "temp_Luckyworld_Launcher.exe")
final_file = os.path.join(os.getcwd(), "Luckyworld Launcher.exe")

# Esperar un momento para asegurarse de que el programa principal haya cerrado (opcional)
time.sleep(2)

# Verificar si el archivo temporal existe
if os.path.exists(temp_file):
    try:
        # Intentar mover el archivo descargado a su ubicación final
        os.rename(temp_file, final_file)
        print("El archivo ha sido actualizado con éxito.")

        # Asegurarse de que el archivo final existe antes de reiniciar
        if os.path.exists(final_file):
            # Reiniciar el programa
            print("Reiniciando el launcher...")
            os.execv(final_file, sys.argv)  # Ejecutar el nuevo archivo .exe
        else:
            print("Error: El archivo actualizado no se encuentra en la ubicación esperada.")
    
    except Exception as e:
        print(f"Error al mover el archivo: {e}")
else:
    print("No se encontró el archivo descargado.")
