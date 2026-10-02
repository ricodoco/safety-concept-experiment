# Pre-registration: Experiment 4 framing ablation, mechanism test (v3)

Written and committed before the analysis below is run and before any of its
scores are seen.

## Hypothesis, and its status

The v1 and v2 ablations found that naming the Regulated concept in the
classifier prompt impaired generalization to the withheld frame family
(`implied_by_stance`), and that the name accounted for most of the effect. The
proposed mechanism, formed after those results were seen: the concept's name
("A chatbot response that makes a personalized investment recommendation")
carries a meaning from pretraining that covers explicit advice but not a
recommendation implied only by stance. Training reshapes the decision where
examples exist; on the unseen withheld form the model falls back on that prior
meaning and misses it. A neutral label carries no prior, so the boundary is
built only from what the training examples share.

Because the hypothesis was formed after seeing the ablation results, it is
treated here as a hypothesis under test, not a finding.

## Test

`tools/zero_shot_prior.py` scores the 2600-case Regulated locked test set with
the untrained base model (Qwen2.5-1.5B-Instruct, no adapter), using the
toolkit's own scorer, under three prompt labels:

- **name:** the concept's real label, as in Arm A;
- **neutral:** "Category T", as in Arm B;
- **matched:** "A chatbot response that steers the reader toward a specific
  investment decision suited to their own situation, whether it says so
  explicitly or implies it through the stance it takes", a label written to
  match the specification, including implied forms.

For each label it computes, for each positive frame family, the AUC of that
family's cases against all 2000 safe test cases. "Covered" means the four
families used in training (`comparative_steer`, `direct_instruction`,
`fitted_suggestion`, `negative_instruction`), pooled.

## Predictions, fixed in advance

- **P1 (primary):** under the name label, the untrained model separates the
  covered families from safe cases better than it separates the withheld family:
  AUC(covered) minus AUC(withheld) is at least 0.10, and its bootstrap 95
  percent interval (2000 resamples of cases, seed 20261001) excludes zero.
- **P2:** under the neutral label, no family's AUC exceeds 0.65.
- **P3:** the matched label narrows the gap: gap(name) minus gap(matched) has a
  bootstrap 95 percent interval that excludes zero, in the positive direction.

## Interpretation, fixed in advance

- P1 supported: the name's prior meaning already disfavors the withheld form
  before any training, as the mechanism requires.
- P1 not supported: the mechanism as stated is not supported; the ablation
  result stands but its explanation remains open.
- P2 and P3 are reported whatever P1 shows. P3 supported, together with P1,
  indicates that the harm comes from a mismatch between the name's meaning and
  the specification, not from naming as such.

This analysis needs no training and makes no claim about trained models. A
direct test of P3 in training (a run under the matched label) would require new
runs and a further pre-registration.

## Reporting rule

All three predictions are reported whatever they show, with the full table of
AUCs by family and label, in the paper and the repository.
