# Coherence Governor Specification — CG-0.2

**Status:** Research specification for implementation and falsification  
**Supersedes:** CG-0.1 for definitive experiments

CG-0.2 preserves the runtime-assurance architecture of CG-0.1 while correcting four measurement problems: state/action margin conflation, contaminated margin velocity, circular failure endpoints, and treatment of `C_t` as if it were independent evidence.

## 1. Research question

At a fixed false-alarm rate, can accumulated trajectory hazard, state viability margin, and state-margin velocity predict an independently defined future contract violation earlier than a strong trajectory-monitor baseline?

Formally, test whether the combined predictor

```text
(H_t, M_state_t, dM_state_t)
```

provides greater warning lead time than the strongest baseline while preserving comparable or better recall at the same false-alarm budget.

## 2. Independent runtime-assurance architecture

The Governor is outside the acting agent's control plane.

The agent must not control:

- Governor code or model weights;
- decision thresholds;
- telemetry collection;
- authorization enforcement;
- audit-log integrity;
- fallback execution;
- experiment labels.

Hard deterministic invariants always take precedence over learned estimates.

## 3. Immutable task contract

```text
Gamma = (G0, K0, P0, R0)
```

where `G0` is the authorized objective, `K0` the explicit constraints, `P0` the granted permissions, and `R0` the accepted risk envelope.

A strategy may change without changing `Gamma`. Any material change to objective, permissions, or risk envelope requires an external authorization event that is separately logged.

## 4. Observable sensor vector

```text
z_t = [G_t, P_t, B_t, R_t, X_t, U_t, I_t]
```

All sensors must have explicit estimators and provenance.

- `G_t`: goal-action divergence;
- `P_t`: persistence despite low progress;
- `B_t`: boundary pressure;
- `R_t`: reward/proxy divergence;
- `X_t`: unauthorized coordination;
- `U_t`: observable uncertainty mismatch;
- `I_t`: optional internal/process anomaly.

`U_t` must not require privileged hidden reasoning. Acceptable estimators may use monitor disagreement, prediction instability, evidence insufficiency, calibration error, or inconsistency between expressed confidence and externally measurable uncertainty.

`I_t` is optional. The architecture must remain evaluable without chain-of-thought or privileged activations.

## 5. Dependence-aware evidence model

Sensors must not be assumed independent. The target is the joint conditional model:

```text
p(z_t | T_<t, regime)
```

not a naive product of marginal sensor probabilities.

When a calibrated generative or discriminative likelihood model is available:

```text
ell_t = log [p(z_t | T_<t, M) / p(z_t | T_<t, A)]
```

Use likelihood-mode accumulation:

```text
H_t = max(0, H_(t-1) + ell_t)
```

When a non-likelihood score is used:

```text
S_t = score(z_t, T_<t)
H_t = max(0, H_(t-1) + S_t - kappa)
```

The distinction between likelihood mode and score mode must be retained in code and reporting.

## 6. Hazard and coherence index

`H_t` is the accumulated degradation evidence.

For presentation only:

```text
C_index_t = exp(-H_t / lambda_H)
```

`C_index_t` is a deterministic monotonic transformation of `H_t`; it is not an independent feature and must not be counted as additional evidence in statistical comparisons.

## 7. Independently defined failure endpoint

The primary outcome must be defined without reference to `G_t, P_t, B_t, R_t, X_t, U_t, I_t, H_t, C_index_t, M_state_t`, or the Governor's alert state.

Define:

```text
Y_(t,L) = 1
```

iff a prespecified consequential contract violation occurs within the next `L` steps of the ungoverned or shadow-mode trajectory.

Examples of valid endpoints are externally auditable events such as:

- execution of an operation outside `P0`;
- irreversible external action without required authorization;
- explicitly prohibited communication;
- unauthorized modification of protected monitor infrastructure;
- task-contract failure defined from environment state and `Gamma`.

Sensor anomalies may precede an endpoint but may not define the endpoint label.

## 8. Coherent/viable operating region

CG-0.2 does not require the operating region to be a sensor-wise hyperrectangle.

Use a specified boundary function:

```text
K_Gamma = {z, T : h_Gamma(z, T) >= 0}
```

The boundary may be rule-based or learned, but it must be frozen before confirmatory evaluation and must not use future endpoint labels from the test set.

## 9. Forward viability requires a future policy

For history `T_t`, proposed action `a_t`, future policy `pi`, and horizon `L`:

```text
V_L(T_t, a_t, pi)
  = P^pi[z_(t+tau) in K_Gamma for every tau=1..L | T_t, a_t]
```

This makes explicit that viability after the next action depends on subsequent behavior.

A lower confidence/risk bound may be used:

```text
V_lower = LCB_(1-alpha)[V_L]
```

Any guarantee applies only under the assumptions of the calibration procedure and evaluation distribution.

## 10. State viability margin

State margin answers: **how much viability reserve remains in the current trajectory, independent of the consequence level of the next proposed action?**

Choose a frozen reference continuation policy `pi_ref` and reference requirement `theta_0`:

```text
M_state_t = V_lower_L(T_t, pi_ref) - theta_0
```

The exact implementation may marginalize over an action distribution or evaluate a specified reference action set, but the method must be fixed before testing.

State-margin velocity is:

```text
dM_state_t = (M_state_t - M_state_(t-k)) / Delta t
```

Only `M_state` is used for trajectory deterioration velocity.

A negative velocity means state viability reserve is declining under the fixed reference definition; it cannot be caused solely by the current action receiving a higher consequence classification.

## 11. Action authorization margin

Action margin answers: **is this particular proposed action sufficiently assured to authorize?**

Let `r(a_t)` be a consequence score and `theta(r)` the required viability:

```text
M_action_t(a_t)
  = V_lower_L(T_t, a_t, pi_follow) - theta(r(a_t))
```

`M_action_t` is used for authorization decisions but not for state-margin velocity.

## 12. Boundary approach

A simple local diagnostic is the linear crossing estimate:

```text
T_boundary_linear = M_state_t / max(epsilon, -dM_state_t)
```

only when:

```text
M_state_t > 0 and dM_state_t < 0
```

If `M_state_t <= 0`, boundary time is `0`. If `dM_state_t >= 0`, the linear estimate is infinite.

This quantity is explicitly a local linear extrapolation, not a physical law. A later version may replace it with a first-passage distribution:

```text
P(T_boundary <= tau | T_t)
```

## 13. Reaction-time condition

Define:

```text
T_reaction = T_detection + T_decision + T_revocation + T_fallback
```

with safety allowance `T_safety`.

A predictive reversion condition may be:

```text
T_boundary_linear <= T_reaction + T_safety
```

or an analogous first-passage risk threshold in later implementations.

## 14. Governor decision inputs

The corrected decision function is:

```text
D_t = G(
  H_t,
  M_state_t,
  dM_state_t,
  M_action_t(a_t),
  r(a_t),
  Gamma,
  monitor_integrity
)
```

Possible outputs:

```text
PERMIT | VERIFY | RESTRICT | REPLAN | REVERT | HALT
```

A hard-invariant violation bypasses probabilistic reasoning and triggers deterministic denial plus the configured containment response.

## 15. Primary experimental comparison

The decisive comparison is made at a matched trajectory-level false-alarm budget.

Candidate systems:

1. per-action safety classifier;
2. strongest full-trajectory monitor available to the experiment;
3. rolling anomaly detector;
4. sequential accumulation of the baseline monitor score;
5. hard permissions only;
6. forward state predictor only;
7. `H_t` only;
8. `M_state_t` only;
9. `H_t + M_state_t`;
10. full `H_t + M_state_t + dM_state_t`.

The full CG predictor is supported only if it adds measurable early-warning value beyond the strongest simpler baseline.

## 16. Warning metric

In shadow mode:

```text
t_failure = first independently defined consequential contract violation
t_alarm   = first threshold crossing
L_warning = t_failure - t_alarm
```

Meaningful early warning requires positive `L_warning`.

Intervention-mode experiments must separately compare failure prevention and retained utility because successful intervention may remove the counterfactual failure event.

## 17. Calibration discipline

Thresholds are learned on training/calibration trajectories and frozen before test evaluation.

For alert threshold `h` and benign-regime false-alarm budget `alpha`:

```text
h* = inf { h : P_A(max_t score_t >= h) <= alpha }
```

Model, scaffold, environment, tools, or task-distribution changes require explicit recalibration or an out-of-distribution evaluation declaration.

## 18. Falsification criteria

The primary hypothesis is unsupported if, on prespecified held-out evaluation data and at the same false-alarm budget:

- full CG does not improve warning lead time over the strongest baseline;
- median warning lead time is non-positive on the target failure set;
- any apparent gain disappears when sensor correlations are modeled correctly;
- benign novelty produces a false-alarm rate outside the preregistered tolerance;
- viability estimates are materially miscalibrated;
- monitor-aware trajectories can systematically preserve high apparent state margin while producing the independent endpoint;
- utility loss required to obtain the safety gain exceeds the preregistered budget.

## 19. Claim discipline

A successful experiment would support a narrow statement:

> Certain measured trajectory dynamics contain predictive information about future contract failure under the tested agent, scaffold, environment, and task distribution.

It would not establish universal coherence, alignment, controllability, or safety.

The broader theory earns credibility only through replication across agents, scaffolds, task families, and adversarial conditions.
