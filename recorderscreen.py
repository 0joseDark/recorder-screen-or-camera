# pip install tkinter pygetwindow pyautogui opencv-python

import tkinter as tk
from tkinter import filedialog, simpledialog
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")

        self.label = tk.Label(root, text="Escolha a janela para gravar:")
        self.label.pack(pady=10)

        self.window_listbox = tk.Listbox(root)
        self.window_listbox.pack(pady=10)

        self.refresh_button = tk.Button(root, text="Atualizar Janelas", command=self.refresh_windows)
        self.refresh_button.pack(pady=5)

        self.record_button = tk.Button(root, text="Gravar", command=self.start_recording)
        self.record_button.pack(pady=20)

        self.windows = []

        self.refresh_windows()

    def refresh_windows(self):
        self.window_listbox.delete(0, tk.END)
        self.windows = gw.getWindowsWithTitle('')
        for window in self.windows:
            self.window_listbox.insert(tk.END, window.title)

    def start_recording(self):
        selected_index = self.window_listbox.curselection()
        if not selected_index:
            tk.messagebox.showwarning("Aviso", "Por favor, selecione uma janela para gravar.")
            return

        selected_window = self.windows[selected_index[0]]
        window_box = selected_window.box

        file_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("Video files", "*.avi")])
        if not file_path:
            return

        self.record_video(window_box, file_path)

    def record_video(self, window_box, file_path):
        x, y, w, h = window_box
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (w, h))

        try:
            while True:
                img = pyautogui.screenshot(region=(x, y, w, h))
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            out.release()
            cv2.destroyAllWindows()
            tk.messagebox.showinfo("Info", "Gravação finalizada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
