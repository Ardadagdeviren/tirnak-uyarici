import math

from tirnak_uyarici.gesture_logic import (
    DetectionParams,
    FaceInfo,
    HandInfo,
    Observation,
    TrackerState,
    closest_ratio,
    hand_mouth_ratio,
    step,
)

PARAMS = DetectionParams(
    near_ratio=0.35,
    hold_seconds=0.5,
    cooldown_seconds=4.0,
    face_memory_seconds=1.0,
    release_grace_seconds=0.25,
    max_palm_to_eye_ratio=2.2,
)

# Göz arası 100 px, ağız (300, 400) civarında.
FACE = FaceInfo(mouth_points=((280.0, 400.0), (320.0, 400.0), (300.0, 395.0)), eye_distance=100.0)


def hand_at(x: float, y: float, palm_length: float = 110.0) -> HandInfo:
    return HandInfo(fingertips=((x, y), (x + 200, y + 200)), palm_length=palm_length)


HAND_AT_MOUTH = hand_at(300.0, 402.0)
HAND_FAR = hand_at(600.0, 700.0)


def run(observations, times, params=PARAMS):
    state = TrackerState()
    alerts = []
    for obs, t in zip(observations, times):
        result = step(state, obs, t, params)
        state = result.state
        alerts.append(result.should_alert)
    return alerts, state


def test_ratio_is_small_when_fingertip_touches_lips():
    ratio = hand_mouth_ratio(HAND_AT_MOUTH, FACE, PARAMS)
    assert ratio is not None and ratio < 0.1


def test_ratio_is_scale_invariant():
    big_face = FaceInfo(
        mouth_points=tuple((x * 2, y * 2) for x, y in FACE.mouth_points), eye_distance=200.0
    )
    big_hand = HandInfo(fingertips=((600.0, 804.0),), palm_length=220.0)
    small = hand_mouth_ratio(HAND_AT_MOUTH, FACE, PARAMS)
    big = hand_mouth_ratio(big_hand, big_face, PARAMS)
    assert math.isclose(small, big, rel_tol=1e-6)


def test_hand_much_closer_to_camera_than_face_is_ignored():
    near_camera_hand = hand_at(300.0, 402.0, palm_length=300.0)
    assert hand_mouth_ratio(near_camera_hand, FACE, PARAMS) is None


def test_zero_eye_distance_is_ignored():
    broken_face = FaceInfo(mouth_points=FACE.mouth_points, eye_distance=0.0)
    assert hand_mouth_ratio(HAND_AT_MOUTH, broken_face, PARAMS) is None


def test_closest_ratio_picks_nearest_hand_and_handles_no_hands():
    assert closest_ratio([], FACE, PARAMS) is None
    ratio = closest_ratio([HAND_FAR, HAND_AT_MOUTH], FACE, PARAMS)
    assert ratio == hand_mouth_ratio(HAND_AT_MOUTH, FACE, PARAMS)


def test_no_alert_when_hand_is_far():
    obs = Observation(hands=(HAND_FAR,), face=FACE)
    alerts, _ = run([obs] * 20, [i * 0.1 for i in range(20)])
    assert not any(alerts)


def test_alert_fires_after_hold_duration():
    obs = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    times = [0.0, 0.2, 0.4, 0.5, 0.6]
    alerts, _ = run([obs] * len(times), times)
    assert alerts == [False, False, False, True, False]


def test_brief_touch_does_not_alert():
    near = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    far = Observation(hands=(HAND_FAR,), face=FACE)
    observations = [near, near, far, far, far, far]
    times = [0.0, 0.2, 0.6, 0.8, 1.0, 1.2]
    alerts, state = run(observations, times)
    assert not any(alerts)
    assert state.near_since is None


def test_single_frame_dropout_keeps_hold_timer():
    near = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    no_hand = Observation(hands=(), face=FACE)
    observations = [near, near, no_hand, near]
    times = [0.0, 0.3, 0.4, 0.5]
    alerts, _ = run(observations, times)
    assert alerts[-1] is True


def test_cooldown_limits_repeated_alerts():
    obs = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    times = [i * 0.1 for i in range(100)]  # 10 saniye boyunca el ağızda
    alerts, _ = run([obs] * len(times), times)
    fired_at = [t for t, a in zip(times, alerts) if a]
    assert len(fired_at) == 3
    assert all(b - a >= PARAMS.cooldown_seconds - 1e-9 for a, b in zip(fired_at, fired_at[1:]))


def test_face_lost_while_hand_covers_mouth_still_alerts():
    with_face = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    face_lost = Observation(hands=(HAND_AT_MOUTH,), face=None)
    observations = [with_face, face_lost, face_lost, face_lost]
    times = [0.0, 0.2, 0.4, 0.6]
    alerts, _ = run(observations, times)
    assert alerts[-1] is True


def test_face_memory_expires():
    with_face = Observation(hands=(HAND_FAR,), face=FACE)
    face_lost = Observation(hands=(HAND_AT_MOUTH,), face=None)
    observations = [with_face] + [face_lost] * 6
    times = [0.0, 1.5, 1.7, 1.9, 2.1, 2.3, 2.5]
    alerts, _ = run(observations, times)
    assert not any(alerts)


def test_step_does_not_mutate_input_state():
    state = TrackerState()
    obs = Observation(hands=(HAND_AT_MOUTH,), face=FACE)
    step(state, obs, 0.0, PARAMS)
    assert state == TrackerState()
