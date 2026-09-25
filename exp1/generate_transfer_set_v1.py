"""
generate_transfer_set_v1.py
============================
Fixes the transfer-domain sampling bug in generate_cases_v2.py.

The original generate_set() sampled exactly one case per concept per transfer
domain (3 cases/domain) regardless of the n_per_concept argument -- the
transfer-domain loop was never parameterized by it. This produced 3 cases in
hospital, warehouse, and construction site, too few to estimate a domain rate
with any precision (Wilson 95% CI on 2/3 spans 20.8 to 93.9).

This script uses the exact same per-concept case generators as
generate_cases_v2.py (make_C1_case, make_C2_case, make_C3_case -- imported
unchanged, same templates and vocabulary pools) and generates
N_PER_CONCEPT_PER_DOMAIN complex, single-concept cases per concept in each of
four domains: fleet, hospital, warehouse, construction site. Fleet is included
as a matched in-domain baseline so all four domains have the same n and the
same case composition (complex, single-concept only), making the domain
comparison fair for the first time.

This is a new, separate, self-contained transfer study. It does not touch or
replace test_cases_v2.json / results_v3.json, and the original 36-case primary
result (34/36 vs 17/36) is untouched and still the paper's primary finding.

Same seed (42), so re-running this script reproduces the identical case set.
"""

import json
import random
import exec_lib as lib   # make_C1_case, make_C2_case, make_C3_case (unchanged)

SEED = 42
N_PER_CONCEPT_PER_DOMAIN = 4   # 4 concepts-worth x 3 concepts = 12 cases/domain
DOMAINS = ["fleet", "hospital", "warehouse", "construction site"]
MAKERS = {"C1": lib.make_C1_case, "C2": lib.make_C2_case, "C3": lib.make_C3_case}


def generate_transfer_set(tag):
    random.seed(SEED)
    cases = []
    for domain in DOMAINS:
        for _ in range(N_PER_CONCEPT_PER_DOMAIN):
            for concept in ["C1", "C2", "C3"]:
                cases.append(MAKERS[concept](complexity="complex", domain=domain))
    random.shuffle(cases)
    for i, c in enumerate(cases):
        c["id"] = f"{tag}{i+1:03d}"
    return cases


if __name__ == "__main__":
    print(f"Random seed: {SEED}")
    test = generate_transfer_set(tag="XD")   # "cross-domain"

    with open("test_cases_transfer_v1.json", "w") as f:
        json.dump(test, f, indent=2)

    log = {
        "seed": SEED,
        "script": "generate_transfer_set_v1.py",
        "purpose": "Adequately powered domain-transfer follow-up to Experiment 1. "
                   "Does not replace or alter test_cases_v2.json / results_v3.json.",
        "n_per_concept_per_domain": N_PER_CONCEPT_PER_DOMAIN,
        "domains": DOMAINS,
        "n_total": len(test),
        "n_per_domain": {d: sum(1 for c in test if c["domain"] == d) for d in DOMAINS},
        "concept_counts": {c: sum(1 for x in test if c in x["concepts"]) for c in ["C1", "C2", "C3"]},
        "complexity": sorted(set(c["complexity"] for c in test)),
    }
    with open("generation_log_transfer_v1.json", "w") as f:
        json.dump(log, f, indent=2)

    print(f"Total cases: {len(test)}")
    for d in DOMAINS:
        print(f"  {d}: {sum(1 for c in test if c['domain']==d)}")
    print("\nSample case:")
    print(test[0]["user"])
