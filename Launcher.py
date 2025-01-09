import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import os
import time
import zipfile
from PIL import Image, ImageTk
import webbrowser  # Importar el módulo webbrowser
import re
import platform
import subprocess
import sys

class LWLauncher:
    def __init__(self, root):
        self.root = root
        # Cargar la imagen
        self.cargar_imagen()
        self.verificar_o_crear_version_txt()
        
        self.inicializar_variables()
        self.configurar_interfaz()
        self.configurar_ventana()
        self.verificar_version_launcher()
        

    def verificar_o_crear_version_txt(self):
        # Nombre del archivo y ruta (en la misma carpeta donde se ejecuta el programa)
        archivo_version = "Version.txt"

        # Verificar si el archivo existe
        if not os.path.exists(archivo_version):
            # Si no existe, crear el archivo con las dos líneas inicializadas como "0.0.0"
            with open(archivo_version, "w") as archivo:
                archivo.write("0.0.0\n0.1.0\n")
            print(f"{archivo_version} no existía y ha sido creado con valores predeterminados.")
        else:
            print(f"{archivo_version} ya existe.")


    def inicializar_variables(self):
        self.url_version = "https://raw.githubusercontent.com/Halosesparta13/LW-2024-ALPHA/refs/heads/main/Version_Test"
        self.url_launcher_version = "https://raw.githubusercontent.com/Halosesparta13/LW-2024-ALPHA/refs/heads/main/Launcher_Version.txt"
        self.carpeta_destino = None
        self.descargando = False
        self.pausado = False
        self.thread = None
        self.current_file = None
        self.urls = []  # Lista para almacenar URLs de archivos adicionales
        self.version_local = self.obtener_version_local()  # Obtener versión local al iniciar
        self.zip_files = []  # Lista para almacenar archivos ZIP descargados
        self.opcionesCB = []
        #print(f"url_version: {self.url_version}")


    def configurar_ventana(self):
        self.root.title("Launcher LuckyWorld - BETA")
        #WidthB = 980
        #HeightB = 650
        self.root.geometry("850x550")  # Definir tamaño de la ventana (ancho x alto)
        self.root.resizable(False, False)
        self.crear_menu()  # Crear el menú en la parte superior
        
        # Cambiar color de fondo de la ventana
        self.root.configure(bg="#2E2E2E")  # Fondo oscuro

    def crear_menu(self):
        # Crear la barra de menú
        menu_bar = tk.Menu(self.root)
        
        # Crear el primer menú desplegable: "Archivo"
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.salir)
        archivo_menu.add_command(label="Directorio", command=self.abrir_directorio)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)
        
        # Crear el segundo menú desplegable: "Configuración"
        configuracion_menu = tk.Menu(menu_bar, tearoff=0)
        configuracion_menu.add_command(label="Preferencias", command=self.abrir_preferencias)
        menu_bar.add_cascade(label="Configuración", menu=configuracion_menu)
         # Menú "Links"
        links_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Links", menu=links_menu)
        links_menu.add_command(label="Links del Modpack", command=self.abrir_url_version)
        # Crear el tercer menú desplegable: "Ayuda"
        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)
        
        # Configurar la barra de menús en la ventana
        self.root.config(menu=menu_bar)

##-Re trabajar esta función, no está optimizada
    def verificar_y_eliminar_launcher_antiguo(self, nuevo_nombre):
        try:
            # Obtener el directorio actual (donde está el nuevo launcher)
            directorio_actual = os.getcwd()

            # Buscar todos los archivos que empiecen con "LuckyWorld Launcher" y terminen con ".exe"
            archivos = os.listdir(directorio_actual)
            patron = re.compile(r"LuckyWorld Launcher (\d+\.\d+\.\d+)v\.exe")  # Patente para encontrar versiones en los nombres

            for archivo in archivos:
                # Verificar si el archivo coincide con el patrón
                match = patron.match(archivo)
                if match:
                    version_encontrada = match.group(1)  # Extraer la versión del nombre del archivo
                    if f"LuckyWorld Launcher {version_encontrada}v.exe" != nuevo_nombre:
                        # Si el archivo tiene una versión distinta a la del nuevo launcher, eliminarlo
                        print(f"Eliminando el archivo antiguo: {archivo}")
                        os.remove(os.path.join(directorio_actual, archivo))

        except Exception as e:
            print(f"Error al intentar verificar y eliminar el launcher antiguo: {e}")

## SE NECESITA TRABAJAR
    def verificar_version_launcher(self):
        try:
            # Leer la versión local desde la segunda línea de Version.txt
            with open("Version.txt", "r") as f:
                lines = f.readlines()
                if len(lines) < 2:
                    messagebox.showerror("Error", "El archivo Version.txt no tiene una segunda línea con la versión.")
                    return
                version_local = lines[1].strip()

            # Obtener la versión remota y el enlace de descarga desde self.url_launcher_version
            response = requests.get(self.url_launcher_version)
            response.raise_for_status()
            content = response.text.strip().split('\n')
            if len(content) < 2:
                messagebox.showerror("Error", "El archivo en url_launcher_version no tiene una segunda línea con el link de descarga. \n[ERROR INTERNO, COMUNICARSE CON HALOSESPARTA]")
                return
            version_remota_Launcher = content[0].strip()
            url_descarga = content[1].strip()  # Segunda línea, link de descarga

            # Comparar versiones
            if version_remota_Launcher > version_local:
                respuesta = messagebox.askyesno("Actualización disponible", 
                                                "Hay una versión superior del launcher. ¿Desea actualizar?")
                if respuesta:
                    # Verificar y eliminar el launcher anterior si no coincide con la versión nueva
                    nuevo_nombre = f"LuckyWorld Launcher {version_remota_Launcher}v.exe"
                    self.verificar_y_eliminar_launcher_antiguo(nuevo_nombre)

                    # Descargar el archivo de actualización a una ubicación temporal
                    temp_file = os.path.join(os.getcwd(), "temp_Luckyworld_Launcher.exe")
                    descarga = requests.get(url_descarga, stream=True)
                    with open(temp_file, "wb") as archivo:
                        for chunk in descarga.iter_content(chunk_size=8192):
                            archivo.write(chunk)

                    # Actualizar solo la segunda línea de Version.txt
                    lines[1] = f"{version_remota_Launcher}\n"  # Modificar solo la segunda línea
                    with open("Version.txt", "w") as f:
                        f.writelines(lines)

                    messagebox.showinfo("Actualización completada", "El launcher se ha descargado. El programa se cerrará y actualizará...")

                    # Renombrar el archivo descargado a LuckyWorld Launcher [version_remota_Launcher].exe
                    os.rename(temp_file, nuevo_nombre)

                    # Ejecutar el nuevo launcher
                    subprocess.Popen([nuevo_nombre])

                    # Cerrar el programa principal
                    sys.exit()  # Cierra el programa

        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar la versión del launcher: {e}")

    def abrir_url_version(self):
        if not self.url_version:
            messagebox.showerror("Error", "No hay una URL de versión disponible para abrir.")
            return

        try:
            # Intentar abrir con webbrowser, que es multiplataforma
            webbrowser.open(self.url_version)
        except Exception as e:
            # Si webbrowser falla, intentar con comandos específicos de cada sistema
            sistema = platform.system()
            try:
                if sistema == "Windows":
                    os.startfile(self.url_version)
                elif sistema == "Darwin":  # macOS
                    subprocess.call(["open", self.url_version])
                elif sistema == "Linux":
                    subprocess.call(["xdg-open", self.url_version])
                else:
                    messagebox.showerror("Error", "Sistema operativo no soportado para abrir la URL.")
            except Exception as e:
                print(f"Error al abrir la URL: {e}")
                messagebox.showerror("Error", f"No se pudo abrir la URL: {e}")
        
    def salir(self):
        self.root.quit()

    def abrir_preferencias(self):
        messagebox.showinfo("Preferencias", "Función de preferencias aún no implementada.")
    
    def abrir_directorio(self):
        # Verificar si la carpeta de destino está definida
        if not self.carpeta_destino:
            messagebox.showerror("Error", "No has elegido aún una ubicación para los mods")
            return

        # Intentar abrir la carpeta de destino según el sistema operativo
        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(self.carpeta_destino)  # Windows
            elif sistema == "Darwin":  # macOS
                subprocess.call(["open", self.carpeta_destino])
            elif sistema == "Linux":
                subprocess.call(["xdg-open", self.carpeta_destino])
            else:
                messagebox.showerror("Error", "Sistema operativo no soportado para abrir el directorio.")
        except Exception as e:
            print(f"Error al abrir el directorio: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el directorio: {e}")

    def mostrar_acerca_de(self):
        mensaje = ("Launcher LuckyWorld - BETA\n\n"
                   f"Versión {self.obtener_version_local()}\n"
                   "Desarrollado por Halosesparta\n"
                   "Modpacks por Aarods21\n\n"
                   "¡Descarga tus mods en un solo lugar!"
                   "Asegúrate de tener siempre la última versión disponible.")
        messagebox.showinfo("Acerca de", mensaje)

    def cargar_imagen(self):
        # Determinar la ruta base, ya sea en modo desarrollo o en el ejecutable
        if getattr(sys, 'frozen', False):  # Si el script está ejecutándose desde el ejecutable
            ruta_base = sys._MEIPASS  # Directorio temporal donde PyInstaller extrae los archivos
        else:
            ruta_base = os.path.dirname(__file__)  # Si está ejecutándose desde el script

        # Ruta completa de la imagen en la carpeta 'assets'
        ruta_imagen = os.path.join(ruta_base, 'assets', 'lw_bg.png')

        try:
            # Cargar la imagen desde la ruta
            imagen_original = Image.open(ruta_imagen)
        
            # Redimensionar la imagen
            nueva_ancho, nueva_alto = 850, 400  # Define el tamaño deseado
            imagen_redimensionada = imagen_original.resize((nueva_ancho, nueva_alto), Image.LANCZOS) #ANTIALIAS
        
            # Convertir para mostrar en Tkinter
            self.imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
            fondo_color = "#2E2E2E"
        
            # Crear un Label y asignar la imagen
            self.label_imagen = tk.Label(self.root, image=self.imagen_tk, bg=fondo_color)
            self.label_imagen.place(x=0, y=0)
        except FileNotFoundError:
            print(f"Error: No se encuentra la imagen en {ruta_imagen}.")
            # Si no se encuentra la imagen, puedes manejarlo de alguna manera
            self.label_imagen = tk.Label(self.root, text="Imagen no encontrada", bg=fondo_color)
            self.label_imagen.place(x=0, y=0)

    def obtener_versiones(self):
        try:
            # Realizar solicitud para obtener contenido del archivo
            response = requests.get(self.url_version)
            response.raise_for_status()  # Verificar que no hay errores en la solicitud
            contenido = response.text

            # Usar una expresión regular para encontrar todas las versiones en el formato "//Modpack - [versión]"
            versiones = re.findall(r"//Modpack - ([\w\s.]+)", contenido)

            # Limpiar las versiones encontradas para eliminar cualquier texto adicional como 'https'
            versiones_limpias = [version.split('https')[0].strip() for version in versiones]

            # Guardar las versiones limpias en la lista 'opcionesCB'
            self.opcionesCB = versiones_limpias
            return versiones_limpias  # Retornar todas las versiones encontradas

        except requests.RequestException as e:
            print("Error al obtener versiones:", e)
            self.opcionesCB = ["Error al cargar versiones"]  # Guardar el error en la lista 'opciones'
            return self.opcionesCB

    def configurar_interfaz(self):
        # Colores de fondo y texto
        fondo_color = "#2E2E2E"
        texto_color = "white"

        # Llamar a la función para obtener las versiones
        versiones = self.obtener_versiones()

        
        # Aplica estos colores a la etiqueta de la versión
        self.version_label = tk.Label(
            self.root,
            text=f"{self.obtener_version_local()} BETA",  # Muestra la versión local
            font=("Helvetica", 14),
            fg=texto_color,
            bg=fondo_color
        )
        self.version_label.place(x=15, y=370)
        
        # Etiqueta de estado
        self.status_label = tk.Label(self.root, text="Status: ???", font=("Helvetica", 11), fg=texto_color, bg=fondo_color)
        self.status_label.place(x=15, y=418)

        # Barra de progreso
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.place(x=15, y=440)

        # Etiqueta para mostrar el porcentaje de progreso
        self.porcentaje_label = tk.Label(self.root, text="0%", font=("Helvetica", 11), fg=texto_color, bg=fondo_color)
        self.porcentaje_label.place(x=420, y=440)

        # Frame para agrupar el botón "Seleccionar ubicación" y el ComboBox
        ubicacion_frame = tk.Frame(self.root, bg=fondo_color)
        ubicacion_frame.place(relx=0.8, y=500, anchor=tk.CENTER)

        # Botón "Seleccionar ubicación" dentro del Frame
        self.elegir_button = tk.Button(ubicacion_frame, text="Seleccionar ubicación", command=self.elegir_ubicacion, height=2, bg=fondo_color, fg=texto_color)
        self.elegir_button.pack(side=tk.LEFT, padx=5)

        # ComboBox junto al botón en el mismo Frame
        self.combobox = ttk.Combobox(ubicacion_frame, values=versiones, height=2)
        self.combobox.set("Elige un modpack")
        self.combobox.pack(side=tk.LEFT, padx=5)

        # Frame para agrupar los botones de acción en la parte inferior
        botones_frame = tk.Frame(self.root, bg=fondo_color)
        botones_frame.place(relx=0.8, y=450, anchor=tk.CENTER)

        # Botones "Start", "Pause" y "Resume"
        widthB = 11
        heightB = 2
        self.comenzar_button = tk.Button(botones_frame, text="Start", command=self.iniciar_descarga, width=widthB, height=heightB, bg=fondo_color, fg=texto_color)
        self.comenzar_button.pack(side=tk.LEFT, padx=5)

        self.pausar_button = tk.Button(botones_frame, text="Pause", command=self.pausar_descarga, state=tk.DISABLED, width=widthB, height=heightB, bg=fondo_color, fg=texto_color)
        self.pausar_button.pack(side=tk.LEFT, padx=5)

        self.reanudar_button = tk.Button(botones_frame, text="Resume", command=self.reanudar_descarga, state=tk.DISABLED, width=widthB, height=heightB, bg=fondo_color, fg=texto_color)
        self.reanudar_button.pack(side=tk.LEFT, padx=5)

        # Frame para agrupar los labels
        info_frame = tk.Frame(self.root, bg=fondo_color)
        info_frame.place(x=10, y=480)

        # Etiqueta de descarga
        self.descargado_label = tk.Label(info_frame, text="Descarga: 0 MB", font=("Helvetica", 11), fg=texto_color, bg=fondo_color)
        self.descargado_label.pack(side=tk.LEFT, padx=5)

        # Etiqueta de tiempo estimado
        self.tiempo_label = tk.Label(info_frame, text="Tiempo estimado: 00:00:00", font=("Helvetica", 11), fg=texto_color, bg=fondo_color)
        self.tiempo_label.pack(side=tk.LEFT, padx=5)

        # Etiqueta de velocidad
        self.speed_label = tk.Label(self.root, text="Velocidad: 0 MB/s", font=("Helvetica", 11), fg=texto_color, bg=fondo_color)
        self.speed_label.place(x=15, y=510)

###-Simplificar codigo
    def obtener_version_local(self):
        version_archivo = "Version.txt"
        if os.path.exists(version_archivo):
            with open(version_archivo, "r") as archivo:
                lines = archivo.readlines()
                # Verifica si hay al menos dos líneas
                if len(lines) >= 2:
                    return lines[1].strip()  # Devuelve la segunda línea
                else:
                    # Si no hay segunda línea, retorna una versión por defecto
                    return "0.0.0"
        else:
            # Si el archivo no existe, crea uno con la versión por defecto en la segunda línea
            with open(version_archivo, "w") as archivo:
                archivo.write("0.0.0\n0.0.0\n")  # Escribe la versión por defecto en ambas líneas
            return "0.0.0"
        
    def guardar_version(self, version):
        version_archivo = "Version.txt"
        with open(version_archivo, "w") as archivo:
            archivo.write(f"{version}\n")  # Guardar solo la versión
        print(f"Versión actualizada a {version}")

    def elegir_ubicacion(self):
        # Definir la ruta predeterminada según el sistema operativo
        if self.carpeta_destino == "":
            messagebox.showinfo("Info", "Elija la carpeta donde se encuentran los archivos de Minecraft.")
        sistema = platform.system()
        if sistema == "Windows":
            ruta_predeterminada = os.path.join(os.getenv('APPDATA'), '.minecraft')
        elif sistema == "Darwin":  # macOS
            ruta_predeterminada = os.path.expanduser('~/Library/Application Support/minecraft')
        elif sistema == "Linux":  # Linux
            ruta_predeterminada = os.path.expanduser('~/.minecraft')
        else:
            # Ruta genérica para otros sistemas operativos
            ruta_predeterminada = "./minecraft"

        print(f"Ruta predeterminada: {ruta_predeterminada}")

        # Abrir el diálogo para seleccionar una carpeta, usando la ruta predeterminada
        self.carpeta_destino = filedialog.askdirectory(initialdir=ruta_predeterminada)
        print(f"Carpeta destino (elegida): {self.carpeta_destino}")
        archivo_version = "Version.txt"
        with open(archivo_version, "r") as archivo:
                lineas = archivo.readlines()

        # Asegurarse de que haya al menos 3 líneas
        while len(lineas) < 3:
            lineas.append("\n")
        
        # Escribir "ruta" en la tercera línea
        lineas[2] = self.carpeta_destino + "\n"
        
        # Sobrescribir el archivo con las líneas actualizadas
        with open(archivo_version, "w") as archivo:
            archivo.writelines(lineas)
        
        print(f"Se escribió la carpeta destino en la tercera línea de {archivo_version}.")


        #if not self.carpeta_destino:  # Si no se selecciona ninguna carpeta
            #messagebox.showinfo("Info", "No se seleccionó carpeta, se usará ./descargas por defecto.")
        #    self.carpeta_destino = "./descargas"
        #    print(f"Carpeta destino actualizada (no seleccionó carpeta): {self.carpeta_destino}")
        
        # Crear la carpeta destino si no existe
       # if not os.path.exists(self.carpeta_destino):
        #    os.makedirs(self.carpeta_destino)
        #    print(f"Carpeta destino creada (no existía): {self.carpeta_destino}")
            
   ##Incluyendo eliminación de config, emojis y mods
    def eliminar_carpetas(self):
        carpetas_a_eliminar = ['mods', 'config', 'emotes']

        # Iterar por las carpetas que se desean eliminar
        for nombre_carpeta in carpetas_a_eliminar:
            ruta_carpeta = os.path.join(self.carpeta_destino, nombre_carpeta)

            if os.path.exists(ruta_carpeta):
                respuesta = messagebox.askyesno(
                    "Confirmación",
                    f"Se procederá a eliminar la carpeta '{nombre_carpeta}' para asegurar una instalación limpia. ¿Desea continuar?"
                )
                if respuesta:
                    try:
                        # Eliminar la carpeta y todo su contenido
                        for root, dirs, files in os.walk(ruta_carpeta, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(ruta_carpeta)
                        print(f"Carpeta '{nombre_carpeta}' eliminada.")
                    except Exception as e:
                        print(f"Error al eliminar la carpeta '{nombre_carpeta}': {e}")
                        messagebox.showerror("Error", f"Error al eliminar la carpeta '{nombre_carpeta}': {e}")
                else:
                    print(f"La eliminación de la carpeta '{nombre_carpeta}' ha sido cancelada.")
            else:
                print(f"No se ha encontrado la carpeta '{nombre_carpeta}', por lo que se saltea este paso.")
   
    def descargar_archivo(self, url, destino):
        try:
            nombre_archivo = url.split("/")[-1].split("?")[0]
            ruta_archivo = os.path.join(destino, nombre_archivo)
            print(f"Descargar_archivo ruta {destino}")

            self.status_label.config(text=f"Descargando {nombre_archivo}...")
            print(f"Descargando {nombre_archivo}...")
            respuesta = requests.get(url, stream=True)
            tamano_total = int(respuesta.headers.get('content-length', 0))

            chunk_size = 8192
            tamano_descargado = 0
            inicio_tiempo = time.time()

            with open(ruta_archivo, "wb") as archivo:
                for chunk in respuesta.iter_content(chunk_size=chunk_size):
                    while self.pausado:
                        time.sleep(0.1)  # Pausa mientras esté pausado

                    archivo.write(chunk)
                    tamano_descargado += len(chunk)

                    # Actualizar la barra de progreso y etiquetas
                    self.actualizar_progreso(tamano_descargado, tamano_total, inicio_tiempo)

                    if not self.descargando:  # Si se detiene la descarga
                        break

            if self.descargando:
                if nombre_archivo == "Version.txt":
                    self.actualizar_version(ruta_archivo)
                if nombre_archivo.endswith(".zip"):
                    self.zip_files.append(ruta_archivo)  # Añadir el archivo ZIP a la lista
                #messagebox.showinfo("Completado", f"Archivo guardado en {ruta_archivo}")
            else:
                messagebox.showinfo("Cancelado", "Descarga pausada o cancelada.")

        except Exception as e:
            print(f"Ocurrió un error al descargar el archivo: {e}")
            messagebox.showerror("Error", f"Error al descargar: {e}")

        self.current_file = None
        self.comenzar_button.config(state=tk.NORMAL)
        self.elegir_button.config(state=tk.NORMAL)
        self.pausar_button.config(state=tk.DISABLED)
        self.reanudar_button.config(state=tk.DISABLED)

    def actualizar_progreso(self, tamano_descargado, tamano_total, inicio_tiempo):
        porcentaje_completado = (tamano_descargado / tamano_total) * 100
        self.progress["value"] = porcentaje_completado
        self.porcentaje_label.config(text=f"{porcentaje_completado:.2f}%")

        # Calcular la velocidad de descarga
        tiempo_transcurrido = time.time() - inicio_tiempo
        velocidad = tamano_descargado / 1024 / 1024 / max(tiempo_transcurrido, 1)  # MB/s (dividir por 1 para evitar división por cero)
        self.speed_label.config(text=f"Velocidad: {velocidad:.2f} MB/s")

        # Actualizar tamaño descargado
        descargado_mb = tamano_descargado / 1024 / 1024
        self.descargado_label.config(text=f"Descarga: {descargado_mb:.2f} MB")

        # Calcular tiempo estimado restante
        if velocidad > 0:
            tiempo_restante = (tamano_total - tamano_descargado) / (velocidad * 1024 * 1024)
            self.tiempo_label.config(text=f"Tiempo estimado: {self.formato_tiempo(tiempo_restante)}")
        else:
            self.tiempo_label.config(text="Tiempo estimado: Calculando...")

    def formato_tiempo(self, segundos):
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos = int(segundos % 60)
        return f"{horas:02}:{minutos:02}:{segundos:02}"

    def actualizar_version(self, ruta_archivo):
        try:
            with open(ruta_archivo, "r") as archivo:
                lineas = archivo.readlines()
                version_remota = lineas[0].strip()
                if version_remota > self.version_local:
                    self.version_local = version_remota
                    self.guardar_version(version_remota)
                    self.urls = [lineas[i].strip() for i in range(2, 8)] + [lineas[10].strip()]  # Extraer los enlaces de las líneas 3 a 8 y la línea 11
                else:
                    print(f"La versión remota {version_remota} no es mayor que la versión local {self.version_local}.")
        except Exception as e:
            print(f"Error al leer el archivo de versión: {e}")

    def iniciar_descarga(self):
        print("Iniciando descarga")
        try:
            # Verificar la versión primero
            response = requests.get(self.url_version)
            print(self.url_version)
            response.raise_for_status()  # Lanza una excepción si la solicitud falló
            content = response.text.strip().split('\n')
            version_remota = content[0].strip()
            print(version_remota)
            # Validar si el usuario seleccionó una carpeta de destino
            if not self.carpeta_destino:  # Si carpeta_destino está vacía
                messagebox.showerror("Error", "Debes de elegir una carpeta destino antes de descargar")
                return  # Detener ejecución hasta que elija una carpeta

            # Validar si el usuario seleccionó una versión en el 
            if self.combobox.current() == -1:  # -1 indica que no se ha seleccionado ningún valor
                messagebox.showerror("Error", "Debes elegir una versión a instalar antes de descargar")
                return  # Detener ejecución hasta que elija una versión

            if version_remota == self.version_local:
                respuesta = messagebox.askyesno("Advertencia", "Ya tienes la última versión. ¿Deseas continuar con la descarga?")
                if respuesta:
                    print("Eliminando carpeta de mods...")
                    self.eliminar_carpeta_mods()
                    print("Carpeta mods eliminada. Continuando con el flujo.")
                    print("Configurando carpeta destino y estado de descarga...")
                    if not self.carpeta_destino:
                        self.carpeta_destino = "./descargas"  # Usar ./descargas si no se elige carpeta
                        print(f"Carpeta destino Iniciar_Descarga (FALLO) {self.carpeta_destino}")
                    if not os.path.exists(self.carpeta_destino):
                        os.makedirs(self.carpeta_destino)
                        print(f"Carpeta destino Iniciar_Descarga (FALLO) {self.carpeta_destino}")
                    
                    if not self.descargando:
                        self.descargando = True
                        self.pausado = False
                        self.comenzar_button.config(state=tk.DISABLED)
                        self.elegir_button.config(state=tk.DISABLED)
                        self.pausar_button.config(state=tk.NORMAL)
                        self.reanudar_button.config(state=tk.DISABLED)

                        # Buscar la línea que coincide con el valor del combobox
                        combobox_value = self.opcionesCB[self.combobox.current()]  # Obtener el valor seleccionado en el combobox
                        self.urls = []  # Limpiar la lista de URLs

                        # Encontrar la línea que contiene el valor seleccionado en el combobox
                        encontrado = False
                        for i, line in enumerate(content):
                            if combobox_value in line:  # Buscar la línea que contiene el valor del combobox
                                encontrado = True
                                # Extraer las URLs debajo de esa línea
                                for j in range(i + 1, len(content)):
                                    if content[j].startswith("http"):  # Si la línea es una URL
                                        self.urls.append(content[j])
                                    elif content[j].strip() == "":  # Si encontramos una línea en blanco, terminamos
                                        break
                                break  # Salir del bucle una vez que encontramos la versión

                        # Si no encontramos la versión seleccionada o las URLs
                        if not encontrado or not self.urls:
                            messagebox.showerror("Error", "No se encontraron URLs para descargar después de la versión seleccionada.")
                            return

                        # Iniciar el proceso de descarga
                        self.thread = threading.Thread(target=self.procesar_descargas)
                        self.thread.start()
                else:
                    messagebox.showinfo("Descarga cancelada", "La descarga ha sido cancelada.")
            elif version_remota > self.version_local:
                self.version_local = version_remota
                self.guardar_version(version_remota)

                self.eliminar_carpeta_mods()
                if not self.carpeta_destino:
                    self.carpeta_destino = "./descargas_Launcher"  # Usar ./descargas si no se elige carpeta
                if not os.path.exists(self.carpeta_destino):
                    os.makedirs(self.carpeta_destino)

                if not self.descargando:
                    self.descargando = True
                    self.pausado = False
                    self.comenzar_button.config(state=tk.DISABLED)
                    self.pausar_button.config(state=tk.NORMAL)
                    self.reanudar_button.config(state=tk.DISABLED)

                    # Buscar la línea que coincide con el valor del combobox
                    combobox_value = self.opcionesCB[self.combobox.current()]  # Obtener el valor seleccionado en el combobox
                    self.urls = []  # Limpiar la lista de URLs

                    # Encontrar la línea que contiene el valor seleccionado en el combobox
                    encontrado = False
                    for i, line in enumerate(content):
                        if combobox_value in line:  # Buscar la línea que contiene el valor del combobox
                            encontrado = True
                            # Extraer las URLs debajo de esa línea
                            for j in range(i + 1, len(content)):
                                if content[j].startswith("http"):  # Si la línea es una URL
                                    self.urls.append(content[j])
                                elif content[j].strip() == "":  # Si encontramos una línea en blanco, terminamos
                                    break
                            break  # Salir del bucle una vez que encontramos la versión

                    # Si no encontramos la versión seleccionada o las URLs
                    if not encontrado or not self.urls:
                        messagebox.showerror("Error", "No se encontraron URLs para descargar después de la versión seleccionada.")
                        return

                    # Iniciar el proceso de descarga
                    self.thread = threading.Thread(target=self.procesar_descargas)
                    self.thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar la versión: {e}")

    def procesar_descargas(self):
        self.descargando = True
        self.pausado = False

        # Definir rutas de destino
        ruta_mods =os.path.join(self.carpeta_destino, 'mods')
        print(f"Ruta Mods PROCESAR DESCARGA {ruta_mods}")
        ruta_minecraft = os.path.join(self.carpeta_destino)
        print(f"Ruta Minecraft PROCESAR DESCARGA {ruta_minecraft}")

        ##UH.. creo que esto lo borrare pero no estoy seguro
        if not os.path.exists(ruta_mods):
            os.makedirs(ruta_mods)
        if not os.path.exists(ruta_minecraft):
            os.makedirs(ruta_minecraft)

        # Descargar archivos a las rutas correspondientes
        for i, url in enumerate(self.urls):
            if i < 6:  # Índices 0 a 5 corresponden a líneas 3 a 8
                self.descargar_archivo(url, ruta_mods)
            elif i == 6:  # Índice 6 corresponde a la línea 11
                self.descargar_archivo(url, ruta_minecraft)

        # Descomprimir y eliminar archivos ZIP después de todas las descargas
        self.descomprimir_y_eliminar_archivos()
        self.descargando = False
        self.pausado = False


    def descomprimir_y_eliminar_archivos(self):
        print("Iniciando proceso para descomprimir")
        ruta_mods = os.path.join(self.carpeta_destino, 'mods')
        print(f"Descomprimir RUTA MODS {ruta_mods}")
        ruta_minecraft = os.path.join(self.carpeta_destino)
        print(f"Descomprimir RUTA MINECRAFT {ruta_mods}")

        for archivo_zip in self.zip_files:
            try:
                # Determinar la ruta de destino basada en el nombre del archivo ZIP
                nombre_archivo = os.path.basename(archivo_zip)
                if nombre_archivo in ["config.zip", "emotes.zip", "resourcepacks.zip"]:
                    destino = ruta_minecraft
                else:
                    destino = ruta_mods

                # Asegurarse de que la carpeta de destino exista (no se si borrarlo ya que no tiene sentido)
                if not os.path.exists(destino):
                    os.makedirs(destino)

                # Descomprimir el archivo ZIP en la carpeta de destino
                with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                    zip_ref.extractall(destino)  # Extraer todo el contenido
                    print(f"Descomprimiendo en {destino}")
                os.remove(archivo_zip)  # Eliminar el archivo ZIP
                self.status_label.config(text=f"Descomprimiendo {archivo_zip}...")
                print(f"Archivo {archivo_zip} descomprimido y eliminado en {destino}.")
            except Exception as e:
                print(f"Error al descomprimir el archivo {archivo_zip}: {e}")
        messagebox.showinfo("Completado", "¡Se completó de forma exitosa del Modpack!")
        self.status_label.config(text=f"¡Completado!")
        self.elegir_button.config(state=tk.NORMAL)

    def pausar_descarga(self):
        if self.descargando:
            self.pausado = True
            self.pausar_button.config(state=tk.DISABLED)
            self.reanudar_button.config(state=tk.NORMAL)

    def reanudar_descarga(self):
        if self.descargando and self.pausado:
            self.pausado = False
            self.pausar_button.config(state=tk.NORMAL)
            self.reanudar_button.config(state=tk.DISABLED)
    def cancelar_descarga(self):
        if self.descargando:
            self.descargando = False
            if self.thread and self.thread.is_alive():
                # Aquí puedes implementar la lógica para detener el hilo si es necesario
                pass
            self.comenzar_button.config(state=tk.NORMAL)
            self.elegir_button.config(state=tk.NORMAL)
            self.pausar_button.config(state=tk.DISABLED)
            self.reanudar_button.config(state=tk.DISABLED)
            messagebox.showinfo("Cancelado", "La descarga ha sido cancelada.")
# Crear la ventana raíz
root = tk.Tk()

# Crear la aplicación
app = LWLauncher(root)

# Ejecutar el bucle principal de Tkinter
root.mainloop()