"""Kamerayı arka planda okuyup tespiti çalıştıran iş parçacığı."""

from __future__ import annotations

import logging
import sys
import time

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .config import Settings
from .detector import HandFaceDetector
from .gesture_logic import TrackerState, step
from .preview import draw_preview, to_qimage

logger = logging.getLogger(__name__)

TARGET_FPS = 12
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
MAX_READ_FAILURES = 30


def open_camera(index: int) -> cv2.VideoCapture:
    # Windows'ta DirectShow çok daha hızlı açılır; olmazsa varsayılan arka uca düş.
    backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if sys.platform == "win32" else [cv2.CAP_ANY]
    for backend in backends:
        capture = cv2.VideoCapture(index, backend)
        if capture.isOpened():
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return capture
        capture.release()
    raise RuntimeError(
        f"Kamera açılamadı (kamera {index}). Başka bir uygulama kullanıyor olabilir "
        "veya kamera izni kapalı olabilir."
    )


class CameraWorker(QThread):
    alert_triggered = Signal()
    frame_ready = Signal(QImage)
    failed = Signal(str)

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings
        self._preview_enabled = False
        self._stop_requested = False

    def update_settings(self, settings: Settings) -> None:
        self._settings = settings

    def set_preview_enabled(self, enabled: bool) -> None:
        self._preview_enabled = enabled

    def stop(self) -> None:
        self._stop_requested = True
        self.wait()

    def run(self) -> None:
        try:
            self._loop()
        except Exception as exc:  # İş parçacığı sessizce ölmesin, kullanıcıya bildir.
            logger.exception("Kamera döngüsü hata ile durdu")
            self.failed.emit(str(exc))

    def _loop(self) -> None:
        capture = open_camera(self._settings.camera_index)
        detector = HandFaceDetector()
        try:
            self._process_frames(capture, detector)
        finally:
            capture.release()
            detector.close()

    def _process_frames(self, capture: cv2.VideoCapture, detector: HandFaceDetector) -> None:
        state = TrackerState()
        frame_interval = 1.0 / TARGET_FPS
        failures = 0
        while not self._stop_requested:
            started = time.monotonic()
            ok, frame = capture.read()
            if not ok:
                failures += 1
                if failures >= MAX_READ_FAILURES:
                    raise RuntimeError("Kameradan görüntü alınamıyor.")
                time.sleep(frame_interval)
                continue
            failures = 0

            frame = cv2.flip(frame, 1)  # Ayna görüntüsü: önizleme doğal görünsün.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection = detector.detect(rgb, int(started * 1000))
            params = self._settings.detection_params()
            result = step(state, detection.observation, started, params)
            state = result.state

            if result.should_alert:
                self.alert_triggered.emit()
            if self._preview_enabled:
                annotated = draw_preview(frame, detection, result.ratio, params.near_ratio)
                self.frame_ready.emit(to_qimage(annotated))

            remaining = frame_interval - (time.monotonic() - started)
            if remaining > 0:
                time.sleep(remaining)
