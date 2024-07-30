import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import time

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
    total_arquivos = len(arquivos)

    progress_bar['maximum'] = total_arquivos

    for i, nome_arquivo in enumerate(arquivos):
        if pausar_renomeacao:
            return

        extensao = os.path.splitext(nome_arquivo)[1]
        novo_nome = f"{i+1:04d}{extensao}"
        caminho_antigo = os.path.join(pasta_entrada, nome_arquivo)
        caminho_novo = os.path.join(pasta_saida, novo_nome)
        os.rename(caminho_antigo, caminho_novo)

        progress_bar['value'] = i + 1
        porcentagem.set(f"{int(((i + 1) / total_arquivos) * 100)}%")
        janela.update_idletasks()
        time.sleep(0.1)  # Simula um pequeno atraso para ver a barra de progresso em ação

    messagebox.showinfo("Sucesso", "Arquivos renomeados com sucesso!")

# Função para iniciar o renomeio em uma nova thread
def iniciar_renomeacao():
    global pausar_renomeacao
    pausar_renomeacao = False
    thread = threading.Thread(target=renomear_arquivos)
    thread.start()

# Função para pausar o renomeio
def pausar_renomeacao_func():
    global pausar_renomeacao
    pausar_renomeacao = True

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

# Barra de progresso e label para a percentagem
progress_bar = ttk.Progressbar(janela, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

porcentagem = tk.StringVar()
label_porcentagem = tk.Label(janela, textvariable=porcentagem)
label_porcentagem.pack()

# Botões para renomear, pausar e sair
botao_renomear = tk.Button(janela, text="Renomear Arquivos", command=iniciar_renomeacao)
botao_renomear.pack(pady=5)

botao_pausar = tk.Button(janela, text="Pausar Renomeação", command=pausar_renomeacao_func)
botao_pausar.pack(pady=5)

botao_sair = tk.Button(janela, text="Sair", command=janela.quit)
botao_sair.pack(pady=5)

# Variáveis globais para armazenar os caminhos das pastas
pasta_entrada = ""
pasta_saida = ""
pausar_renomeacao = False

# Executar a janela principal
janela.mainloop()
