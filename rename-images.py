import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Função para selecionar a pasta de entrada
def escolher_pasta_entrada():
    global pasta_entrada
    pasta_entrada = filedialog.askdirectory()
    label_pasta_entrada.config(text=f"Pasta de Entrada: {pasta_entrada}")

# Função para selecionar a pasta de saída
def escolher_pasta_saida():
    global pasta_saida
    pasta_saida = filedialog.askdirectory()
    label_pasta_saida.config(text=f"Pasta de Saída: {pasta_saida}")

# Função para renomear os arquivos
def renomear_arquivos():
    if not pasta_entrada or not pasta_saida:
        messagebox.showwarning("Aviso", "Selecione ambas as pastas de entrada e saída.")
        return

    arquivos = os.listdir(pasta_entrada)
    for i, nome_arquivo in enumerate(arquivos):
        extensao = os.path.splitext(nome_arquivo)[1]
        novo_nome = f"{i+1:04d}{extensao}"
        caminho_antigo = os.path.join(pasta_entrada, nome_arquivo)
        caminho_novo = os.path.join(pasta_saida, novo_nome)
        os.rename(caminho_antigo, caminho_novo)

    messagebox.showinfo("Sucesso", "Arquivos renomeados com sucesso!")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Renomear Arquivos")

# Adicionando um menu
menu = tk.Menu(janela)
janela.config(menu=menu)

menu_arquivo = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Arquivo", menu=menu_arquivo)
menu_arquivo.add_command(label="Sair", command=janela.quit)

# Labels para mostrar as pastas selecionadas
label_pasta_entrada = tk.Label(janela, text="Pasta de Entrada: Não selecionada")
label_pasta_entrada.pack(pady=5)

label_pasta_saida = tk.Label(janela, text="Pasta de Saída: Não selecionada")
label_pasta_saida.pack(pady=5)

# Botões para selecionar as pastas
botao_escolher_entrada = tk.Button(janela, text="Escolher Pasta de Entrada", command=escolher_pasta_entrada)
botao_escolher_entrada.pack(pady=5)

botao_escolher_saida = tk.Button(janela, text="Escolher Pasta de Saída", command=escolher_pasta_saida)
botao_escolher_saida.pack(pady=5)

# Botão para renomear os arquivos
botao_renomear = tk.Button(janela, text="Renomear Arquivos", command=renomear_arquivos)
botao_renomear.pack(pady=20)

# Variáveis globais para armazenar os caminhos das pastas
pasta_entrada = ""
pasta_saida = ""

# Executar a janela principal
janela.mainloop()
