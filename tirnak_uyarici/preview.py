"""Önizleme penceresi: kamera görüntüsü üzerinde algılanan noktaları gösterir."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent, QImage, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from . import APP_NAME
from .detector import Detection

GREEN = (80, 200, 80)
RED = (40, 40, 230)
YELLOW = (0, 210, 255)


def draw_preview(
    frame_bgr: np.ndarray, detection: Detection, ratio: Optional[float], threshold: float
) -> np.ndarray:
    """Görüntünün kopyası üzerine ağız, parmak uçları ve oranı çizer."""
    image = frame_bgr.copy()
    is_near = ratio is not None and ratio <= threshold
    face = detection.observation.face
    if face is not None:
        for x, y in face.mouth_points:
            cv2.circle(image, (int(x), int(y)), 3, RED if is_near else YELLOW, -1)
    for hand in detection.hand_points:
        for x, y in hand:
            cv2.circle(image, (int(x), int(y)), 2, GREEN, -1)
    for hand in detection.observation.hands:
        for x, y in hand.fingertips:
            cv2.circle(image, (int(x), int(y)), 6, RED if is_near else GREEN, 2)

    ratio_text = "-" if ratio is None else f"{ratio:.2f}"
    label = f"Oran: {ratio_text}  Esik: {threshold:.2f}"  # OpenCV yazı tipi Türkçe karakter desteklemiyor
    cv2.putText(image, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
    cv2.putText(image, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    if face is None:
        cv2.putText(image, "Yuz bulunamadi", (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
    return image


def to_qimage(frame_bgr: np.ndarray) -> QImage:
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    height, width = rgb.shape[:2]
    # copy(): QImage numpy belleğini paylaşmasın, iş parçacıkları arası güvenli olsun.
    return QImage(rgb.data, width, height, 3 * width, QImage.Format.Format_RGB888).copy()


class PreviewWindow(QWidget):
    closed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} – Kamera önizleme")
        self._image = QLabel("Kamera başlatılıyor…")
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setMinimumSize(640, 480)
        hint = QLabel(
            "Kırmızı noktalar: el ağıza yeterince yakın. Oran eşiğin altına düşüp "
            "bir süre kalınca uyarı verilir. Hassasiyeti Ayarlar'dan değiştirebilirsin."
        )
        hint.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._image)
        layout.addWidget(hint)

    def show_frame(self, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image).scaled(
            self._image.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image.setPixmap(pixmap)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit()
        super().closeEvent(event)
