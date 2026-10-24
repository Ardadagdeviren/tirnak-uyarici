"""Paketlenmiş (.exe) ve geliştirme ortamında dosya yollarını çözer."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return Path(bundle_dir)
    return Path(__file__).resolve().parent.parent


def model_path(name: str) -> Path:
    return resource_root() / "models" / name


def read_model(name: str) -> bytes:
    """Modeli bayt olarak okur.

    MediaPipe, Windows'ta Türkçe/ASCII dışı karakter içeren yollardan model
    yükleyemeyebiliyor; bayt olarak vermek bu sorunu ortadan kaldırır.
    """
    path = model_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Model dosyası bulunamadı: {path}")
    return path.read_bytes()
