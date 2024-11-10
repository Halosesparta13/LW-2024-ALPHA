from flet import *
import flet
import os

WidthB = 980
HeightB = 650

def deshabilitar_botones(page):
    # Deshabilitar los botones específicos
    page.boton_start.disabled = True
    page.boton_pausar.disabled = True
    page.boton_cancelar.disabled = True
    page.update()  # Se debe actualizar la interfaz para reflejar los cambios

# Función principal
def main(page: Page):
    page.horizontal_alignment = "center"
    page.title = "Lucky World Launcher (BETA)"
    page.window_width = WidthB
    page.window_height = HeightB
    page.window_max_width = WidthB
    page.window_max_height = HeightB
    page.window_resizable = False
    page.padding = 0

    # Función para manejar la selección de carpeta
    def folder_picked(e):
        if e.path:
            # Mostrar la ruta seleccionada
            location_text.value = f"Ubicación seleccionada: {e.path}"
            location_text.update()
            print(location_text.value)
        else:
            # Mostrar que no se ha seleccionado una carpeta
            location_text.value = "No se seleccionó ninguna ubicación."
            location_text.update()

    # Contenedor principal de la aplicación
    body = Container(
        Stack([
            # BACKGROUND IMAGE
            Image(
                "assets/background_1.png",
                width=WidthB,  # Puede ser también 1200 px
                height=HeightB,
                top=0,
                fit=ImageFit.COVER
            ),
            # logo
            Image(
                "assets/logo.png",
                height=160,
                left=150,
                top=150
            ),
            # contenedor-azul
            Container(
                bgcolor="blue",
                height=150,  # 170
                width=980,
                top=465,  # Posición calculada para estar en la parte inferior
            ),
            # Agrupación para el Combobox y elegir botón
            Row([
                # Dropdown
                Dropdown(
                    options=[
                        dropdown.Option("1.18   - Server Oficial"),
                        dropdown.Option("1.20.2 - Server Oficial"),
                        dropdown.Option("1.20.2 - ElseWorlds"),
                    ],
                    width=200,
                    height=60,
                    value="1.18   - Server Oficial",
                ),
                # Botón elegir ubicación
                Container(
                    bgcolor="red",
                    height=60,
                    width=150,
                    content=Text("Elegir Ubicación", size=14, weight=FontWeight.BOLD),
                    margin=5,
                    padding=10,
                    alignment=alignment.center,
                    border_radius=10,
                    #ink=True,
                    on_click=lambda e: folder_picker.get_directory_path()  # Abre el selector de carpetas
                )
            ],
                alignment=MainAxisAlignment.CENTER,
                top=535,
                right=70,
            ),

            # Barra de progreso
            Container(
                ProgressBar(
                    value=0.5,
                    color="#ffc936",
                ),  # Aquí puedes iniciar el progreso en 50%
                height=30,
                width=400,
                border_radius=10,
                top=505,  # Ajuste la posición vertical según el diseño
                left=10,
            ),
            Row([
                Container(
                    content=Text("Estado", size=15, color="white", weight=FontWeight.BOLD),
                    margin=10,
                ),
                Container(
                    content=Text("--", size=15, color="white", weight=FontWeight.BOLD),
                    margin=10,
                )
            ],
                alignment=MainAxisAlignment.START,
                top=470,  # Ajuste la posición vertical según el diseño
                left=5,
            ),

            # Etiquetas debajo de la barra de progreso
            Column([
                Row([
                    Text("Descarga:", size=15, color="white", weight=FontWeight.BOLD),
                    Text("0%", size=15, color="white"),  # Cambia el valor según sea necesario
                    Text("Velocidad:", size=15, color="white", weight=FontWeight.BOLD),
                    Text("0 KB/s", size=15, color="white"),  # Cambia el valor según sea necesario
                ],
                    alignment=MainAxisAlignment.START,
                ),
                Row([

                    Text("Tiempo Restante:", size=15, color="white", weight=FontWeight.BOLD),
                    Text("00:00:00", size=15, color="white"),  # Cambia el valor según sea necesario
                ],
                    alignment=MainAxisAlignment.START,
                ),
            ],
                alignment=MainAxisAlignment.CENTER,
                top=545,  # Ajuste la posición vertical según el diseño
                left=10,
            ),
            # Agrupación de botones en un Row
            Row([
                # Botón START
                Container(
                    bgcolor="red",
                    height=60,
                    width=150,
                    content=Text("START", size=14, weight=FontWeight.BOLD),
                    margin=5,
                    padding=10,
                    alignment=alignment.center,
                    border_radius=10,
                    ink=True,
                ),
                # Botón PAUSAR
                Container(
                    bgcolor="red",
                    height=60,
                    width=150,
                    content=Text("PAUSAR", size=14, weight=FontWeight.BOLD),
                    margin=5,
                    padding=10,
                    alignment=alignment.center,
                    border_radius=10,
                    ink=True,
                ),

                # Botón CANCELAR
                Container(
                    bgcolor="red",
                    height=60,
                    width=150,
                    content=Text("CANCELAR", size=14, weight=FontWeight.BOLD),
                    margin=5,
                    padding=10,
                    alignment=alignment.center,
                    border_radius=10,
                    ink=True,
                ),
            ],
                alignment=MainAxisAlignment.END,  # Alineación a la derecha
                top=470,  # Posición del Row en la pantalla
                right=10,
            ),

            # descripción
            Container(
                height=100,
                width=450,
                # content=Text(
                #    "¡Este es el launcher de Luckyworld! Aquí se actualizará a tiempo real los archivos de los Mods y RS",
                #    size=18, font_family="Minecraft", text_align="center"),
                margin=10,
                padding=10,
                alignment=alignment.center,
                border_radius=10,
                top=350,
                ink=False,
                left=250,
            ),
            Row([
                Text(
                    "Version Beta 0.1.8 ",
                    color="white",
                    size=25,
                    weight="bold",
                    opacity=0.5,
                ),
            ],
                alignment=MainAxisAlignment.END,
            ),
        ]),
        width=WidthB,
        height=HeightB
    )

    # Texto para mostrar la ubicación seleccionada
    location_text = Text("No se ha seleccionado ubicación.", size=15, color="white")

    # Agregar el contenedor de texto al body
    body.content.controls.append(
        Row([location_text], alignment=MainAxisAlignment.CENTER, top=600)
    )

    # FilePicker para seleccionar la carpeta
    folder_picker = FilePicker(on_result=folder_picked)
    page.overlay.append(folder_picker)

    # Agregar todo el cuerpo a la página
    page.add(body)


flet.app(target=main)
