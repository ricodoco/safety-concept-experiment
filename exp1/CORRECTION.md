# Correction: domain-transfer sample size

## What was wrong

`test_cases.json` and `results.json` in this folder hold 3 cases per
non-fleet domain (hospital, warehouse, construction site) — too few to
support a domain-level claim. The manuscript this data supports
(PONE-D-26-31237) originally reported domain-transfer statistics computed
at 12 cases per domain in its Section 5.1. No 12-per-domain dataset existed
at submission. This file explains both the code defect that caused the
small sample and the correction.

## The bug

`generate_cases_v2.py`'s `generate_set()` function built cases for the
fleet domain in blocks sized by its `n_per_concept` argument, but the
transfer-domain block ran its per-concept loop exactly once per domain
regardless of that argument — always 1 case per concept, 3 per domain,
however large a set was requested. The version of the script in this
repository is patched: the transfer-domain loop now takes its own
`n_transfer_per_concept` argument, defaulting to 1 so that
`generate_set(3, tag)` still reproduces this folder's original 36-case
dataset exactly, under the same seed (42). This has been verified
byte-for-byte against `test_cases.json`.

## The follow-up

`generate_transfer_set_v1.py`, in `../exp1` alongside this file, calls the
same patched `generate_cases_v2.py` functions with
`n_transfer_per_concept=4`, producing 12 cases per concept-domain cell
across all four domains (fleet included as a matched in-domain reference,
which the original transfer test never had). `PREREGISTRATION_transfer_v1.md`
states the comparison — Fisher exact, B vs A, tested within each domain —
before `evaluate_transfer_v1.py` was run against it. `results_transfer_v1.json`
holds the per-case results; `test_cases_transfer_v1.json` and
`generation_log_transfer_v1.json` document exactly what was tested.

## Corrected results

| Domain | Concept (Positive) | Untrained (Control) | Fisher p |
|---|---|---|---|
| Fleet | 12/12 (100%) | 7/12 (58.3%) | 0.037 |
| Hospital | 12/12 (100%) | 9/12 (75.0%) | 0.217 |
| Warehouse | 12/12 (100%) | 8/12 (66.7%) | 0.093 |
| Construction | 12/12 (100%) | 6/12 (50.0%) | 0.014 |

The direction is consistent across all four domains. It reaches
significance individually in two of four at this sample size; the other
two show the same direction and a comparable gap without crossing the
conventional threshold alone, which is reported plainly rather than
resolved by pooling domains after the fact.

## Files in this folder

- `test_cases.json`, `results.json` — the original 36-case primary test
  (unchanged; this is not what was wrong)
- `generate_cases_v2.py` — patched generator (see bugfix note in its own header)
- `evaluate_v3.py` — the evaluation pipeline (unchanged)
- `system_prompts.json`, `Modelfile_B`, `Modelfile_C` — unchanged
- `generate_transfer_set_v1.py`, `evaluate_transfer_v1.py` — the follow-up
- `test_cases_transfer_v1.json`, `generation_log_transfer_v1.json`,
  `results_transfer_v1.json` — the follow-up's cases, generation log, and results
- `PREREGISTRATION_transfer_v1.md` — the analysis plan, committed before evaluation
