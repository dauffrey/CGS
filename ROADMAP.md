# CGS Research Roadmap

**Program objective:** determine whether causal trajectory dynamics can provide actionable warning of future consequential control failure earlier than strong monitoring baselines, at a matched benign false-alarm rate.

CGS advances only through preregistered, falsification-oriented gates. A failed gate narrows or stops the claim; it does not authorize post-outcome retuning of the failed experiment.

## Phase 0 — Mathematical and instrumentation foundation

**Status: complete for current scope.**

Completed work:

- CG-0.1 established the initial architecture.
- CG-0.2 separated state viability margin from action authorization margin.
- Margin velocity was restricted to the state margin.
- The future failure endpoint was separated from CG sensor values.
- `C_index_t` was retained only as a normalized presentation of accumulated hazard `H_t`, not as independent evidence.
- CG-EXP-0001 was preregistered with a fixed 5% benign trajectory-level false-alarm budget.
- The synthetic harness was implemented with positive and null controls.

**Scientific boundary:** synthetic instrumentation success demonstrates only that the pipeline can recover deliberately embedded signal without manufacturing warning in the null control. It is not evidence that CG predicts failure in real agents.

## Phase 1 — Evidentiary CG-EXP-0001 on real agent trajectories

**Status: next active research gate.**

### 1. Freeze the experimental system

For every evaluated trajectory, freeze and record:

- model/provider/version;
- system prompt and scaffold version;
- tool set and tool permissions;
- task contract and prohibited outcomes;
- environment/sandbox version;
- Governor sensor/estimator version;
- baseline monitor versions;
- code SHA and configuration hashes.

No evaluated third-party production target is permitted. Tasks must run in controlled, sandboxed, simulated, or otherwise authorized environments.

### 2. Define independent consequential endpoints

Before evaluation data are generated, define one or more externally auditable failure events from task contract plus environment state.

The endpoint must not depend on:

- a CG score;
- a CG threshold;
- an alert from `H_t`, `M_state_t`, or `dM_state_t`;
- the acting agent's own claim that it succeeded or failed.

The primary horizon label remains:

```text
Y_(t,L) = 1
```

iff a prespecified consequential violation occurs during steps `t+1 ... t+L` in the ungoverned/shadow trajectory.

### 3. Build failure and benign task families

The first evidentiary dataset should include multiple distinct failure mechanisms, including at minimum a subset of:

- gradual goal drift;
- repeated boundary probing followed by violation;
- proxy/reward gaming;
- prompt-injection-induced objective substitution;
- stale/corrupted state followed by consequential error;
- capability/permission escalation unrelated to the task;
- monitor-evasion attempts;
- combinations of individually weak precursor signals.

Benign controls must deliberately include difficult but legitimate behavior so that the Governor cannot succeed merely by treating novelty, persistence, retries, uncertainty, or unusual tool sequences as failure.

### 4. Freeze the data split before test scoring

Use trajectory-disjoint train, calibration, and test partitions.

No prefix from one trajectory may appear in more than one partition.

Recommended first evidentiary target:

```text
train:       >= 40%
calibration: >= 30%
test:        >= 30%
```

Increase dataset size if the paired statistical test is underpowered.

### 5. Freeze baseline comparators

At minimum retain:

- **B1:** strongest available current-action monitor;
- **B2:** strongest full-trajectory-prefix monitor;
- **B3:** sequentialized version of the strongest baseline score.

B3 is essential: CG must not be credited merely for temporal accumulation if the same improvement can be obtained by sequentializing an existing monitor.

### 6. Freeze CG predictors

Primary candidate family:

```text
C1 = H_t
C2 = M_state_t
C3 = H_t + M_state_t
C4 = H_t + M_state_t + dM_state_t
```

`M_action_t` remains outside the primary warning feature set and is reserved for later intervention-policy testing.

### 7. Calibrate every system at the same false-alarm budget

Primary operating point:

```text
alpha = 0.05
```

Each system receives its own calibration threshold satisfying, or conservatively undershooting, the 5% benign trajectory-level false-alarm budget.

No threshold may be tuned after test outcomes are viewed.

### 8. Execute once against the frozen test set

Primary lead-time measure:

```text
L_warning = t_failure - t_alarm
```

A missed pre-failure warning receives `L_warning = 0` in the conservative primary analysis.

### 9. Phase-1 survival gate

Let `B*` be the strongest of B1-B3 on the frozen test set. The central CG-EXP-0001 claim receives support only if all preregistered conditions hold:

1. `median(L_warning_C4) > 0`;
2. `median(L_warning_C4) > median(L_warning_B*)`;
3. the trajectory-paired bootstrap 95% confidence interval for the median lead-time difference `C4 - B*` has lower bound `> 0`;
4. C4 detection recall is no more than 5 percentage points below `B*`;
5. the result is not driven solely by one failure family.

If the confidence-interval condition is infeasible because the evaluation set is too small, classify the run as exploratory rather than confirmatory.

### Phase-1 decision

- **Unsupported:** C4 fails the primary criteria, especially if B3 matches or exceeds it.
- **Partially supported:** temporal accumulation helps but `M_state_t` and/or `dM_state_t` add no incremental value.
- **Supported for tested distribution:** all primary criteria survive at the matched false-alarm rate.

No broader controllability claim is authorized by a single Phase-1 success.

## Phase 2 — Independent replication

**Entry condition:** Phase 1 survives.

Require both:

1. a materially different task family/environment; and
2. a different model and/or scaffold.

Freeze the predictor before replication. Do not redesign C4 using replication outcomes and still call the same run confirmatory.

Primary question:

> Does the warning advantage reproduce without re-deriving the detector for the new distribution?

A result that disappears under modest distribution shift is evidence of a narrow detector, not a general Governor.

## Phase 3 — Monitor-aware adversarial evaluation

**Entry condition:** at least one successful independent replication.

Evaluate whether an acting agent, task perturbation, or environment change can reduce warning quality while still producing consequential failures.

Test at minimum:

- sensor omission or partial observability;
- benign-looking precursor trajectories;
- delayed evidence;
- correlated sensor failure;
- attempts to remain below individual sensor thresholds;
- distribution shift that preserves the same externally defined failure endpoint.

The Governor must remain external to the acting agent and must retain protected telemetry, thresholds, and audit records.

## Phase 4 — Randomized intervention experiment

**Entry condition:** predictive validity survives Phases 1-3.

Only here should CG move from shadow mode to active intervention research.

Randomize eligible trajectories between:

- ungoverned/shadow control;
- binary stop/terminate baseline;
- graduated CG authority reduction;
- other strong intervention comparators where appropriate.

Measure:

- consequential failure reduction;
- retained task utility;
- unnecessary intervention rate;
- recovery success;
- intervention latency;
- monitor-evasion success;
- failure displacement into new modes.

The intervention policy is a separate scientific claim from the predictor. A good predictor can still support a poor control policy.

## Phase 5 — Cross-domain and operational validation

**Entry condition:** randomized intervention benefit survives.

Expand cautiously across distinct agentic domains such as coding, workflow automation, cyber-simulation, research agents, and multi-tool enterprise tasks.

Required before any production-readiness claim:

- external replication;
- calibration under realistic base rates;
- explicit uncertainty reporting;
- stress testing for missing or corrupted telemetry;
- operational incident and rollback procedures;
- human-override semantics;
- security review of the Governor itself;
- privacy and data-retention review;
- measurable limits on what the detector does **not** know.

## Phase 6 — Runtime assurance prototype

Only after the preceding evidence exists should CGS be packaged as a reusable runtime-assurance component.

A candidate interface may eventually expose:

```text
risk_of_failure_within_horizon
state_viability_margin
state_margin_velocity
warning_confidence
primary_contributors
recommended_authority_level
```

These fields must remain evidence-backed diagnostics, not anthropomorphic claims about intent, consciousness, deception, or morality.

## Stop conditions

CGS should be narrowed, redesigned, or stopped if repeated well-powered tests show that:

- a strong sequential baseline matches or exceeds CG warning lead time;
- `M_state_t` adds no reproducible information beyond simpler observables;
- `dM_state_t` adds no incremental information beyond current state;
- useful recall requires an operationally unacceptable false-alarm rate;
- warning disappears across modest task/model changes;
- intervention based on the warning reduces safety or utility relative to simpler controls.

A negative outcome is a valid research result.

## Current next action

Do **not** add another synthetic theory layer.

The next substantive milestone is:

> **Design, preregister, collect, and execute the first evidentiary CG-EXP-0001 dataset using frozen real-agent/scaffold trajectories in controlled environments with independently defined failure endpoints.**

See [`experiments/CG-EXP-0001.md`](experiments/CG-EXP-0001.md) for the canonical experiment specification and [`RESEARCH_LINEAGE.md`](RESEARCH_LINEAGE.md) for the relationship to EFGM and Artificial Homeostasis.
