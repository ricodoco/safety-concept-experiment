# Pre-registration: Experiment 1 domain-transfer follow-up (v1)

Written and committed before `evaluate_transfer_v1.py` is run against any model.

## Why this exists

The original Experiment 1 test set (`test_cases_v2.json`, 36 cases) held only
3 cases per non-fleet domain (hospital, warehouse, construction site) — a bug
in `generate_cases_v2.py`, where the transfer-domain sampling loop ran once
per domain regardless of the requested case count. Three cases cannot
support a domain-level claim (Wilson 95% CI on 2/3 = 20.8 to 93.9). This
follow-up does not replace that test. The original 36-case result (34/36 vs
17/36 correct, Fisher p < 0.0001) is untouched and remains the paper's
primary finding.

## What this follow-up adds

`generate_transfer_set_v1.py`, seed 42, generates 12 complex, single-concept
cases per concept-domain cell across four domains — fleet, hospital,
warehouse, construction site — 48 cases total, using the same per-concept
case templates as the original generator (`make_C1_case`, `make_C2_case`,
`make_C3_case`, unchanged). Fleet is included so all four domains share the
same n and the same case composition, which the original design never had.

## Primary comparison (specified now, before evaluation)

Condition B (positive concept) vs Condition A (control), by Fisher exact
test, computed separately within each of the four domains.

## Secondary

- Condition C (punishment) vs A, and B vs C, within each domain.
- Whether B's pass rate in fleet (the trained domain) differs from its
  pooled rate across the three transfer domains.

## What would count as replication

The original exploratory finding was a gap between B and A that held up
under social pressure. This follow-up counts as support if B outperforms A
in at least the three transfer domains individually, not merely when they
are pooled together — pooling can hide a domain where the effect is absent.

## Unchanged from the original pipeline

Same three models (`llama3.2`, `llama3.2-positive`, `llama3.2-punishment`),
same `system_prompts.json`, same double-judge Claude scoring with flipped
concept order, same conservative AND-of-both-judges pass rule.

## Commit this file first

This plan should be committed to the repository, timestamped, before
`evaluate_transfer_v1.py` is run. That is what allows the paper to call the
comparison specified in advance rather than after seeing results.
