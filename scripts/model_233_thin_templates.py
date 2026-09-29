#!/usr/bin/env python3
"""Count thin templates on the repository snapshot (MODEL-233).

A template is thin when it ranks models but has no leader: every ranked model
sits in ``bands.thin``, the "Not enough evidence yet" band. A template that
ranks nobody has no leader either, and is counted apart. The script builds the
``repo`` snapshot as the corpus does (as of the date given, default today),
answers every template through the Worker's decide service at
``explain: summary``, and prints one JSON line per template and the totals.
Run it before and after an evidence change to report the delta.
"""

from __future__ import annotations

import json
import sys
from datetime import date

from decision.excluded import excluded_sources
from decision.registry import default
from decision.snapshot import build_snapshot, collect_repo, load_premier
from decision.templates import load_templates
from tests.corpus.corpus import KEY, REPO, load, worker_service


def main() -> None:
    as_of = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    built = build_snapshot(
        collect_repo(REPO), registry=default(),
        premier=load_premier(REPO / "premier" / "slice-1.yaml"),
        as_of=as_of, guard=excluded_sources(), gate=False,
    )
    snapshot = load(built.to_bytes(key=KEY))
    service = worker_service()
    thin = no_leader = 0
    rows = []
    for template in load_templates():
        spec = dict(template["spec"]) | {"explain": "summary"}
        status, body = service.decide(spec, snapshot, expected_snapshot=None)
        answer = json.loads(service.serialise(body))
        bands = (answer.get("decision") or answer).get("bands") or {}
        ranked = sum(len(bands.get(k) or ()) for k in ("best", "rest", "thin"))
        leaderless = status == 200 and bands.get("leader") is None
        is_thin = leaderless and ranked > 0
        thin += is_thin
        no_leader += leaderless
        rows.append({
            "template": template["id"], "status": status, "leader": bands.get("leader"),
            "best": len(bands.get("best") or ()), "rest": len(bands.get("rest") or ()),
            "thin": len(bands.get("thin") or ()), "ranked": ranked, "is_thin": is_thin,
        })
    for row in rows:
        print(json.dumps(row))
    print(json.dumps({"templates": len(rows), "thin_templates": thin,
                      "no_leader": no_leader}), file=sys.stderr)


if __name__ == "__main__":
    main()
