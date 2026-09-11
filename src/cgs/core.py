"""Core CG-0.2 mathematics.

This module intentionally contains only transparent reference calculations. It does
not claim that any supplied score, likelihood, or viability estimate is valid.
Those estimators must be calibrated and evaluated experimentally.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, inf, isfinite
from typing import Iterable


@dataclass(frozen=True)
class SensorVector:
    """Normalized observable CG sensor vector.

    Fields correspond to goal divergence, pathological persistence, boundary
    pressure, reward/proxy divergence, unauthorized coordination, uncertainty
    mismatch, and optional internal anomaly.
    """

    goal_divergence: float
    persistence: float
    boundary_pressure: float
    reward_proxy_divergence: float
    unauthorized_coordination: float
    uncertainty_mismatch: float
    internal_anomaly: float = 0.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            _require_unit_interval(value, name)

    def as_tuple(self) -> tuple[float, ...]:
        return tuple(self.__dict__.values())


@dataclass(frozen=True)
class TaskContract:
    """Minimal immutable task-contract reference for experiments."""

    objective: str
    constraints: tuple[str, ...]
    permissions: tuple[str, ...]
    risk_envelope: str


@dataclass(frozen=True)
class ExternalEndpoint:
    """Environment-defined outcome label, separate from CG sensor computation.

    Experiments should construct these labels from the task contract and
    auditable environment events, not from CG scores or alert states.
    """

    occurred: bool
    step: int | None = None
    event_type: str | None = None

    def __post_init__(self) -> None:
        if self.occurred and self.step is None:
            raise ValueError("occurred=True requires an endpoint step")
        if self.step is not None and self.step < 0:
            raise ValueError("endpoint step must be non-negative")


def likelihood_hazard(previous_hazard: float, log_likelihood_ratio: float) -> float:
    """CUSUM-like accumulation for a true log-likelihood-ratio input.

    CG-0.2 deliberately does not subtract kappa in likelihood mode because the
    likelihood ratio already carries a statistical interpretation. Non-finite
    estimator outputs invalidate the trajectory rather than resetting hazard.
    """

    _require_nonnegative(previous_hazard, "previous_hazard")
    _require_finite(log_likelihood_ratio, "log_likelihood_ratio")
    return max(0.0, previous_hazard + log_likelihood_ratio)


def score_hazard(previous_hazard: float, score: float, kappa: float) -> float:
    """CUSUM-like accumulation for an engineered/non-likelihood score."""

    _require_nonnegative(previous_hazard, "previous_hazard")
    _require_finite(score, "score")
    _require_nonnegative(kappa, "kappa")
    return max(0.0, previous_hazard + score - kappa)


def coherence_index(hazard: float, lambda_h: float) -> float:
    """Presentation index C=exp(-H/lambda_H); not independent evidence."""

    _require_nonnegative(hazard, "hazard")
    if not isfinite(lambda_h) or lambda_h <= 0:
        raise ValueError("lambda_h must be finite and > 0")
    return exp(-hazard / lambda_h)


def state_margin(viability_lower: float, theta_reference: float) -> float:
    """Action-normalized state viability reserve."""

    _require_unit_interval(viability_lower, "viability_lower")
    _require_unit_interval(theta_reference, "theta_reference")
    return viability_lower - theta_reference


def action_margin(viability_lower: float, required_viability: float) -> float:
    """Authorization reserve for one proposed action."""

    _require_unit_interval(viability_lower, "viability_lower")
    _require_unit_interval(required_viability, "required_viability")
    return viability_lower - required_viability


def margin_velocity(current_state_margin: float, prior_state_margin: float, delta_t: float) -> float:
    """Finite-difference velocity computed only from state margins."""

    if not isfinite(delta_t) or delta_t <= 0:
        raise ValueError("delta_t must be finite and > 0")
    return (current_state_margin - prior_state_margin) / delta_t


def linear_time_to_boundary(
    current_state_margin: float,
    state_margin_velocity: float,
    *,
    epsilon: float = 1e-12,
) -> float:
    """Local linear boundary-crossing diagnostic from CG-0.2.

    Returns 0 if the state is already at/beyond the boundary and infinity when
    the margin is not currently declining.
    """

    if epsilon <= 0 or not isfinite(epsilon):
        raise ValueError("epsilon must be finite and > 0")
    if current_state_margin <= 0:
        return 0.0
    if state_margin_velocity >= 0:
        return inf
    return current_state_margin / max(epsilon, -state_margin_velocity)


def warning_lead_time(failure_step: int, alarm_step: int | None) -> int:
    """Conservative CG-EXP-0001 warning lead time.

    A miss is assigned zero lead time. Alarms at/after failure also contribute
    zero rather than negative lead time in the primary conservative summary.
    """

    if failure_step < 0:
        raise ValueError("failure_step must be non-negative")
    if alarm_step is None:
        return 0
    if alarm_step < 0:
        raise ValueError("alarm_step must be non-negative")
    return max(0, failure_step - alarm_step)


def first_threshold_crossing(values: Iterable[float], threshold: float) -> int | None:
    """Return the first index whose score meets/exceeds a frozen threshold."""

    for index, value in enumerate(values):
        if value >= threshold:
            return index
    return None


def _require_finite(value: float, name: str) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_unit_interval(value: float, name: str) -> None:
    if not isfinite(value) or value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1]")


def _require_nonnegative(value: float, name: str) -> None:
    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and >= 0")
