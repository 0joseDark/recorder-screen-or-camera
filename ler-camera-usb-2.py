import cv2
import tkinter as tk

# Variáveis globais
camera_on = False
recording = False
image_counter = 0

# Função para capturar a imagem da câmera
def capturar_imagem():
    global camera_on, image_counter

    if camera_on:
        # Ler imagem da câmera
        ret, frame = cap.read()

        # Exibir imagem na janela
        cv2.imshow("Câmera", frame)

        # Se gravando, salvar imagem
        if recording:
            image_counter += 1
            cv2.imwrite(f"imagem_{image_counter}.png", frame)

        # Chamar a função novamente após 30ms
        window.after(30, capturar_imagem)

# Função para ligar/desligar a câmera
def ligar_desligar_camera():
    global camera_on

    if camera_on:
        # Desligar a câmera
        cap.release()
        cv2.destroyAllWindows()
        camera_on = False
        botao_ligar_desligar["text"] = "Ligar Câmera"
    else:
        # Ligar a câmera
        cap = cv2.VideoCapture(0)
        camera_on = True
        botao_ligar_desligar["text"] = "Desligar Câmera"
        capturar_imagem()

# Função para iniciar/parar a gravação
def iniciar_parar_gravacao():
    global recording

    if recording:
        recording = False
        botao_gravar["text"] = "Iniciar Gravação"
    else:
        recording = True
        botao_gravar["text"] = "Parar Gravação"

# Criar janela
window = tk.Tk()
window.title("Câmera")

# Criar botões
botao_ligar_desligar = tk.Button(
    text="Ligar Câmera", command=ligar_desligar_camera
)
botao_ligar_desligar.pack()

botao_gravar = tk.Button(
    text="Iniciar Gravação", command=iniciar_parar_gravacao
)
botao_gravar.pack()

# Iniciar a captura de imagens
capturar_imagem()

# Manter a janela aberta
window.mainloop()
