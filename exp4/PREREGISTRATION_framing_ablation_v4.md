# Pre-registration: Experiment 4 framing ablation, label-wording test (v4)

Written and committed before either run below begins.

## Background

On Regulated, the concept's name in the classifier prompt impaired
generalization to the withheld frame family (v1, v2). The v3 untrained-model
test found that the name disfavors the withheld family only slightly before
training (P1 not supported at its 0.10 threshold), that the neutral label is not
free of prior structure (P2 not supported), and that a label worded to match the
specification raised the untrained model's AUC on the withheld family (P3
supported).

**A correction to v3.** The v3 "matched" label described the withheld form
itself ("whether it says so explicitly or implies it through the stance it
takes"). It was written after the withheld family's identity was known, so it
carried information about that family into the prompt. The v3 P3 result must
therefore be read as showing that describing the withheld form in the label
helps the untrained model, not that a faithful label does. This will be stated
wherever P3 is reported.

## Question

Does the harm come from the specific wording of the concept's name, which in
ordinary usage means explicit advice, or from naming the concept at all? To
avoid the v3 leak, the test label is built only from the concept's pre-existing
specification (its `essential_features`, written before any ablation), with no
reference to implication, stance, or any frame family:

> "A chatbot response that advises this customer to take or avoid an action on a
> specific security, fund, product, or allocation"

## Runs

Regulated, seed 20260820, `config/default_ablation.yaml` (batch size 4, at most
4 rounds), `--no-propose --local`, published data verified by fingerprint, each
run fresh. Same toolkit copy and settings as Arms A to D.

| Arm | Label | Constituents instilled |
|---|---|---|
| E1 | specification label | no |
| E2 | specification label | yes |

With Arms A to D these form a 3-by-2 design: label (name, specification,
neutral) by constituents (yes, no), at one seed.

## Endpoint and tests

Withheld-family (`implied_by_stance`) miss rate at each arm's delivered round,
two-sided Fisher exact test.

- **Primary:** E1 against C (specification label against the name, both
  without constituents).
- **Secondary, Holm-corrected together:** E1 against B (specification label
  against neutral, no constituents); E2 against A (specification label against
  the name, with constituents); E2 against E1 (constituent effect under the
  specification label).
- **Secondary, untrained model:** `tools/zero_shot_v4.py` scores the locked test
  set with the untrained model under the name and specification labels.
  Prediction S1: gap(name) minus gap(specification), with gap defined as in v3,
  has a bootstrap 95 percent interval excluding zero in the positive direction.

## Interpretation, fixed in advance

- **E1 significantly lower than C:** the wording matters. A label faithful to
  the specification reduces the harm, which points to the colloquial meaning of
  the name.
- **No significant difference:** naming the concept with any descriptive label
  harms generalization here; the specific wording is not shown to be the cause.
- **E1 significantly higher than C:** reported as such.
- E1 against B then says whether the specification label removes the harm
  entirely (no difference) or only partly (E1 higher).

The specification label was written after the ablation results were known, but
only from text that predates them. This will be disclosed.

## Reporting rule

Both runs and all tests above are reported whatever they show, together with all
earlier runs. No run is dropped, repeated, or replaced. Any further run needs a
further pre-registration committed before it starts.
