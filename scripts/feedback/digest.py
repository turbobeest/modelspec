"""The weekly feedback digest, and Linear-ready issue drafts (MODEL-221).

Reads feedback records (JSON Lines, one stored record per line, as
`export.py` writes them from the FEEDBACK namespace) and writes two files:

    digest.md     counts by rating, by page and by template for the window
    drafts.json   one draft per cluster of unreliable, untrustworthy or
                  confusing feedback, with its decision IDs attached

A **cluster** is negative feedback that shares a rating and a surface: the
template when one was named, else the page, else the client. A cluster needs
`--min-cluster` records (default 2) to become a draft; a single report is
listed in the digest, not drafted.

**Deduplication.** Within a draft, each decision ID and each note appears once.
Across weeks, `--ledger` (a JSON file the operator keeps with the output)
records every cluster already drafted; a cluster seen again becomes an
`update` of that draft — new decision IDs and counts to add as a comment —
never a second issue. The orchestrator files `new` drafts and comments
`update`s; `drafts.json` says which is which.

**Privacy.** Feedback text never enters this repository or public CI: the
output directory and the ledger are refused if they are inside the repository,
and this runs where the export was made, never in a GitHub workflow. Notes are
scrubbed again with the Worker's own `scrub` before they are quoted.

    python scripts/feedback/digest.py --records ~/feedback/2026-10-05.jsonl \\
        --out ~/feedback/digest-2026-10-05 --ledger ~/feedback/ledger.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))
import feedback_service as fb  # noqa: E402

MIN_CLUSTER = 2
SAMPLE_NOTES = 5
NOTE_QUOTE_MAX = 280


class DigestError(ValueError):
    pass


def refuse_repo_path(path: Path, what: str) -> Path:
    """Feedback text is private: never write it where `git add` could publish it."""
    resolved = Path(path).expanduser().resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise DigestError(
            f"{what} is inside the public ModelSpec repository ({resolved}). Feedback "
            "text is private and never lives here; write it beside the export.")
    return resolved


def load(path: Path) -> list[dict[str, Any]]:
    """Every record, checked against the stored shape. A bad line is an error, not a skip."""
    records = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if tuple(record) != fb.STORED_FIELDS:
            raise DigestError(f"line {number}: fields {sorted(record)} are not a stored record")
        if record["rating"] not in fb.RATINGS:
            raise DigestError(f"line {number}: rating {record['rating']!r}")
        records.append(record)
    return records


def surface(record: dict[str, Any]) -> str:
    if record["template"]:
        return f"template:{record['template']}"
    if record["page"]:
        return f"page:{record['page']}"
    return f"client:{record['client']}"


def cluster_key(rating: str, where: str) -> str:
    return f"{rating}|{where}"


@dataclass
class Cluster:
    rating: str
    surface: str
    records: list[dict[str, Any]] = field(default_factory=list)

    @property
    def key(self) -> str:
        return cluster_key(self.rating, self.surface)

    @property
    def decision_ids(self) -> list[str]:
        return sorted({r["decision_id"] for r in self.records if r["decision_id"]})

    def notes(self) -> list[str]:
        seen: dict[str, str] = {}
        for record in self.records:
            for text in (record["note"], record["trying_to_decide"]):
                if not text:
                    continue
                cleaned, _ = fb.scrub(text)
                normal = " ".join(cleaned.lower().split())
                if normal and normal not in seen:
                    seen[normal] = cleaned[:NOTE_QUOTE_MAX]
        return list(seen.values())


def clusters(records: list[dict[str, Any]]) -> list[Cluster]:
    grouped: dict[str, Cluster] = {}
    for record in records:
        if record["rating"] not in fb.NEGATIVE_RATINGS:
            continue
        where = surface(record)
        grouped.setdefault(cluster_key(record["rating"], where),
                           Cluster(record["rating"], where)).records.append(record)
    return sorted(grouped.values(), key=lambda c: (-len(c.records), c.key))


def _title(cluster: Cluster) -> str:
    kind, _, name = cluster.surface.partition(":")
    where = {"template": f"the {name} template", "page": f"{name}",
             "client": f"{name} callers"}[kind]
    return f"Feedback: {len(cluster.records)} × {cluster.rating} on {where}"


def _description(cluster: Cluster, since: date, until: date) -> str:
    lines = [
        f"{len(cluster.records)} people or agents rated **{cluster.rating}** on "
        f"`{cluster.surface}` between {since} and {until} (MODEL-221 weekly digest).",
        "",
        "**Decision IDs** (reproduce each with the spec and snapshot it names):",
    ]
    lines += [f"- `{d}`" for d in cluster.decision_ids] or ["- none given"]
    notes = cluster.notes()
    if notes:
        lines += ["", "**What they said** (scrubbed; paraphrase before quoting publicly):"]
        lines += [f"> {n}" for n in notes[:SAMPLE_NOTES]]
    clients = Counter(r["client"] for r in cluster.records)
    lines += ["", "Sent by: " + ", ".join(f"{c} ×{n}" for c, n in sorted(clients.items())),
              "", f"Cluster key: `{cluster.key}`. When fixed, add an entry to "
              "`docs/feedback/changes.yaml` so /feedback/ says what changed."]
    return "\n".join(lines)


def drafts(found: list[Cluster], ledger: dict[str, Any], since: date, until: date,
           min_cluster: int = MIN_CLUSTER) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Drafts to file (`new`) or to comment on (`update`), and the ledger after them."""
    out, updated = [], {key: dict(value) for key, value in ledger.items()}
    for cluster in found:
        if len(cluster.records) < min_cluster:
            continue
        known = updated.get(cluster.key)
        ids = cluster.decision_ids
        base = {
            "cluster_key": cluster.key,
            "rating": cluster.rating,
            "surface": cluster.surface,
            "count": len(cluster.records),
            "decision_ids": ids,
            "window": {"since": since.isoformat(), "until": until.isoformat()},
        }
        if known is None:
            out.append({**base, "action": "new", "title": _title(cluster),
                        "description": _description(cluster, since, until),
                        "labels": ["feedback", f"feedback:{cluster.rating}"],
                        "team": "ModelSpec"})
            updated[cluster.key] = {"first_drafted": until.isoformat(), "issue": None,
                                    "decision_ids": ids, "total": len(cluster.records)}
            continue
        new_ids = sorted(set(ids) - set(known.get("decision_ids", [])))
        out.append({**base, "action": "update", "issue": known.get("issue"),
                    "new_decision_ids": new_ids,
                    "comment": (f"{len(cluster.records)} more {cluster.rating} reports on "
                                f"`{cluster.surface}` between {since} and {until}. "
                                + ("New decision IDs: " + ", ".join(f"`{d}`" for d in new_ids)
                                   if new_ids else "No new decision IDs."))})
        known["decision_ids"] = sorted(set(known.get("decision_ids", [])) | set(ids))
        known["total"] = int(known.get("total", 0)) + len(cluster.records)
    return out, updated


def _table(counter: Counter, heading: str) -> list[str]:
    rows = [f"| {heading} | count |", "|---|---|"]
    rows += [f"| {name or '—'} | {n} |" for name, n in sorted(counter.items(),
                                                              key=lambda kv: (-kv[1], str(kv[0])))]
    return rows


def digest_markdown(records: list[dict[str, Any]], found: list[Cluster],
                    made: list[dict[str, Any]], since: date, until: date) -> str:
    by_rating = Counter(r["rating"] for r in records)
    lines = [f"# Feedback digest, {since} to {until}", "",
             f"{len(records)} pieces of feedback. "
             f"{sum(1 for r in records if r['rating'] in fb.NEGATIVE_RATINGS)} negative.", ""]
    lines += ["## By rating", ""] + _table(Counter({r: by_rating[r] for r in fb.RATINGS}),
                                            "rating") + [""]
    lines += ["## By page", ""] + _table(Counter(r["page"] for r in records), "page") + [""]
    lines += ["## By template", ""] + _table(Counter(r["template"] for r in records),
                                              "template") + [""]
    lines += ["## By rating and page", ""]
    pairs = Counter(f"{r['rating']} · {r['page'] or '—'}" for r in records)
    lines += _table(pairs, "rating · page") + [""]
    lines += ["## Negative clusters", ""]
    if not found:
        lines.append("None.")
    for cluster in found:
        state = next((d["action"] for d in made if d["cluster_key"] == cluster.key),
                     "below threshold")
        lines.append(f"- `{cluster.key}`: {len(cluster.records)} ({state}); "
                     f"decision IDs: {', '.join(cluster.decision_ids) or 'none'}")
    return "\n".join(lines) + "\n"


def run(records_path: Path, out: Path, ledger_path: Path | None, *, until: date,
        days: int = 7, min_cluster: int = MIN_CLUSTER) -> dict[str, Any]:
    out = refuse_repo_path(out, "--out")
    if ledger_path is not None:
        ledger_path = refuse_repo_path(ledger_path, "--ledger")
    since = until - timedelta(days=days - 1)
    records = [r for r in load(records_path)
               if since.isoformat() <= r["received_on"] <= until.isoformat()]
    ledger = (json.loads(ledger_path.read_text(encoding="utf-8"))
              if ledger_path is not None and ledger_path.exists() else {})
    found = clusters(records)
    made, updated = drafts(found, ledger, since, until, min_cluster)
    out.mkdir(parents=True, exist_ok=True)
    (out / "digest.md").write_text(digest_markdown(records, found, made, since, until),
                                   encoding="utf-8")
    (out / "drafts.json").write_text(json.dumps(made, indent=2) + "\n", encoding="utf-8")
    if ledger_path is not None:
        ledger_path.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    return {"records": len(records), "clusters": len(found),
            "new": sum(d["action"] == "new" for d in made),
            "update": sum(d["action"] == "update" for d in made),
            "digest_sha256": hashlib.sha256((out / "digest.md").read_bytes()).hexdigest()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--until", type=date.fromisoformat, default=date.today())
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--min-cluster", type=int, default=MIN_CLUSTER)
    args = parser.parse_args(argv)
    try:
        summary = run(args.records, args.out, args.ledger, until=args.until, days=args.days,
                      min_cluster=args.min_cluster)
    except DigestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
