"""Count assurance transitions within the original mixed-fact repair scope."""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--repaired-root", type=Path, required=True)
    parser.add_argument("--assurance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.code.resolve()))
    os.environ.pop("MODELSPEC_SOURCE_CACHE", None)
    from decision import registry, snapshot
    from decision.citation import ref_states

    registry.use_root(args.baseline_root)
    baseline = snapshot.collect_repo(args.baseline_root)
    repaired = snapshot.collect_repo(args.repaired_root)

    def facts(inputs):
        return {
            f["id"]: f
            for group in (inputs.models, inputs.offerings, inputs.subscriptions)
            for owner in group
            for f in owner.get("facts", [])
        }

    before, after = facts(baseline), facts(repaired)
    mixed = set()
    rule2 = set()
    for rid, fact in before.items():
        if registry.facet(fact["facet"]).tier != "guaranteed":
            continue
        states = ref_states(fact, baseline.sources)
        if not ("cited" in states and any(s != "cited" for s in states)):
            continue
        mixed.add(rid)
        current = after.get(rid)
        if current:
            states = ref_states(current, repaired.sources)
            if states and all(s == "cited" for s in states):
                rule2.add(rid)
    results = json.loads(args.assurance.read_text())
    report = {}
    listing = {}
    for period, state in results.items():
        changes = [
            c for c in state["changes"] if c["before"] == "verified" and c["after"] == "cited"
        ]
        listing[period] = changes
        ids = {c["record_id"] for c in changes}
        report[period] = {
            "diagnostic_only": True,
            "deploy_export_accepted": False,
            "original_mixed_guaranteed_facts": len(mixed),
            "raw_rule2_facts": len(rule2),
            "verified_to_cited_total": len(ids),
            "among_original_mixed_facts": len(ids & mixed),
            "among_raw_rule2_facts": len(ids & rule2),
            "outside_original_mixed_facts": len(ids - mixed),
        }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "verified-to-cited.private.json").write_text(
        json.dumps(listing, indent=2) + "\n"
    )
    (args.output / "verified-to-cited-scope.public.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    consistency = {
        "diagnostic_only": True,
        "deploy_export_accepted": False,
        "same_verified_to_cited_listing_both_periods": listing["current"] == listing["successor"],
        "record_count_each_period": {period: len(rows) for period, rows in listing.items()},
    }
    (args.output / "period-consistency.public.json").write_text(
        json.dumps(consistency, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
