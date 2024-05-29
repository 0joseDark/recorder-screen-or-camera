# pip install opencv-python-headless pillow
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import threading
import os
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera App")

        self.is_running = False
        self.is_paused = False
        self.capture = None
        self.output_file = ""
        self.fps = 30  # Aumentar FPS aqui

        self.create_widgets()

    def create_widgets(self):
        self.port_label = ttk.Label(self.root, text="Escolha a Porta USB:")
        self.port_label.pack(pady=5)

        self.port_combobox = ttk.Combobox(self.root, values=["0", "1", "2"])
        self.port_combobox.pack(pady=5)

        self.output_button = ttk.Button(self.root, text="Escolher Caminho e Ficheiro para Gravar", command=self.select_output_file)
        self.output_button.pack(pady=5)

        self.start_button = ttk.Button(self.root, text="Ligar", command=self.start_camera)
        self.start_button.pack(pady=5)

        self.pause_button = ttk.Button(self.root, text="Pausar", command=self.pause_camera)
        self.pause_button.pack(pady=5)

        self.stop_button = ttk.Button(self.root, text="Desligar", command=self.stop_camera)
        self.stop_button.pack(pady=5)

        self.video_label = ttk.Label(self.root)
        self.video_label.pack()

        self.exit_button = ttk.Button(self.root, text="Sair", command=self.exit_app)
        self.exit_button.pack(pady=5)

    def select_output_file(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension=".avi",
                                                        filetypes=[("AVI files", "*.avi")])
        if self.output_file:
            messagebox.showinfo("Ficheiro Selecionado", f"Ficheiro selecionado: {self.output_file}")

    def start_camera(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "A câmera já está em execução.")
            return

        port = self.port_combobox.get()
        if not port.isdigit():
            messagebox.showerror("Erro", "Por favor, selecione uma porta USB válida.")
            return

        self.capture = cv2.VideoCapture(int(port))
        if not self.capture.isOpened():
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
            return

        # Configurar FPS da câmera
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)

        self.is_running = True
        self.is_paused = False
        threading.Thread(target=self.update_frame).start()

    def pause_camera(self):
        if not self.is_running:
            messagebox.showwarning("Aviso", "A câmera não está em execução.")
            return

        self.is_paused = not self.is_paused
        state = "Pausado" if self.is_paused else "Retomado"
        messagebox.showinfo("Estado da Câmera", f"A câmera foi {state}.")

    def stop_camera(self):
        if self.is_running:
            self.is_running = False
            if self.capture:
                self.capture.release()
            self.video_label.config(image='')
            cv2.destroyAllWindows()

    def update_frame(self):
        if self.output_file:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(self.output_file, fourcc, self.fps, (frame_width, frame_height))
        else:
            out = None

        while self.is_running:
            if not self.is_paused:
                ret, frame = self.capture.read()
                if ret:
                    if out:
                        out.write(frame)
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                else:
                    messagebox.showerror("Erro", "Não foi possível ler a imagem da câmera.")
                    self.stop_camera()
                    break
        if out:
            out.release()

    def exit_app(self):
        self.stop_camera()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
