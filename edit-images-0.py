import os
from tkinter import Tk, Label, Button, filedialog, Listbox, SINGLE
from PIL import Image, ImageTk

# Função para selecionar uma pasta
def selecionar_pasta():
    global pasta, imagem_atual
    pasta = filedialog.askdirectory()
    carregar_lista_imagens()
    imagem_atual = 0

# Função para carregar lista de imagens da pasta selecionada
def carregar_lista_imagens():
    if pasta:
        lista_imagens.delete(0, 'end')
        for arquivo in os.listdir(pasta):
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                lista_imagens.insert('end', arquivo)
        if lista_imagens.size() > 0:
            lista_imagens.selection_set(0)
            mostrar_imagem()

# Função para mostrar a imagem atual
def mostrar_imagem():
    global imagem_atual
    if lista_imagens.size() > 0:
        imagem_selecionada = lista_imagens.get(imagem_atual)
        caminho_imagem = os.path.join(pasta, imagem_selecionada)
        imagem = Image.open(caminho_imagem)
        imagem.thumbnail((250, 250))
        imagem_tk = ImageTk.PhotoImage(imagem)
        label_imagem.config(image=imagem_tk)
        label_imagem.image = imagem_tk

# Função para avançar para a próxima imagem
def proxima_imagem():
    global imagem_atual
    if lista_imagens.size() > 0:
        imagem_atual = (imagem_atual + 1) % lista_imagens.size()
        lista_imagens.selection_clear(0, 'end')
        lista_imagens.selection_set(imagem_atual)
        mostrar_imagem()

# Função para voltar para a imagem anterior
def imagem_anterior():
    global imagem_atual
    if lista_imagens.size() > 0:
        imagem_atual = (imagem_atual - 1) % lista_imagens.size()
        lista_imagens.selection_clear(0, 'end')
        lista_imagens.selection_set(imagem_atual)
        mostrar_imagem()

# Função para apagar a imagem selecionada
def apagar_imagem():
    if lista_imagens.size() > 0:
        imagem_selecionada = lista_imagens.get(imagem_atual)
        caminho_imagem = os.path.join(pasta, imagem_selecionada)
        os.remove(caminho_imagem)
        carregar_lista_imagens()

# Criação da janela principal
root = Tk()
root.title("Editor de Imagens")

# Botão para selecionar a pasta
botao_selecionar_pasta = Button(root, text="Selecionar Pasta", command=selecionar_pasta)
botao_selecionar_pasta.pack()

# Listbox para mostrar as imagens na pasta selecionada
lista_imagens = Listbox(root, selectmode=SINGLE)
lista_imagens.pack()

# Botão para mostrar a imagem anterior
botao_imagem_anterior = Button(root, text="Imagem Anterior", command=imagem_anterior)
botao_imagem_anterior.pack()

# Botão para mostrar a próxima imagem
botao_proxima_imagem = Button(root, text="Próxima Imagem", command=proxima_imagem)
botao_proxima_imagem.pack()

# Botão para apagar a imagem selecionada
botao_apagar_imagem = Button(root, text="Apagar Imagem", command=apagar_imagem)
botao_apagar_imagem.pack()

# Label para mostrar a imagem atual
label_imagem = Label(root)
label_imagem.pack()

# Variável global para guardar o caminho da pasta selecionada
pasta = ''
# Variável global para guardar o índice da imagem atual
imagem_atual = 0

# Inicia a aplicação
root.mainloop()
