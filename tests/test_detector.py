from types import SimpleNamespace

import numpy as np
import pytest

from tirnak_uyarici.detector import (
    FINGERTIPS,
    LEFT_EYE_OUTER,
    MOUTH_LANDMARKS,
    RIGHT_EYE_OUTER,
    HandFaceDetector,
    _face_info,
    _hand_info,
)
from tirnak_uyarici.resources import read_model


def landmark(x, y):
    return SimpleNamespace(x=x, y=y)


def test_face_info_uses_mouth_points_and_eye_distance_in_pixels():
    landmarks = [landmark(0.5, 0.5) for _ in range(478)]
    landmarks[LEFT_EYE_OUTER] = landmark(0.4, 0.3)
    landmarks[RIGHT_EYE_OUTER] = landmark(0.6, 0.3)
    face = _face_info([landmarks], width=1000, height=500)
    assert face.eye_distance == pytest.approx(200.0)
    assert len(face.mouth_points) == len(MOUTH_LANDMARKS)
    assert face.mouth_points[0] == (500.0, 250.0)


def test_face_info_returns_none_without_faces():
    assert _face_info([], 640, 480) is None


def test_hand_info_picks_fingertips_and_palm_length():
    points = tuple((float(i), 0.0) for i in range(21))
    hand = _hand_info(points)
    assert hand.fingertips == tuple(points[i] for i in FINGERTIPS)
    assert hand.palm_length == pytest.approx(9.0)


def test_missing_model_raises_clear_error():
    with pytest.raises(FileNotFoundError, match="Model dosyası bulunamadı"):
        read_model("olmayan.task")


def test_real_models_run_on_blank_frame_and_accept_repeated_timestamps():
    detector = HandFaceDetector()
    try:
        frame = np.zeros((480, 640, 3), np.uint8)
        first = detector.detect(frame, 1000)
        second = detector.detect(frame, 1000)  # Aynı zaman damgası hata vermemeli.
    finally:
        detector.close()
    assert first.observation.hands == () and first.observation.face is None
    assert second.hand_points == ()
