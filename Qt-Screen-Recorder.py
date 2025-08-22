# -*- coding: utf-8 -*-
"""
Qt Screen/Camera Recorder (Windows 10, Ubuntu, macOS) — v2

Novidades nesta versão:
- Seleção de região com "arrastar para desenhar" (overlay transparente)
- Pré‑visualização ao vivo
- Escolha de resolução (redimensionamento) e bitrate
- Áudio do microfone (via sounddevice) + mux com ffmpeg (opção re‑encode)

Dependências (Python 3.9+ recomendado):
    pip install PyQt6 opencv-python mss numpy pygetwindow sounddevice soundfile
    # ffmpeg tem de estar instalado no sistema (linha de comandos "ffmpeg")

Notas:
- No macOS, autoriza a app/terminal em: System Settings → Privacy & Security → Screen Recording & Microphone.
- Em Window mode, a deteção de janelas via pygetwindow é best‑effort. Se falhar, usa Ecrã inteiro + região.
"""

import os
import sys
import time
import threading
import tempfile
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import cv2

# Qt
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QColor, QPen, QGuiApplication, QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QHBoxLayout,
    QVBoxLayout, QGroupBox, QRadioButton, QListWidget, QMessageBox,
    QSpinBox, QComboBox, QFormLayout, QLineEdit, QCheckBox
)

# Screen capture
from mss import mss

# Window enumeration (optional)
try:
    import pygetwindow as gw  # type: ignore
    HAVE_GW = True
except Exception:
    HAVE_GW = False

# Audio recording (microfone)
try:
    import sounddevice as sd
    import soundfile as sf
    HAVE_SD = True
except Exception:
    HAVE_SD = False


@dataclass
class CaptureRegion:
    left: int
    top: int
    width: int
    height: int


class SafeFrameBuffer:
    """Thread-safe último frame capturado (numpy BGR)."""
    def __init__(self):
        self._lock = threading.Lock()
        self._frame = None  # type: Optional[np.ndarray]

    def set(self, frame: np.ndarray):
        with self._lock:
            self._frame = frame.copy()

    def get(self) -> Optional[np.ndarray]:
        with self._lock:
            return None if self._frame is None else self._frame.copy()


class RegionOverlay(QWidget):
    """Overlay de ecrã inteiro para desenhar uma caixa com o rato."""
    region_selected = pyqtSignal(int, int, int, int)  # left, top, width, height

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        # Cobrir todos os ecrãs
        geo = QGuiApplication.primaryScreen().geometry()
        # Nota: para setups multi-monitor avançados, poderíamos unir geometrias.
        self.setGeometry(geo)
        self._dragging = False
        self._start = None
        self._end = None

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start = e.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._end = e.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._end = e.position().toPoint()
            rect = self._normalized_rect()
            self.region_selected.emit(rect.left(), rect.top(), rect.width(), rect.height())
            self.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self._start and self._end:
            rect = self._normalized_rect()
            # recorte claro
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            # moldura
            pen = QPen(QColor(255, 255, 255, 220), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(rect)

    def _normalized_rect(self) -> QRect:
        x1, y1 = self._start.x(), self._start.y()
        x2, y2 = self._end.x(), self._end.y()
        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        return QRect(left, top, right - left, bottom - top)


class RecorderThread(threading.Thread):
    def __init__(self, *, mode: str, file_path: str, fps: int = 20,
                 camera_index: int = 0, region: CaptureRegion | None = None,
                 codec: str = 'mp4v', out_size: Tuple[int, int] | None = None,
                 preview_buf: SafeFrameBuffer | None = None,
                 running_flag: threading.Event | None = None):
        super().__init__(daemon=True)
        self.mode = mode            # 'camera' | 'screen' | 'window'
        self.file_path = file_path
        self.fps = max(1, int(fps))
        self.camera_index = camera_index
        self.region = region
        self.codec = codec
        self.out_size = out_size
        self.preview_buf = preview_buf
        self._running = running_flag or threading.Event()
        self._running.set()

    def stop(self):
        self._running.clear()

    def run(self):
        if self.mode == 'camera':
            self._record_camera()
        else:
            self._record_screen_like()

    def _open_writer(self, size_wh: tuple[int, int]):
        fourcc = cv2.VideoWriter_fourcc(*self.codec.upper())
        writer = cv2.VideoWriter(self.file_path, fourcc, float(self.fps), size_wh)
        if not writer.isOpened():
            raise RuntimeError("Não foi possível abrir o VideoWriter. Tente outro codec/ficheiro.")
        return writer

    def _resize_if_needed(self, frame: np.ndarray) -> np.ndarray:
        if self.out_size is None:
            return frame
        w, h = self.out_size
        if w > 0 and h > 0 and (frame.shape[1] != w or frame.shape[0] != h):
            return cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        return frame

    def _record_camera(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível acessar a câmera (índice {self.camera_index}).")
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        # respeitar out_size se definido
        target_size = (self.out_size[0], self.out_size[1]) if self.out_size else (width, height)
        writer = self._open_writer(target_size)
        frame_interval = 1.0 / self.fps
        try:
            while self._running.is_set():
                t0 = time.perf_counter()
                ok, frame = cap.read()
                if not ok:
                    break
                if self.preview_buf is not None:
                    self.preview_buf.set(frame)
                frame = self._resize_if_needed(frame)
                writer.write(frame)
                dt = time.perf_counter() - t0
                to_wait = frame_interval - dt
                if to_wait > 0:
                    time.sleep(to_wait)
        finally:
            cap.release()
            writer.release()

    def _record_screen_like(self):
        with mss() as sct:
            if self.region is None:
                mon = sct.monitors[1]
                region = CaptureRegion(mon['left'], mon['top'], mon['width'], mon['height'])
            else:
                region = self.region
            monitor = {'left': int(region.left), 'top': int(region.top), 'width': int(region.width), 'height': int(region.height)}
            # respeitar out_size
            out_w = self.out_size[0] if self.out_size else monitor['width']
            out_h = self.out_size[1] if self.out_size else monitor['height']
            writer = self._open_writer((out_w, out_h))
            frame_interval = 1.0 / self.fps
            try:
                while self._running.is_set():
                    t0 = time.perf_counter()
                    img = sct.grab(monitor)  # BGRA
                    frame = np.array(img)[:, :, :3]  # BGR
                    if self.preview_buf is not None:
                        self.preview_buf.set(frame)
                    if self.out_size is not None:
                        frame = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_AREA)
                    writer.write(frame)
                    dt = time.perf_counter() - t0
                    to_wait = frame_interval - dt
                    if to_wait > 0:
                        time.sleep(to_wait)
            finally:
                writer.release()


class AudioRecorder(threading.Thread):
    """Grava áudio do microfone para WAV temporário usando sounddevice+soundfile."""
    def __init__(self, samplerate: int = 48000, channels: int = 1, device: Optional[int] = None):
        super().__init__(daemon=True)
        self.samplerate = int(samplerate)
        self.channels = int(channels)
        self.device = device
        self._running = threading.Event()
        self._running.set()
        self.wav_path = os.path.join(tempfile.gettempdir(), f"qtrec_audio_{int(time.time())}.wav")

    def stop(self):
        self._running.clear()

    def run(self):
        if not HAVE_SD:
            return
        with sf.SoundFile(self.wav_path, mode='w', samplerate=self.samplerate, channels=self.channels, subtype='PCM_16') as wav:
            def callback(indata, frames, time_info, status):
                if status:
                    # Opcional: log de status
                    pass
                if not self._running.is_set():
                    raise sd.CallbackStop()
                wav.write(indata.copy())
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, device=self.device, callback=callback):
                while self._running.is_set():
                    time.sleep(0.1)


class RecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gravador de Ecrã/Câmara (Qt) — v2")
        self.setMinimumWidth(860)

        # State
        self.output_path: str = ''
        self.rec_thread: RecorderThread | None = None
        self.audio_thread: AudioRecorder | None = None
        self.preview_buf = SafeFrameBuffer()
        self._running_flag = threading.Event()
        self._running_flag.clear()
        self.selected_region: CaptureRegion | None = None
        self.temp_video_path: str | None = None

        # --- UI ---
        # Modes
        self.mode_camera = QRadioButton("Câmara USB")
        self.mode_screen = QRadioButton("Ecrã inteiro")
        self.mode_window = QRadioButton("Janela específica")
        self.mode_screen.setChecked(True)

        mode_box = QGroupBox("Fonte de gravação")
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.mode_screen)
        mode_layout.addWidget(self.mode_window)
        mode_layout.addWidget(self.mode_camera)
        mode_box.setLayout(mode_layout)

        self.window_list = QListWidget(); self.window_list.setMinimumHeight(140)
        self.refresh_btn = QPushButton("Atualizar janelas")
        self.refresh_btn.clicked.connect(self.refresh_windows)
        if not HAVE_GW:
            self.mode_window.setEnabled(False)
            self.window_list.setEnabled(False)
            self.refresh_btn.setEnabled(False)

        # Seleção de região
        self.select_region_btn = QPushButton("Selecionar região…")
        self.clear_region_btn = QPushButton("Limpar região")
        self.select_region_btn.clicked.connect(self.open_region_overlay)
        self.clear_region_btn.clicked.connect(self.clear_region)

        # Settings box
        settings_box = QGroupBox("Definições de Vídeo")
        form = QFormLayout()
        self.fps_spin = QSpinBox(); self.fps_spin.setRange(1, 120); self.fps_spin.setValue(30)
        self.cam_index = QSpinBox(); self.cam_index.setRange(0, 10); self.cam_index.setValue(0)
        self.codec_combo = QComboBox(); self.codec_combo.addItems(["mp4v", "XVID", "MJPG", "H264"])  # disponibilidade varia
        self.res_combo = QComboBox(); self.res_combo.addItems([
            "Nativo/Original", "3840x2160", "2560x1440", "1920x1080", "1600x900", "1280x720", "1024x576", "854x480"
        ])
        self.bitrate_spin = QSpinBox(); self.bitrate_spin.setRange(200, 50000); self.bitrate_spin.setValue(6000); self.bitrate_spin.setSuffix(" kbps")

        self.filename_edit = QLineEdit(); self.filename_edit.setPlaceholderText("Escolha o ficheiro de saída (.mp4)")
        choose_btn = QPushButton("Escolher ficheiro…"); choose_btn.clicked.connect(self.choose_file)
        h = QHBoxLayout(); h.addWidget(self.filename_edit); h.addWidget(choose_btn)

        form.addRow("FPS:", self.fps_spin)
        form.addRow("Índice da câmara:", self.cam_index)
        form.addRow("Codec (captura):", self.codec_combo)
        form.addRow("Resolução de saída:", self.res_combo)
        form.addRow("Bitrate (ffmpeg):", self.bitrate_spin)
        form.addRow("Saída:", h)
        settings_box.setLayout(form)

        # Áudio
        audio_box = QGroupBox("Áudio do Microfone")
        aform = QFormLayout()
        self.audio_enable = QCheckBox("Gravar áudio do microfone")
        self.audio_sr = QSpinBox(); self.audio_sr.setRange(8000, 192000); self.audio_sr.setValue(48000); self.audio_sr.setSuffix(" Hz")
        self.audio_ch = QComboBox(); self.audio_ch.addItems(["Mono (1)", "Stereo (2)"])
        self.audio_dev = QComboBox(); self.populate_audio_devices()
        self.reencode_cb = QCheckBox("Mux/Re‑encode com ffmpeg (para aplicar bitrate)"); self.reencode_cb.setChecked(True)
        aform.addRow(self.audio_enable)
        aform.addRow("Sample rate:", self.audio_sr)
        aform.addRow("Canais:", self.audio_ch)
        aform.addRow("Dispositivo:", self.audio_dev)
        aform.addRow(self.reencode_cb)
        audio_box.setLayout(aform)
        if not HAVE_SD:
            audio_box.setEnabled(False)
            self.audio_enable.setChecked(False)

        # Pré-visualização
        preview_box = QGroupBox("Pré‑visualização ao vivo")
        pv_layout = QVBoxLayout()
        self.preview_enable = QCheckBox("Ativar pré‑visualização")
        self.preview_label = QLabel("(sem pré‑visualização)")
        self.preview_label.setFixedHeight(300)
        self.preview_label.setStyleSheet("background:#111; color:#ccc; border:1px solid #333;")
        pv_layout.addWidget(self.preview_enable)
        pv_layout.addWidget(self.preview_label)
        preview_box.setLayout(pv_layout)

        # Controls
        self.start_btn = QPushButton("Gravar")
        self.stop_btn = QPushButton("Parar"); self.stop_btn.setEnabled(False)
        self.exit_btn = QPushButton("Sair")
        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.exit_btn.clicked.connect(self.close)

        # Layout
        left_col = QVBoxLayout()
        left_col.addWidget(mode_box)
        left_col.addWidget(self.window_list)
        left_col.addWidget(self.refresh_btn)
        left_col.addWidget(self.select_region_btn)
        left_col.addWidget(self.clear_region_btn)

        right_col = QVBoxLayout()
        right_col.addWidget(settings_box)
        right_col.addWidget(audio_box)
        right_col.addWidget(preview_box)
        btn_row = QHBoxLayout(); btn_row.addWidget(self.start_btn); btn_row.addWidget(self.stop_btn); btn_row.addWidget(self.exit_btn)
        right_col.addLayout(btn_row)

        root = QHBoxLayout(); root.addLayout(left_col, 1); root.addLayout(right_col, 2)
        self.setLayout(root)

        # timers
        self.ui_pulse = QTimer(self); self.ui_pulse.setInterval(60)
        self.ui_pulse.timeout.connect(self._tick)
        self.ui_pulse.start()

        self.refresh_windows()

    # --- Audio devices ---
    def populate_audio_devices(self):
        self.audio_dev.clear()
        if not HAVE_SD:
            self.audio_dev.addItem("(sounddevice não disponível)", userData=None)
            return
        try:
            devices = sd.query_devices()
            # preencher apenas dispositivos de input
            for idx, d in enumerate(devices):
                if d.get('max_input_channels', 0) > 0:
                    name = d.get('name', f'Device {idx}')
                    self.audio_dev.addItem(f"{idx}: {name}", userData=idx)
            if self.audio_dev.count() == 0:
                self.audio_dev.addItem("(nenhum dispositivo de entrada)", userData=None)
        except Exception:
            self.audio_dev.addItem("(erro a listar dispositivos)", userData=None)

    # --- Preview helpers ---
    def _update_preview(self):
        if not self.preview_enable.isChecked():
            return
        frame = self.preview_buf.get()
        if frame is None:
            return
        # Converter BGR -> RGB e mostrar
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimg = QImage(rgb.data, w, h, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(pix.scaled(self.preview_label.width(), self.preview_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    # --- UI logic ---
    def choose_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar vídeo", "output.mp4", "Vídeo MP4 (*.mp4);;AVI (*.avi)")
        if path:
            self.output_path = path
            self.filename_edit.setText(path)
            if path.lower().endswith('.avi'):
                idx = self.codec_combo.findText('XVID');
            else:
                idx = self.codec_combo.findText('mp4v')
            if idx >= 0:
                self.codec_combo.setCurrentIndex(idx)

    def refresh_windows(self):
        self.window_list.clear()
        if not HAVE_GW:
            return
        try:
            wins = gw.getAllWindows()
            items = []
            for w in wins:
                try:
                    if not w.title or w.width <= 0 or w.height <= 0:
                        continue
                    if hasattr(w, 'isMinimized') and w.isMinimized:
                        continue
                    items.append((w.title, w))
                except Exception:
                    continue
            seen = set(); self._win_map = []
            for title, w in items:
                key = title.strip()
                if key in seen:
                    continue
                seen.add(key)
                self.window_list.addItem(title)
                self._win_map.append(w)
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Falha ao listar janelas: {e}")

    def _selected_window_region(self) -> CaptureRegion | None:
        if not HAVE_GW or not self.mode_window.isChecked():
            return None
        row = self.window_list.currentRow()
        if row < 0 or row >= len(getattr(self, '_win_map', [])):
            return None
        w = self._win_map[row]
        try:
            left, top = int(w.left), int(w.top)
            width, height = int(w.width), int(w.height)
            return CaptureRegion(left, top, width, height)
        except Exception:
            try:
                bx = w.box
                if len(bx) == 4:
                    l, t, a, b = bx
                    if a > 0 and b > 0 and (a > l and b > t):
                        width = int(a - l); height = int(b - t)
                        return CaptureRegion(int(l), int(t), width, height)
                    else:
                        return CaptureRegion(int(l), int(t), int(a), int(b))
            except Exception:
                return None

    def open_region_overlay(self):
        if self.rec_thread is not None:
            QMessageBox.information(self, "Info", "Pare a gravação antes de selecionar uma região.")
            return
        overlay = RegionOverlay(self)
        overlay.region_selected.connect(self._set_region_from_overlay)
        overlay.showFullScreen()

    def _set_region_from_overlay(self, left, top, width, height):
        if width < 10 or height < 10:
            QMessageBox.information(self, "Info", "Região demasiado pequena.")
            return
        self.selected_region = CaptureRegion(left, top, width, height)
        QMessageBox.information(self, "Região", f"Selecionada: {width}x{height} @ ({left},{top})")

    def clear_region(self):
        self.selected_region = None
        QMessageBox.information(self, "Região", "Região limpa. A usar ecrã inteiro/janela.")

    def _parse_resolution(self) -> Optional[Tuple[int, int]]:
        text = self.res_combo.currentText()
        if "x" not in text:
            return None
        try:
            w, h = text.split("x")
            return (int(w), int(h))
        except Exception:
            return None

    def start_recording(self):
        if self.rec_thread is not None:
            QMessageBox.information(self, "Info", "Já está a gravar.")
            return
        path = self.filename_edit.text().strip() or self.output_path
        if not path:
            QMessageBox.warning(self, "Aviso", "Escolha o ficheiro de saída.")
            return
        fps = self.fps_spin.value()
        codec = self.codec_combo.currentText()
        out_size = self._parse_resolution()

        # determinar modo e região
        if self.mode_camera.isChecked():
            mode = 'camera'; region = None
        elif self.mode_window.isChecked():
            mode = 'window'; region = self._selected_window_region()
            if region is None:
                QMessageBox.warning(self, "Aviso", "Selecione uma janela válida ou use Ecrã inteiro.")
                return
        else:
            mode = 'screen'; region = self.selected_region  # pode ser None → ecrã inteiro

        # ficheiro temporário de vídeo para permitir mux posterior
        base, ext = os.path.splitext(path)
        self.temp_video_path = os.path.join(tempfile.gettempdir(), f"qtrec_video_{int(time.time())}{ext or '.mp4'}")

        # construir thread de vídeo
        self._running_flag.set()
        self.rec_thread = RecorderThread(
            mode=mode,
            file_path=self.temp_video_path,
            fps=fps,
            camera_index=self.cam_index.value(),
            region=region,
            codec=codec,
            out_size=out_size,
            preview_buf=self.preview_buf,
            running_flag=self._running_flag,
        )

        # áudio
        if HAVE_SD and self.audio_enable.isChecked():
            device = self.audio_dev.currentData()
            ch = 1 if self.audio_ch.currentIndex() == 0 else 2
            self.audio_thread = AudioRecorder(samplerate=self.audio_sr.value(), channels=ch, device=device)
        else:
            self.audio_thread = None

        # UI
        self._set_controls_running(True)

        # start threads
        self.rec_thread.start()
        if self.audio_thread is not None:
            self.audio_thread.start()

    def stop_recording(self):
        if self.rec_thread is None:
            return
        # sinalizar paragem
        self._running_flag.clear()
        self.rec_thread.stop()
        if self.audio_thread is not None:
            self.audio_thread.stop()
        # esperar
        self.rec_thread.join(timeout=5)
        if self.audio_thread is not None:
            self.audio_thread.join(timeout=5)
        # mux/encode final
        final_path = self.filename_edit.text().strip() or self.output_path
        self._mux_or_copy(final_path)
        # limpar estado
        self.rec_thread = None
        self.audio_thread = None
        self._set_controls_running(False)
        QMessageBox.information(self, "Info", f"Gravação finalizada: {final_path}")

    def _mux_or_copy(self, final_path: str):
        # Sem ffmpeg, copia o vídeo temporário para o destino
        if not self.temp_video_path or not os.path.exists(self.temp_video_path):
            return
        have_ffmpeg = self._has_ffmpeg()
        try:
            if have_ffmpeg:
                args = ["ffmpeg", "-y", "-i", self.temp_video_path]
                if self.audio_thread is not None and os.path.exists(self.audio_thread.wav_path):
                    args += ["-i", self.audio_thread.wav_path]
                    if self.reencode_cb.isChecked():
                        # re‑encode para aplicar bitrate
                        kbps = self.bitrate_spin.value()
                        args += ["-c:v", "libx264", "-b:v", f"{kbps}k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k"]
                    else:
                        args += ["-c:v", "copy", "-c:a", "aac", "-b:a", "160k"]
                else:
                    if self.reencode_cb.isChecked():
                        kbps = self.bitrate_spin.value()
                        args += ["-c:v", "libx264", "-b:v", f"{kbps}k", "-pix_fmt", "yuv420p"]
                    else:
                        args += ["-c", "copy"]
                args += [final_path]
                subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # sem ffmpeg: apenas copia
                if final_path != self.temp_video_path:
                    try:
                        import shutil
                        shutil.copyfile(self.temp_video_path, final_path)
                    except Exception:
                        pass
        finally:
            # limpar temporários
            try:
                os.remove(self.temp_video_path)
            except Exception:
                pass
            if self.audio_thread is not None:
                try:
                    os.remove(self.audio_thread.wav_path)
                except Exception:
                    pass

    def _has_ffmpeg(self) -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def _set_controls_running(self, running: bool):
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.exit_btn.setEnabled(not running)
        self.mode_camera.setEnabled(not running)
        self.mode_screen.setEnabled(not running)
        self.mode_window.setEnabled(not running)
        self.window_list.setEnabled(not running and HAVE_GW)
        self.refresh_btn.setEnabled(not running and HAVE_GW)
        self.fps_spin.setEnabled(not running)
        self.cam_index.setEnabled(not running)
        self.codec_combo.setEnabled(not running)
        self.res_combo.setEnabled(not running)
        self.bitrate_spin.setEnabled(not running)
        self.audio_enable.setEnabled(not running and HAVE_SD)
        self.audio_sr.setEnabled(not running and HAVE_SD)
        self.audio_ch.setEnabled(not running and HAVE_SD)
        self.audio_dev.setEnabled(not running and HAVE_SD)
        self.reencode_cb.setEnabled(not running)
        self.select_region_btn.setEnabled(not running)
        self.clear_region_btn.setEnabled(not running)

    def _tick(self):
        self._update_preview()


def main():
    app = QApplication(sys.argv)
    w = RecorderApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
