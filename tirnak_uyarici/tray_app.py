"""Sistem tepsisi simgesi ve uygulamanın parçalarını birbirine bağlayan denetleyici."""

from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import APP_NAME
from .alert_overlay import AlertController
from .camera_worker import CameraWorker
from .config import Settings, save_settings
from .platform_utils import play_alert_sound, set_autostart
from .preview import PreviewWindow
from .settings_dialog import SettingsDialog

logger = logging.getLogger(__name__)

ICON_SIZE = 64


def make_icon(color: QColor) -> QIcon:
    pixmap = QPixmap(ICON_SIZE, ICON_SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, ICON_SIZE - 8, ICON_SIZE - 8)
    painter.setBrush(QColor("white"))
    painter.drawRoundedRect(18, 34, 28, 10, 5, 5)  # Basit bir ağız çizgisi
    painter.end()
    return QIcon(pixmap)


ACTIVE_ICON_COLOR = QColor(220, 40, 40)
PAUSED_ICON_COLOR = QColor(140, 140, 140)


class TrayApp(QObject):
    def __init__(self, app: QApplication, settings: Settings) -> None:
        super().__init__()
        self._app = app
        self._settings = settings
        self._worker: Optional[CameraWorker] = None
        self._preview: Optional[PreviewWindow] = None
        self._alerts = AlertController()

        self._active_icon = make_icon(ACTIVE_ICON_COLOR)
        self._paused_icon = make_icon(PAUSED_ICON_COLOR)
        self._tray = QSystemTrayIcon(self._active_icon)
        self._tray.setContextMenu(self._build_menu())
        self._tray.activated.connect(self._on_tray_activated)
        app.setWindowIcon(self._active_icon)

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        self._status_action = QAction("Durum: başlatılıyor…")
        self._status_action.setEnabled(False)
        self._toggle_action = QAction("Duraklat")
        self._toggle_action.triggered.connect(self.toggle_running)
        preview_action = QAction("Kamera önizlemesi…")
        preview_action.triggered.connect(self.show_preview)
        test_action = QAction("Uyarıyı test et")
        test_action.triggered.connect(self.trigger_alert)
        settings_action = QAction("Ayarlar…")
        settings_action.triggered.connect(self.show_settings)
        quit_action = QAction("Çıkış")
        quit_action.triggered.connect(self.quit)

        self._actions = [
            self._status_action,
            self._toggle_action,
            preview_action,
            test_action,
            settings_action,
            quit_action,
        ]
        menu.addAction(self._status_action)
        menu.addSeparator()
        for action in self._actions[1:-1]:
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self._menu = menu
        return menu

    @property
    def is_running(self) -> bool:
        return self._worker is not None

    def start(self) -> None:
        self._tray.show()
        self.start_detection()
        self._tray.showMessage(
            APP_NAME,
            "Arka planda çalışıyor. Menü için saatin yanındaki simgeye sağ tıkla.",
            QSystemTrayIcon.MessageIcon.Information,
            4000,
        )

    def start_detection(self) -> None:
        if self._worker is not None:
            return
        worker = CameraWorker(self._settings)
        worker.alert_triggered.connect(self.trigger_alert)
        worker.failed.connect(self._on_worker_failed)
        worker.frame_ready.connect(self._on_frame)
        worker.set_preview_enabled(self._preview is not None and self._preview.isVisible())
        self._worker = worker
        worker.start()
        self._set_status(True, "Durum: izleniyor")

    def stop_detection(self, status: str = "Durum: duraklatıldı") -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.deleteLater()
            self._worker = None
        self._set_status(False, status)

    def toggle_running(self) -> None:
        if self.is_running:
            self.stop_detection()
        else:
            self.start_detection()

    def trigger_alert(self) -> None:
        self._alerts.flash()
        if self._settings.sound_enabled:
            play_alert_sound()

    def show_preview(self) -> None:
        if self._preview is None:
            self._preview = PreviewWindow()
            self._preview.closed.connect(self._on_preview_closed)
        self._preview.show()
        self._preview.raise_()
        self._preview.activateWindow()
        if self._worker is not None:
            self._worker.set_preview_enabled(True)

    def show_settings(self) -> None:
        dialog = SettingsDialog(self._settings)
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        self._apply_settings(dialog.result_settings())

    def quit(self) -> None:
        self.stop_detection()
        self._tray.hide()
        self._app.quit()

    def _apply_settings(self, new_settings: Settings) -> None:
        old_settings = self._settings
        self._settings = new_settings
        try:
            save_settings(new_settings)
        except OSError as exc:
            logger.exception("Ayarlar kaydedilemedi")
            self._notify_error(f"Ayarlar kaydedilemedi: {exc}")
        if new_settings.start_with_windows != old_settings.start_with_windows:
            try:
                set_autostart(new_settings.start_with_windows)
            except OSError as exc:
                logger.exception("Otomatik başlatma ayarlanamadı")
                self._notify_error(f"Otomatik başlatma ayarlanamadı: {exc}")

        if self._worker is None:
            return
        if new_settings.camera_index != old_settings.camera_index:
            self.stop_detection()
            self.start_detection()
        else:
            self._worker.update_settings(new_settings)

    def _on_worker_failed(self, message: str) -> None:
        self.stop_detection("Durum: hata – duraklatıldı")
        self._notify_error(f"{message}\nTekrar denemek için menüden 'Devam et'e tıkla.")

    def _on_frame(self, image) -> None:
        if self._preview is not None and self._preview.isVisible():
            self._preview.show_frame(image)

    def _on_preview_closed(self) -> None:
        if self._worker is not None:
            self._worker.set_preview_enabled(False)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_preview()

    def _set_status(self, running: bool, text: str) -> None:
        self._status_action.setText(text)
        self._toggle_action.setText("Duraklat" if running else "Devam et")
        self._tray.setIcon(self._active_icon if running else self._paused_icon)
        self._tray.setToolTip(f"{APP_NAME} – {text.removeprefix('Durum: ')}")

    def _notify_error(self, message: str) -> None:
        self._tray.showMessage(APP_NAME, message, QSystemTrayIcon.MessageIcon.Warning, 8000)
