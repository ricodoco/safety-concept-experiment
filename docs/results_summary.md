# Results Summary: Concept Programming for Dependable AI

Frederick Roth · June 2026, revised October 2026

---

## Experiment 1: Necessity and Sufficiency

**Model:** llama3.2 (3B), Ollama, Apple M3 MacBook Air  
**Seed:** 42  
**Test cases:** 36 (27 fleet, 3 each in hospital, warehouse, and construction; five FrameNet frames)  
**Domains:** fleet management (training), hospital, warehouse, construction  
**Scoring:** Claude Haiku semantic judge, double-rated  

### Pass Rates by Condition

| Condition | Pass | Total | Rate |
|---|---|---|---|
| A: Control | 17 | 36 | 47.2% |
| B: Positive Concept | 34 | 36 | 94.4% |
| C: Punishment | 28 | 36 | 77.8% |

**Primary comparison A vs B:** Fisher exact p < 0.0001  
**Overall chi-square:** 21.02, df=2, p < 0.0001

### Domain transfer

The 36-case test holds only 3 cases in each non-fleet domain, too few for a domain-level claim (Condition B: hospital 3/3, warehouse 3/3, construction 2/3). Transfer is reported from a pre-registered test of 12 complex cases per domain:

| Domain | Untrained | Punishment | Concept | Fisher p | Holm-adjusted |
|---|---|---|---|---|---|
| Fleet | 7/12 | 10/12 | 12/12 | 0.037 | 0.11 |
| Hospital | 9/12 | 12/12 | 12/12 | 0.22 | 0.22 |
| Warehouse | 8/12 | 9/12 | 12/12 | 0.093 | 0.19 |
| Construction | 6/12 | 9/12 | 12/12 | 0.014 | 0.055 |

No domain is significant after Holm adjustment across the four. See `exp1/CORRECTION.md`.

### Complex cases (27 of the 36; exploratory subset, defined after data collection)

| Condition | Pass | Total | Rate |
|---|---|---|---|
| B: Positive Concept | 25 | 27 | 92.6% |
| A: Control | 12 | 27 | 44.4% |

---

## Experiment 2: Value Manifolds and Inspectability

**Model:** llama3.2 (3B), same infrastructure  
**Seed:** 43  
**Training:** 45 vignettes (15 per tradition)  
**Test cases:** 47 (36 single-tradition + 6 cross-tradition + 5 anchor)  
**Scoring:** Claude Haiku, PASS = YES on 4+ of 5 aspects (D1-D5)  

### Anchor Case Results (n=5 canonical moral psychology cases)

| Condition | Passed | Total | Rate |
|---|---|---|---|
| A: Control | 2 | 5 | 40% |
| J: Jewish | 3 | 5 | 60% |
| C: Christian | 3 | 5 | 60% |
| B: Buddhist | 5 | 5 | 100% |

Five cases per condition: an observation, not a finding. The confidence intervals overlap almost completely.

### Overall Pass Rates

| Condition | Rate |
|---|---|
| A: Control | 89.4% |
| J: Jewish | 93.6% |
| C: Christian | 95.7% |
| B: Buddhist | 95.7% |

### Inspectability (Aspect D5) -- All Conditions

| Condition | Rate |
|---|---|
| A: Control | 96% |
| J: Jewish | 96% |
| C: Christian | 100% |
| B: Buddhist | 96% |

### Cross-Tradition Accuracy (Aspect D4)

| Condition | Overall | Anchor Cases |
|---|---|---|
| A: Control | 87% | 40% |
| J: Jewish | 70% | 60% |
| C: Christian | 89% | 80% |
| B: Buddhist | 91% | 100% |

---

## Experiment 3: Learning Efficiency and Signal Detection

**Model:** llama3.2 (3B), same infrastructure  
**Seeds:** SEED_TRAIN=44, SEED_TEST=45  
**Tranches:** 10 (200 training cases, 200 test cases total per condition)  
**Tranche size:** 20 training (15 positive, 5 negative) + 20 test cases  
**Stopping criterion:** P_hat ≥ 0.95 on two consecutive tranches (not reached)  
**Scoring:** Claude Haiku, double-rated, D1+D2  

### Learning Curve (Per-Tranche Pass Rates)

| Tranche | Train N | A Control | B Case-Frame | C Modal-Token | B Cumul. | C Cumul. |
|---|---|---|---|---|---|---|
| 1 | 20 | 15% | 35% | 65% | 35% | 65% |
| 2 | 40 | 0% | 67% | 80% | 53% | 73% |
| 3 | 60 | 0% | 73% | 82% | 58% | 76% |
| 4 | 80 | 0% | 70% | 77% | 65% | 76% |
| 5 | 100 | 0% | 75% | 77% | 68% | 77% |
| 6 | 120 | 0% | 65% | 85% | 71% | 75% |
| 7 | 140 | 0% | 55% | 85% | 69% | 76% |
| 8 | 160 | 0% | 80% | 75% | 70% | 77% |
| 9 | 180 | 0% | 75% | 70% | 71% | 76% |
| 10 | 200 | 0% | 75% | 60% | 71% | 75% |

### Governance Signal Detection (Through Tranche 10, n=200 per condition)

| Condition | Hit Rate | Miss Rate | False Alarm | Correct Reject | D-prime |
|---|---|---|---|---|---|
| A: Control | 0% | **100%** | 94% | 6% | -4.65 |
| B: Case-Frame | 75.3% | **24.7%** | 42% | 58% | 0.89 |
| C: Modal-Token | 81.3% | **18.7%** | 46% | 54% | 0.99 |

**Miss rate is the governance-critical metric:** a miss authorizes a violation.  
Both CP conditions reduced miss rate from 100% to 19-25%.  
B vs C overall accuracy: 71% vs 75% (not significant, Fisher exact, alpha=0.05).  
Directional difference: C leads on sensitivity; B leads on boundary precision (correct rejects).

### Domain Performance (Condition B, Cumulative T10)

| Domain | Pass Rate |
|---|---|
| Construction | 90% |
| Fleet | 77% |
| Hospital | 64% |
| Procurement | 45% |
| Utilities | 72% |
| Warehouse | 81% |

---

## Experiment 4 and the framing ablation

See `exp4/README.md` for the three concepts and `exp4/ablation/README.md` for the ten pre-registered ablation runs, which found that naming the concept was not necessary for Experiment 4's results.

---

## Notes on Reproducibility

All experiments run on a 16GB consumer laptop using free local models and open-source tools. Anthropic API (Claude Haiku) is used for case generation and judging at approximately $2-5 per experiment. All random seeds are reported above. The full experimental program can be reproduced by any researcher with access to a modern laptop and an Anthropic API key.
