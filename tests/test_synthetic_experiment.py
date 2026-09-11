from pathlib import Path

from cgs.experiment import HarnessConfig, run_harness, write_report
from cgs.synthetic import assert_disjoint_splits, estimate_sensors, generate_split


def test_synthetic_splits_are_disjoint():
    train = generate_split(
        scenario="positive_control",
        split="train",
        per_family=2,
        seed=1,
    )
    calibration = generate_split(
        scenario="positive_control",
        split="calibration",
        per_family=2,
        seed=2,
    )
    test = generate_split(
        scenario="positive_control",
        split="test",
        per_family=2,
        seed=3,
    )
    assert_disjoint_splits(train, calibration, test)


def test_sensor_estimators_remain_normalized():
    trajectory = generate_split(
        scenario="positive_control",
        split="train",
        per_family=1,
        seed=7,
    )[0]
    for step in trajectory.telemetry:
        sensors = estimate_sensors(step)
        assert all(0.0 <= value <= 1.0 for value in sensors.as_tuple())


def test_positive_control_detects_known_precursor_structure():
    report = run_harness(
        HarnessConfig(
            train_per_family=4,
            calibration_per_family=6,
            test_per_family=6,
            bootstrap_replicates=400,
        )
    )
    positive = report.scenarios["positive_control"]

    assert positive.positive_control_passed is True
    assert positive.metrics["C4"].median_warning_lead > 0
    assert (
        positive.metrics["C4"].median_warning_lead
        > positive.metrics[positive.strongest_baseline].median_warning_lead
    )
    assert positive.c4_minus_baseline_bootstrap_ci95[0] > 0


def test_null_control_has_no_manufactured_warning_lead():
    report = run_harness(
        HarnessConfig(
            train_per_family=4,
            calibration_per_family=6,
            test_per_family=6,
            bootstrap_replicates=400,
        )
    )
    null = report.scenarios["null_control"]

    assert null.null_control_passed is True
    assert null.metrics["C4"].median_warning_lead == 0.0
    assert null.c4_minus_baseline_median_paired_difference == 0.0


def test_report_is_explicitly_non_evidentiary(tmp_path: Path):
    report = run_harness(
        HarnessConfig(
            train_per_family=2,
            calibration_per_family=4,
            test_per_family=4,
            bootstrap_replicates=200,
        )
    )
    json_path, markdown_path = write_report(report, tmp_path)

    assert report.evidentiary is False
    assert "MUST NOT" in report.warning
    assert json_path.exists()
    assert markdown_path.exists()
    assert "NON-EVIDENTIARY" in markdown_path.read_text(encoding="utf-8")
