"""MediaPipe ile el ve yüz noktalarını bulup gesture_logic tiplerine çevirir."""

from __future__ import annotations

from dataclasses import dataclass

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

from .gesture_logic import FaceInfo, HandInfo, Observation, Point
from .resources import read_model

HAND_MODEL = "hand_landmarker.task"
FACE_MODEL = "face_landmarker.task"

# MediaPipe el noktaları
WRIST = 0
MIDDLE_MCP = 9
FINGERTIPS = (4, 8, 12, 16, 20)

# MediaPipe yüz noktaları: dudak çevresi ve dış göz köşeleri
MOUTH_LANDMARKS = (0, 13, 14, 17, 61, 291, 37, 267, 84, 314)
LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263

MAX_HANDS = 2


@dataclass(frozen=True)
class Detection:
    observation: Observation
    hand_points: tuple[tuple[Point, ...], ...]


def _to_pixels(landmark, width: int, height: int) -> Point:
    return (landmark.x * width, landmark.y * height)


def _distance(a: Point, b: Point) -> float:
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


class HandFaceDetector:
    """El ve yüz landmark modellerini VIDEO modunda çalıştırır."""

    def __init__(self) -> None:
        self._hands = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_buffer=read_model(HAND_MODEL)),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=MAX_HANDS,
                min_hand_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self._faces = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_buffer=read_model(FACE_MODEL)),
                running_mode=vision.RunningMode.VIDEO,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self._last_timestamp_ms = -1

    def detect(self, rgb_frame: np.ndarray, timestamp_ms: int) -> Detection:
        # VIDEO modu zaman damgalarının kesin artan olmasını ister.
        timestamp_ms = max(timestamp_ms, self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms

        height, width = rgb_frame.shape[:2]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        hand_result = self._hands.detect_for_video(image, timestamp_ms)
        face_result = self._faces.detect_for_video(image, timestamp_ms)

        hand_points = tuple(
            tuple(_to_pixels(lm, width, height) for lm in landmarks)
            for landmarks in hand_result.hand_landmarks
        )
        hands = tuple(_hand_info(points) for points in hand_points)
        face = _face_info(face_result.face_landmarks, width, height)
        return Detection(observation=Observation(hands=hands, face=face), hand_points=hand_points)

    def close(self) -> None:
        self._hands.close()
        self._faces.close()


def _hand_info(points: tuple[Point, ...]) -> HandInfo:
    return HandInfo(
        fingertips=tuple(points[i] for i in FINGERTIPS),
        palm_length=_distance(points[WRIST], points[MIDDLE_MCP]),
    )


def _face_info(face_landmarks, width: int, height: int) -> FaceInfo | None:
    if not face_landmarks:
        return None
    landmarks = face_landmarks[0]
    mouth = tuple(_to_pixels(landmarks[i], width, height) for i in MOUTH_LANDMARKS)
    eye_distance = _distance(
        _to_pixels(landmarks[LEFT_EYE_OUTER], width, height),
        _to_pixels(landmarks[RIGHT_EYE_OUTER], width, height),
    )
    return FaceInfo(mouth_points=mouth, eye_distance=eye_distance)
