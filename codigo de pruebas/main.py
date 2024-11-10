import requests
import threading
import os
import time
import zipfile


class DownloaderApp:
    def __init__(self):
        self.inicializar_variables()

    def inicializar_variables(self):
        self.url_version = "https://raw.githubusercontent.com/Halosesparta13/LauncherVersion-TEST/main/Version.txt"
        self.carpeta_destino = None
        self.descargando = False
        self.pausado = False
        self.thread = None
        self.current_file = None
        self.urls = []  # Lista para almacenar URLs de archivos adicionales
        self.version_local = self.obtener_version_local()  # Obtener versión local al iniciar
        self.zip_files = []  # Lista para almacenar archivos ZIP descargados

    def obtener_version_local(self):
        version_archivo = "Version.txt"
        if os.path.exists(version_archivo):
            with open(version_archivo, "r") as archivo:
                return archivo.read().strip()
        else:
            with open(version_archivo, "w") as archivo:
                archivo.write("0.0.0\n")
            return "0.0.0"

    def guardar_version(self, version):
        version_archivo = "Version.txt"
        with open(version_archivo, "w") as archivo:
            archivo.write(f"{version}\n")  # Guardar solo la versión
        print(f"Versión actualizada a {version}")

    def elegir_ubicacion(self, ruta_predeterminada=None):
        # Si no se especifica ruta, usar "./descargas" por defecto
        if not ruta_predeterminada:
            ruta_predeterminada = os.path.join(os.getcwd(), 'descargas')  # Cambiar a ./descargas

        # Asignar la ruta de destino
        self.carpeta_destino = ruta_predeterminada

        # Comprobar si la carpeta ya existe
        if not os.path.exists(self.carpeta_destino):
            # Intentar crear la carpeta
            try:
                os.makedirs(self.carpeta_destino)
                print(f"La carpeta {self.carpeta_destino} ha sido creada.")
            except Exception as e:
                print(f"No se pudo crear la carpeta: {e}")
        else:
            print(f"La carpeta {self.carpeta_destino} ya existe.")

        return self.carpeta_destino  # Opcional: devuelve la ruta seleccionada

    def eliminar_carpeta_mods(self):
        ruta_mods = os.path.join(os.getenv('APPDATA'), '.minecraft', 'mods')

        if os.path.exists(ruta_mods):
            try:
                # Eliminar la carpeta y todo su contenido
                for root, dirs, files in os.walk(ruta_mods, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(ruta_mods)
                print("Carpeta 'mods' eliminada.")
            except Exception as e:
                print(f"Error al eliminar la carpeta 'mods': {e}")

    def descargar_archivo(self, url, destino):
        try:
            nombre_archivo = url.split("/")[-1].split("?")[0]
            ruta_archivo = os.path.join(destino, nombre_archivo)

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

        except Exception as e:
            print(f"Ocurrió un error al descargar el archivo: {e}")

        self.current_file = None

    def actualizar_progreso(self, tamano_descargado, tamano_total, inicio_tiempo):
        porcentaje_completado = (tamano_descargado / tamano_total) * 100
        print(f"Progreso: {porcentaje_completado:.2f}%")

        # Calcular la velocidad de descarga
        tiempo_transcurrido = time.time() - inicio_tiempo
        velocidad = tamano_descargado / 1024 / 1024 / max(tiempo_transcurrido, 1)  # MB/s
        print(f"Velocidad: {velocidad:.2f} MB/s")

        # Calcular tiempo estimado restante
        if velocidad > 0:
            tiempo_restante = (tamano_total - tamano_descargado) / (velocidad * 1024 * 1024)
            print(f"Tiempo estimado: {self.formato_tiempo(tiempo_restante)}")
        else:
            print("Tiempo estimado: Calculando...")

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
        try:
            # Verificar la versión primero
            response = requests.get(self.url_version)
            response.raise_for_status()  # Lanza una excepción si la solicitud falló
            content = response.text.strip().split('\n')
            version_remota = content[0].strip()

            if version_remota == self.version_local:
                print("Ya tienes la última versión.")
                self.eliminar_carpeta_mods()

                if not self.carpeta_destino:
                    self.carpeta_destino = "./descargas"
                if not os.path.exists(self.carpeta_destino):
                    os.makedirs(self.carpeta_destino)

                if not self.descargando:
                    self.descargando = True
                    self.pausado = False

                    # Extraer links desde las líneas 3 a 8 y línea 11
                    self.urls = content[2:8] + [content[10]]

                    self.thread = threading.Thread(target=self.procesar_descargas)
                    self.thread.start()
            elif version_remota > self.version_local:
                self.version_local = version_remota
                self.guardar_version(version_remota)

                self.eliminar_carpeta_mods()

                if not self.carpeta_destino:
                    self.carpeta_destino = "./descargas"
                if not os.path.exists(self.carpeta_destino):
                    os.makedirs(self.carpeta_destino)

                if not self.descargando:
                    self.descargando = True
                    self.pausado = False

                    # Extraer links desde las líneas 3 a 8 y línea 11
                    self.urls = content[2:8] + [content[10]]

                    self.thread = threading.Thread(target=self.procesar_descargas)
                    self.thread.start()

        except Exception as e:
            print(f"Error al verificar la versión: {e}")

    def procesar_descargas(self):
        self.descargando = True
        self.pausado = False

        # Definir rutas de destino
        ruta_mods = os.path.join(os.getenv('APPDATA'), '.minecraft', 'mods')
        ruta_minecraft = os.path.join(os.getenv('APPDATA'), '.minecraft')

        # Crear carpetas si no existen
        os.makedirs(ruta_mods, exist_ok=True)
        os.makedirs(ruta_minecraft, exist_ok=True)

        # Descargar archivos a las rutas correspondientes
        for i, url in enumerate(self.urls):
            if i < 6:  # Índices 0 a 5 corresponden a líneas 3 a 8
                self.descargar_archivo(url, ruta_mods)
            elif i == 6:  # Índice 6 corresponde a la línea 11
                self.descargar_archivo(url, ruta_minecraft)

        # Descomprimir y eliminar archivos ZIP después de todas las descargas
        self.descomprimir_y_eliminar_archivos()

    def descomprimir_y_eliminar_archivos(self):
        print("Iniciando proceso para descomprimir...")
        ruta_mods = os.path.join(os.getenv('APPDATA'), '.minecraft', 'mods')
        ruta_minecraft = os.path.join(os.getenv('APPDATA'), '.minecraft')

        for archivo_zip in self.zip_files:
            try:
                # Determinar la ruta de destino basada en el nombre del archivo ZIP
                nombre_archivo = os.path.basename(archivo_zip)
                if nombre_archivo in ["config.zip", "emotes.zip", "resourcepacks.zip"]:
                    destino = ruta_minecraft
                else:
                    destino = ruta_mods

                # Asegurarse de que la carpeta de destino exista
                if not os.path.exists(destino):
                    os.makedirs(destino)

                # Descomprimir el archivo ZIP en la carpeta de destino
                with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                    zip_ref.extractall(destino)  # Extraer todo el contenido
                os.remove(archivo_zip)  # Eliminar el archivo ZIP
                print(f"Archivo {archivo_zip} descomprimido y eliminado en {destino}.")
            
            except zipfile.BadZipFile:
                print(f"Error: El archivo {archivo_zip} no es un archivo ZIP válido.")
            except Exception as e:
                print(f"Error al descomprimir el archivo {archivo_zip}: {e}")

        print("Proceso de descompresión completado.")
        # Actualizar la interfaz gráfica si es necesario
        # self.status_label.config(text="¡Descompresión completada!")
        # messagebox.showinfo("Completado", "¡Se completó de forma exitosa el Modpack!")
