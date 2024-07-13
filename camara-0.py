import tkinter as tk
from tkinter import filedialog
import cv2
import threading

# Define a classe principal para o aplicativo da câmera
class CameraApp:
    def __init__(self, master):
        # Configuração inicial da janela principal
        self.master = master
        self.master.title("Camera App")
        self.master.geometry("640x640")

        # Inicializa a fonte de vídeo (0 para a câmera padrão do sistema)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        self.ret = False
        self.frame = None

        # Cria um canvas para exibir os frames do vídeo
        self.canvas = tk.Canvas(self.master, width=640, height=480)
        self.canvas.pack()

        # Botões de controle da aplicação
        self.btn_start = tk.Button(self.master, text="Ligar Câmera", width=15, command=self.start_camera)
        self.btn_start.pack(anchor=tk.CENTER, expand=True)

        self.btn_pause = tk.Button(self.master, text="Pausar", width=15, command=self.pause_camera)
        self.btn_pause.pack(anchor=tk.CENTER, expand=True)

        self.btn_record = tk.Button(self.master, text="Gravar", width=15, command=self.record_video)
        self.btn_record.pack(anchor=tk.CENTER, expand=True)

        self.btn_quit = tk.Button(self.master, text="Sair", width=15, command=self.master.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        self.btn_save = tk.Button(self.master, text="Escolher Caminho", width=15, command=self.choose_save_path)
        self.btn_save.pack(anchor=tk.CENTER, expand=True)

        # Variáveis de estado
        self.recording = False
        self.out = None
        self.save_path = None

        # Chama o método update para atualizar os frames continuamente
        self.update()

    def choose_save_path(self):
        # Abre uma caixa de diálogo para escolher o caminho do arquivo a ser salvo
        self.save_path = filedialog.asksaveasfilename(defaultextension=".avi",
                                                      filetypes=[("AVI files", "*.avi"), ("All files", "*.*")])
        print(f"Save path set to: {self.save_path}")

    def start_camera(self):
        # Inicia a captura de vídeo se não estiver ativa
        if not self.ret:
            self.vid = cv2.VideoCapture(self.video_source)
            self.ret = True
        self.recording = False

    def pause_camera(self):
        # Pausa a captura de vídeo e libera a câmera
        if self.ret:
            self.ret = False
            self.vid.release()

    def record_video(self):
        # Inicia a gravação do vídeo se um caminho de arquivo foi escolhido
        if self.ret:
            if self.save_path:
                self.recording = True
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter(self.save_path, fourcc, 20.0, (640, 480))
            else:
                print("Escolha um caminho para salvar o vídeo primeiro.")

    def update(self):
        # Atualiza o frame do vídeo no canvas
        if self.ret:
            ret, frame = self.vid.read()
            if ret:
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo = self.cv2_to_tkinter(self.frame)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

                # Grava o frame se a gravação estiver ativa
                if self.recording:
                    self.out.write(frame)

        # Chama a função update novamente após 10ms
        self.master.after(10, self.update)

    def cv2_to_tkinter(self, frame):
        # Converte um frame OpenCV para um formato exibível no tkinter
        frame = cv2.resize(frame, (640, 480))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.imencode(".png", img)[1].tobytes()
        return tk.PhotoImage(data=img)

    def __del__(self):
        # Libera os recursos quando o objeto é destruído
        if self.vid.isOpened():
            self.vid.release()
        if self.recording:
            self.out.release()

# Executa o aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
