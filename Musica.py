import pygame
from pygame import mixer
import PySimpleGUI as sg
from threading import Thread
import os

class Reproductor:
    def __init__(self):
        sg.LOOK_AND_FEEL_TABLE['ModernPurple'] = {
            'BACKGROUND': '#2D1B36',
            'TEXT': '#FFFFFF',
            'INPUT': '#4B2C5E',
            'TEXT_INPUT': '#FFFFFF',
            'SCROLL': '#4B2C5E',
            'BUTTON': ('#FFFFFF', '#6A359C'), 
            'PROGRESS': ('#D187FF', '#4B2C5E'),
            'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
        }
        sg.theme('ModernPurple')

        # Fuentes
        font_main = ("Segoe UI", 12)
        font_title = ("Segoe UI Bold", 13)
        
        logo_path = os.path.join(os.path.dirname(__file__), "logop.png")

        layout = [
            [
                sg.Push(),
                sg.Button("📁 Carpeta", key="carpeta", font=font_main, border_width=0, mouseover_colors=('#FFFFFF', '#8A4FFF')),
                sg.Button("🎵 Canción", key="cancion", font=font_main, border_width=0, mouseover_colors=('#FFFFFF', '#8A4FFF')),
                sg.Push()
            ],

            [sg.VPush()],

            [sg.Push(), sg.Image(filename=logo_path, background_color='#2D1B36'), sg.Push()],

            [sg.VPush()],

            [sg.Text("Ninguna canción", key="name",
                     justification="center", size=(40, 1), 
                     font=font_title, text_color='#D187FF')],

            [sg.VPush()],

            [
                sg.Push(),
                sg.Button("⏮", key="anterior", size=(5, 1), font=("Segoe UI", 18), border_width=0),
                sg.Button("⏸", key="pausa", size=(5, 1), font=("Segoe UI", 18), border_width=0, button_color=('#FFFFFF', '#8A4FFF')),
                sg.Button("⏭", key="siguiente", size=(5, 1), font=("Segoe UI", 18), border_width=0),
                sg.Push()
            ],

            [sg.VPush()],

            # Control de Volumen 
            [
                sg.Push(),
                sg.Text("󠃁󠃁󠃁󠃁󠃁🔊", font=font_main),
                sg.Slider(
                    range=(0, 100),
                    default_value=70,
                    orientation="h",
                    size=(25, 12),
                    key="volumen",
                    enable_events=True,
                    disable_number_display=True,
                    background_color='#4B2C5E',
                    trough_color='#D187FF'
                ),
                sg.Push()
            ],
            [sg.VPush()],
        ]

        self.window = sg.Window(
            "Reproductor de Música",
            layout,
            size=(450, 600), # Tamaño fijo
            element_justification="center",
            finalize=True,
            margins=(20, 20)
        )

        self.boton_pausa = self.window["pausa"]
        self.nombre_cancion = self.window["name"]

        self.ruta = ""
        self.canciones = []
        self.posicion = 0
        self.estado = False
        self.pausa = False

        mixer.init()
        mixer.music.set_volume(0.7)

  
    def reproducir(self, ruta):
        try:
            mixer.music.load(ruta)
            mixer.music.play()
            self.estado = True
        except pygame.error:
            sg.popup("No se pudo reproducir la canción")

    def reproducir_hilo(self, ruta):
        Thread(target=self.reproducir, args=(ruta,), daemon=True).start()

    def cargar_actual(self):
        ruta_completa = os.path.join(self.ruta, self.canciones[self.posicion])
        self.nombre_cancion.update(self.canciones[self.posicion])
        mixer.music.stop()
        self.reproducir_hilo(ruta_completa)

    def siguiente(self):
        if self.canciones:
            self.posicion = (self.posicion + 1) % len(self.canciones)
            self.cargar_actual()

    def anterior(self):
        if self.canciones:
            self.posicion = (self.posicion - 1) % len(self.canciones)
            self.cargar_actual()

    def pausar(self):
        if not self.estado:
            return
        if not self.pausa:
            mixer.music.pause()
            self.boton_pausa.update("▶")
            self.pausa = True
        else:
            mixer.music.unpause()
            self.boton_pausa.update("⏸")
            self.pausa = False

    def iniciar(self):
        while True:
            event, values = self.window.read(timeout=100)
            if event in (sg.WINDOW_CLOSED, None):
                break
            elif event == "carpeta":
                carpeta = sg.popup_get_folder("Selecciona una carpeta")
                if carpeta:
                    self.ruta = carpeta
                    self.canciones = [f for f in os.listdir(carpeta) if f.lower().endswith(".mp3")]
                    self.posicion = 0
                    if self.canciones: self.cargar_actual()
                    else: sg.popup("No se encontraron MP3")
            elif event == "cancion":
                archivo = sg.popup_get_file("Selecciona una canción", file_types=(("MP3 Files", "*.mp3"),))
                if archivo:
                    self.nombre_cancion.update(os.path.basename(archivo))
                    mixer.music.stop()
                    self.reproducir_hilo(archivo)
            elif event == "siguiente": self.siguiente()
            elif event == "anterior": self.anterior()
            elif event == "pausa": self.pausar()
            elif event == "volumen": mixer.music.set_volume(values["volumen"] / 100)

        mixer.music.stop()
        self.window.close()

if __name__ == "__main__":
    app = Reproductor()
    app.iniciar()