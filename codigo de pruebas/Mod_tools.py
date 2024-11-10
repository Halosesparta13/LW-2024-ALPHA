import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime

# Función para elegir ubicación de origen
def elegir_ubicacion_origen():
    global origen
    ruta_mods = os.path.join(os.getenv('APPDATA'), '.minecraft', 'mods')
    origen = filedialog.askdirectory(initialdir=ruta_mods)
    lbl_origen.config(text="Origen: " + origen)

# Función para elegir ubicación de construcción
def elegir_ubicacion_construccion():
    global construccion
    
    construccion = filedialog.askdirectory()
    lbl_construccion.config(text="Construcción: " + construccion)

# Función para construir carpetas y comprimir cada grupo de archivos
def construir_carpetas():
    if not origen or not construccion:
        messagebox.showwarning("Advertencia", "Debe seleccionar las ubicaciones.")
        return

    # Obtener lista de archivos y ordenar por tamaño (de mayor a menor)
    archivos = sorted(
        (os.path.join(origen, f) for f in os.listdir(origen)), 
        key=os.path.getsize, 
        reverse=True
    )

    # Crear archivo de texto para registrar los cambios
    changelog_path = os.path.join(construccion, "CHANGELOG.txt")
    with open(changelog_path, 'w') as changelog:
        # Escribir el encabezado y la fecha
        changelog.write("###CHANGELOG###\n")
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        changelog.write(f"Fecha de conversión: {fecha_actual}\n")
        changelog.write("\nLista de archivos:\n")
        
        # Listar los nombres de los archivos en la carpeta de origen
        for archivo in archivos:
            changelog.write(f"{os.path.basename(archivo)}\n")

    # Dividir archivos en 6 grupos
    num_grupos = 6
    grupos = [[] for _ in range(num_grupos)]
    for i, archivo in enumerate(archivos):
        grupos[i % num_grupos].append(archivo)

    # Configuración de la barra de progreso
    progress['value'] = 0
    progress['maximum'] = num_grupos
    ventana.update_idletasks()

    # Comprimir archivos en cada grupo
    for i, grupo in enumerate(grupos, start=1):
        nombre_zip = os.path.join(construccion, f"Mod {i}.zip")
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for archivo in grupo:
                zipf.write(archivo, os.path.basename(archivo))
        # Actualizar la barra de progreso
        progress['value'] = i
        ventana.update_idletasks()

    messagebox.showinfo("Éxito", "Archivos distribuidos y comprimidos en archivos Mod.")
    # Asegurarse de que la barra de progreso esté completa
    progress['value'] = num_grupos
    ventana.update_idletasks()

# Configuración de la ventana
ventana = tk.Tk()
ventana.title("Mod Tools")
ventana.geometry("400x250")

origen = ""
construccion = ""

# Etiquetas
lbl_origen = tk.Label(ventana, text="Origen: No seleccionado")
lbl_origen.pack(pady=5)

lbl_construccion = tk.Label(ventana, text="Construcción: No seleccionado")
lbl_construccion.pack(pady=5)

# Botones
btn_elegir_origen = tk.Button(ventana, text="Elegir ubicación origen", command=elegir_ubicacion_origen)
btn_elegir_origen.pack(pady=5)

btn_elegir_construccion = tk.Button(ventana, text="Elegir ubicación construcción", command=elegir_ubicacion_construccion)
btn_elegir_construccion.pack(pady=5)

btn_construir = tk.Button(ventana, text="Construir", command=construir_carpetas)
btn_construir.pack(pady=10)

# Barra de progreso
progress = ttk.Progressbar(ventana, orient='horizontal', length=300, mode='determinate')
progress.pack(pady=20)

ventana.mainloop()
