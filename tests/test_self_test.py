from tirnak_uyarici import detector, self_test


def test_self_test_passes_with_real_models():
    assert self_test.run_self_test() == 0


def test_self_test_reports_failure_instead_of_raising(monkeypatch):
    def broken_detector():
        raise ModuleNotFoundError("No module named 'matplotlib'")

    monkeypatch.setattr(detector, "HandFaceDetector", broken_detector)
    assert self_test.run_self_test() == 1
