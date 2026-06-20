# Experiment 1: Necessity and Sufficiency

Establishes that positive concept training outperforms punishment-analog framing and untrained control on governance safety constraints, and transfers to novel domains with no domain-specific training.

## Results

| Condition | Pass | Total | Rate |
|---|---|---|---|
| A: Control | 17 | 36 | 47.2% |
| B: Positive Concept | 34 | 36 | **94.4%** |
| C: Punishment | 28 | 36 | 77.8% |

Fisher exact p < 0.0001. Domain transfer (no retraining): Hospital 100%, Warehouse 100%, Construction 66.7%. Seed: 42.

## Files

- `Modelfile_A` -- Control (helpful assistant, no safety framing)
- `Modelfile_B` -- Positive Concept (named positive attractors + worked examples)
- `Modelfile_C` -- Punishment (prohibitions only)
- `generate_test_cases.py` -- Generates 36 test cases via Claude Haiku (seed=42)
- `evaluate.py` -- Evaluates all three conditions

## Running

```bash
# Create models
ollama create exp1_condA -f Modelfile_A
ollama create exp1_condB -f Modelfile_B
ollama create exp1_condC -f Modelfile_C

# Generate test cases (or use supplied test_cases.json)
python generate_test_cases.py

# Evaluate
python evaluate.py
```

## Concepts
- SPEED_LIMIT_IS_ABSOLUTE
- BUDGET_IS_ABSOLUTE
- SAFETY_VIOLATION_MUST_BE_REPORTED

## FrameNet Frames
Compliance, Reporting, Imposing_obligation, Required_event, Expensiveness

## Domains
Fleet management (training), hospital operations, warehouse logistics, construction site
