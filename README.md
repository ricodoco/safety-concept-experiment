# Concept Programming for Dependable AI

**Frederick Roth** · Professor, Information Sciences, Naval Postgraduate School (Retired) · Fellow, AAAI  
`ricodoco@gmail.com` · GitHub: `ricodoco` · SSRN author ID: 1667607

---

## What This Repository Contains

This repository is the complete open-science release accompanying the paper:

> Roth, F. (2026). Concept Programming for Dependable AI. *PLOS ONE* [submitted].

It contains all experimental code, training data, test cases, result files, and analysis scripts for four controlled experiments demonstrating that Concept Programming (CP) produces dependable, inspectable, certifiable behavior in Language-Grounded Neural Systems (LGNS).

**The entire program runs on a consumer laptop at negligible cost.** No GPU cluster, institutional affiliation, or proprietary model access is required.

---

## Overview

Language-Grounded Neural Systems deployed in governance, healthcare, law, and public administration fail dependably under pressure. Current safety methods train what to avoid rather than what to embody. Concept Programming instills each behavioral concept as a named positive attractor in the LGNS's neural state space, paired with an appropriate response: blocking (prohibitions), required action (obligations), or value-shaped inference (values).

Four experiments establish the method:

| Experiment | Claim | Key Result |
|---|---|---|
| 1 | Necessity and sufficiency | CP 94.4% (34/36) vs punishment 77.8% (28/36) vs control 47.2% (17/36); complex pressure cases 25/27 vs 12/27; transfer 3/3 hospital, 3/3 warehouse, 2/3 construction |
| 2 | Value manifolds and inspectability | Buddhist condition 5/5 anchor cases; control 2/5 |
| 3 | Learning efficiency and signal detection | Miss rate reduced from 100% (control) to 19-25% within 200 training cases |
| 4 | Frame-family generalization after fine-tuning | Zero misses on trained frame families in all 13 training rounds; all misses confined to the withheld family |

---

## Repository Structure

```
├── README.md                    # This file
├── LICENSE                      # MIT License
├── exp1/                        # Experiment 1: Necessity and Sufficiency
│   ├── README.md
│   ├── Modelfile_A              # Control condition Modelfile
│   ├── Modelfile_B              # Positive concept condition Modelfile
│   ├── Modelfile_C              # Punishment framing condition Modelfile
│   ├── test_cases.json          # 36 test cases (seed 42)
│   ├── results.json             # Full results
│   └── evaluate.py              # Evaluation script
├── exp2/                        # Experiment 2: Value Manifolds
│   ├── README.md
│   ├── Modelfiles/              # One per tradition (A, Jewish, Christian, Buddhist)
│   ├── training_vignettes.json  # 45 training vignettes (seed 43)
│   ├── test_cases.json          # 47 test cases (3 tiers)
│   ├── results_values.json      # Full results
│   └── evaluate.py              # Evaluation script
├── exp3/                        # Experiment 3: Learning Efficiency
│   ├── README.md
│   ├── config.py                # Concepts, frames, domains, Modelfile templates
│   ├── generate.py              # Case generator (case-frame and modal-token)
│   ├── build_models.py          # Ollama model builder
│   ├── evaluate.py              # Evaluation with SDT framework
│   ├── run_tranche.py           # Single tranche runner
│   ├── run_experiment.py        # Auto-running experiment loop
│   └── data/                    # Generated cases and results (10 tranches)
├── exp4/                        # Experiment 4: Frame-family generalization (LoRA fine-tuning)
│   ├── runs/                    # Per-case scores for every run and round
│   └── tools/recompute_tables.py  # Recomputes every reported figure (standard library only)
└── docs/
    ├── CP_Paper_v7.docx         # Submitted manuscript
    └── results_summary.md       # Summary of all results
```

---

## Requirements

### Hardware
- Apple M3 MacBook Air (16GB) or equivalent consumer laptop
- Any macOS, Linux, or Windows system capable of running Ollama

### Software
```bash
# Install Ollama
# macOS: https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Pull the base model
ollama pull llama3.2

# Python dependencies
pip install anthropic requests

# Set your Anthropic API key (used for case generation and judging only)
export ANTHROPIC_API_KEY=your_key_here
```

### Model
All experiments use `llama3.2` (3B parameters) served locally via Ollama. The Anthropic API (Claude Haiku) is used only for case generation and double-rated scoring -- approximately $2-5 per experiment.

---

## Running the Experiments

### Experiment 1 (Necessity and Sufficiency)
```bash
cd exp1
# Build condition models
ollama create exp1_condA -f Modelfile_A
ollama create exp1_condB -f Modelfile_B
ollama create exp1_condC -f Modelfile_C
# Evaluate
python evaluate.py
```

### Experiment 2 (Value Manifolds)
```bash
cd exp2
# Build tradition models
ollama create exp2_condA -f Modelfiles/Modelfile_A
ollama create exp2_condJ -f Modelfiles/Modelfile_J
ollama create exp2_condC -f Modelfiles/Modelfile_C
ollama create exp2_condB -f Modelfiles/Modelfile_B
# Evaluate
python evaluate.py
```

### Experiment 3 (Learning Efficiency) -- full run
```bash
cd exp3
python run_experiment.py --from-tranche 1
# Runs all 10 tranches automatically (~3-4 hours total)
# Or run one tranche at a time:
python run_tranche.py --tranche 1
python run_tranche.py --tranche 2
# ...
```

---

## Key Results

### Experiment 1
- Condition B (Positive Concept): 94.4% (34/36)
- Condition C (Punishment): 77.8% (28/36)  
- Condition A (Control): 47.2% (17/36)
- Fisher exact p < 0.0001; chi-square = 21.02, df = 2
- Domain transfer (novel domains, no retraining): Hospital 100%, Warehouse 100%, Construction 66.7%
- Seeds: seed=42

### Experiment 2
- Buddhist condition: 5/5 anchor cases
- Jewish condition: 3/5; Christian condition: 3/5; Control: 2/5
- Inspectability (D5): 96-100% across all conditions including control
- Overall pass rates: Control 89.4%, Jewish 93.6%, Christian 95.7%, Buddhist 95.7%
- Seeds: seed=43

### Experiment 3 (10 tranches, 200 training cases)

| Condition | Hit Rate | Miss Rate | False Alarm | Correct Reject | D-prime |
|---|---|---|---|---|---|
| A: Control | 0% | **100%** | 94% | 6% | -4.65 |
| B: Case-Frame | 75.3% | **24.7%** | 42% | 58% | 0.89 |
| C: Modal-Token | 81.3% | **18.7%** | 46% | 54% | 0.99 |

- Seeds: SEED_TRAIN=44, SEED_TEST=45

---

## Licensing

This repository is released under the **MIT License**. The experimental program, training data, test cases, and all code are freely available for research, education, and public-interest applications.

Two patent applications cover methods described in the companion paper. The patent applications preserve commercial licensing rights while ensuring the methodology remains freely available for non-commercial use under the MIT License.

---

## Citation

```
Roth, F. (2026). Concept Programming for Dependable AI. PLOS ONE [submitted].
Available: https://github.com/ricodoco/safety-concept-experiment
SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6970658
```

---

## Contact

Frederick Roth · `ricodoco@gmail.com`  
SSRN: https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=1667607  
Google Scholar: https://scholar.google.com/citations?user=nErgouIAAAAJ
