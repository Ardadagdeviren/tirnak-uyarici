"""Windows'a özgü işler: uyarı sesi ve Windows ile otomatik başlama."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from . import APP_ID

logger = logging.getLogger(__name__)

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
IS_WINDOWS = sys.platform == "win32"


def play_alert_sound() -> None:
    if IS_WINDOWS:
        import winsound

        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    else:
        QApplication.beep()


def autostart_supported() -> bool:
    return IS_WINDOWS


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    interpreter = pythonw if pythonw.exists() else Path(sys.executable)
    return f'"{interpreter}" -m tirnak_uyarici'


def set_autostart(enabled: bool) -> None:
    """Windows açılışında başlatmayı açar/kapatır (HKCU\\...\\Run)."""
    if not IS_WINDOWS:
        return
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_ID, 0, winreg.REG_SZ, _launch_command())
            return
        try:
            winreg.DeleteValue(key, APP_ID)
        except FileNotFoundError:
            pass
