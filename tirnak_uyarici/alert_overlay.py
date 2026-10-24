"""Tüm pencerelerin üstünde, tıklamaları engellemeyen kırmızı parlama uyarısı."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QObject, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPaintEvent, QPen, QScreen
from PySide6.QtWidgets import QWidget

ALERT_TEXT = "Elini ağzından çek!"
FLASH_DURATION_MS = 1800
PULSE_COUNT = 2
BORDER_WIDTH = 28
MAX_TINT_ALPHA = 70
MAX_BORDER_ALPHA = 230
TEXT_POINT_SIZE = 48


class FlashOverlay(QWidget):
    """Tek bir ekranı kaplayan yarı saydam kırmızı katman."""

    def __init__(self, screen: QScreen) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setGeometry(screen.geometry())
        self._intensity = 0.0

    def set_intensity(self, value: float) -> None:
        self._intensity = max(0.0, min(value, 1.0))
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        painter.fillRect(rect, QColor(220, 0, 0, int(MAX_TINT_ALPHA * self._intensity)))

        pen = QPen(QColor(255, 0, 0, int(MAX_BORDER_ALPHA * self._intensity)), BORDER_WIDTH)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        half = BORDER_WIDTH / 2
        painter.drawRect(rect.adjusted(half, half, -half, -half))

        font = QFont()
        font.setPointSize(TEXT_POINT_SIZE)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0, int(160 * self._intensity)))
        painter.drawText(rect.translated(3, 3), Qt.AlignmentFlag.AlignCenter, ALERT_TEXT)
        painter.setPen(QColor(255, 255, 255, int(255 * self._intensity)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, ALERT_TEXT)


def _pulse(progress: float) -> float:
    """0→1 ilerlemeyi PULSE_COUNT kez 0→1→0 parlamaya çevirir."""
    phase = (progress * PULSE_COUNT) % 1.0
    return 1.0 - abs(phase * 2.0 - 1.0)


class AlertController(QObject):
    """Her ekranda bir parlama penceresi açar ve canlandırır."""

    def __init__(self) -> None:
        super().__init__()
        self._overlays: list[FlashOverlay] = []
        self._animation: QVariantAnimation | None = None

    @property
    def is_active(self) -> bool:
        return self._animation is not None

    def flash(self) -> None:
        if self.is_active:
            return
        # Ekranlar değişmiş olabilir (monitör takılıp çıkarılmış); her seferinde yeniden oluştur.
        self._overlays = [FlashOverlay(screen) for screen in QGuiApplication.screens()]
        for overlay in self._overlays:
            overlay.show()
            overlay.raise_()

        animation = QVariantAnimation(self)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setDuration(FLASH_DURATION_MS)
        animation.setEasingCurve(QEasingCurve.Type.Linear)
        animation.valueChanged.connect(self._on_progress)
        animation.finished.connect(self._on_finished)
        self._animation = animation
        animation.start()

    def _on_progress(self, progress: float) -> None:
        intensity = _pulse(float(progress))
        for overlay in self._overlays:
            overlay.set_intensity(intensity)

    def _on_finished(self) -> None:
        for overlay in self._overlays:
            overlay.close()
        self._overlays = []
        if self._animation is not None:
            self._animation.deleteLater()
        self._animation = None
