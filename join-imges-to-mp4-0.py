import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import os
from threading import Thread, Event

# Função para selecionar a pasta de imagens
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

# Função para juntar as imagens em um vídeo
def create_video():
    global pause_event, stop_event
    pause_event.clear()
    stop_event.clear()

    folder_path = folder_entry.get()
    if not folder_path:
        messagebox.showerror("Erro", "Por favor, selecione uma pasta.")
        return

    images = [img for img in os.listdir(folder_path) if img.endswith(".jpg") or img.endswith(".png")]
    if not images:
        messagebox.showerror("Erro", "A pasta não contém imagens válidas.")
        return

    images.sort()  # Ordenar as imagens pelo nome do arquivo
    frame = cv2.imread(os.path.join(folder_path, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1, (width, height))

    progress_bar['maximum'] = len(images)
    for i, image in enumerate(images):
        while pause_event.is_set():
            if stop_event.is_set():
                video.release()
                return
        if stop_event.is_set():
            video.release()
            return
        
        img_path = os.path.join(folder_path, image)
        frame = cv2.imread(img_path)
        video.write(frame)

        progress_bar['value'] = i + 1
        root.update_idletasks()

    video.release()
    messagebox.showinfo("Sucesso", "Vídeo criado com sucesso!")

# Função para pausar o processo
def pause_video():
    if pause_event.is_set():
        pause_event.clear()
        pause_button.config(text="Pausar")
    else:
        pause_event.set()
        pause_button.config(text="Continuar")

# Função para parar o processo
def stop_video():
    stop_event.set()
    root.quit()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Criador de Vídeo")

tk.Label(root, text="Selecione a pasta de imagens:").pack(pady=10)

folder_entry = tk.Entry(root, width=50)
folder_entry.pack(pady=5)

browse_button = tk.Button(root, text="Procurar", command=select_folder)
browse_button.pack(pady=5)

start_button = tk.Button(root, text="Juntar", command=lambda: Thread(target=create_video).start())
start_button.pack(pady=10)

pause_event = Event()
stop_event = Event()

pause_button = tk.Button(root, text="Pausar", command=pause_video)
pause_button.pack(pady=5)

stop_button = tk.Button(root, text="Sair", command=stop_video)
stop_button.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
