# Pre-registration: Experiment 4 framing ablation, follow-up (v2)

Written and committed before any run listed here begins.

## Why this follow-up exists

The v1 ablation (`PREREGISTRATION_framing_ablation_v1.md`) compared, on the
Regulated concept, the full method (Arm A: concept name in every prompt, weak
constituent instilled) with the same training stripped of framing (Arm B:
neutral label "Category T", no constituents). Result at each arm's delivered
round: withheld-family miss A 55/120 (0.458), B 1/120 (0.008), Fisher p = 6e-19.
False alarms did not differ. Arm B's first round alone also beat Arm A's
delivered round. The result runs against the paper's framing hypothesis.

One uncontrolled difference was found afterward. Arm A's round 1 trained at
batch size 8; a memory fix then set batch size 4, used for Arm A's later rounds
and all of Arm B. Each round trains a fresh adapter from the base model, so the
delivered rounds of both arms trained under identical settings; round 1's batch
size could affect only which cases were mined into the corpus. Arm A was also
interrupted and resumed once.

This follow-up asks three questions: does the v1 result hold under a new seed
with no uncontrolled differences; which component of framing, the name or the
constituent instillation, accounts for it; and does it hold on a second concept.
It is designed to find out, not to favor any outcome.

## Settings common to every run

Toolkit copy `~/Downloads/sg` as used for v1, including the gradient-
checkpointing patch to `train.py`. Base model Qwen2.5-1.5B-Instruct. Batch size
4 throughout. At most 4 rounds. `--no-propose --local`. Published data splits,
verified by fingerprint before each run. Each run started fresh. If a run is
interrupted, it is resumed with `--resume` and the interruption is reported.

## The six runs

| Run | Concept | Arm | Name in prompt | Constituents instilled | Seed |
|---|---|---|---|---|---|
| 1 | Regulated | A2 | yes | yes | 20260821 |
| 2 | Regulated | B2 | no | no | 20260821 |
| 3 | Regulated | C | yes | no | 20260820 |
| 4 | Regulated | D | no | yes | 20260820 |
| 5 | Rule 1 | A | yes | yes | 20260820 |
| 6 | Rule 1 | B | no | no | 20260820 |

Runs 3 and 4 use the seed of v1 Arms A and B, so the four Regulated arms at that
seed form a 2-by-2 design (name × constituents). Each arm's configuration
differs from Arm A's only in `id` and in the factor(s) its row changes.

## Endpoint and tests

Primary endpoint for every comparison: miss rate on the withheld frame family at
each arm's delivered round, two-sided Fisher exact test. Withheld family:
`implied_by_stance` for Regulated, `narrative_embedded` for Rule 1. Delivered
round chosen by the toolkit's own rule, identically for all arms.

- **Q1, replication:** A2 against B2.
- **Q2, decomposition (seed 20260820):** name effect, A against D and C against
  B; constituent effect, A against C and D against B. Holm correction across
  these four tests.
- **Q3, generality:** Rule 1 A against Rule 1 B.

Secondary, reported for every run: overall miss, trained-family miss, false
alarms on the concept's safe cases, false alarms on ordinary requests, and the
round-by-round trajectory.

## Interpretation, fixed in advance

- **Q1:** B2 significantly lower than A2: the v1 reversal replicates. No
  significant difference: the v1 result does not survive a change of seed and is
  reported as not robust. A2 significantly lower: the v1 result reverses under a
  new seed; both seeds are reported and neither is preferred.
- **Q2:** a significant effect attributes the v1 difference to that component
  (name, constituents, or both). No significant effect for either: the
  decomposition is inconclusive at this sample size.
- **Q3:** reported in the same three-way terms as Q1, for Rule 1.

## Reporting rule

Every run listed here, and both v1 runs, will be reported in the paper and the
repository whatever they show, including runs that favor or disfavor concept
framing. No run is dropped, repeated, or replaced after its result is seen.
Results are not averaged across seeds to produce a single favorable figure. Any
run added beyond these six requires a further pre-registration (v3) committed
before it starts.
