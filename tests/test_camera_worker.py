import itertools

import numpy as np
import pytest

from tirnak_uyarici import camera_worker
from tirnak_uyarici.camera_worker import CameraWorker
from tirnak_uyarici.config import Settings
from tirnak_uyarici.detector import Detection
from tirnak_uyarici.gesture_logic import FaceInfo, HandInfo, Observation

FRAME = np.zeros((480, 640, 3), np.uint8)
AT_MOUTH = Detection(
    observation=Observation(
        hands=(HandInfo(fingertips=((300.0, 400.0),), palm_length=100.0),),
        face=FaceInfo(mouth_points=((300.0, 402.0),), eye_distance=100.0),
    ),
    hand_points=(),
)


class FakeCapture:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok

    def read(self):
        return self.ok, FRAME if self.ok else None


class StopAfter:
    """Belirli sayıda kareden sonra iş parçacığına durmasını söyleyen sahte dedektör."""

    def __init__(self, worker: CameraWorker, frames: int) -> None:
        self.worker = worker
        self.remaining = frames

    def detect(self, rgb, timestamp_ms):
        self.remaining -= 1
        if self.remaining <= 0:
            self.worker._stop_requested = True
        return AT_MOUTH


@pytest.fixture
def fast_clock(monkeypatch):
    ticks = itertools.count(0.0, 0.1)
    monkeypatch.setattr(camera_worker.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(camera_worker.time, "sleep", lambda _: None)


def test_worker_emits_alert_and_preview_frames(qapp, fast_clock):
    worker = CameraWorker(Settings(hold_seconds=0.3))
    worker.set_preview_enabled(True)
    alerts, frames = [], []
    worker.alert_triggered.connect(lambda: alerts.append(1))
    worker.frame_ready.connect(frames.append)

    worker._process_frames(FakeCapture(), StopAfter(worker, frames=10))

    assert len(alerts) == 1
    assert len(frames) == 10


def test_worker_raises_after_repeated_read_failures(qapp, fast_clock):
    worker = CameraWorker(Settings())
    with pytest.raises(RuntimeError, match="görüntü alınamıyor"):
        worker._process_frames(FakeCapture(ok=False), StopAfter(worker, frames=10**6))


def test_run_reports_failure_instead_of_crashing(qapp, monkeypatch):
    def broken_open(index):
        raise RuntimeError("Kamera açılamadı")

    monkeypatch.setattr(camera_worker, "open_camera", broken_open)
    worker = CameraWorker(Settings())
    messages = []
    worker.failed.connect(messages.append)
    worker.run()
    assert messages == ["Kamera açılamadı"]
