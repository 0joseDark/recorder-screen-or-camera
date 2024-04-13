# Script Python para Gravar Tela em Vídeo para Rede Neural
# OpenCV: https://docs.opencv.org/
# Este script Python usa a biblioteca OpenCV para gravar a tela do computador em um arquivo de vídeo. A janela a ser gravada pode ser selecionada pelo usuário. 
# O vídeo é salvo no formato MP4, que é compatível com a maioria das redes neurais.

# Requisitos:

    # Python 3.x
    # OpenCV (instale com pip install opencv-python)
import cv2

def selecionar_janela():
    # Obter todas as janelas abertas
    janelas = []
    for w in cv2.waitKey(1) & 0xFF:
        if w == 27: # Esc para sair
            break
        elif w == ord(' '): # Barra de espaço para selecionar
            id_janela = cv2.getWindowProperty('Selecione a Janela', cv2.WND_PROP_ID)
            janelas.append(id_janela)
            print(f"Janela {id_janela} selecionada.")
        else:
            print(f"Pressione ' ' para selecionar a janela {w} ou Esc para sair.")
    return janelas

def gravar_tela(janelas, nome_arquivo):
    # Definir codec de vídeo
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    # Obter resolução da tela
    largura = cv2.getScreenWidth()
    altura = cv2.getScreenHeight()

    # Criar gravador de vídeo para cada janela
    gravadores = [cv2.VideoWriter(f'{nome_arquivo}_{janela}.mp4', codec, 25.0, (largura, altura)) for janela in janelas]

    # Loop de gravação
    while True:
        # Capturar frame da tela
        frame = cv2.grabFrame()

        # Mostrar frame para cada janela selecionada
        for gravador, janela in zip(gravadores, janelas):
            if cv2.getWindowProperty(f'Janela {janela}', cv2.WND_PROP_VISIBLE) >= 1:
                frame_janela = cv2.cvtColor(frame[cv2.getWindowImageRect(janela)], cv2.COLOR_BGR2RGB)
                gravador.write(frame_janela)

        # Mostrar frame principal
        cv2.imshow('Gravação de Tela', frame)

        # Tecla 'q' para parar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Finalizar gravadores
    for gravador in gravadores:
        gravador.release()

    # Fechar todas as janelas
    cv2.destroyAllWindows()

# Selecionar janelas
janelas = selecionar_janela()

# Gravar tela
if janelas:
    nome_arquivo = input("Digite o nome do arquivo de vídeo: ")
    gravar_tela(janelas, nome_arquivo)
    print("Gravação finalizada!")
else:
    print("Nenhuma janela selecionada.")

