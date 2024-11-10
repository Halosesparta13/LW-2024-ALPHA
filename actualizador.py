import os
import sys
import time

# Espera un momento para asegurarse de que el programa principal haya cerrado
time.sleep(3)

# Ruta del archivo descargado y la ruta de destino
temp_file = os.path.join(os.getcwd(), "temp_Luckyworld_Launcher.exe")
final_file = os.path.join(os.getcwd(), "Luckyworld Launcher.exe")

# Verificar si el archivo temporal existe
if os.path.exists(temp_file):
    try:
        # Mover el archivo descargado a su ubicación final
        os.rename(temp_file, final_file)
        print("El archivo ha sido actualizado con éxito.")

        # Reiniciar el programa
        os.execv(final_file, sys.argv)  # Ejecutar el nuevo archivo .exe
    except Exception as e:
        print(f"Error al mover el archivo: {e}")
else:
    print("No se encontró el archivo descargado.")
