
# pip install tkinter pygetwindow pyautogui opencv-python
- 
# g++ -fPIC main.cpp -o ScreenRecorder -I /path/to/Qt/include -L /path/to/Qt/libs -lQt5Widgets -lQt5Core -lopencv_core -lopencv_videoio -lopencv_highgui

 ![Texto alternativo](https://github.com/0joseDark/recorder-screen-or-camera/blob/main/images/tools/recorder-screen-or-camera.jpg)
 
 ---
 **Qt (PyQt6)**

###  Agora tem:

* **Modos de captura:** Câmara USB, Ecrã inteiro, ou **Janela específica** (quando suportado pelo `pygetwindow`).
* **Cross-platform:** Windows 10, Ubuntu e macOS (no macOS lembra-te de autorizar *Screen Recording* em *Privacy & Security*).
* **Controlos:** escolher ficheiro de saída, FPS, índice da câmara, codec (mp4v/XVID/MJPG/H264), **Gravar/Parar/Sair**.
* **Desempenho:** captura de ecrã via **`mss`** (rápido e portátil). Escrita com OpenCV.

### Instalação

```bash
pip install PyQt6 opencv-python mss numpy pygetwindow
```

> Dica: se fores gravar para `.mp4`, usa o codec **mp4v** (pré-definido). Para `.avi`, troca para **XVID**.

### Execução

```bash
python qt_recorder.py
```

* No macOS, se a janela ficar preta ao gravar ecrã, vai a **System Settings → Privacy & Security → Screen Recording** e autoriza o Python/Terminal.
---
Feito ✅ — atualizei o script, tem agora:

* seleção de região por “arrastar para desenhar” (overlay transparente, ecrã inteiro)
* pré-visualização ao vivo (ativável)
* escolha de resolução (redimensiona na captura) e bitrate (aplicado no passo ffmpeg)
* áudio do microfone com `sounddevice` + `soundfile`, e mux/encode final com `ffmpeg` (opcional re-encode)

### Instalar dependências

```bash
pip install PyQt6 opencv-python mss numpy pygetwindow sounddevice soundfile
# Também precisas do ffmpeg instalado no sistema (acessível como comando "ffmpeg")
```

### Como funciona (resumo)

* O vídeo é gravado primeiro para um ficheiro temporário (OpenCV).
* O áudio (se ativado) é gravado para WAV temporário.
* No fim, o `ffmpeg` faz o mux (e opcionalmente re-encode para aplicar o bitrate escolhido, com `libx264 + aac`).
* Podes gravar: câmara, ecrã inteiro, janela (quando suportado) ou região arrastada.

 
