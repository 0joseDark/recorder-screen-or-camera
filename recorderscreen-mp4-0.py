import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Variáveis globais para controle de gravação e arquivo de saída
recording = False
paused = False
out = None
file_path = None

def select_window():
    """
    Seleciona a janela com base no título escolhido pelo usuário.
    """
    windows = gw.getAllTitles()
    selected_window = selected_window_var.get()
    if selected_window in windows:
        return gw.getWindowsWithTitle(selected_window)[0]
    else:
        return None

def record_screen():
    """
    Função de gravação da tela da janela selecionada.
    """
    global recording, paused, out, file_path
    selected_window = select_window()
    if not selected_window:
        messagebox.showerror("Erro", "Janela não encontrada!")
        return

    recording = True
    paused = False

    # Configurações do vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(file_path, fourcc, 20.0, (selected_window.width, selected_window.height))

    while recording:
        if not paused:
            img = pyautogui.screenshot(region=(selected_window.left, selected_window.top, selected_window.width, selected_window.height))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            out.write(frame)

def start_recording():
    """
    Inicia a gravação em uma thread separada.
    """
    if not file_path:
        messagebox.showerror("Erro", "Selecione o caminho e nome do arquivo primeiro!")
        return
    threading.Thread(target=record_screen).start()

def pause_recording():
    """
    Pausa ou retoma a gravação.
    """
    global paused
    paused = not paused
    pause_button.config(text="Pausar" if not paused else "Continuar")

def stop_recording():
    """
    Para a gravação e salva o arquivo.
    """
    global recording, out
    recording = False
    if out:
        out.release()
    out = None
    messagebox.showinfo("Informação", f"Gravação finalizada e salva como {file_path}")

def on_closing():
    """
    Trata o fechamento da aplicação, garantindo que a gravação seja parada.
    """
    global recording
    if recording:
        messagebox.showwarning("Aviso", "Pare a gravação antes de sair.")
    else:
        root.destroy()

def select_file_path():
    """
    Abre um diálogo para selecionar o caminho e o nome do arquivo MP4.
    """
    global file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    file_path_label.config(text=file_path if file_path else "Nenhum arquivo selecionado")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gravador de Tela")

selected_window_var = tk.StringVar()

# Menu de seleção de janela
windows = gw.getAllTitles()
window_label = tk.Label(root, text="Selecione a janela para gravar:")
window_label.pack(pady=5)
window_menu = ttk.Combobox(root, textvariable=selected_window_var)
window_menu['values'] = windows
window_menu.pack(pady=5)

# Botão para selecionar o caminho do arquivo
file_button = tk.Button(root, text="Selecionar Caminho e Nome do Arquivo", command=select_file_path)
file_button.pack(pady=5)

# Label para mostrar o caminho do arquivo selecionado
file_path_label = tk.Label(root, text="Nenhum arquivo selecionado")
file_path_label.pack(pady=5)

# Botões de controle de gravação
start_button = tk.Button(root, text="Gravar", command=start_recording)
start_button.pack(pady=5)

pause_button = tk.Button(root, text="Pausar", command=pause_recording)
pause_button.pack(pady=5)

stop_button = tk.Button(root, text="Parar", command=stop_recording)
stop_button.pack(pady=5)

exit_button = tk.Button(root, text="Sair", command=on_closing)
exit_button.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
