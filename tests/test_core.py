from math import inf

import pytest

from cgs.core import (
    SensorVector,
    action_margin,
    coherence_index,
    likelihood_hazard,
    linear_time_to_boundary,
    margin_velocity,
    score_hazard,
    state_margin,
    warning_lead_time,
)


def test_likelihood_hazard_accumulates_and_resets_at_zero():
    assert likelihood_hazard(0.0, 0.4) == pytest.approx(0.4)
    assert likelihood_hazard(0.4, -1.0) == 0.0


@pytest.mark.parametrize("increment", [float("nan"), float("inf"), float("-inf")])
def test_likelihood_hazard_rejects_nonfinite_increment(increment):
    with pytest.raises(ValueError):
        likelihood_hazard(0.4, increment)


def test_score_hazard_uses_kappa_only_in_score_mode():
    assert score_hazard(0.5, 0.4, 0.2) == pytest.approx(0.7)
    assert score_hazard(0.1, 0.0, 0.2) == 0.0


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_score_hazard_rejects_nonfinite_score(score):
    with pytest.raises(ValueError):
        score_hazard(0.5, score, 0.2)


def test_coherence_index_is_monotone_transform_of_hazard():
    assert coherence_index(0.0, 2.0) == pytest.approx(1.0)
    assert coherence_index(2.0, 2.0) < coherence_index(1.0, 2.0)


def test_state_margin_is_independent_of_action_risk_threshold():
    viability = 0.97
    assert state_margin(viability, 0.95) == pytest.approx(0.02)
    assert action_margin(viability, 0.90) == pytest.approx(0.07)
    assert action_margin(viability, 0.99) == pytest.approx(-0.02)


def test_margin_velocity_uses_state_margins_only():
    assert margin_velocity(0.02, 0.08, 2.0) == pytest.approx(-0.03)


def test_linear_time_to_boundary_semantics():
    assert linear_time_to_boundary(-0.01, -0.02) == 0.0
    assert linear_time_to_boundary(0.10, 0.0) == inf
    assert linear_time_to_boundary(0.10, 0.02) == inf
    assert linear_time_to_boundary(0.10, -0.02) == pytest.approx(5.0)


def test_warning_lead_time_assigns_miss_zero():
    assert warning_lead_time(10, None) == 0
    assert warning_lead_time(10, 7) == 3
    assert warning_lead_time(10, 10) == 0
    assert warning_lead_time(10, 12) == 0


def test_sensor_vector_requires_normalized_values():
    SensorVector(0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 1.0)
    with pytest.raises(ValueError):
        SensorVector(1.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
