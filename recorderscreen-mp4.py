import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# Inicializar variáveis globais
recording = False
paused = False
out = None

def select_window():
    windows = gw.getAllTitles()
    selected_window = selected_window_var.get()
    if selected_window in windows:
        return gw.getWindowsWithTitle(selected_window)[0]
    else:
        return None

def record_screen():
    global recording, paused, out
    selected_window = select_window()
    if not selected_window:
        messagebox.showerror("Erro", "Janela não encontrada!")
        return

    recording = True
    paused = False

    # Configurações do vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (selected_window.width, selected_window.height))

    while recording:
        if not paused:
            img = pyautogui.screenshot(region=(selected_window.left, selected_window.top, selected_window.width, selected_window.height))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            out.write(frame)

def start_recording():
    threading.Thread(target=record_screen).start()

def pause_recording():
    global paused
    paused = not paused
    pause_button.config(text="Pausar" if not paused else "Continuar")

def stop_recording():
    global recording, out
    recording = False
    if out:
        out.release()
    out = None
    messagebox.showinfo("Informação", "Gravação finalizada e salva como output.mp4")

def on_closing():
    global recording
    if recording:
        messagebox.showwarning("Aviso", "Pare a gravação antes de sair.")
    else:
        root.destroy()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gravador de Tela")

selected_window_var = tk.StringVar()

windows = gw.getAllTitles()
window_label = tk.Label(root, text="Selecione a janela para gravar:")
window_label.pack(pady=5)
window_menu = ttk.Combobox(root, textvariable=selected_window_var)
window_menu['values'] = windows
window_menu.pack(pady=5)

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
