# Altere a variável pasta_do_servidor para o caminho da pasta que contém os seus arquivos HTML e outros recursos do servidor.
# Abra um navegador web e acesse o endereço http://localhost:<porta>, substituindo <porta> pelo número da porta que você configurou.
# Este é um exemplo básico

import tkinter as tk
from tkinter import messagebox
import http.server

class MeuServidor(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Tratar requisições GET
        # Exemplo: exibir o conteúdo de um arquivo HTML
        caminho_arquivo = self.path.lstrip("/")
        if not caminho_arquivo:
            caminho_arquivo = "index.html"
        try:
            with open(f"pasta_do_servidor/{caminho_arquivo}", "rb") as f:
                conteudo = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(conteudo))
            self.end_headers()
            self.wfile.write(conteudo)
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Arquivo não encontrado</h1>")

    def do_POST(self):
        # Tratar requisições POST
        # Exemplo: salvar dados enviados em um formulário
        tamanho_conteudo = int(self.headers["Content-Length"])
        dados_post = self.rfile.read(tamanho_conteudo).decode("utf-8")
        # ... processar dados_post ...

def iniciar_servidor():
    porta = int(entry_porta.get())
    pasta = entry_pasta.get()
    try:
        # Iniciar o servidor com as configurações fornecidas
        servidor = http.server.HTTPServer(('', porta), MeuServidor)
        servidor.serve_forever()
    except OSError as e:
        messagebox.showerror("Erro", f"Erro ao iniciar o servidor: {e}")

janela = tk.Tk()
janela.geometry("400x300")
janela.title("Configuração do Servidor")

label_porta = tk.Label(text="Porta do Servidor:")
label_porta.place(x=10, y=10)

entry_porta = tk.Entry()
entry_porta.place(x=100, y=10)

label_pasta = tk.Label(text="Pasta do Servidor:")
label_pasta.place(x=10, y=40)

entry_pasta = tk.Entry()
entry_pasta.place(x=100, y=40)

botao_iniciar = tk.Button(text="Iniciar Servidor", command=iniciar_servidor)
botao_iniciar.place(x=100, y=80)

janela.mainloop()
