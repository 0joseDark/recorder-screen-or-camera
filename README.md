
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

Exemplo Android em **Java** :

* **Escolher origem**:

  * *Ecrã inteiro* (via `MediaProjection`)
  * *Câmara frontal ou traseira* (via `Camera2` + `MediaRecorder`)

* **Pré-visualização ao vivo**:

  * Para a **câmara**, usamos um `SurfaceView` que mostra a imagem em tempo real.
  * Para o **ecrã**, não há preview (porque estamos a capturar a própria tela).

* **Configurações de resolução e bitrate**:

  * Caixas de seleção (`Spinner`) para escolher resolução (`1920x1080`, `1280x720`, etc.) e bitrate (`2000k`, `4000k`, `8000k`).

---

# 📱 Código Expandido

### `AndroidManifest.xml`

Permissões necessárias:

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
```

---

### `activity_main.xml`

Layout com botões + seletores:

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp"
    android:gravity="center">

    <Spinner
        android:id="@+id/modeSpinner"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:entries="@array/mode_options"/>

    <Spinner
        android:id="@+id/resolutionSpinner"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:entries="@array/resolution_options"/>

    <Spinner
        android:id="@+id/bitrateSpinner"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:entries="@array/bitrate_options"/>

    <SurfaceView
        android:id="@+id/previewSurface"
        android:layout_width="match_parent"
        android:layout_height="300dp"
        android:layout_marginTop="16dp"
        android:background="#000"/>

    <Button
        android:id="@+id/startBtn"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Iniciar Gravação"/>

    <Button
        android:id="@+id/stopBtn"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Parar Gravação"/>
</LinearLayout>
```

---

### `res/values/strings.xml`

Opções de seleção:

```xml
<string-array name="mode_options">
    <item>Ecrã</item>
    <item>Câmara Frontal</item>
    <item>Câmara Traseira</item>
</string-array>

<string-array name="resolution_options">
    <item>1920x1080</item>
    <item>1280x720</item>
    <item>640x480</item>
</string-array>

<string-array name="bitrate_options">
    <item>2000k</item>
    <item>4000k</item>
    <item>8000k</item>
</string-array>
```

---

### `MainActivity.java`

```java
package com.example.recorderapp;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.*;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.os.Environment;
import android.util.Size;
import android.view.*;
import android.widget.*;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;

public class MainActivity extends Activity {

    private static final int SCREEN_RECORD_REQUEST_CODE = 1000;
    private static final int REQUEST_PERMS = 2000;

    private Spinner modeSpinner, resolutionSpinner, bitrateSpinner;
    private Button startBtn, stopBtn;
    private SurfaceView previewSurface;

    private MediaProjectionManager projectionManager;
    private MediaProjection mediaProjection;
    private MediaRecorder mediaRecorder;
    private CameraDevice cameraDevice;
    private CameraCaptureSession captureSession;

    private String videoPath;
    private boolean isRecording = false;

    private int outWidth = 1280, outHeight = 720, outBitrate = 4000000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        modeSpinner = findViewById(R.id.modeSpinner);
        resolutionSpinner = findViewById(R.id.resolutionSpinner);
        bitrateSpinner = findViewById(R.id.bitrateSpinner);
        startBtn = findViewById(R.id.startBtn);
        stopBtn = findViewById(R.id.stopBtn);
        previewSurface = findViewById(R.id.previewSurface);

        projectionManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);

        ActivityCompat.requestPermissions(this, new String[]{
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.CAMERA,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
        }, REQUEST_PERMS);

        startBtn.setOnClickListener(v -> startRecording());
        stopBtn.setOnClickListener(v -> stopRecording());
    }

    private void updateSettings() {
        // resolução
        String res = (String) resolutionSpinner.getSelectedItem();
        String[] parts = res.split("x");
        outWidth = Integer.parseInt(parts[0]);
        outHeight = Integer.parseInt(parts[1]);

        // bitrate
        String br = (String) bitrateSpinner.getSelectedItem();
        outBitrate = Integer.parseInt(br.replace("k", "")) * 1000;
    }

    private void initRecorder() throws IOException {
        updateSettings();
        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);

        File outFile = new File(Environment.getExternalStorageDirectory(),
                "recorded_" + System.currentTimeMillis() + ".mp4");
        videoPath = outFile.getAbsolutePath();
        mediaRecorder.setOutputFile(videoPath);

        mediaRecorder.setVideoSize(outWidth, outHeight);
        mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
        mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
        mediaRecorder.setVideoEncodingBitRate(outBitrate);
        mediaRecorder.setVideoFrameRate(30);

        mediaRecorder.prepare();
    }

    private void startRecording() {
        String mode = (String) modeSpinner.getSelectedItem();
        if (mode.equals("Ecrã")) {
            startScreenCapture();
        } else {
            startCameraCapture(mode.equals("Câmara Frontal"));
        }
    }

    private void startScreenCapture() {
        if (mediaProjection == null) {
            Intent intent = projectionManager.createScreenCaptureIntent();
            startActivityForResult(intent, SCREEN_RECORD_REQUEST_CODE);
        } else {
            try {
                initRecorder();
                mediaProjection.createVirtualDisplay("ScreenRecorder",
                        outWidth, outHeight, getResources().getDisplayMetrics().densityDpi,
                        0, mediaRecorder.getSurface(), null, null);
                mediaRecorder.start();
                isRecording = true;
                Toast.makeText(this, "Gravação do ecrã iniciada", Toast.LENGTH_SHORT).show();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void startCameraCapture(boolean front) {
        try {
            initRecorder();
            String cameraId = getCameraId(front);
            CameraManager cm = (CameraManager) getSystemService(CAMERA_SERVICE);
            cm.openCamera(cameraId, new CameraDevice.StateCallback() {
                @Override
                public void onOpened(CameraDevice camera) {
                    cameraDevice = camera;
                    try {
                        Surface recorderSurface = mediaRecorder.getSurface();
                        Surface previewSurf = previewSurface.getHolder().getSurface();
                        CaptureRequest.Builder builder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_RECORD);
                        builder.addTarget(recorderSurface);
                        builder.addTarget(previewSurf);

                        cameraDevice.createCaptureSession(Arrays.asList(recorderSurface, previewSurf),
                                new CameraCaptureSession.StateCallback() {
                                    @Override
                                    public void onConfigured(CameraCaptureSession session) {
                                        captureSession = session;
                                        try {
                                            session.setRepeatingRequest(builder.build(), null, null);
                                            mediaRecorder.start();
                                            isRecording = true;
                                            Toast.makeText(MainActivity.this, "Gravação da câmara iniciada", Toast.LENGTH_SHORT).show();
                                        } catch (Exception e) {
                                            e.printStackTrace();
                                        }
                                    }

                                    @Override
                                    public void onConfigureFailed(CameraCaptureSession session) {}
                                }, null);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }

                @Override
                public void onDisconnected(CameraDevice camera) {}
                @Override
                public void onError(CameraDevice camera, int error) {}
            }, null);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private String getCameraId(boolean front) throws CameraAccessException {
        CameraManager cm = (CameraManager) getSystemService(CAMERA_SERVICE);
        for (String id : cm.getCameraIdList()) {
            CameraCharacteristics chars = cm.getCameraCharacteristics(id);
            Integer facing = chars.get(CameraCharacteristics.LENS_FACING);
            if (front && facing == CameraCharacteristics.LENS_FACING_FRONT)
                return id;
            if (!front && facing == CameraCharacteristics.LENS_FACING_BACK)
                return id;
        }
        return cm.getCameraIdList()[0];
    }

    private void stopRecording() {
        if (!isRecording) return;
        mediaRecorder.stop();
        mediaRecorder.reset();
        if (captureSession != null) {
            captureSession.close();
        }
        if (cameraDevice != null) {
            cameraDevice.close();
        }
        if (mediaProjection != null) {
            mediaProjection.stop();
        }
        isRecording = false;
        Toast.makeText(this, "Gravação guardada em: " + videoPath, Toast.LENGTH_LONG).show();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == SCREEN_RECORD_REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                mediaProjection = projectionManager.getMediaProjection(resultCode, data);
                startScreenCapture();
            } else {
                Toast.makeText(this, "Permissão negada!", Toast.LENGTH_SHORT).show();
            }
        }
    }
}
```

---

# 🚀 O que este código faz

* **Modo Ecrã** → usa `MediaProjection` + `MediaRecorder`.
* **Modo Câmara Frontal/Traseira** → usa `Camera2` + `MediaRecorder` + `SurfaceView` para preview.
* **Resolução e bitrate** → escolhidos via `Spinner` antes de iniciar.

---




 
