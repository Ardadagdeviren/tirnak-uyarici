import json

import pytest

from tirnak_uyarici.config import (
    NEAR_RATIO_AT_MAX,
    NEAR_RATIO_AT_MIN,
    Settings,
    load_settings,
    save_settings,
    sensitivity_to_ratio,
)


def test_missing_file_returns_defaults(tmp_path):
    assert load_settings(tmp_path / "yok.json") == Settings()


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "alt" / "config.json"
    settings = Settings(camera_index=1, sensitivity=8, hold_seconds=1.0, sound_enabled=False)
    save_settings(settings, path)
    assert load_settings(path) == settings


@pytest.mark.parametrize("content", ["{bozuk json", "[1, 2, 3]", '{"sensitivity": "abc"}'])
def test_invalid_file_falls_back_to_defaults(tmp_path, content):
    path = tmp_path / "config.json"
    path.write_text(content, encoding="utf-8")
    assert load_settings(path) == Settings()


def test_out_of_range_values_are_clamped_and_unknown_keys_ignored(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"sensitivity": 99, "hold_seconds": -3, "camera_index": -1, "eski": 1}),
        encoding="utf-8",
    )
    settings = load_settings(path)
    assert settings.sensitivity == 10
    assert settings.hold_seconds == 0.1
    assert settings.camera_index == 0


def test_sensitivity_maps_to_ratio_range():
    assert sensitivity_to_ratio(1) == pytest.approx(NEAR_RATIO_AT_MIN)
    assert sensitivity_to_ratio(10) == pytest.approx(NEAR_RATIO_AT_MAX)
    assert sensitivity_to_ratio(3) < sensitivity_to_ratio(7)


def test_detection_params_follow_settings():
    params = Settings(sensitivity=10, hold_seconds=1.5, cooldown_seconds=7).detection_params()
    assert params.near_ratio == pytest.approx(NEAR_RATIO_AT_MAX)
    assert params.hold_seconds == 1.5
    assert params.cooldown_seconds == 7
