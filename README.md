```bash
pip install tkinter pygetwindow pyautogui opencv-python
```
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
---
Boa pergunta 👌 — sem **ffmpeg** o teu gravador funciona, mas só guarda o vídeo “cru” (sem áudio, sem bitrate controlado).
Para poderes juntar áudio + vídeo e aplicar **bitrate/resolução profissional**, precisas de instalar o **ffmpeg** no teu sistema operativo. Vou explicar para **Windows 10, Ubuntu Linux e macOS**.

---

# 🔹 1. Windows 10

### Instalação manual

1. Vai ao site oficial: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   → escolhe **Windows builds** (por ex. [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) ou [BtbN builds](https://github.com/BtbN/FFmpeg-Builds/releases))
2. Faz download do **ZIP estático** (ex: `ffmpeg-release-full.7z` ou `ffmpeg-release-essentials.zip`).
  - https://github.com/BtbN/FFmpeg-Builds/releases
4. Extrai o ZIP (por exemplo para `C:\\ffmpeg`).
5. Dentro de `C:\\ffmpeg\\bin` está o executável `ffmpeg.exe`.

### Adicionar ao PATH

1. Pesquisa por **Variáveis de ambiente** no Windows.
2. Edita a variável **Path** e adiciona `C:\\ffmpeg\\bin`.
3. Abre uma nova janela do **CMD/PowerShell** e testa:

   ```bat
   ffmpeg -version
   ```

   Se aparecer a versão, está ok.

---

# 🔹 2. Ubuntu / Debian Linux

O ffmpeg já está nos repositórios oficiais:

```bash
sudo apt update
sudo apt install ffmpeg
```

Depois verifica:

```bash
ffmpeg -version
```

Se quiseres uma versão mais recente, podes usar o **PPA oficial**:

```bash
sudo add-apt-repository ppa:jonathonf/ffmpeg-4
sudo apt update
sudo apt install ffmpeg
```

---

# 🔹 3. macOS

No macOS, a forma mais simples é via **Homebrew**:

1. Instala o Homebrew (se ainda não tens):

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Depois instala o ffmpeg:

   ```bash
   brew install ffmpeg
   ```
3. Verifica:

   ```bash
   ffmpeg -version
   ```

Se não usar Homebrew, também pode fazer download de builds prontos de [evermeet.cx](https://evermeet.cx/ffmpeg/) ou [ffmpeg.org](https://ffmpeg.org/download.html).

---

# 🔹 4. Como o script usa o ffmpeg

No teu código, depois da gravação:

* gera-se um **vídeo temporário (sem áudio)**
* gera-se um **WAV temporário (com áudio do microfone)**
* depois o Python corre:

```bash
ffmpeg -y -i video_temp.mp4 -i audio_temp.wav -c:v libx264 -b:v 6000k -pix_fmt yuv420p -c:a aac -b:a 160k final.mp4
```

👉 Isto junta vídeo + áudio e aplica o bitrate/resolução escolhidos.

---

⚡ Ou seja:

* **Windows** → download ZIP, extrair e pôr `bin` no PATH.
* **Ubuntu** → `sudo apt install ffmpeg`.
* **macOS** → `brew install ffmpeg`.

---
