# pip install pygetwindow pyautogui opencv-python numpy

import tkinter as tk  # Importa o módulo tkinter para criar a interface gráfica do usuário (GUI).
from tkinter import filedialog, messagebox  # Importa componentes específicos do tkinter para diálogos de arquivos e mensagens.
import pygetwindow as gw  # Importa pygetwindow para obter informações sobre as janelas abertas no sistema.
import pyautogui  # Importa pyautogui para capturar screenshots da tela.
import cv2  # Importa OpenCV para manipulação de vídeo.
import numpy as np  # Importa numpy para manipulação de arrays.
import threading  # Importa threading para executar gravação de vídeo em um thread separado.

# Classe principal que define o gravador de tela.
class ScreenRecorder:
    def __init__(self, root):
        # Inicializa a janela principal do aplicativo.
        self.root = root
        self.root.title("Screen Recorder")

        # Cria e posiciona os componentes da GUI.
        self.label = tk.Label(root, text="Escolha a janela para gravar:")
        self.label.pack(pady=10)

        self.window_listbox = tk.Listbox(root)
        self.window_listbox.pack(pady=10)

        self.refresh_button = tk.Button(root, text="Atualizar Janelas", command=self.refresh_windows)
        self.refresh_button.pack(pady=5)

        self.select_file_button = tk.Button(root, text="Escolher Local e Nome do Arquivo", command=self.select_file)
        self.select_file_button.pack(pady=5)

        self.record_button = tk.Button(root, text="Gravar", command=self.start_recording)
        self.record_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Parar Gravação", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="Sair", command=root.quit)
        self.exit_button.pack(pady=5)

        # Inicializa variáveis importantes.
        self.file_path = ""  # Caminho do arquivo onde o vídeo será salvo.
        self.recording = False  # Estado de gravação.

        self.windows = []  # Lista de janelas disponíveis.
        self.refresh_windows()  # Atualiza a lista de janelas no início.

    # Atualiza a lista de janelas abertas no sistema.
    def refresh_windows(self):
        self.window_listbox.delete(0, tk.END)  # Limpa a listbox.
        self.windows = gw.getWindowsWithTitle('')  # Obtém todas as janelas abertas.
        for window in self.windows:
            self.window_listbox.insert(tk.END, window.title)  # Adiciona o título de cada janela à listbox.

    # Abre um diálogo para selecionar o local e o nome do arquivo de gravação.
    def select_file(self):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("Video files", "*.avi")])
        if self.file_path:
            messagebox.showinfo("Info", f"Arquivo selecionado: {self.file_path}")  # Exibe uma mensagem informando o arquivo selecionado.

    # Inicia a gravação de vídeo.
    def start_recording(self):
        selected_index = self.window_listbox.curselection()  # Obtém a janela selecionada.
        if not selected_index:
            messagebox.showwarning("Aviso", "Por favor, selecione uma janela para gravar.")  # Exibe um aviso se nenhuma janela for selecionada.
            return
        if not self.file_path:
            messagebox.showwarning("Aviso", "Por favor, selecione o local e nome do arquivo.")  # Exibe um aviso se o caminho do arquivo não for definido.
            return

        # Desabilita botões e inicia a gravação.
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.DISABLED)

        selected_window = self.windows[selected_index[0]]  # Obtém a janela selecionada.
        window_box = selected_window.box  # Obtém as coordenadas da janela.

        self.recording = True
        threading.Thread(target=self.record_video, args=(window_box, self.file_path)).start()  # Inicia a gravação em um thread separado.

    # Para a gravação de vídeo.
    def stop_recording(self):
        self.recording = False  # Define o estado de gravação como falso.
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.NORMAL)

    # Grava o vídeo da janela selecionada.
    def record_video(self, window_box, file_path):
        x, y, w, h = window_box  # Descompacta as coordenadas da janela.
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Define o codec de vídeo.
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (w, h))  # Cria o objeto VideoWriter.

        try:
            while self.recording:
                img = pyautogui.screenshot(region=(x, y, w, h))  # Captura uma screenshot da janela.
                frame = np.array(img)  # Converte a imagem para um array numpy.
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte a imagem para o formato correto.
                out.write(frame)  # Escreve o frame no arquivo de vídeo.
        finally:
            out.release()  # Libera o objeto VideoWriter.
            messagebox.showinfo("Info", "Gravação finalizada.")  # Exibe uma mensagem informando que a gravação foi finalizada.

# Cria a janela principal e inicia o aplicativo.
if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
