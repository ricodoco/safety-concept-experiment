# Framing ablation: ten runs

Data and tools for Section 5.5 of "Concept Programming for Dependable AI" (PONE-D-26-31237). The ablation tests whether the concept's name in the classifier prompt, and the instillation of weak constituents before composite training (the curriculum), contribute anything beyond fine-tuning on the same examples.

The four pre-registrations are in the parent directory. Each was committed before the runs it governs; `PROVENANCE.txt` lists when each run directory was created. `PREREGISTRATION_framing_ablation_v2_ERRATUM.md` corrects one sentence of the v2 pre-registration.

## Runs

| Run | Folder | Concept | Label | Curriculum | Seed | Delivered round | Pre-registration |
|---|---|---|---|---|---|---|---|
| A | `regulated_A_s1/` | Regulated | own | yes | 1 | 4 | v1 |
| B | `regulated_B_s1/` | Regulated | neutral | no | 1 | 3 | v1 |
| C | `regulated_C_s1/` | Regulated | own | no | 1 | 4 | v2 |
| D | `regulated_D_s1/` | Regulated | neutral | yes | 1 | 1 | v2 |
| E1 | `regulated_E1_s1/` | Regulated | specification | no | 1 | 4 | v4 |
| E2 | `regulated_E2_s1/` | Regulated | specification | yes | 1 | 2 | v4 |
| A2 | `regulated_A2_s2/` | Regulated | own | yes | 2 | 1 | v2 |
| B2 | `regulated_B2_s2/` | Regulated | neutral | no | 2 | 3 | v2 |
| R1A | `rule1_A_s1/` | Rule 1 | own | yes | 1 | 1 | v2 |
| R1B | `rule1_B_s1/` | Rule 1 | neutral | no | 1 | 4 | v2 |

Labels: *own* is the concept's own label; *neutral* is "Category T"; *specification* is built only from the specification's essential features. The exact wording of every label, the constituent predicates used, the seed, the batch size, and the maximum rounds for each run are in `arms.json`. Seed 1 is 20260820 and seed 2 is 20260821. Within a concept, all runs used the published data splits in `../runs/advice_unlicensed/data` (Regulated) and `../runs/glyph_synth/data` (Rule 1).

## Contents

- `<folder>/`: for each run, `history.json` (per-round results and decision thresholds), `manifest.json` (model, settings, toolkit version, code fingerprints), `corpus.json` (the accumulated training corpus), and `scores/` (per-case scores on the locked test, the ordinary requests, and the calibration cases, one file per round).
- `arms.json`: the definition of every arm.
- `comparisons/`: the output of each pre-registered comparison, as run.
- `untrained/`: per-case scores of the untrained base model under the labels of the two pre-registered mechanism tests, and the results computed from them.
- `tools/`: the analysis scripts.
- `PROVENANCE.txt`: run start times against pre-registration commit times.

## Recomputing the paper's numbers

```bash
pip install numpy scipy
cd exp4/ablation
python3 tools/recompute_ablation.py            # Tables 20 and 21
python3 tools/compare_arms.py regulated_A_s1 regulated_B_s1    # any single pair
python3 tools/zero_shot_prior.py --reanalyse --test-data ../runs/advice_unlicensed/data/test.jsonl --scores untrained/zero_shot_prior_scores.jsonl --results /tmp/prior.json
python3 tools/zero_shot_v4.py --reanalyse --test-data ../runs/advice_unlicensed/data/test.jsonl --scores untrained/zero_shot_v4_scores.jsonl --results /tmp/v4.json
```

The last two reproduce Table 22. Scoring the untrained model anew needs the training toolkit's scorer and is not possible from this repository; the saved per-case scores make the analysis reproducible without it.

## Notes

- The training toolkit is not included because the author has a commercial interest in it. Adapter weights and run logs are not included either.
- The ablation runs used one copy of the toolkit, which differs from the copies behind the three main concepts in its training and loop code and default configuration. Each manifest records the version and file fingerprints.
- Two changes were made to that copy for memory reasons: gradient checkpointing, which changes memory use and not the gradient computed, and a training batch size of 4 in place of the default 8.
- Arm A (seed 1) was interrupted several times by memory and disk limits and resumed from saved state, and its batch size was reduced from 8 to 4 while it ran. Its delivered round trained at batch size 4. Every other run used batch size 4 throughout and ran from start to finish.
- The mechanism hypotheses discussed in Section 6.2 of the paper were formed after the ablation results were seen.
