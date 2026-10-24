"""Uygulamanın giriş noktası."""

from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from . import APP_ID, APP_NAME
from .config import config_dir, load_settings
from .tray_app import TrayApp

LOCK_TIMEOUT_MS = 0


def setup_logging() -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        config_dir().mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(config_dir() / "uygulama.log", encoding="utf-8"))
    except OSError:
        pass  # Günlük dosyası olmadan da çalışabilir; konsol günlüğü yeterli.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )


def main() -> int:
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ID)
    app.setQuitOnLastWindowClosed(False)

    # Aynı anda iki kopya kamerayı paylaşmaya çalışmasın.
    config_dir().mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(config_dir() / "calisiyor.lock"))
    if not lock.tryLock(LOCK_TIMEOUT_MS):
        QMessageBox.information(None, APP_NAME, f"{APP_NAME} zaten çalışıyor.")
        return 0

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, APP_NAME, "Sistem tepsisi bulunamadı; uygulama çalışamıyor.")
        return 1

    tray = TrayApp(app, load_settings())
    tray.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
