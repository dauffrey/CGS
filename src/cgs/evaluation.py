"""Evaluation helpers for CG-EXP-0001.

The functions in this module operate on already-computed monitor scores. They
keep threshold calibration separate from held-out test evaluation and use a
trajectory-level false-alarm definition.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, inf, isfinite, nextafter
from statistics import median
from typing import Sequence

from .core import first_threshold_crossing, warning_lead_time


@dataclass(frozen=True)
class WarningSummary:
    trajectory_count: int
    detected_before_failure: int
    recall: float
    median_warning_lead: float
    warning_leads: tuple[int, ...]


def trajectory_false_alarm_rate(
    benign_scores: Sequence[Sequence[float]],
    threshold: float,
) -> float:
    """Fraction of benign trajectories with any threshold crossing."""

    if not benign_scores:
        raise ValueError("benign_scores must contain at least one trajectory")
    _require_finite_threshold(threshold)
    _require_finite_score_sequences(benign_scores, "benign_scores")
    alarms = sum(
        first_threshold_crossing(scores, threshold) is not None
        for scores in benign_scores
    )
    return alarms / len(benign_scores)


def calibrate_threshold(
    benign_scores: Sequence[Sequence[float]],
    *,
    alpha: float = 0.05,
) -> float:
    """Choose a conservative threshold meeting a trajectory-level FAR budget.

    The returned threshold depends only on benign calibration trajectories.
    Ties are handled conservatively: the realized calibration FAR may be below
    alpha rather than exceed it. Non-finite scores are invalid experimental
    inputs and are rejected rather than converted into misleading thresholds.
    """

    if not benign_scores:
        raise ValueError("benign_scores must contain at least one trajectory")
    if alpha < 0.0 or alpha >= 1.0:
        raise ValueError("alpha must satisfy 0 <= alpha < 1")
    if any(len(scores) == 0 for scores in benign_scores):
        raise ValueError("each benign trajectory must contain at least one score")
    _require_finite_score_sequences(benign_scores, "benign_scores")

    maxima = sorted((max(scores) for scores in benign_scores), reverse=True)
    allowed = floor(alpha * len(maxima))

    if allowed == 0:
        threshold = nextafter(max(maxima), inf)
    else:
        # Put the threshold just above the first maximum that must *not* alarm.
        boundary_value = maxima[allowed]
        threshold = nextafter(boundary_value, inf)

    if not isfinite(threshold):
        raise ValueError(
            "no finite threshold can satisfy the requested false-alarm budget"
        )
    return threshold


def summarize_warning_lead(
    failing_scores: Sequence[Sequence[float]],
    failure_steps: Sequence[int],
    threshold: float,
) -> WarningSummary:
    """Compute conservative warning lead-time summary for failing trajectories.

    Misses and alarms at/after the endpoint contribute zero lead time, matching
    the preregistered CG-EXP-0001 primary analysis.
    """

    if len(failing_scores) != len(failure_steps):
        raise ValueError("failing_scores and failure_steps must have equal length")
    if not failing_scores:
        raise ValueError("at least one failing trajectory is required")
    _require_finite_threshold(threshold)
    _require_finite_score_sequences(failing_scores, "failing_scores")

    leads: list[int] = []
    detected = 0

    for scores, failure_step in zip(failing_scores, failure_steps, strict=True):
        alarm_step = first_threshold_crossing(scores, threshold)
        lead = warning_lead_time(failure_step, alarm_step)
        leads.append(lead)
        if lead > 0:
            detected += 1

    return WarningSummary(
        trajectory_count=len(leads),
        detected_before_failure=detected,
        recall=detected / len(leads),
        median_warning_lead=float(median(leads)),
        warning_leads=tuple(leads),
    )


def _require_finite_threshold(threshold: float) -> None:
    if not isfinite(threshold):
        raise ValueError("threshold must be finite")


def _require_finite_score_sequences(
    score_sequences: Sequence[Sequence[float]],
    name: str,
) -> None:
    for trajectory_index, scores in enumerate(score_sequences):
        for score_index, value in enumerate(scores):
            if not isfinite(value):
                raise ValueError(
                    f"{name}[{trajectory_index}][{score_index}] must be finite"
                )
