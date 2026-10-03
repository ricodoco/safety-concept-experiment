#!/usr/bin/env python3
"""compare_arms.py -- framing ablation, pre-registered comparison.

Reads two finished runs from the per-case score files and each round's recorded
threshold, recomputes every rate from the scores, and prints:

  1. per-round rates for each arm;
  2. the pre-registered comparison at each arm's delivered round;
  3. Arm B round 1 (one-shot fine-tuning, no mining) as the plainest baseline.

Usage (from the toolkit root):
  python3 tools/compare_arms.py runs/advice_unlicensed/armA_concept \
                                runs/advice_unlicensed_noframe/armB_noframe \
                                --holdout implied_by_stance

A run directory is the folder holding history.json and scores/. The script also
accepts a parent folder and searches it for history.json.
"""

import argparse
import glob
import json
import math
import os
import sys


def find_run(path):
    if os.path.exists(os.path.join(path, "history.json")):
        return path
    hits = sorted(glob.glob(os.path.join(path, "**", "history.json"), recursive=True),
                  key=os.path.getmtime)
    if not hits:
        sys.exit(f"no history.json under {path}")
    return os.path.dirname(hits[-1])


def read_jsonl(p):
    with open(p) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def fisher(a, n1, b, n2):
    try:
        from scipy.stats import fisher_exact
        return fisher_exact([[a, n1 - a], [b, n2 - b]])[1]
    except ImportError:
        return float("nan")


def round_stats(run, rnd, thr, holdout):
    sd = os.path.join(run, "scores")
    test = read_jsonl(os.path.join(sd, f"r{rnd}_test.jsonl"))
    out = {"round": rnd}
    tab = [r for r in test if r["label"] == 1]
    safe = [r for r in test if r["label"] == 0]
    held = [r for r in tab if r.get("frame") == holdout]
    trained = [r for r in tab if r.get("frame") != holdout]
    miss = lambda rows: sum(1 for r in rows if r["score"] < thr)
    fa = lambda rows: sum(1 for r in rows if r["score"] >= thr)
    out["miss"] = (miss(tab), len(tab))
    out["miss_trained"] = (miss(trained), len(trained))
    out["miss_withheld"] = (miss(held), len(held))
    out["fa_concept_safe"] = (fa(safe), len(safe))
    capf = os.path.join(sd, f"r{rnd}_capability.jsonl")
    if os.path.exists(capf):
        cap = read_jsonl(capf)
        out["fa_ordinary"] = (fa(cap), len(cap))
    return out


def load(run, holdout):
    run = find_run(run)
    h = json.load(open(os.path.join(run, "history.json")))
    rounds = [r for r in h["history"] if r.get("phase") == "train_test"]
    stats = [round_stats(run, r["round"], r["threshold"], holdout) for r in rounds]
    sel = h.get("selected") or {}
    delivered = sel.get("round", rounds[-1]["round"] if rounds else None)
    return run, stats, delivered, h


def fmt(k_n):
    k, n = k_n
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]" if n else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arm_a")
    ap.add_argument("arm_b")
    ap.add_argument("--holdout", default="implied_by_stance")
    ap.add_argument("--json", default="framing_ablation_results.json")
    a = ap.parse_args()

    arms = {}
    for name, path in (("A (concept framing)", a.arm_a), ("B (framing removed)", a.arm_b)):
        run, stats, delivered, h = load(path, a.holdout)
        arms[name] = {"run": run, "stats": stats, "delivered": delivered}
        print(f"\n=== Arm {name}  [{run}]  delivered round: {delivered}")
        for s in stats:
            print(f"  round {s['round']}: miss {fmt(s['miss'])} | withheld {fmt(s['miss_withheld'])}"
                  f" | FA concept-safe {fmt(s['fa_concept_safe'])}"
                  + (f" | FA ordinary {fmt(s['fa_ordinary'])}" if 'fa_ordinary' in s else ""))

    (na, A), (nb, B) = list(arms.items())
    pick = lambda arm, rnd: next(s for s in arm["stats"] if s["round"] == rnd)
    sa, sb = pick(A, A["delivered"]), pick(B, B["delivered"])
    b1 = pick(B, 1)

    print("\n=== Pre-registered comparison at each arm's delivered round (Fisher exact, two-sided)")
    results = {}
    for key, label in (("miss", "overall miss"), ("miss_withheld", "withheld-family miss"),
                       ("miss_trained", "trained-family miss"),
                       ("fa_concept_safe", "false alarm, concept safe cases"),
                       ("fa_ordinary", "false alarm, ordinary requests")):
        if key not in sa or key not in sb:
            continue
        p = fisher(sa[key][0], sa[key][1], sb[key][0], sb[key][1])
        results[key] = {"A": sa[key], "B": sb[key], "p": p}
        print(f"  {label:34s} A {fmt(sa[key])}   B {fmt(sb[key])}   p = {p:.4g}")

    print("\n=== Plainest baseline: Arm B round 1 (one-shot fine-tuning, no mining, no framing)")
    for key, label in (("miss", "overall miss"), ("miss_withheld", "withheld-family miss"),
                       ("fa_concept_safe", "false alarm, concept safe cases")):
        p = fisher(sa[key][0], sa[key][1], b1[key][0], b1[key][1])
        print(f"  {label:34s} A(delivered) {fmt(sa[key])}   B round 1 {fmt(b1[key])}   p = {p:.4g}")

    with open(a.json, "w") as fh:
        json.dump({"arms": arms, "comparison": results,
                   "baseline_b_round1": b1}, fh, indent=1, default=str)
    print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
