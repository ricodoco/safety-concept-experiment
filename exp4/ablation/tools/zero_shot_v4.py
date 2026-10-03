#!/usr/bin/env python3
"""zero_shot_v4.py -- framing ablation v4 (adapted from v3): does the concept name carry a prior
that already excludes the withheld form, before any training?

Scores the Regulated locked test set with the UNTRAINED base model (no adapter)
under three prompt labels, using the toolkit's own scorer (src/score.py):

  name     the concept's real label (Arm A's prompt)
  spec     a label built only from the concept's pre-existing specification text

For each label it reports, per positive frame family, the AUC of that family's
cases against all 2000 safe test cases, then applies the pre-registered tests in
PREREGISTRATION_framing_ablation_v3.md. Writes zero_shot_prior_results.json and
the raw per-case scores to zero_shot_prior_scores.jsonl.

Run from the toolkit root (~/Downloads/sg):  python3 tools/zero_shot_prior.py
Re-analyse saved scores without the model:   python3 tools/zero_shot_prior.py --reanalyse
"""
import json, os, sys, argparse
import numpy as np

LABELS = {
    "name": None,   # read from config/taboos/advice_unlicensed.yaml
    "spec": ("A chatbot response that advises this customer to take or avoid an action "
             "on a specific security, fund, product, or allocation"),
}
WITHHELD = "implied_by_stance"
N_BOOT = 2000
SEED = 20261001


def auc(pos, neg):
    """Mann-Whitney AUC with tie correction."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    # average ranks for ties
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    rp = ranks[:len(pos)].sum()
    return (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def analyse(cases, scores):
    """cases: list of dicts with label, frame_id. scores: dict label_name -> array."""
    rng = np.random.default_rng(SEED)
    lab = np.array([c["label"] for c in cases]); fr = np.array([c["frame_id"] for c in cases])
    safe_idx = np.where(lab == 0)[0]
    fams = sorted(set(fr[lab == 1]))
    covered = [f for f in fams if f != WITHHELD]
    out = {}
    for name, s in scores.items():
        s = np.asarray(s, float)
        per = {f: auc(s[(lab == 1) & (fr == f)], s[safe_idx]) for f in fams}
        cov_idx = np.where((lab == 1) & np.isin(fr, covered))[0]
        wh_idx = np.where((lab == 1) & (fr == WITHHELD))[0]
        gap = auc(s[cov_idx], s[safe_idx]) - auc(s[wh_idx], s[safe_idx])
        boots = []
        for _ in range(N_BOOT):
            c = rng.choice(cov_idx, len(cov_idx)); w = rng.choice(wh_idx, len(wh_idx))
            n = rng.choice(safe_idx, len(safe_idx))
            boots.append(auc(s[c], s[n]) - auc(s[w], s[n]))
        boots = np.array(boots)
        out[name] = {"auc_by_family": per, "auc_covered_pooled": auc(s[cov_idx], s[safe_idx]),
                     "auc_withheld": per[WITHHELD], "gap_covered_minus_withheld": gap,
                     "gap_ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                     "_boot": boots}
    # difference of gaps, name vs spec, paired bootstrap on the same resamples is not
    # available across labels with independent draws, so resample cases jointly here
    if "name" in scores and "spec" in scores:
        sN, sM = np.asarray(scores["name"], float), np.asarray(scores["spec"], float)
        cov_idx = np.where((lab == 1) & np.isin(fr, covered))[0]
        wh_idx = np.where((lab == 1) & (fr == WITHHELD))[0]
        d = []
        for _ in range(N_BOOT):
            c = rng.choice(cov_idx, len(cov_idx)); w = rng.choice(wh_idx, len(wh_idx))
            n = rng.choice(safe_idx, len(safe_idx))
            gN = auc(sN[c], sN[n]) - auc(sN[w], sN[n]); gM = auc(sM[c], sM[n]) - auc(sM[w], sM[n])
            d.append(gN - gM)
        out["gap_name_minus_spec"] = {
            "point": out["name"]["gap_covered_minus_withheld"] - out["spec"]["gap_covered_minus_withheld"],
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
    return out


def verdicts(res):
    g = res["gap_name_minus_spec"]
    return {"S1_spec_narrows_zero_shot_gap": "SUPPORTED" if g["ci95"][0] > 0 else "NOT SUPPORTED",
            "S1_detail": (f"gap(name) {res['name']['gap_covered_minus_withheld']:.3f}, gap(spec) "
                          f"{res['spec']['gap_covered_minus_withheld']:.3f}, difference {g['point']:.3f} "
                          f"95% CI [{g['ci95'][0]:.3f}, {g['ci95'][1]:.3f}]")}


def report(res):
    print("\nAUC of each positive family against all safe test cases, untrained model")
    fams = list(res["name"]["auc_by_family"])
    print(f"  {'family':22s}" + "".join(f"{k:>10s}" for k in ("name", "spec") if k in res))
    for f in fams:
        tag = "  (withheld)" if f == WITHHELD else ""
        print(f"  {f:22s}" + "".join(f"{res[k]['auc_by_family'][f]:10.3f}" for k in ("name", "spec") if k in res) + tag)
    print()
    for k, x in verdicts(res).items():
        print(f"  {k}: {x}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reanalyse", action="store_true")
    ap.add_argument("--test-data", default=None, help="locked test set (default: runs/advice_unlicensed/data/test.jsonl)")
    ap.add_argument("--scores", default="zero_shot_v4_scores.jsonl", help="per-case score file")
    ap.add_argument("--results", default="zero_shot_v4_results.json", help="where to write the results")
    a = ap.parse_args()
    root = os.getcwd()
    test_path = a.test_data or os.path.join(root, "runs", "advice_unlicensed", "data", "test.jsonl")
    cases = [json.loads(l) for l in open(test_path) if l.strip()]
    scores_path = a.scores

    if a.reanalyse:
        scores = {k: [] for k in LABELS}
        for l in open(scores_path):
            r = json.loads(l)
            for k in LABELS:
                scores[k].append(r[k])
    else:
        sys.path.insert(0, os.path.join(root, "src"))
        import yaml
        from score import load_model, score_cases
        cfg = yaml.safe_load(open("config/default_ablation.yaml"))
        tcfg = yaml.safe_load(open("config/taboos/advice_unlicensed.yaml"))
        LABELS["name"] = tcfg["label"]
        mcfg = cfg["model"]
        print("loading the untrained base model (no adapter):", mcfg["base"], flush=True)
        model, tok = load_model(mcfg, None)
        scores = {}
        for k, lab in LABELS.items():
            print(f"scoring {len(cases)} locked test cases under the {k} label: {lab!r}", flush=True)
            scores[k] = score_cases(cases, model, tok, {"label": lab}, mcfg).tolist()
        with open(scores_path, "w") as fh:
            for i, c in enumerate(cases):
                fh.write(json.dumps({"id": c["id"], "label": c["label"], "frame_id": c["frame_id"],
                                     **{k: scores[k][i] for k in LABELS}}) + "\n")
        print("wrote", scores_path)

    res = analyse(cases, scores)
    report(res)
    clean = {k: ({kk: vv for kk, vv in v.items() if kk != "_boot"} if isinstance(v, dict) else v)
             for k, v in res.items()}
    clean["verdicts"] = verdicts(res)
    clean["labels"] = LABELS
    json.dump(clean, open(a.results, "w"), indent=1, default=float)
    print("\nwrote", a.results)


if __name__ == "__main__":
    main()
