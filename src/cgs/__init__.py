"""Coherence Governor System research package."""

from .core import (
    ExternalEndpoint,
    SensorVector,
    TaskContract,
    action_margin,
    coherence_index,
    first_threshold_crossing,
    likelihood_hazard,
    linear_time_to_boundary,
    margin_velocity,
    score_hazard,
    state_margin,
    warning_lead_time,
)

__all__ = [
    "ExternalEndpoint",
    "SensorVector",
    "TaskContract",
    "action_margin",
    "coherence_index",
    "first_threshold_crossing",
    "likelihood_hazard",
    "linear_time_to_boundary",
    "margin_velocity",
    "score_hazard",
    "state_margin",
    "warning_lead_time",
]
