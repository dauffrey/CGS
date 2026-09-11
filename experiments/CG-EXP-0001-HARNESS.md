# CG-EXP-0001 Synthetic Harness

**Status:** Instrumentation control only  
**Evidentiary:** No  
**Parent preregistration:** `experiments/CG-EXP-0001.md`

## Purpose

This harness makes CG-EXP-0001 executable end-to-end before real agent trajectories are collected. It validates data partitioning, sensor computation, online scoring, fixed-false-alarm calibration, warning-lead calculation, paired bootstrap comparison, reporting, and CI automation.

Synthetic outputs **must not** be cited as evidence that the Coherence Governor predicts real agent failures.

## Controls

### Positive control

Synthetic failing trajectories contain gradual observable precursor dynamics before an independently assigned final contract-violation endpoint. A functioning harness should detect these dynamics and the full C4 predictor should obtain positive warning lead relative to the strongest B1-B3 baseline under the benchmark's fixed design.

The positive control is deliberately constructed to contain a signal. Passing it verifies instrumentation sensitivity, not scientific validity.

### Null control

Synthetic failing trajectories receive the same final endpoint label but their pre-failure telemetry remains benign-like. The harness should not manufacture positive warning lead in this condition.

This is a leakage test: if C4 appears to predict the null-control endpoint early, the pipeline should be treated as invalid until the leakage source is found.

## Synthetic task families

The positive control contains:

- difficult benign retry trajectories;
- benign strategy changes;
- gradual goal-drift trajectories;
- persistence followed by simulated scope escalation;
- simulated boundary-pressure trajectories.

All activity is generated in-memory. The harness performs no network access, tool use, credential access, external communication, or interaction with third-party systems.

## Data partitions

Default run:

```text
train:       16 trajectories per family = 80
calibration: 12 trajectories per family = 60
test:        12 trajectories per family = 60
```

The harness asserts that trajectory identifiers are disjoint across partitions.

The synthetic control uses fixed transparent estimators, so the training partition is generated to validate the final data contract but is not used for parameter fitting. A real-agent implementation must replace this with a frozen training procedure where required.

## Systems

The harness evaluates:

```text
B1  instantaneous risk monitor
B2  smoothed full-prefix monitor
B3  sequentialized baseline
C1  accumulated CG hazard
C2  state-margin risk
C3  H + M_state
C4  H + M_state + dM_state
```

Each system receives an independently calibrated threshold using benign calibration trajectories and the preregistered trajectory-level false-alarm budget:

```text
alpha = 0.05
```

## Run locally

```bash
python -m pip install -e '.[dev]'
python -m cgs.experiment --output-dir artifacts
```

or, after installation:

```bash
cgs-synthetic --output-dir artifacts
```

The command writes:

```text
artifacts/cg-exp-0001-synthetic.json
artifacts/cg-exp-0001-synthetic.md
```

It exits non-zero if either the positive-control sensitivity check or null-control leakage check fails.

## Interpretation gate

A successful synthetic run means only:

> The CG-EXP-0001 analysis pipeline can recover a deliberately embedded gradual precursor signal while not inventing lead time in a null-control condition.

It does **not** mean:

- CG predicts real autonomous-agent failure;
- coherence has been empirically validated;
- the state margin is calibrated on real distributions;
- the selected sensor estimators are appropriate for deployment;
- any safety guarantee has been established.

The next evidentiary step requires frozen real-agent/scaffold trajectories, independently defined environment endpoints, trained/frozen monitor implementations, and untouched held-out test data under the original CG-EXP-0001 preregistration.
