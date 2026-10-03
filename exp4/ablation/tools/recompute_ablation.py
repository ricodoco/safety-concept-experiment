#!/usr/bin/env python3
"""recompute_ablation.py -- recompute Tables 20 and 21 of the paper from the deposited per-case scores.

Reads arms.json and, for every run, the history (decision thresholds, delivered round) and the per-case
test and ordinary-request scores. Needs numpy and scipy; loads no model.

  cd exp4/ablation
  python3 tools/recompute_ablation.py
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_arms import load, fisher, wilson


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); out = [0.0] * m; run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i])); out[i] = run
    return out


def kn(pair):
    k, n = pair
    if not n: return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} [{lo:.3f}, {hi:.3f}]"


def safe_p(x, nx, y, ny):
    try:
        return fisher(x, nx, y, ny)
    except Exception:
        return float("nan")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(here, ".."), help="folder holding arms.json")
    a = ap.parse_args()
    runs = json.load(open(os.path.join(a.root, "arms.json")))["runs"]
    R = {}
    for k, m in runs.items():
        _, stats, delivered, _ = load(os.path.join(a.root, m["dir"]), m["holdout"])
        R[k] = {"m": m, "stats": stats, "delivered": delivered,
                "s": next(x for x in stats if x["round"] == delivered)}

    print("TABLE 20: delivered round of each run")
    print(f"{'run':5s} {'concept':10s} {'label':14s} {'curric.':8s} {'rnd':>3s}  withheld-family miss (95% CI)       safe-case false alarm")
    for k, r in R.items():
        m, s = r["m"], r["s"]
        print(f"{k:5s} {m['concept']:10s} {m['label_kind']:14s} {m['curriculum']:8s} {r['delivered']:>3d}  {kn(s['miss_withheld']):38s}{kn(s['fa_concept_safe'])}")
    print("\nwithheld-family misses by round:")
    for k, r in R.items():
        print(f"  {k:5s}", ", ".join(f"r{x['round']}: {x['miss_withheld'][0]}/{x['miss_withheld'][1]}" for x in r["stats"]))
    print("\ntrained-family misses (overall minus withheld), every round of every run:",
          sorted({x["miss"][0] - x["miss_withheld"][0] for r in R.values() for x in r["stats"]}))
    print("ordinary requests flagged at delivered rounds:", sorted({r["s"].get("fa_ordinary", (None,))[0] for r in R.values()}))

    def pair(x, y):
        (kx, nx), (ky, ny) = R[x]["s"]["miss_withheld"], R[y]["s"]["miss_withheld"]
        return kx, nx, ky, ny, safe_p(kx, nx, ky, ny)

    print("\nTABLE 21: pre-registered comparisons (withheld-family miss, two-sided Fisher exact)")
    for label, x, y in [("Stage 1: A vs B", "A", "B"), ("Stage 2 Q1: A2 vs B2", "A2", "B2"),
                        ("Stage 2 Q3: Rule 1 A vs B", "R1A", "R1B"), ("Stage 4 primary: E1 vs C", "E1", "C")]:
        kx, nx, ky, ny, p = pair(x, y)
        print(f"  {label:28s} {kx}/{nx} vs {ky}/{ny}   p = {p:.4g}")
    for title, fam in [("Stage 2 Q2 (Holm over 4)", [("C", "B"), ("D", "B"), ("A", "D"), ("A", "C")]),
                       ("Stage 4 secondary (Holm over 3)", [("E1", "B"), ("E2", "A"), ("E2", "E1")])]:
        res = [pair(x, y) for x, y in fam]; adj = holm([r[4] for r in res])
        print(f"  {title}")
        for (x, y), r, h in zip(fam, res, adj):
            print(f"    {x} vs {y:3s} {r[0]}/{r[1]} vs {r[2]}/{r[3]}   p = {r[4]:.4g}   Holm-adjusted p = {h:.4g}")


if __name__ == "__main__":
    main()
