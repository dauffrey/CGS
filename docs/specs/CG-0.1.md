# Coherence Governor Specification — CG-0.1

**Status:** Historical research hypothesis / prototype specification  
**Purpose:** Early detection and containment of coherence degradation in autonomous and agentic AI systems.

CG-0.1 is preserved as the original operational formulation. It is not a safety theorem. The corrected experimental formulation is CG-0.2.

## 1. Governing principle

> **Autonomous authority should not exceed demonstrated coherence.**

The Governor is an independent runtime-assurance system. It observes the acting agent, estimates degradation, predicts whether proposed actions remain inside a coherent operating envelope, and reduces authority before a consequential unsafe action when evidence warrants intervention.

The acting agent must not control the Governor, its thresholds, telemetry, permission enforcement, audit records, or fallback mechanism.

## 2. Conceptual model

The original conceptual chain is:

```text
T × E -> Et -> F ± e -> A | M
```

where:

- `T`: time / trajectory length;
- `E`: available capability, resources, computational energy;
- `Et`: transfer of capability into action;
- `F`: directed functional flow;
- `e`: entropic pressure, including noise, drift, contradiction, disturbance, and uncertainty;
- `A`: aligned/coherent regime;
- `M`: misaligned/degraded regime.

Working definition:

> Coherence is the degree to which a system sustains directed functional flow over time while preserving alignment against noise, drift, disturbance, uncertainty, and accumulated degradation.

## 3. Safety objective

The Governor attempts to detect a transition of the form:

```text
A -> A' -> A'' -> ? -> M
```

before waiting for:

```text
M -> consequential unsafe action
```

The primary research question is whether measurable precursors predict loss of coherent operation sufficiently early to permit intervention.

## 4. Immutable task contract

Before execution:

```text
Gamma = (G0, K0, P0, R0)
```

with:

- `G0`: authorized objective;
- `K0`: constraints;
- `P0`: granted permissions;
- `R0`: acceptable risk envelope.

The agent may change strategy but may not silently redefine `Gamma`. Objective, permission, or risk-envelope changes require an external authorization event.

## 5. Coherence sensor vector

At each decision step:

```text
z_t = [G_t, P_t, B_t, R_t, X_t, U_t, I_t]
```

with components normalized to `[0, 1]`.

- `G_t`: goal-action divergence;
- `P_t`: pathological persistence without progress;
- `B_t`: pressure against authorization boundaries;
- `R_t`: reward/proxy divergence;
- `X_t`: unauthorized coordination;
- `U_t`: uncertainty mismatch;
- `I_t`: optional internal/process anomaly.

No single sensor is assumed trustworthy.

## 6. Instantaneous degradation evidence

The preferred statistical form is a trajectory-conditioned log-likelihood ratio:

```text
ell_t = log p(z_t | T_<t, M) / p(z_t | T_<t, A)
```

Positive evidence favors degradation; negative evidence favors the coherent regime.

When a reliable likelihood model is unavailable, an experimentally calibrated score may be used:

```text
ell_t ~= w^T z_t - b
```

## 7. Accumulated hazard

CG-0.1 proposed:

```text
H_t = max(0, H_(t-1) + ell_t - kappa)
```

where `kappa` tolerates ordinary fluctuations.

Persistent weak anomalies can therefore accumulate while temporary anomalies can decay toward baseline.

## 8. Present coherence index

CG-0.1 defined:

```text
C_t = exp(-H_t / lambda_H)
```

so that `H_t -> 0` implies `C_t -> 1` and increasing hazard lowers the index.

`C_t` is not a probability unless explicitly calibrated as one.

## 9. Coherent operating envelope

The initial prototype envelope was a threshold region:

```text
K = {z : G<Gmax, P<Pmax, B<Bmax, R<Rmax, X<Xmax, U<Umax, I<Imax}
```

The Governor is intended to predict boundary approach rather than merely detect that the boundary has already been crossed.

## 10. Forward viability

For proposed action `a_t` and horizon `L`:

```text
V_L(s_t, a_t) = P(s_(t+1:t+L) in K | T_t, a_t)
```

A calibrated lower confidence bound is used when possible:

```text
V_lower = LCB_(1-alpha)[V_L]
```

## 11. Risk-conditioned requirement

Let consequence score `r(a_t)` lie in `[0,1]` and let required viability increase with consequence:

```text
theta(r) = 1 - delta(r),  d delta / dr < 0
```

Higher-consequence actions therefore require stronger evidence of continued viability.

## 12. Original coherence margin

CG-0.1 defined one action-conditioned margin:

```text
M_t(a_t) = V_lower(s_t, a_t) - theta(r(a_t))
```

and a margin velocity:

```text
dM_t = (M_t - M_(t-k)) / Delta t
```

with a linear time-to-boundary approximation:

```text
T_boundary = M_t / (-dM_t + epsilon),  when dM_t < 0
```

The Governor compares this with detection, decision, revocation, fallback, and safety time.

## 13. Intervention states

The conceptual control states are:

- **GREEN:** normal authorized operation;
- **YELLOW:** increasing monitoring and verification;
- **ORANGE:** remove high-risk permissions, disable irreversible actions, checkpoint, and replan;
- **RED:** trusted reversion or halt.

Hard deterministic invariants always override probabilistic coherence estimates.

## 14. Evaluation

Primary metric:

```text
L_warning = t_unsafe - t_alarm
```

Positive warning lead time is required for meaningful early warning.

Additional metrics include detection recall, false-alarm rate, missed consequential event rate, retained task utility, intervention frequency, recovery success, and monitor-evasion success.

Ablations compare individual sensors, instantaneous monitoring, sequential monitoring, and sequential monitoring plus forward prediction.

## 15. Falsification

The hypothesis is unsupported if, at matched false-alarm rates, it fails to provide positive warning lead time on important independently defined failures, performs no better than strong trajectory-monitor baselines, fails under benign novelty, produces poorly calibrated viability estimates, is systematically evadable, or destroys practical task utility.

## 16. Known CG-0.1 limitations

CG-0.1 contains four issues corrected in CG-0.2:

1. **State and action margins are conflated.** A change in action consequence can change `theta(r)` and therefore create apparent negative margin velocity without any deterioration in the underlying trajectory.
2. **Margin velocity is therefore contaminated by action selection.** Velocity should be computed from an action-normalized state viability reserve.
3. **Evaluation endpoints can become circular unless defined independently of the sensors.** Future contract failure must not be labeled by the same signals used to predict it.
4. **`C_t` is not independent evidence.** It is a monotonic transformation of `H_t` and should be treated as an index or presentation variable.

CG-0.2 makes these corrections and is the specification to use for definitive experiments.
