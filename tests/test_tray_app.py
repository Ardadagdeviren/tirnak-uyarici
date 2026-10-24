import pytest
from PySide6.QtCore import QObject, Signal

from tirnak_uyarici import tray_app
from tirnak_uyarici.config import Settings


class FakeWorker(QObject):
    alert_triggered = Signal()
    frame_ready = Signal(object)
    failed = Signal(str)
    instances: list["FakeWorker"] = []

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.preview = False
        self.started = False
        self.stopped = False
        FakeWorker.instances.append(self)

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def update_settings(self, settings):
        self.settings = settings

    def set_preview_enabled(self, enabled):
        self.preview = enabled


@pytest.fixture
def app_under_test(qapp, monkeypatch):
    FakeWorker.instances = []
    calls = {"sound": 0, "flash": 0, "saved": [], "autostart": []}
    monkeypatch.setattr(tray_app, "CameraWorker", FakeWorker)
    monkeypatch.setattr(tray_app, "play_alert_sound", lambda: calls.__setitem__("sound", calls["sound"] + 1))
    monkeypatch.setattr(tray_app, "save_settings", lambda s: calls["saved"].append(s))
    monkeypatch.setattr(tray_app, "set_autostart", lambda e: calls["autostart"].append(e))
    tray = tray_app.TrayApp(qapp, Settings())
    monkeypatch.setattr(tray._alerts, "flash", lambda: calls.__setitem__("flash", calls["flash"] + 1))
    tray.start()
    yield tray, calls
    tray.stop_detection()


def test_start_launches_worker(app_under_test):
    tray, _ = app_under_test
    assert tray.is_running
    assert FakeWorker.instances[-1].started


def test_toggle_pauses_and_resumes(app_under_test):
    tray, _ = app_under_test
    first = FakeWorker.instances[-1]
    tray.toggle_running()
    assert not tray.is_running and first.stopped
    assert tray._toggle_action.text() == "Devam et"
    tray.toggle_running()
    assert tray.is_running and FakeWorker.instances[-1] is not first
    assert tray._toggle_action.text() == "Duraklat"


def test_alert_flashes_and_plays_sound_only_when_enabled(app_under_test):
    tray, calls = app_under_test
    FakeWorker.instances[-1].alert_triggered.emit()
    assert calls == {**calls, "flash": 1, "sound": 1}
    tray._apply_settings(Settings(sound_enabled=False))
    tray.trigger_alert()
    assert calls["flash"] == 2 and calls["sound"] == 1


def test_camera_change_restarts_worker(app_under_test):
    tray, calls = app_under_test
    first = FakeWorker.instances[-1]
    tray._apply_settings(Settings(camera_index=1))
    assert first.stopped
    assert FakeWorker.instances[-1].settings.camera_index == 1
    assert calls["saved"][-1].camera_index == 1


def test_other_settings_update_running_worker(app_under_test):
    tray, calls = app_under_test
    worker = FakeWorker.instances[-1]
    tray._apply_settings(Settings(sensitivity=9, start_with_windows=True))
    assert not worker.stopped and worker.settings.sensitivity == 9
    assert calls["autostart"] == [True]


def test_worker_failure_pauses_and_shows_error_status(app_under_test):
    tray, _ = app_under_test
    FakeWorker.instances[-1].failed.emit("Kamera açılamadı")
    assert not tray.is_running
    assert "hata" in tray._status_action.text()


def test_preview_enables_frames_and_closing_disables_them(app_under_test):
    tray, _ = app_under_test
    worker = FakeWorker.instances[-1]
    tray.show_preview()
    assert worker.preview
    tray._preview.close()
    assert not worker.preview
