# CGS Research Lineage

**Status:** research-program convergence record  
**Date:** 2026-09-14  
**Active program:** Coherence Governor System (CGS)

CGS is the focused runtime-assurance research program for testing whether observable trajectory dynamics can provide actionable warning of declining behavioral viability **before** an independently defined consequential control failure occurs.

This document records how CGS relates to two earlier and still-preserved research repositories. It does not merge their Git histories, rewrite their results, or transfer scientific support from one repository to another.

## Repository roles

| Repository | Current role | What it contributes | What it does **not** establish for CGS |
|---|---|---|---|
| [`dauffrey/efgm`](https://github.com/dauffrey/efgm) | Foundational/provenance research | Entropy-flow lineage, decision-integrity measurement, governance constructs, temporal experiments, falsification discipline, and historical negative/positive results | It does not validate the CGS predictor, CGS thresholds, CGS sensors, or CGS deployment claims |
| [`dauffrey/EFGM-artificial-homeostasis`](https://github.com/dauffrey/EFGM-artificial-homeostasis) | Mechanism-discovery/evidence laboratory | Disturbance/reserve coupling, resilience-margin ideas, recovery behavior, counterfactual abstention, failure-boundary work, and trajectory-warning experiments | Its controller/observer results do not count as CGS validation unless prospectively transferred and independently tested under CGS criteria |
| [`dauffrey/CGS`](https://github.com/dauffrey/CGS) | Primary active early-warning research program | Independent runtime Governor, state/action-margin separation, fixed-false-alarm comparison, independently defined failure endpoints, warning lead time, and intervention research | It is not yet a proven safety system, production assurance layer, or universal controllability detector |

## Conceptual lineage

The three repositories are best understood as an evolutionary research sequence rather than three competing products:

```text
EFGM
broad theory and measurement of flow / entropy / governance
        |
        v
EFGM Artificial Homeostasis
self-regulation under disturbance / reserve / recovery
        |
        v
candidate insight
state reserve and its trajectory may carry pre-failure information
        |
        v
CGS
independent runtime early-warning hypothesis
        |
        v
Can H_t, M_state_t and dM_state_t predict a future control failure
before a strong trajectory monitor, at the same false-alarm rate?
```

The lineage is explanatory only. Each repository retains its own scientific scope and evidence boundaries.

## Scientific custody rule

No result is inherited merely because a later project was inspired by an earlier one.

A construct may move from EFGM or Artificial Homeostasis into CGS only when all of the following are true:

1. the transferred construct is defined explicitly in CGS terminology;
2. its causal observation boundary is specified;
3. its failure endpoint is defined independently of the construct;
4. the hypothesis and success/falsification criteria are frozen before confirmatory test outcomes are observed;
5. thresholds are calibrated without test-set leakage;
6. performance is compared against strong independent baselines at a matched false-alarm operating point;
7. negative, null, weakening, and invalid results are preserved;
8. any positive result is claimed only for the tested model/scaffold/task distribution until replicated.

This prevents cross-repository idea transfer from becoming cross-repository evidence leakage.

## What is frozen versus active

### EFGM

EFGM remains the canonical provenance record for its original formulation, v1/v2 models, Agent Governance work, experiment history, baselines, and falsification results. New work whose **primary scientific claim** is runtime prediction of impending control failure should normally be developed in CGS rather than creating a parallel early-warning formulation in EFGM.

Existing EFGM experiments remain scientifically intact. Candidate ideas may still be documented there when their purpose is EFGM-specific theory or provenance, but they do not automatically become CGS features.

### EFGM Artificial Homeostasis

Artificial Homeostasis remains a mechanism-discovery laboratory for internal regulation, disturbance pressure, operational reserve, recovery, over-regulation, counterfactual intervention, and related warning mechanisms.

Its historical and in-flight experimental chains remain intact. They are not being collapsed into CGS. New experiments should remain there when their primary question concerns self-regulation or homeostatic mechanism discovery rather than the general runtime early-warning claim.

### CGS

CGS is the active convergence point for the narrower hypothesis:

> At a fixed benign false-alarm rate, can causal trajectory-level signals predict an independently defined consequential control failure with useful positive lead time and outperform the strongest tested trajectory-monitor baseline?

The current preregistered experiment is [`experiments/CG-EXP-0001.md`](experiments/CG-EXP-0001.md). The synthetic harness is an instrumentation check only; it is not evidentiary support for the hypothesis.

## Terminology boundary

CGS should not import historical terminology solely for continuity. A term is retained only if it improves measurement or falsifiability.

In particular:

- **EFGM entropy/flow/governance measures** are not assumed to be CGS sensors;
- **Artificial Homeostasis resilience margin** is a precursor concept, not identical by definition to `M_state_t`;
- **CGS coherence** is not a claim of consciousness, moral alignment, semantic truth, or a universal scalar property of intelligence;
- **controllability** in CGS is operationalized through externally auditable future contract failure, not inferred from the Governor's own score.

## Research-program decision

From this convergence point forward:

- keep the three Git histories separate;
- preserve all prior experiments and frozen evidence in place;
- do not duplicate the same early-warning hypothesis across repositories;
- concentrate new general runtime early-warning validation in CGS;
- treat EFGM and Artificial Homeostasis as upstream sources of hypotheses, mechanisms, counterexamples, and historical evidence;
- require prospective CGS validation before any upstream construct is credited as a CGS improvement.

## Success condition for convergence

The convergence is successful if the repository structure makes one question unambiguous:

> **Does CGS provide earlier, statistically defensible warning of a future independently defined loss-of-control event than strong existing monitors at the same false-alarm budget?**

If not, CGS should be weakened, redesigned, or rejected according to its preregistered evidence rather than rescued by moving the claim back into another repository.
