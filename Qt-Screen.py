# -*- coding: utf-8 -*-
"""
Qt Screen/Camera Recorder (Windows 10, Ubuntu, macOS)

Dependencies (Python 3.9+ recommended):
    pip install PyQt6 opencv-python mss numpy pygetwindow

Notes:
- On macOS, grant the terminal/python app Screen Recording permission in System Settings > Privacy & Security.
- Window capture relies on pygetwindow where supported. If unavailable on your OS/WM, use Full Screen mode.
- Default output is MP4 (mp4v). You can change codec/container if needed.
"""

import sys
import time
import threading
from dataclasses import dataclass

import numpy as np
import cv2

# Qt
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QHBoxLayout,
    QVBoxLayout, QGroupBox, QRadioButton, QListWidget, QMessageBox,
    QSpinBox, QComboBox, QFormLayout, QLineEdit
)

# Screen capture
from mss import mss

# Window enumeration (optional, best-effort cross-platform)
try:
    import pygetwindow as gw  # type: ignore
    HAVE_GW = True
except Exception:
    HAVE_GW = False


@dataclass
class CaptureRegion:
    left: int
    top: int
    width: int
    height: int


class RecorderThread(threading.Thread):
    def __init__(self, *, mode: str, file_path: str, fps: int = 20,
                 camera_index: int = 0, region: CaptureRegion | None = None,
                 codec: str = 'mp4v', on_finish=None):
        super().__init__(daemon=True)
        self.mode = mode            # 'camera' | 'screen' | 'window'
        self.file_path = file_path
        self.fps = max(1, int(fps))
        self.camera_index = camera_index
        self.region = region
        self.codec = codec
        self._running = threading.Event()
        self._running.set()
        self.on_finish = on_finish

    def stop(self):
        self._running.clear()

    def run(self):
        try:
            if self.mode == 'camera':
                self._record_camera()
            else:
                self._record_screen_like()
        finally:
            if callable(self.on_finish):
                self.on_finish()

    # --- Helpers ---
    def _open_writer(self, size_wh: tuple[int, int]):
        fourcc = cv2.VideoWriter_fourcc(*self.codec.upper())
        writer = cv2.VideoWriter(self.file_path, fourcc, float(self.fps), size_wh)
        if not writer.isOpened():
            raise RuntimeError("Não foi possível abrir o VideoWriter. Tente outro codec/ficheiro.")
        return writer

    def _record_camera(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Não foi possível acessar a câmera (índice %d)." % self.camera_index)

        # Determine frame size
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        writer = self._open_writer((width, height))

        frame_interval = 1.0 / self.fps
        try:
            while self._running.is_set():
                t0 = time.perf_counter()
                ok, frame = cap.read()
                if not ok:
                    break
                # frame is already BGR
                writer.write(frame)
                # pacing
                dt = time.perf_counter() - t0
                to_wait = frame_interval - dt
                if to_wait > 0:
                    time.sleep(to_wait)
        finally:
            cap.release()
            writer.release()

    def _record_screen_like(self):
        # Determine region for screen/window
        with mss() as sct:
            if self.region is None:
                # Primary monitor (index 1 in mss)
                mon = sct.monitors[1]
                region = CaptureRegion(mon['left'], mon['top'], mon['width'], mon['height'])
            else:
                region = self.region

            monitor = {
                'left': int(region.left),
                'top': int(region.top),
                'width': int(region.width),
                'height': int(region.height)
            }

            writer = self._open_writer((monitor['width'], monitor['height']))
            frame_interval = 1.0 / self.fps

            try:
                while self._running.is_set():
                    t0 = time.perf_counter()
                    img = sct.grab(monitor)        # BGRA
                    frame = np.array(img)
                    frame = frame[:, :, :3]        # BGR (drop alpha)
                    writer.write(frame)

                    dt = time.perf_counter() - t0
                    to_wait = frame_interval - dt
                    if to_wait > 0:
                        time.sleep(to_wait)
            finally:
                writer.release()


class RecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gravador de Ecrã/Câmera (Qt)")
        self.setMinimumWidth(640)

        # State
        self.output_path: str = ''
        self.rec_thread: RecorderThread | None = None

        # --- UI ---
        self.mode_camera = QRadioButton("Câmara USB")
        self.mode_screen = QRadioButton("Ecrã inteiro")
        self.mode_window = QRadioButton("Janela específica")
        self.mode_camera.setChecked(True)

        mode_box = QGroupBox("Fonte de gravação")
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.mode_camera)
        mode_layout.addWidget(self.mode_screen)
        mode_layout.addWidget(self.mode_window)
        mode_box.setLayout(mode_layout)

        self.window_list = QListWidget()
        self.window_list.setMinimumHeight(140)

        self.refresh_btn = QPushButton("Atualizar janelas")
        self.refresh_btn.clicked.connect(self.refresh_windows)
        if not HAVE_GW:
            self.mode_window.setEnabled(False)
            self.window_list.setEnabled(False)
            self.refresh_btn.setEnabled(False)

        # Settings box
        settings_box = QGroupBox("Definições")
        form = QFormLayout()

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(20)
        form.addRow("FPS:", self.fps_spin)

        self.cam_index = QSpinBox()
        self.cam_index.setRange(0, 10)
        self.cam_index.setValue(0)
        form.addRow("Índice da câmara:", self.cam_index)

        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["mp4v", "XVID", "MJPG", "H264"])  # availability depends on system
        form.addRow("Codec:", self.codec_combo)

        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("Escolha o ficheiro de saída (.mp4)")
        choose_btn = QPushButton("Escolher ficheiro…")
        choose_btn.clicked.connect(self.choose_file)
        h = QHBoxLayout()
        h.addWidget(self.filename_edit)
        h.addWidget(choose_btn)
        form.addRow("Saída:", h)

        settings_box.setLayout(form)

        # Controls
        self.start_btn = QPushButton("Gravar")
        self.stop_btn = QPushButton("Parar")
        self.stop_btn.setEnabled(False)
        self.exit_btn = QPushButton("Sair")

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.exit_btn.clicked.connect(self.close)

        # Layout
        left_col = QVBoxLayout()
        left_col.addWidget(mode_box)
        left_col.addWidget(self.window_list)
        left_col.addWidget(self.refresh_btn)

        right_col = QVBoxLayout()
        right_col.addWidget(settings_box)
        right_col.addStretch(1)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.exit_btn)
        right_col.addLayout(btn_row)

        root = QHBoxLayout()
        root.addLayout(left_col, 1)
        root.addLayout(right_col, 2)
        self.setLayout(root)

        # timers
        self.ui_pulse = QTimer(self)
        self.ui_pulse.setInterval(500)
        self.ui_pulse.timeout.connect(self._tick)
        self.ui_pulse.start()

        self.refresh_windows()

    # --- UI logic ---
    def choose_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar vídeo", "output.mp4", "Vídeo MP4 (*.mp4);;AVI (*.avi)")
        if path:
            self.output_path = path
            self.filename_edit.setText(path)
            # Heuristic: switch codec by extension
            if path.lower().endswith('.avi'):
                idx = self.codec_combo.findText('XVID')
                if idx >= 0:
                    self.codec_combo.setCurrentIndex(idx)
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
            # Filter decent entries
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
            # Unique by title (best-effort)
            seen = set()
            self._win_map = []
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
            # pygetwindow exposes .left/.top/.width/.height on Windows; .box may vary
            left, top = int(w.left), int(w.top)
            width, height = int(w.width), int(w.height)
            return CaptureRegion(left, top, width, height)
        except Exception:
            # Fallback using box (left, top, right, bottom)
            try:
                bx = w.box  # (left, top, width, height) in some versions; or (x, y, r, b)
                if len(bx) == 4:
                    l, t, a, b = bx
                    # Heuristic: if a<b assume (r,b)
                    if a > 0 and b > 0 and (a > l and b > t):
                        width = int(a - l)
                        height = int(b - t)
                        return CaptureRegion(int(l), int(t), width, height)
                    else:
                        return CaptureRegion(int(l), int(t), int(a), int(b))
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

        if self.mode_camera.isChecked():
            mode = 'camera'
            region = None
        elif self.mode_window.isChecked():
            mode = 'window'
            region = self._selected_window_region()
            if region is None:
                QMessageBox.warning(self, "Aviso", "Selecione uma janela válida ou use Ecrã inteiro.")
                return
        else:
            mode = 'screen'
            region = None

        # Build thread
        self.rec_thread = RecorderThread(
            mode=mode,
            file_path=path,
            fps=fps,
            camera_index=self.cam_index.value(),
            region=region,
            codec=codec,
            on_finish=self._on_recording_finished
        )
        self._set_controls_running(True)
        self.rec_thread.start()

    def stop_recording(self):
        if self.rec_thread is not None:
            self.rec_thread.stop()

    def _on_recording_finished(self):
        # Called from worker thread; marshal to GUI thread via single-shot timer
        QTimer.singleShot(0, self._finish_ui)

    def _finish_ui(self):
        self.rec_thread = None
        self._set_controls_running(False)
        QMessageBox.information(self, "Info", "Gravação finalizada.")

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

    def _tick(self):
        # Keep UI responsive; could be used for future stats
        pass


def main():
    app = QApplication(sys.argv)
    w = RecorderApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
