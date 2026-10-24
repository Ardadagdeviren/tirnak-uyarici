"""Kullanıcı ayarları: %APPDATA%\\TirnakUyarici\\config.json içinde saklanır."""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path

from . import APP_ID
from .gesture_logic import DetectionParams

logger = logging.getLogger(__name__)

SENSITIVITY_MIN = 1
SENSITIVITY_MAX = 10
# Hassasiyet 1 → oran 0.20 (sadece dudağa değince), 10 → 0.60 (ağza yaklaşınca).
NEAR_RATIO_AT_MIN = 0.20
NEAR_RATIO_AT_MAX = 0.60


@dataclass(frozen=True)
class Settings:
    camera_index: int = 0
    sensitivity: int = 5
    hold_seconds: float = 0.5
    cooldown_seconds: float = 4.0
    sound_enabled: bool = True
    start_with_windows: bool = False

    def validated(self) -> "Settings":
        """Geçersiz değerleri güvenli aralığa çeker."""
        return replace(
            self,
            camera_index=max(0, min(int(self.camera_index), 9)),
            sensitivity=max(SENSITIVITY_MIN, min(int(self.sensitivity), SENSITIVITY_MAX)),
            hold_seconds=max(0.1, min(float(self.hold_seconds), 5.0)),
            cooldown_seconds=max(1.0, min(float(self.cooldown_seconds), 60.0)),
            sound_enabled=bool(self.sound_enabled),
            start_with_windows=bool(self.start_with_windows),
        )

    def detection_params(self) -> DetectionParams:
        return DetectionParams(
            near_ratio=sensitivity_to_ratio(self.sensitivity),
            hold_seconds=self.hold_seconds,
            cooldown_seconds=self.cooldown_seconds,
        )


def sensitivity_to_ratio(sensitivity: int) -> float:
    span = SENSITIVITY_MAX - SENSITIVITY_MIN
    fraction = (sensitivity - SENSITIVITY_MIN) / span
    return NEAR_RATIO_AT_MIN + fraction * (NEAR_RATIO_AT_MAX - NEAR_RATIO_AT_MIN)


def config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_ID


def config_path() -> Path:
    return config_dir() / "config.json"


def load_settings(path: Path | None = None) -> Settings:
    path = path or config_path()
    if not path.exists():
        return Settings()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Ayar dosyası okunamadı (%s), varsayılanlar kullanılıyor: %s", path, exc)
        return Settings()
    if not isinstance(raw, dict):
        logger.warning("Ayar dosyası beklenen biçimde değil, varsayılanlar kullanılıyor: %s", path)
        return Settings()
    known = {f.name for f in fields(Settings)}
    try:
        return Settings(**{k: v for k, v in raw.items() if k in known}).validated()
    except (TypeError, ValueError) as exc:
        logger.warning("Ayar değerleri geçersiz, varsayılanlar kullanılıyor: %s", exc)
        return Settings()


def save_settings(settings: Settings, path: Path | None = None) -> None:
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")
