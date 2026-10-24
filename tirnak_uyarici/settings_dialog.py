"""Ayarlar penceresi."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QWidget,
)

from . import APP_NAME
from .config import SENSITIVITY_MAX, SENSITIVITY_MIN, Settings
from .platform_utils import autostart_supported


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} – Ayarlar")
        self._original = settings

        self._camera = QSpinBox()
        self._camera.setRange(0, 9)
        self._camera.setValue(settings.camera_index)
        self._camera.setToolTip("Birden fazla kameran varsa 1, 2… dene. Genelde 0 doğrudur.")

        self._sensitivity = QSlider(Qt.Orientation.Horizontal)
        self._sensitivity.setRange(SENSITIVITY_MIN, SENSITIVITY_MAX)
        self._sensitivity.setValue(settings.sensitivity)
        sensitivity_value = QLabel(str(settings.sensitivity))
        self._sensitivity.valueChanged.connect(lambda v: sensitivity_value.setText(str(v)))
        sensitivity_row = QHBoxLayout()
        sensitivity_row.addWidget(QLabel("Düşük"))
        sensitivity_row.addWidget(self._sensitivity)
        sensitivity_row.addWidget(QLabel("Yüksek"))
        sensitivity_row.addWidget(sensitivity_value)

        self._hold = QDoubleSpinBox()
        self._hold.setRange(0.1, 5.0)
        self._hold.setSingleStep(0.1)
        self._hold.setSuffix(" sn")
        self._hold.setValue(settings.hold_seconds)

        self._cooldown = QDoubleSpinBox()
        self._cooldown.setRange(1.0, 60.0)
        self._cooldown.setSingleStep(1.0)
        self._cooldown.setSuffix(" sn")
        self._cooldown.setValue(settings.cooldown_seconds)

        self._sound = QCheckBox("Uyarıda ses çal")
        self._sound.setChecked(settings.sound_enabled)

        self._autostart = QCheckBox("Windows açılınca otomatik başlat")
        self._autostart.setChecked(settings.start_with_windows)
        self._autostart.setEnabled(autostart_supported())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Kaydet")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("İptal")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form = QFormLayout(self)
        form.addRow("Kamera:", self._camera)
        form.addRow("Hassasiyet:", sensitivity_row)
        form.addRow("Uyarı için bekleme:", self._hold)
        form.addRow("Tekrar uyarı aralığı:", self._cooldown)
        form.addRow(self._sound)
        form.addRow(self._autostart)
        form.addRow(buttons)

    def result_settings(self) -> Settings:
        return Settings(
            camera_index=self._camera.value(),
            sensitivity=self._sensitivity.value(),
            hold_seconds=self._hold.value(),
            cooldown_seconds=self._cooldown.value(),
            sound_enabled=self._sound.isChecked(),
            start_with_windows=self._autostart.isChecked(),
        ).validated()
