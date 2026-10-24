import numpy as np
import pytest

from tirnak_uyarici.alert_overlay import PULSE_COUNT, AlertController, _pulse
from tirnak_uyarici.config import Settings
from tirnak_uyarici.detector import Detection
from tirnak_uyarici.gesture_logic import FaceInfo, HandInfo, Observation
from tirnak_uyarici.preview import draw_preview, to_qimage


def test_pulse_starts_and_ends_dark_and_peaks_each_cycle():
    assert _pulse(0.0) == pytest.approx(0.0)
    peaks = [(i + 0.5) / PULSE_COUNT for i in range(PULSE_COUNT)]
    assert all(_pulse(p) == pytest.approx(1.0) for p in peaks)
    assert all(0.0 <= _pulse(x / 100) <= 1.0 for x in range(101))


def test_draw_preview_returns_annotated_copy_without_touching_input():
    frame = np.zeros((480, 640, 3), np.uint8)
    detection = Detection(
        observation=Observation(
            hands=(HandInfo(fingertips=((300.0, 400.0),), palm_length=100.0),),
            face=FaceInfo(mouth_points=((300.0, 402.0),), eye_distance=100.0),
        ),
        hand_points=(((300.0, 400.0), (310.0, 410.0)),),
    )
    annotated = draw_preview(frame, detection, ratio=0.02, threshold=0.35)
    assert frame.sum() == 0
    assert annotated.sum() > 0
    assert annotated.shape == frame.shape


def test_draw_preview_handles_missing_face_and_ratio():
    frame = np.zeros((120, 160, 3), np.uint8)
    detection = Detection(observation=Observation(), hand_points=())
    assert draw_preview(frame, detection, ratio=None, threshold=0.35).shape == frame.shape


def test_to_qimage_keeps_size(qapp):
    image = to_qimage(np.zeros((48, 64, 3), np.uint8))
    assert (image.width(), image.height()) == (64, 48)


def test_alert_controller_creates_overlay_per_screen_and_ignores_overlap(qapp):
    controller = AlertController()
    controller.flash()
    assert controller.is_active
    overlays = list(controller._overlays)
    assert len(overlays) == len(qapp.screens())
    controller.flash()  # Parlama sürerken ikinci çağrı yeni pencere açmamalı.
    assert controller._overlays == overlays
    controller._animation.stop()
    controller._on_finished()
    assert not controller.is_active


def test_settings_dialog_returns_edited_values(qapp):
    from tirnak_uyarici.settings_dialog import SettingsDialog

    dialog = SettingsDialog(Settings())
    dialog._camera.setValue(2)
    dialog._sensitivity.setValue(9)
    dialog._sound.setChecked(False)
    result = dialog.result_settings()
    assert result.camera_index == 2
    assert result.sensitivity == 9
    assert result.sound_enabled is False
