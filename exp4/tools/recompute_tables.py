#!/usr/bin/env python3
"""Recompute the Experiment 4 tables from persisted per-case scores.

Standard library only. No model, no GPU, no toolkit. Run from the exp4 directory:

    python3 tools/recompute_tables.py .

For each run it reports, per round: the overall miss rate on the locked test set,
the miss rate broken out by frame family, the false alarm rate on ordinary
requests, and the false alarm rate on the concept's own safe cases. These are the
figures in Tables 14 through 19 of the manuscript.

A score record is one JSON object per line with at least:
    {"id": ..., "label": 0 or 1, "frame": "...", "score": float}
A case counts as flagged when its score is at or above the round's threshold.
"""
import json, os, sys, glob, re


RECORDED = {}


def read_jsonl(path):
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def report_foundation(run_dir):
    """Print the pre-training constituent probe, which is Table 13."""
    hist = os.path.join(run_dir, 'history.json')
    if not os.path.exists(hist):
        return
    d = json.load(open(hist))
    rounds = d if isinstance(d, list) else (d.get('rounds') or d.get('history') or [])
    for r in rounds:
        if isinstance(r, dict) and isinstance(r.get('foundation'), dict):
            print('  constituent probe on the base model, before any training:')
            print('    %-32s %8s %8s %8s  %s'
                  % ('constituent', 'd\' AUC', 'AUC', 'median', 'verdict'))
            for k, v in r['foundation'].items():
                print('    %-32s %8.4f %8.4f %8.4f  %s'
                      % (k, v.get('d_prime', float('nan')), v.get('auc', float('nan')),
                         v.get('d_prime_median_split', float('nan')),
                         'weak, instilled first' if v.get('weak') else 'already present'))
            sep = r.get('separability') or {}
            if sep:
                print('    whole concept, untrained: AUC %.4f, d\' %.4f'
                      % (sep.get('auc', float('nan')), sep.get('d_prime', float('nan'))))
            return


def report_keys(run_dir):
    hist = os.path.join(run_dir, 'history.json')
    if not os.path.exists(hist):
        return
    d = json.load(open(hist))
    rounds = d if isinstance(d, list) else (d.get('rounds') or d.get('history') or [])
    for i, r in enumerate(rounds, 1):
        if isinstance(r, dict):
            print('  round %d record keys: %s' % (i, sorted(r.keys())))
            break


def find_thresholds(run_dir):
    """Locate the decision threshold for each round.

    Rounds record a threshold in history.json, in a per-round result file, or in
    a delivery specification. Try each in turn and report what was found.
    """
    th = {}
    hist = os.path.join(run_dir, 'history.json')
    if os.path.exists(hist):
        d = json.load(open(hist))
        rounds = d if isinstance(d, list) else (d.get('rounds') or d.get('history') or [])
        for i, r in enumerate(rounds, 1):
            if not isinstance(r, dict):
                continue
            # Key on the record's own round number when it carries one. A
            # leading foundation phase makes positional indexing off by one.
            idx = r.get('round') if isinstance(r.get('round'), int) else i
            for k in ('threshold', 'tau', 'decision_threshold', 'thr'):
                if isinstance(r.get(k), (int, float)):
                    th[idx] = float(r[k]); break
            for k in ('miss', 'miss_rate', 'test_miss'):
                if isinstance(r.get(k), (int, float)):
                    RECORDED[(run_dir, idx)] = float(r[k]); break
    for f in glob.glob(os.path.join(run_dir, '*.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get('threshold'), (int, float)):
            m = re.search(r'r(\d+)', os.path.basename(f))
            th.setdefault(int(m.group(1)) if m else 1, float(d['threshold']))
    return th


def rate(hits, n):
    return (float(hits) / n) if n else None


def fmt(x, nd=4):
    return 'n/a' if x is None else ('%.*f' % (nd, x))


def clopper_pearson_upper(k, n, conf=0.95):
    """One-sided upper bound. Bisection on the binomial tail; no SciPy."""
    if n == 0:
        return None
    from math import comb
    alpha = 1.0 - conf

    def tail(p):
        return sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(0, k + 1))

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if tail(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def score_round(scores, threshold):
    pos = [r for r in scores if r.get('label') == 1]
    neg = [r for r in scores if r.get('label') == 0]
    misses = [r for r in pos if r['score'] < threshold]
    fas = [r for r in neg if r['score'] >= threshold]
    by_frame = {}
    for r in pos:
        f = r.get('frame', 'unknown')
        d = by_frame.setdefault(f, [0, 0])
        d[1] += 1
        if r['score'] < threshold:
            d[0] += 1
    return {
        'n_pos': len(pos), 'n_neg': len(neg),
        'miss': rate(len(misses), len(pos)),
        'fa': rate(len(fas), len(neg)),
        'by_frame': {f: (m, n, rate(m, n)) for f, (m, n) in sorted(by_frame.items())},
    }


def do_run(run_dir, name):
    sdir = os.path.join(run_dir, 'scores')
    if not os.path.isdir(sdir):
        return
    th = find_thresholds(run_dir)
    report_foundation(run_dir)
    rounds = sorted({int(m.group(1)) for f in os.listdir(sdir)
                     for m in [re.match(r'r(\d+)_', f)] if m})
    print('\n' + '=' * 74)
    print(name)
    print('=' * 74)
    if not th:
        print('  NO THRESHOLD FOUND. Cannot recompute rates for this run.')
        print('  Looked in history.json and any *.json holding a "threshold" key.')
        return
    print('  thresholds found: %s' % (', '.join('r%d=%.6f' % (k, v) for k, v in sorted(th.items())) or 'none'))
    covered_hits = covered_n = 0
    for r in rounds:
        t = th.get(r)
        if t is None:
            print('\n round %d: NO THRESHOLD RECORDED, skipped' % r)
            continue
        test = os.path.join(sdir, 'r%d_test.jsonl' % r)
        if not os.path.exists(test):
            continue
        res = score_round(read_jsonl(test), t)
        print('\n round %d   threshold %.6f' % (r, t))
        rec = RECORDED.get((run_dir, r))
        flag = ''
        if rec is not None and res['miss'] is not None:
            flag = '   MATCHES history' if abs(rec - res['miss']) < 5e-4 else \
                   '   DISAGREES with history (%.4f)' % rec
        print('   locked test: miss %s   (%d positive cases)%s'
              % (fmt(res['miss']), res['n_pos'], flag))
        print('   safe cases in the concept frames: false alarm %s  (n=%d)'
              % (fmt(res['fa']), res['n_neg']))
        for f, (m, n, rt) in res['by_frame'].items():
            print('     frame %-22s miss %s   (%d/%d)' % (f, fmt(rt), m, n))
        cap = os.path.join(sdir, 'r%d_capability.jsonl' % r)
        if os.path.exists(cap):
            rows = read_jsonl(cap)
            flagged = sum(1 for x in rows if x['score'] >= t)
            print('   ordinary requests flagged: %s  (%d/%d)'
                  % (fmt(rate(flagged, len(rows))), flagged, len(rows)))
        sel = os.path.join(sdir, 'r%d_select.jsonl' % r)
        if os.path.exists(sel):
            rows = [x for x in read_jsonl(sel) if x.get('label') == 1]
            m = sum(1 for x in rows if x['score'] < t)
            print('   selection frame: miss %s  (%d/%d)' % (fmt(rate(m, len(rows))), m, len(rows)))
        for f, (m, n, _) in res['by_frame'].items():
            if m == 0:
                covered_hits += 0; covered_n += n
    if covered_n:
        ub = clopper_pearson_upper(0, covered_n, 0.95)
        ub999 = clopper_pearson_upper(0, covered_n, 0.999)
        conf = 1.0 - (1.0 - 0.02) ** covered_n
        print('\n covered forms across all rounds: 0 misses in %d cases' % covered_n)
        print('   95%% upper bound %s   99.9%% upper bound %s   Cf(miss<0.02) %.5f'
              % (fmt(ub), fmt(ub999), conf))


def main(root):
    runs = sorted(glob.glob(os.path.join(root, 'runs', '*')))
    if not runs:
        print('No runs/ directory under %s' % root); return 1
    for r in runs:
        loop = os.path.join(r, 'loop')
        if os.path.isdir(os.path.join(loop, 'scores')):
            do_run(loop, os.path.basename(r))
        elif os.path.exists(os.path.join(r, 'result.json')):
            d = json.load(open(os.path.join(r, 'result.json')))
            print('\n' + '=' * 74); print(os.path.basename(r)); print('=' * 74)
            for k in ('miss_rate', 'false_alarm', 'capability_false_alarm',
                      'capability_false_alarm_upper_95', 'n_capability', 'corpus_size'):
                if k in d:
                    print('   %-34s %s' % (k, d[k]))
            if isinstance(d.get('compared_with'), dict):
                print('   compared with:')
                for k, v in d['compared_with'].items():
                    print('     %-32s %s' % (k, v))
    print('\nDone. Compare these against Tables 14 to 19 of the manuscript.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
