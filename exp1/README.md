# Experiment 1: Necessity and Sufficiency

Tests whether positive concept training outperforms punishment-analog framing and an untrained control on governance safety constraints, and whether the effect carries to domains absent from training. All three conditions use llama3.2 (3B) through Ollama. Responses are scored by Claude Haiku (claude-haiku-4-5-20251001), double-rated with concept order flipped; a response counts as correct only if both passes agree it is.

## Results

| Condition | Pass | Total | Rate |
|---|---|---|---|
| A: Control | 17 | 36 | 47.2% |
| B: Positive Concept | 34 | 36 | **94.4%** |
| C: Punishment | 28 | 36 | 77.8% |

Primary comparison, A against B: Fisher exact p < 0.0001. Seed 42.

The 36 cases are 27 fleet cases and 3 each in hospital, warehouse, and construction. Three cases per domain cannot support a domain-level claim, so transfer is reported from a separate pre-registered test of 12 complex cases in each of four domains (`PREREGISTRATION_transfer_v1.md`, `test_cases_transfer_v1.json`, `results_transfer_v1.json`):

| Domain | Untrained | Punishment | Concept | Fisher p, Concept vs Untrained | Holm-adjusted |
|---|---|---|---|---|---|
| Fleet | 7/12 | 10/12 | 12/12 | 0.037 | 0.11 |
| Hospital | 9/12 | 12/12 | 12/12 | 0.22 | 0.22 |
| Warehouse | 8/12 | 9/12 | 12/12 | 0.093 | 0.19 |
| Construction | 6/12 | 9/12 | 12/12 | 0.014 | 0.055 |

No single domain is significant after Holm adjustment across the four. `CORRECTION.md` explains why the original transfer cell was too small and how it was replaced.

## Files

- `test_cases.json`: the 36 test cases. `evaluate_v3.py` reads it under the name `test_cases_v2.json`.
- `results.json`: per-case responses and judgments for those cases. `evaluate_v3.py` writes it as `results_v3.json`.
- `generate_cases_v2.py`: the case generator. Called as `generate_set(3, tag)` after the training set, with seed 42, it reproduces `test_cases.json` exactly. It carries the corrected `n_transfer_per_concept` argument.
- `evaluate_v3.py`, `system_prompts.json`, `generation_log.json`: the evaluation pipeline, the three system prompts, and the generation record.
- `Modelfile_B`, `Modelfile_C`: the Positive Concept and Punishment models. Condition A runs the base `llama3.2` with the control prompt in `system_prompts.json`; `Modelfile_A` is kept for reference.
- `generate_transfer_set_v1.py`, `exec_lib.py`, `evaluate_transfer_v1.py`: the transfer test's generator, the generator functions it imports, and its evaluation script.
- `PREREGISTRATION_transfer_v1.md`, `CORRECTION.md`: the pre-registration, committed before the transfer test ran, and the correction note.

## Running

```bash
ollama pull llama3.2
ollama create llama3.2-positive -f Modelfile_B
ollama create llama3.2-punishment -f Modelfile_C
export ANTHROPIC_API_KEY=your_key_here

# Original 36-case test (evaluate_v3.py expects the v2/v3 file names)
cp test_cases.json test_cases_v2.json
python evaluate_v3.py

# Transfer test: regenerate the 48 cases (seed 42), then evaluate
python generate_transfer_set_v1.py
python evaluate_transfer_v1.py
```

## Concepts
- SPEED_LIMIT_IS_ABSOLUTE
- BUDGET_IS_ABSOLUTE
- SAFETY_VIOLATION_MUST_BE_REPORTED

## FrameNet frames
Compliance, Reporting, Imposing_obligation, Required_event, Expensiveness

## Domains
Fleet management (training), hospital operations, warehouse logistics, construction site
