"""Paketlenmiş exe'nin kamera açmadan sınanması: TirnakUyarici.exe --self-test

Tüm modüllerin pakete girdiğini ve modellerin yüklenip çalıştığını doğrular;
derleme hattı her exe'yi bununla sınar.
"""

from __future__ import annotations

import logging

SELF_TEST_FLAG = "--self-test"
FRAME_SHAPE = (480, 640, 3)

logger = logging.getLogger(__name__)


def run_self_test() -> int:
    try:
        import numpy as np

        from . import tray_app  # noqa: F401  Arayüz modülleri de pakette mi?
        from .detector import HandFaceDetector

        detector = HandFaceDetector()
        try:
            detector.detect(np.zeros(FRAME_SHAPE, np.uint8), 0)
        finally:
            detector.close()
    except Exception:  # Eksik modül dahil her hata, çıkış koduyla bildirilsin.
        logger.exception("Kendi kendini sınama başarısız")
        return 1
    logger.info("Kendi kendini sınama başarılı")
    return 0
