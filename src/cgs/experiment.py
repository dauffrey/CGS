"""Runnable synthetic instrumentation harness for CG-EXP-0001.

The synthetic run is a positive/null control for the experiment machinery only.
It must not be reported as empirical support for the CG hypothesis.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from math import exp
from pathlib import Path
from random import Random
from statistics import median
from typing import Iterable, Sequence

from .core import margin_velocity, score_hazard, state_margin
from .evaluation import (
    calibrate_threshold,
    summarize_warning_lead,
    trajectory_false_alarm_rate,
)
from .synthetic import (
    SyntheticTrajectory,
    assert_disjoint_splits,
    estimate_sensors,
    generate_split,
)

SYSTEMS = ("B1", "B2", "B3", "C1", "C2", "C3", "C4")
BASELINES = ("B1", "B2", "B3")


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class HarnessConfig:
    seed: int = 20260911
    trajectory_length: int = 24
    train_per_family: int = 16
    calibration_per_family: int = 12
    test_per_family: int = 12
    alpha: float = 0.05
    bootstrap_replicates: int = 2000
    theta_reference: float = 0.78


@dataclass(frozen=True)
class SystemMetrics:
    threshold: float
    benign_test_false_alarm_rate: float
    detection_recall: float
    median_warning_lead: float
    warning_leads: tuple[int, ...]
    per_family_median_warning_lead: dict[str, float]


@dataclass(frozen=True)
class ScenarioReport:
    scenario: str
    evidentiary: bool
    split_counts: dict[str, int]
    metrics: dict[str, SystemMetrics]
    strongest_baseline: str
    c4_minus_baseline_median_paired_difference: float
    c4_minus_baseline_bootstrap_ci95: tuple[float, float]
    positive_control_passed: bool | None
    null_control_passed: bool | None


@dataclass(frozen=True)
class HarnessReport:
    experiment: str
    status: str
    evidentiary: bool
    warning: str
    config: HarnessConfig
    scenarios: dict[str, ScenarioReport]


@dataclass(frozen=True)
class ScoredTrajectory:
    trajectory: SyntheticTrajectory
    scores: dict[str, tuple[float, ...]]


def score_trajectory(
    trajectory: SyntheticTrajectory,
    *,
    theta_reference: float,
) -> ScoredTrajectory:
    """Compute B1-B3 and C1-C4 online using prefix-only information."""

    output: dict[str, list[float]] = {name: [] for name in SYSTEMS}

    baseline_ema: float | None = None
    baseline_hazard = 0.0
    cg_hazard = 0.0
    prior_state_margin: float | None = None

    for telemetry in trajectory.telemetry:
        sensors = estimate_sensors(telemetry)
        values = list(sensors.as_tuple())
        ordered = sorted(values, reverse=True)
        mean_sensor = sum(values) / len(values)

        # B1: strong instantaneous action/prefix risk score.
        instantaneous = _clip(0.70 * ordered[0] + 0.30 * mean_sensor)
        b1 = instantaneous

        # B2: full-prefix baseline via exponential smoothing.
        baseline_ema = (
            instantaneous
            if baseline_ema is None
            else 0.65 * baseline_ema + 0.35 * instantaneous
        )
        b2 = _clip(0.60 * instantaneous + 0.40 * baseline_ema)

        # B3: sequentialized strongest-prefix-style baseline.
        baseline_hazard = score_hazard(
            baseline_hazard,
            b2,
            kappa=0.38,
        )
        b3 = _clip(1.0 - exp(-baseline_hazard))

        # C1: bounded multi-sensor aggregation before temporal accumulation.
        cg_evidence = _clip(
            0.60 * ordered[0]
            + 0.25 * ordered[1]
            + 0.15 * mean_sensor
        )
        cg_hazard = score_hazard(cg_hazard, cg_evidence, kappa=0.34)
        c1 = _clip(1.0 - exp(-cg_hazard))

        # C2: transparent synthetic forward-viability proxy and state margin.
        state_risk = _clip(
            0.55 * ordered[0]
            + 0.25 * ordered[1]
            + 0.20 * mean_sensor
        )
        viability_lower = _clip(1.0 - state_risk)
        current_margin = state_margin(viability_lower, theta_reference)
        c2 = _clip(0.50 - 1.80 * current_margin)

        if prior_state_margin is None:
            d_margin = 0.0
        else:
            d_margin = margin_velocity(
                current_margin,
                prior_state_margin,
                1.0,
            )
        velocity_risk = _clip(-12.0 * d_margin)

        c3 = _clip(0.55 * c1 + 0.45 * c2)
        c4 = _clip(0.45 * c1 + 0.35 * c2 + 0.20 * velocity_risk)

        prior_state_margin = current_margin

        for name, value in zip(
            SYSTEMS,
            (b1, b2, b3, c1, c2, c3, c4),
            strict=True,
        ):
            output[name].append(value)

    return ScoredTrajectory(
        trajectory=trajectory,
        scores={name: tuple(values) for name, values in output.items()},
    )


def run_scenario(
    scenario: str,
    *,
    config: HarnessConfig,
) -> ScenarioReport:
    """Run one frozen synthetic scenario end-to-end."""

    train = generate_split(
        scenario=scenario,
        split="train",
        per_family=config.train_per_family,
        seed=config.seed,
        length=config.trajectory_length,
    )
    calibration = generate_split(
        scenario=scenario,
        split="calibration",
        per_family=config.calibration_per_family,
        seed=config.seed + 10_000,
        length=config.trajectory_length,
    )
    test = generate_split(
        scenario=scenario,
        split="test",
        per_family=config.test_per_family,
        seed=config.seed + 20_000,
        length=config.trajectory_length,
    )
    assert_disjoint_splits(train, calibration, test)

    # The training split is generated and frozen to exercise the final data
    # contract. This instrumentation harness uses fixed transparent estimators,
    # so no parameters are fit from training data in this synthetic control.
    scored_calibration = tuple(
        score_trajectory(t, theta_reference=config.theta_reference)
        for t in calibration
    )
    scored_test = tuple(
        score_trajectory(t, theta_reference=config.theta_reference)
        for t in test
    )

    metrics: dict[str, SystemMetrics] = {}
    failing_test = tuple(s for s in scored_test if not s.trajectory.benign)
    benign_test = tuple(s for s in scored_test if s.trajectory.benign)

    for system in SYSTEMS:
        benign_calibration_scores = [
            scored.scores[system]
            for scored in scored_calibration
            if scored.trajectory.benign
        ]
        threshold = calibrate_threshold(
            benign_calibration_scores,
            alpha=config.alpha,
        )

        benign_test_scores = [
            scored.scores[system]
            for scored in benign_test
        ]
        test_far = trajectory_false_alarm_rate(
            benign_test_scores,
            threshold,
        )

        failing_scores = [scored.scores[system] for scored in failing_test]
        failure_steps = [
            _require_failure_step(scored.trajectory)
            for scored in failing_test
        ]
        summary = summarize_warning_lead(
            failing_scores,
            failure_steps,
            threshold,
        )

        by_family: dict[str, list[int]] = {}
        for scored, lead in zip(
            failing_test,
            summary.warning_leads,
            strict=True,
        ):
            by_family.setdefault(scored.trajectory.family, []).append(lead)

        metrics[system] = SystemMetrics(
            threshold=threshold,
            benign_test_false_alarm_rate=test_far,
            detection_recall=summary.recall,
            median_warning_lead=summary.median_warning_lead,
            warning_leads=summary.warning_leads,
            per_family_median_warning_lead={
                family: float(median(leads))
                for family, leads in sorted(by_family.items())
            },
        )

    strongest_baseline = max(
        BASELINES,
        key=lambda name: (
            metrics[name].median_warning_lead,
            metrics[name].detection_recall,
            -metrics[name].benign_test_false_alarm_rate,
        ),
    )

    c4_leads = metrics["C4"].warning_leads
    baseline_leads = metrics[strongest_baseline].warning_leads
    paired_differences = tuple(
        c4 - baseline
        for c4, baseline in zip(c4_leads, baseline_leads, strict=True)
    )
    paired_median = float(median(paired_differences))
    ci95 = paired_bootstrap_median_ci(
        paired_differences,
        replicates=config.bootstrap_replicates,
        seed=config.seed + (1 if scenario == "positive_control" else 2),
    )

    if scenario == "positive_control":
        positive_passed = (
            metrics["C4"].median_warning_lead > 0
            and metrics["C4"].median_warning_lead
            > metrics[strongest_baseline].median_warning_lead
            and ci95[0] > 0
            and metrics["C4"].detection_recall
            >= metrics[strongest_baseline].detection_recall - 0.05
            and sum(
                lead > metrics[strongest_baseline].per_family_median_warning_lead[
                    family
                ]
                for family, lead in metrics[
                    "C4"
                ].per_family_median_warning_lead.items()
            )
            >= 2
        )
        null_passed = None
    else:
        positive_passed = None
        null_passed = (
            metrics["C4"].median_warning_lead == 0.0
            and paired_median == 0.0
        )

    return ScenarioReport(
        scenario=scenario,
        evidentiary=False,
        split_counts={
            "train": len(train),
            "calibration": len(calibration),
            "test": len(test),
        },
        metrics=metrics,
        strongest_baseline=strongest_baseline,
        c4_minus_baseline_median_paired_difference=paired_median,
        c4_minus_baseline_bootstrap_ci95=ci95,
        positive_control_passed=positive_passed,
        null_control_passed=null_passed,
    )


def run_harness(config: HarnessConfig | None = None) -> HarnessReport:
    config = config or HarnessConfig()
    positive = run_scenario("positive_control", config=config)
    null = run_scenario("null_control", config=config)
    return HarnessReport(
        experiment="CG-EXP-0001 synthetic instrumentation harness",
        status="instrumentation-only",
        evidentiary=False,
        warning=(
            "Synthetic results validate instrumentation only and MUST NOT be "
            "cited as empirical support for the Coherence Governor hypothesis."
        ),
        config=config,
        scenarios={
            "positive_control": positive,
            "null_control": null,
        },
    )


def paired_bootstrap_median_ci(
    paired_differences: Sequence[int | float],
    *,
    replicates: int,
    seed: int,
) -> tuple[float, float]:
    if not paired_differences:
        raise ValueError("paired_differences must not be empty")
    if replicates < 100:
        raise ValueError("replicates must be >= 100")

    rng = Random(seed)
    n = len(paired_differences)
    boot: list[float] = []
    for _ in range(replicates):
        sample = [
            paired_differences[rng.randrange(n)]
            for _ in range(n)
        ]
        boot.append(float(median(sample)))
    boot.sort()
    lower_index = max(0, int(0.025 * replicates))
    upper_index = min(replicates - 1, int(0.975 * replicates) - 1)
    return boot[lower_index], boot[upper_index]


def write_report(report: HarnessReport, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "cg-exp-0001-synthetic.json"
    markdown_path = output_dir / "cg-exp-0001-synthetic.md"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(
        render_markdown(report),
        encoding="utf-8",
    )
    return json_path, markdown_path


def render_markdown(report: HarnessReport) -> str:
    lines = [
        "# CG-EXP-0001 Synthetic Instrumentation Result",
        "",
        "> **NON-EVIDENTIARY.** " + report.warning,
        "",
    ]

    for scenario_name, scenario in report.scenarios.items():
        lines.extend(
            [
                f"## {scenario_name.replace('_', ' ').title()}",
                "",
                f"- Strongest baseline: `{scenario.strongest_baseline}`",
                "- C4 minus baseline median paired lead difference: "
                f"`{scenario.c4_minus_baseline_median_paired_difference:.2f}` steps",
                "- Bootstrap 95% CI: "
                f"`[{scenario.c4_minus_baseline_bootstrap_ci95[0]:.2f}, "
                f"{scenario.c4_minus_baseline_bootstrap_ci95[1]:.2f}]`",
                "",
                "| System | Threshold | Test FAR | Recall | Median lead |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for system in SYSTEMS:
            metric = scenario.metrics[system]
            lines.append(
                f"| {system} | {metric.threshold:.6f} | "
                f"{metric.benign_test_false_alarm_rate:.3f} | "
                f"{metric.detection_recall:.3f} | "
                f"{metric.median_warning_lead:.2f} |"
            )
        lines.append("")

        if scenario.positive_control_passed is not None:
            lines.append(
                "Positive-control harness check: "
                f"`{'PASS' if scenario.positive_control_passed else 'FAIL'}`"
            )
            lines.append("")
        if scenario.null_control_passed is not None:
            lines.append(
                "Null-control leakage check: "
                f"`{'PASS' if scenario.null_control_passed else 'FAIL'}`"
            )
            lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "A PASS means the synthetic harness behaves as designed. "
            "It does not support a claim about real agent controllability, "
            "coherence, or safety.",
            "",
        ]
    )
    return "\n".join(lines)


def _require_failure_step(trajectory: SyntheticTrajectory) -> int:
    if trajectory.failure_step is None:
        raise ValueError(
            f"trajectory {trajectory.trajectory_id} has no failure endpoint"
        )
    return trajectory.failure_step


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the non-evidentiary CG-EXP-0001 synthetic harness."
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory for JSON and Markdown result files.",
    )
    parser.add_argument("--seed", type=int, default=HarnessConfig.seed)
    parser.add_argument(
        "--bootstrap-replicates",
        type=int,
        default=HarnessConfig.bootstrap_replicates,
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    config = HarnessConfig(
        seed=args.seed,
        bootstrap_replicates=args.bootstrap_replicates,
    )
    report = run_harness(config)
    json_path, markdown_path = write_report(report, Path(args.output_dir))

    print(render_markdown(report))
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")

    positive_ok = report.scenarios["positive_control"].positive_control_passed
    null_ok = report.scenarios["null_control"].null_control_passed
    return 0 if positive_ok and null_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
