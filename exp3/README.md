# Experiment 3: Case-Frame Concept Training Efficiency

**Research question:** How many training instances does case-frame concept
training require to reach dependable performance (P ≥ 0.95), and how does
it compare to modal-token training?

## Design

| | |
|---|---|
| Model | llama3.2 (3B, local via Ollama) |
| Conditions | A (control), B (case-frame), C (modal-token) |
| Safety concepts | C1 SPEED_LIMIT_IS_ABSOLUTE, C2 BUDGET_IS_ABSOLUTE, C3 SAFETY_VIOLATION_MUST_BE_REPORTED |
| FrameNet frames | Compliance, Reporting, Imposing_obligation, Required_event, Expensiveness, Authority_delegation, Accountability_report |
| Domains | fleet, hospital, warehouse, construction, procurement, utilities |
| Tranche size | 20 training cases (15 pos / 5 neg) + 20 test cases |
| Max tranches | 5 (100 training, 100 test cases) |
| Stopping rule | P_hat ≥ 0.95 on two consecutive tranches |
| Judge | Claude Haiku, double-rated |

**Condition B** generates training scenarios by sampling slot-fillers from
the full lexical frequency distribution of each FrameNet frame, producing
varied natural language covering the concept's case-frame extension.

**Condition C** fills every frame slot with the single most frequent lexical
realization (modal token), producing repetitive, surface-pattern training.

**Negative cases (25%):** Scenarios where the concept legitimately does NOT
apply. Five taxonomic categories per concept (e.g., no posted limit exists,
non-vehicular speed, simulation exercise). The correct response is helpful
engagement without concept invocation.

## Running

### Prerequisites
- Ollama installed with llama3.2 pulled: `ollama pull llama3.2`
- `ANTHROPIC_API_KEY` set in environment (for case generation and judging)
- Python packages: `pip install anthropic`

### Run one tranche
```bash
cd exp3
python run_tranche.py --tranche 1
python run_tranche.py --tranche 2
# ... continue until criterion met or tranche 5 reached
```

### Resume after interruption
```bash
# If cases generated but models not built:
python run_tranche.py --tranche N --skip-generate

# If models built but evaluation not complete:
python run_tranche.py --tranche N --skip-generate --skip-build

# Report only (no new runs):
python evaluate.py --tranche N --report-only
```

### Data files (in data/)
```
train_condB_T1.json     # Training cases, condition B, tranche 1
train_condC_T1.json     # Training cases, condition C, tranche 1
test_condA_T1.json      # Test cases, condition A, tranche 1
test_condB_T1.json      # Test cases, condition B, tranche 1
test_condC_T1.json      # Test cases, condition C, tranche 1
results_condA_T1.json   # Evaluation results, condition A, tranche 1
results_condB_T1.json   # Evaluation results, condition B, tranche 1
results_condC_T1.json   # Evaluation results, condition C, tranche 1
```

## Predicted outcome
- Condition B reaches P ≥ 0.95 by tranche 2-3 (40-60 training cases)
- Condition C plateaus below 0.90, particularly on novel domains and
  negative cases requiring semantic understanding of concept preconditions
- Condition A (control) remains near Experiment 1 baseline (~47%)

## Stopping at 100 cases
If criterion not met after 5 tranches, report learning curves for B and C,
note the gap, and discuss whether a larger base model or extended training
would close it. The B vs. C comparison remains the primary scientific claim
regardless of whether absolute criterion is met.

## Citation
Roth, F. (2026). Concept programming for dependable AI. [In preparation.]
Seeds: SEED_TRAIN=44, SEED_TEST=45
