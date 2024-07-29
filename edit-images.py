# pip install pillow

import os
import shutil
from tkinter import Tk, Label, Button, filedialog, Listbox, SINGLE, PhotoImage
from PIL import Image, ImageTk

# Função para selecionar uma pasta
def selecionar_pasta():
    global pasta
    pasta = filedialog.askdirectory()
    carregar_lista_imagens()

# Função para carregar lista de imagens da pasta selecionada
def carregar_lista_imagens():
    if pasta:
        lista_imagens.delete(0, 'end')
        for arquivo in os.listdir(pasta):
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                lista_imagens.insert('end', arquivo)

# Função para mostrar a imagem antes da edição
def mostrar_imagem_antes():
    imagem_selecionada = lista_imagens.get(lista_imagens.curselection())
    caminho_imagem = os.path.join(pasta, imagem_selecionada)
    imagem = Image.open(caminho_imagem)
    imagem.thumbnail((250, 250))
    imagem_antes = ImageTk.PhotoImage(imagem)
    label_imagem_antes.config(image=imagem_antes)
    label_imagem_antes.image = imagem_antes

# Função fictícia para mostrar a imagem depois da edição
def mostrar_imagem_depois():
    imagem_selecionada = lista_imagens.get(lista_imagens.curselection())
    caminho_imagem = os.path.join(pasta, imagem_selecionada)
    imagem = Image.open(caminho_imagem)
    # Aqui você pode adicionar a edição que quiser. No exemplo, vamos apenas inverter a imagem.
    imagem_editada = imagem.transpose(Image.FLIP_LEFT_RIGHT)
    imagem_editada.thumbnail((250, 250))
    imagem_depois = ImageTk.PhotoImage(imagem_editada)
    label_imagem_depois.config(image=imagem_depois)
    label_imagem_depois.image = imagem_depois

# Função para apagar a imagem selecionada
def apagar_imagem():
    imagem_selecionada = lista_imagens.get(lista_imagens.curselection())
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

# Botões para mostrar a imagem antes e depois da edição
botao_mostrar_antes = Button(root, text="Mostrar Imagem Antes", command=mostrar_imagem_antes)
botao_mostrar_antes.pack()

botao_mostrar_depois = Button(root, text="Mostrar Imagem Depois", command=mostrar_imagem_depois)
botao_mostrar_depois.pack()

# Botão para apagar a imagem selecionada
botao_apagar_imagem = Button(root, text="Apagar Imagem", command=apagar_imagem)
botao_apagar_imagem.pack()

# Labels para mostrar as imagens antes e depois
label_imagem_antes = Label(root)
label_imagem_antes.pack()

label_imagem_depois = Label(root)
label_imagem_depois.pack()

# Variável global para guardar o caminho da pasta selecionada
pasta = ''

# Inicia a aplicação
root.mainloop()
