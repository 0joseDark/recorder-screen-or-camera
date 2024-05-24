# convert_video_to_images
import cv2
import os
from tkinter import Tk, filedialog, simpledialog

def select_file():
    # Cria uma janela de seleção de arquivos
    root = Tk()
    root.withdraw()  # Esconde a janela principal
    file_path = filedialog.askopenfilename(title="Selecione o arquivo AVI", filetypes=[("AVI files", "*.avi")])
    return file_path

def select_directory():
    # Cria uma janela de seleção de diretório
    root = Tk()
    root.withdraw()  # Esconde a janela principal
    directory = filedialog.askdirectory(title="Selecione o diretório para salvar as imagens")
    return directory

def convert_video_to_images(video_path, output_folder):
    # Captura o vídeo
    cap = cv2.VideoCapture(video_path)
    count = 0

    # Verifica se o vídeo foi aberto com sucesso
    if not cap.isOpened():
        print(f"Erro ao abrir o vídeo {video_path}")
        return

    # Loop pelos frames do vídeo
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Salva cada frame como uma imagem
        frame_filename = os.path.join(output_folder, f"frame_{count:04d}.png")
        cv2.imwrite(frame_filename, frame)
        count += 1

    # Libera o objeto de captura de vídeo
    cap.release()
    print(f"Extração concluída. {count} frames foram salvos em {output_folder}")

if __name__ == "__main__":
    # Seleciona o arquivo AVI
    video_path = select_file()
    if not video_path:
        print("Nenhum arquivo AVI selecionado.")
        exit()

    # Seleciona o diretório de saída
    output_folder = select_directory()
    if not output_folder:
        print("Nenhum diretório selecionado.")
        exit()

    # Converte o vídeo em imagens
    convert_video_to_images(video_path, output_folder)
