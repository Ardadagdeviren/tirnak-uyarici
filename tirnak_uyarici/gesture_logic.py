"""El-ağız yakınlık mantığı.

Kameradan ve arayüzden bağımsız, saf fonksiyonlardan oluşur; böylece sahte
nokta verileriyle test edilebilir. Tüm koordinatlar piksel cinsindendir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Optional, Sequence

Point = tuple[float, float]


@dataclass(frozen=True)
class FaceInfo:
    """Bir karedeki yüzün ağız noktaları ve ölçeği."""

    mouth_points: tuple[Point, ...]
    eye_distance: float


@dataclass(frozen=True)
class HandInfo:
    """Bir elin parmak uçları ve ölçeği (bilek → orta parmak kökü)."""

    fingertips: tuple[Point, ...]
    palm_length: float


@dataclass(frozen=True)
class Observation:
    """Tek bir karede görülenler."""

    hands: tuple[HandInfo, ...] = ()
    face: Optional[FaceInfo] = None


@dataclass(frozen=True)
class DetectionParams:
    # Parmak ucu–dudak mesafesinin göz arası mesafeye oranı bu değerin altındaysa "ağızda".
    near_ratio: float = 0.35
    # El bu süre boyunca ağızda kalırsa uyarı verilir.
    hold_seconds: float = 0.5
    # İki uyarı arasındaki en kısa süre.
    cooldown_seconds: float = 4.0
    # Yüz kaybolduğunda (el ağzı kapatınca) son ağız konumu bu kadar süre kullanılır.
    face_memory_seconds: float = 1.0
    # Tespit birkaç kare titrerse "ağızda" durumu hemen sıfırlanmaz.
    release_grace_seconds: float = 0.25
    # El kameraya yüzden çok daha yakınsa (önünden geçiyorsa) yok sayılır.
    max_palm_to_eye_ratio: float = 2.2


@dataclass(frozen=True)
class TrackerState:
    last_face: Optional[FaceInfo] = None
    last_face_time: float = -math.inf
    near_since: Optional[float] = None
    last_near_time: float = -math.inf
    last_alert_time: float = -math.inf


@dataclass(frozen=True)
class StepResult:
    state: TrackerState
    should_alert: bool
    ratio: Optional[float] = field(default=None)


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def min_distance(points_a: Sequence[Point], points_b: Sequence[Point]) -> float:
    if not points_a or not points_b:
        return math.inf
    return min(distance(a, b) for a in points_a for b in points_b)


def hand_mouth_ratio(hand: HandInfo, face: FaceInfo, params: DetectionParams) -> Optional[float]:
    """Elin ağıza yakınlık oranı; el yüz derinliğinde değilse None."""
    if face.eye_distance <= 0:
        return None
    if hand.palm_length / face.eye_distance > params.max_palm_to_eye_ratio:
        return None
    return min_distance(hand.fingertips, face.mouth_points) / face.eye_distance


def closest_ratio(
    hands: Sequence[HandInfo], face: FaceInfo, params: DetectionParams
) -> Optional[float]:
    ratios = [r for r in (hand_mouth_ratio(h, face, params) for h in hands) if r is not None]
    return min(ratios) if ratios else None


def _effective_face(
    state: TrackerState, obs: Observation, now: float, params: DetectionParams
) -> tuple[Optional[FaceInfo], TrackerState]:
    if obs.face is not None:
        return obs.face, replace(state, last_face=obs.face, last_face_time=now)
    if now - state.last_face_time <= params.face_memory_seconds:
        return state.last_face, state
    return None, state


def step(
    state: TrackerState, obs: Observation, now: float, params: DetectionParams
) -> StepResult:
    """Yeni bir karede durumu ilerletir; uyarı verilmesi gerekiyorsa bildirir."""
    face, state = _effective_face(state, obs, now, params)
    ratio = closest_ratio(obs.hands, face, params) if face is not None else None
    is_near = ratio is not None and ratio <= params.near_ratio

    if not is_near:
        if now - state.last_near_time > params.release_grace_seconds:
            state = replace(state, near_since=None)
        return StepResult(state=state, should_alert=False, ratio=ratio)

    near_since = state.near_since if state.near_since is not None else now
    state = replace(state, near_since=near_since, last_near_time=now)

    held_long_enough = now - near_since >= params.hold_seconds
    cooled_down = now - state.last_alert_time >= params.cooldown_seconds
    if held_long_enough and cooled_down:
        return StepResult(state=replace(state, last_alert_time=now), should_alert=True, ratio=ratio)
    return StepResult(state=state, should_alert=False, ratio=ratio)
