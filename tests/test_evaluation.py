import pytest

from cgs.evaluation import (
    calibrate_threshold,
    summarize_warning_lead,
    trajectory_false_alarm_rate,
)


def test_calibration_meets_zero_alarm_budget_when_sample_is_small():
    benign = [
        [0.1, 0.2, 0.3],
        [0.2, 0.4, 0.3],
        [0.1, 0.2, 0.2],
    ]
    threshold = calibrate_threshold(benign, alpha=0.05)
    assert trajectory_false_alarm_rate(benign, threshold) == 0.0


def test_calibration_respects_five_percent_trajectory_budget():
    benign = [[float(i)] for i in range(20)]
    threshold = calibrate_threshold(benign, alpha=0.05)
    assert trajectory_false_alarm_rate(benign, threshold) <= 0.05


def test_warning_summary_counts_only_prefailure_alarms():
    failing = [
        [0.1, 0.2, 0.9, 0.9],
        [0.1, 0.2, 0.3, 0.9],
        [0.1, 0.2, 0.3, 0.4],
    ]
    failures = [4, 3, 4]
    summary = summarize_warning_lead(failing, failures, threshold=0.8)

    assert summary.warning_leads == (2, 0, 0)
    assert summary.detected_before_failure == 1
    assert summary.recall == pytest.approx(1 / 3)
    assert summary.median_warning_lead == 0.0


def test_invalid_alpha_is_rejected():
    with pytest.raises(ValueError):
        calibrate_threshold([[0.1]], alpha=1.0)
