import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera USB Viewer")

        self.selected_camera = tk.StringVar()
        self.selected_camera.set("usb0")  # Configuração padrão, pode ser alterada conforme necessário

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Dropdown para selecionar a câmera USB
        camera_label = ttk.Label(main_frame, text="Selecione a câmera USB:")
        camera_label.grid(row=0, column=0, pady=5, sticky=tk.W)

        camera_options = ["usb0", "usb1", "usb2", "usb3", "usb4", "usb5"]
        camera_dropdown = ttk.Combobox(main_frame, textvariable=self.selected_camera, values=camera_options)
        camera_dropdown.grid(row=0, column=1, pady=5, sticky=tk.W)

        # Botão para iniciar a visualização da câmera
        start_button = ttk.Button(main_frame, text="Iniciar Visualização", command=self.start_camera)
        start_button.grid(row=0, column=2, pady=5, padx=10, sticky=tk.W)

        # Label para exibir a imagem da câmera
        self.camera_label = ttk.Label(main_frame)
        self.camera_label.grid(row=1, column=0, columnspan=3)

    def start_camera(self):
        camera_index = int(self.selected_camera.get()[-1])  # Obtém o número da câmera a partir da seleção
        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            print(f"Erro ao abrir a câmera {camera_index}")
            return

        _, frame = cap.read()
        cap.release()

        # Converte a imagem de OpenCV para o formato Tkinter
