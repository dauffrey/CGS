# Coherence Governor System (CGS)

CGS is a falsification-driven research project investigating whether trajectory-level changes in an agentic AI system can provide **actionable warning of declining behavioral viability before a consequential control failure occurs**.

The project treats the Coherence Governor as an **independent runtime-assurance control plane**, not as another prompt or policy instruction given to the acting agent.

> **Research principle:** Autonomous authority should not exceed demonstrated coherence.
>
> **Early-warning principle:** Intervene on predicted loss of coherent control, not merely observed failure.

## Scientific status

CGS is a research hypothesis and prototype architecture. It is **not** an established safety theorem, deployment guarantee, or substitute for deterministic security controls.

The central empirical question is:

> At a fixed false-alarm rate, can accumulated trajectory hazard, state viability margin, and state-margin velocity predict an independently defined future contract violation earlier than a strong trajectory-monitor baseline?

The hypothesis is useful only if it survives falsification attempts.

## Repository roadmap

- `docs/specs/CG-0.1.md` — original research architecture and terminology.
- `docs/specs/CG-0.2.md` — corrected mathematical specification separating state and action margins.
- `experiments/CG-EXP-0001.md` — preregistered first experiment.
- `src/cgs/` — minimal reference implementation.
- `tests/` — unit tests for the core mathematics and endpoint separation.

## Design constraints

1. The acting agent must not control the Governor, its thresholds, telemetry, audit records, permission enforcement, or fallback.
2. Hard authorization boundaries remain deterministic and take precedence over probabilistic estimates.
3. Failure endpoints used for evaluation must be defined independently of CG sensor values.
4. `C_t` is a normalized presentation of accumulated hazard `H_t`, not an independent source of evidence.
5. State viability and action authorization are separate quantities.
6. Margin velocity is computed only from the state viability margin.
7. Experimental comparisons are made at matched false-alarm budgets.

## Initial hypotheses

- **H1 — Temporal accumulation:** weak correlated anomalies improve early-warning performance relative to single-step monitoring.
- **H2 — State-margin hypothesis:** declining state viability reserve provides positive warning lead time before independently defined control failure.
- **H3 — Multi-sensor hypothesis:** properly modeled joint signals outperform any single sensor without double-counting correlated evidence.
- **H4 — Risk-conditioned autonomy:** graduated authority reduction prevents more consequential failures than binary unrestricted/terminate control while retaining more utility.
- **H5 — Cross-domain hypothesis:** the same high-level structure can generalize across distinct agentic task families.

## License

MIT. See `LICENSE`.
