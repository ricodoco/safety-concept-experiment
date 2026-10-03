# Experiment 4: Data and Recomputation Tools

Supporting data for Roth, F., "Concept Programming for Dependable AI," PLOS ONE,
manuscript PONE-D-26-31237.

This directory holds every case, every per-case score, and the run manifests behind
the Experiment 4 results in Section 5.4 of the paper.

## Recompute the reported numbers

```
python3 tools/recompute_tables.py .
```

Python 3.9 or later, standard library only. No model, no GPU, no network, no
training toolkit. Runs in seconds.

For each run it first reports the pre-training constituent probe, which is Table 14 of the paper, giving each constituent's separation under both the AUC-derived estimate the paper uses and the median-split estimate it replaced. It then reports, for each round, the miss rate on the locked test set, the
miss rate broken out by frame family, the false alarm rate on held-out ordinary
requests, the false alarm rate on the concept's own safe cases, and where a
selection frame was used, its miss rate. It also cross-checks each recomputed miss
rate against the value recorded in that run's history file and prints whether the
two agree.

## Concept labels

The paper uses readable labels. The directories use the internal names.

| Paper | Directory | Concept |
| --- | --- | --- |
| Rule 1 | `runs/glyph_synth` | Two named parties, odd count of items, date in the second half of the month |
| Rule 2 | `runs/glyph_prior` | Perishable food, addressed to a kitchen, time critical |
| Regulated | `runs/advice_unlicensed` | Personalized investment recommendation with no licensing referral, under FINRA Rule 2111 and Regulation Best Interest |

Three further directories support Tables 18 and 19.

| Directory | What it is |
| --- | --- |
| `runs/glyph_synth_hl` | Rule 1 with `ledger_entry` withheld instead of `narrative_embedded` |
| `runs/glyph_synth_hm` | Rule 1 with `message_report` withheld |
| `runs/glyph_synth_ablation` | The containment ablation: the same round-1 corpus with the 300 seeded ordinary requests removed |

## Frame families

Each concept generates its cases through several frame families, which express the
same underlying facts in different wording. Training withholds at least one family
from every run, and that family's miss rate measures generalization to an unseen
form.

| Concept | Families | Withheld |
| --- | --- | --- |
| Rule 1 and Rule 2 | `ledger_entry`, `message_report`, `narrative_embedded` | `narrative_embedded` in the main runs |
| Regulated | `direct_instruction`, `fitted_suggestion`, `comparative_steer`, `negative_instruction`, `implied_by_stance` | `implied_by_stance`, plus a selection frame withheld for round ranking only |

## Layout of a run

```
runs/<concept>/
  data/
    train.jsonl        training cases
    test.jsonl         the locked test set, never trained on
    calib.jsonl        calibration cases
    capability.jsonl   300 held-out ordinary requests
    dev.jsonl          development cases
    select.jsonl       selection frame, Regulated only
  loop/
    manifest.json      base model, numerical settings, toolkit version
    history.json       per-round record including the decision threshold
    corpus.json        the accumulated training corpus
    scores/
      rN_test.jsonl        per-case scores on the locked test set, round N
      rN_capability.jsonl  per-case scores on ordinary requests, round N
      rN_calib.jsonl       per-case scores on calibration cases
      rN_select.jsonl      per-case scores on the selection frame
```

A score record is one JSON object per line:

```
{"id": "...", "label": 1, "frame": "ledger_entry", "score": 9.140625}
```

`label` is 1 for a case the specification covers and 0 for one it does not. A case
counts as flagged when its score is at or above the round's threshold, which is
recorded per round in `history.json`.

Note that `history.json` opens with a foundation phase record before the training
rounds, so its list is offset by one from the score file numbering. The
recomputation tool keys on each record's own `round` field rather than on position.

## Which round the paper reports

| Concept | Reported round | Miss | Withheld family | Ordinary requests |
| --- | --- | --- | --- | --- |
| Rule 1 | 1 of 1 | 0.0083 | 0.025 | 0.000 |
| Rule 2 | 3 | 0.0283 | 0.085 | 0.000 |
| Regulated | 3 of 4 | 0.0850 | 0.425 | 0.000 |

## Model and configuration

Base model: Qwen/Qwen2.5-1.5B-Instruct, float16, MPS device, `sdpa` attention
implementation, trained by low-rank adaptation. Hardware: Apple M3 MacBook Air,
16 GB. Random seeds appear in the Methods section of the paper. Each run's
`manifest.json` records the toolkit version that produced it.

Training is deterministic given corpus and seed. A round rerun on an identical
corpus reproduced its predecessor exactly.

The manifests record provenance. They do not certify the runs against a current
copy of the toolkit, which continued to develop after these runs completed. The
containment ablation was run later than the three main concepts, under a subsequent
toolkit version, and its `result.json` records its configuration in place of a
manifest.

## What is not here

Adapter weights are omitted; they are large and no reported number requires them.

The training toolkit that produced the adapters is not included, because the author
has a commercial interest in it. Its absence does not restrict verification of any
reported result. Every figure in the paper derives from the per-case scores in this
directory, and Section 4 of the paper states the training procedure in sufficient
detail to reimplement.

Runs excluded as superseded or out of scope: earlier runs of the same concepts
under prior toolkit versions, a concept that was explored and not reported, and
runs on a different base model that postdate the paper.

## Framing ablation

`ablation/` holds the ten pre-registered runs that test whether the concept's name and the weak-constituent curriculum contribute anything beyond fine-tuning on the same examples (Section 5.5 of the paper). See `ablation/README.md`. The four pre-registrations are the `PREREGISTRATION_framing_ablation_v*.md` files in this directory.

## Related

Experiments 1 to 3 materials are in `../exp1`, `../exp2`, and `../exp3`.

## License

MIT. See `../LICENSE`.

## Contact

Frederick Roth, ricodoco@gmail.com
Professor, Information Sciences, Naval Postgraduate School (Retired)
