"""Re-file mixed guaranteed facts offline; dry-run unless --write is supplied.

Use existing verification and queue history, never page bytes or a fresh reading.
Unknown support leaves the fact unchanged. No verification record is created.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from decision import registry, retention
from decision.citation import fact_citation, ref_states
from decision.model import (
    Fact,
    SourceRef,
    fact_verification_value,
    matching_value_hashes,
    verification_counts,
)
from decision.snapshot import SnapshotInputs, _Compiler
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue, claim_verification_value

IDENTIFIERS = {"offering.api_model_id", "offering.router_slug"}


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] \
        if path.exists() else []


def verification_history(root, records, compiler):
    """Associate checks only when the entire matching log group is accounted for.

    The two logs have no shared event ID. Never pair their rows by position.
    Every log row in a group must independently verify the same value; every
    corresponding queue check then establishes its own collected references.
    """
    groups = defaultdict(list)
    for index, record in enumerate(records):
        target = record["target"]
        key = (target["kind"], target["id"], record["date"], record["outcome"],
               json.dumps(record["collector"], sort_keys=True), target["value_hash"])
        groups[key].append((index, record))
    claims, copies, checks = {}, defaultdict(dict), defaultdict(list)
    keys_by_target = defaultdict(list)
    for key in groups:
        keys_by_target[key[:5]].append(key)
    for event in json_lines(root / "verification/queue/events.jsonl"):
        if event["event"] == "collected":
            claim = Claim.from_dict(event["claim"])
            key = (claim.target.kind, claim.target.id)
            claims[key], copies[key] = claim, {}
            continue
        target = event["target"]
        key = (target["kind"], target["id"])
        claim = claims.get(key)
        if claim is None:
            continue
        if event["event"] == "changed":
            copies[key].update(event.get("copies") or {})
        elif event["event"] == "checked":
            checked = replace(claim, sources=tuple(
                ref.model_copy(update={
                    "snapshot_ref": copies[key].get(ref.source_id, ref.snapshot_ref)
                })
                for ref in claim.sources
            ))
            copies[key] = {}
            group = (*key, datetime.fromisoformat(event["at"]).date().isoformat(),
                     event["outcome"], json.dumps(claim.collector.model_dump(), sort_keys=True))
            bound = matching_value_hashes(
                claim_verification_value(checked), [key[-1] for key in keys_by_target[group]],
                unordered=compiler._unordered(claim.target.kind, claim.field),
            )
            if len(bound) == 1:
                checks[(*group, next(iter(bound)))].append(checked)
    support = defaultdict(list)
    for key, entries in groups.items():
        collected = checks[key]
        if key[3] != "verified" or len(collected) != len(entries):
            continue
        # Different value bindings in the same group cannot be paired reliably.
        for claim in collected:
            value = claim_verification_value(claim)
            if any(
                compiler._verdicts("fact", claim.target.id, record, value, claim.field)[1]
                or not matching_value_hashes(
                    value, [record["target"]["value_hash"]],
                    unordered=compiler._unordered(claim.target.kind, claim.field),
                )
                or not verification_counts(record["outcome"],
                                           record["collector"]["model_family"],
                                           record["verifier"]["model_family"])
                for _, record in entries
            ):
                break
        else:
            support[(key[0], key[1])].append((entries, collected))
    return support


def supported_side(row, history, compiler, records, urls, store):
    if row.get("effective_from") is not None or row.get("effective_until") is not None:
        return "unknown", None, "dated price admission requires the complete offering schedule"
    value = fact_verification_value(row)
    winner, unsure = compiler._verdicts(
        "fact", row["id"], row.get("verification"), value, row["facet"]
    )
    if unsure or winner is None or winner["outcome"] != "verified":
        return "unknown", winner, "current value has no unambiguous verified record"
    def bound(record):
        return bool(matching_value_hashes(
            value, [record["target"]["value_hash"]],
            unordered=compiler._unordered("fact", row["facet"]),
        ))

    candidates = [(0, row["verification"])] if row.get("verification") else []
    candidates += [(index + 1, record) for index, record in enumerate(records)
                   if record["target"]["kind"] == "fact" and record["target"]["id"] == row["id"]]
    failed = max(((record["date"], index) for index, record in candidates
                  if bound(record) and record["outcome"] != "verified"), default=("", 0))
    retained, cited_winner = False, False
    for entries, claims in history.get(("fact", row["id"]), []):
        if any(not bound(record) or (record["date"], index + 1) <= failed
               for index, record in entries):
            continue
        sides, current_support = [], []
        for claim in claims:
            if claim.subject != row["subject"]["id"] or claim.field != row["facet"]:
                sides.append("unknown")
                continue
            refs = [ref.model_dump(mode="json") for ref in claim.sources]
            states = ref_states({"sources": refs}, urls, store)
            side = ("cited" if all(s == "cited" for s in states) else
                    "retained" if all(s != "cited" for s in states) else "unknown")
            sides.append(side)
            if not all(any(
                ref["source_id"] == current["source_id"]
                and ref["snapshot_ref"] == current["snapshot_ref"]
                and set(ref["cited_regions"]) <= set(current["cited_regions"])
                and ref.get("resolved_urls", []) == current.get("resolved_urls", [])
                for current in row["sources"]
            ) for ref in refs):
                continue
            current_support.append(side)
        retained |= "retained" in current_support
        # Earlier cited support cannot prove that a later mixed reading used
        # only cited sources. Rule 2 requires attribution of the winning group.
        cited_winner |= ("cited" in current_support and all(side == "cited" for side in sides)
                         and any(record == winner for _, record in entries))
    if retained:
        return 1, winner, "existing retained-source check"
    if cited_winner:
        return 2, winner, "winning check used only cite-only sources"
    return "unknown", winner, "no retained-source proof or solely cited winning check"


def mapping(node):
    return {key.value: value for key, value in node.value}


def yaml_body(path, text):
    if path.suffix != ".md":
        return text, 0
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"missing front matter: {path}")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    return "".join(lines[1:end]), len(lines[0])


def documents(root):
    """Yield data and YAML locations without normalizing unrelated file bytes."""
    paths = sorted((root / "models").glob("*/*.md"))
    paths += sorted((root / "offerings").glob("**/*.yaml"))
    for path in paths:
        text = path.read_bytes().decode("utf-8")
        body, offset = yaml_body(path, text)
        data = yaml.load(body, Loader=yaml.CSafeLoader)
        node = yaml.compose(body, Loader=yaml.CSafeLoader)
        if not data:
            continue
        parents = [(data, node)] if path.suffix == ".md" else zip(data, node.value)
        for parent, parent_node in parents:
            if not parent.get("facts"):
                continue
            if path.suffix == ".md":
                subject, kind, model = parent["model_id"], "model", parent["model_id"]
            elif "plan" in parent:
                subject = f"{parent['provider']}/subscription/{parent['plan']}"
                kind, model = "offering", "subscription:" + subject
            else:
                model, kind = parent["model"], "offering"
                subject = "/".join(parent[key] for key in ("provider", "model", "region", "tier"))
            for row, row_node in zip(parent["facts"], mapping(parent_node)["facts"].value):
                record = {
                    "id": f"{subject}#{row['facet']}",
                    "subject": {"kind": kind, "id": subject},
                    **row,
                }
                yield path, text, offset, record, row_node, model, data, row


def drop_refs(text, offset, source_node, keep):
    """Delete only unwanted source items, keeping surviving block YAML verbatim."""
    if source_node.flow_style:
        refs = yaml.safe_load(yaml.serialize(source_node))
        return [
            (
                offset + source_node.start_mark.index,
                offset + source_node.end_mark.index,
                json.dumps([ref for ref, kept in zip(refs, keep) if kept]),
            )
        ]
    edits = []
    for node, kept in zip(source_node.value, keep):
        if kept:
            continue
        start = text.rfind("\n", 0, offset + node.start_mark.index) + 1
        if node.flow_style:
            newline = text.find("\n", offset + node.end_mark.index)
            end = len(text) if newline == -1 else newline + 1
        else:
            end = offset + node.end_mark.index - node.end_mark.column
        edits.append((start, end, ""))
    return edits


def plan(root, store, today):
    sources = load_sources(root / "registry/sources.yaml")
    urls = {sid: str(source.url) for sid, source in sources.items()}
    records = json_lines(root / "verification/log.jsonl")
    compiler = _Compiler(SnapshotInputs(sources=urls, verifications=records),
                         registry.default(), None, today, source_cache=store)
    history = verification_history(root, records, compiler)
    filed = Queue(root / "verification").filed()
    changes = []
    edits, originals, events = defaultdict(list), {}, []
    expected = {}
    for path, text, offset, row, node, model, document, raw in documents(root):
        facet = registry.facet(row["facet"])
        if facet.tier != "guaranteed" and row["facet"] not in IDENTIFIERS:
            continue
        states = ref_states(row, urls, store)
        if "cited" not in states or all(state == "cited" for state in states):
            continue
        if row["facet"] in IDENTIFIERS:
            changes.append({"id": row["id"], "facet": row["facet"], "model": model, "rule": 3})
            continue
        if row["state"] == "unknown":
            continue
        fact_citation(row, urls, store)
        rule, winner, reason = supported_side(row, history, compiler, records, urls, store)
        changes.append({"id": row["id"], "facet": row["facet"], "model": model,
                        "rule": rule, "reason": reason})
        if rule == "unknown":
            continue
        if path not in expected and any(
            isinstance(token, yaml.AliasToken) for token in yaml.scan(yaml_body(path, text)[0])
        ):
            raise ValueError(f"cannot safely edit a document with YAML aliases: {path}")
        fact = Fact.model_validate({**row, "verification": None})
        old = filed[("fact", row["id"])]
        # Preserve reader hints while filing the unchanged current value.
        claim = replace(
            old,
            subject=fact.subject.id,
            field=fact.facet,
            value=fact.value,
            sources=tuple(fact.sources),
            conditions={
                key: getattr(fact, key).isoformat() if getattr(fact, key) else None
                for key in ("effective_from", "effective_until")
            }
            if fact.effective_from or fact.effective_until
            else {},
        )
        retained = [ref for ref, state in zip(row["sources"], states) if state != "cited"]
        if rule == 1:
            refs = retained
        else:
            refs = [ref for ref, state in zip(row["sources"], states) if state == "cited"]
            fact_citation({**row, "sources": refs}, urls, store)
        reduced = {**row, "sources": refs}
        compiler._add_facts(fact.subject.id, fact.subject.kind, [reduced])
        admitted = compiler.records.get(row["id"])
        if admitted is None or (rule == 1 and admitted["verification"] != winner):
            raise ValueError(f"STOP: reduced sources did not preserve admission: {row['id']}")
        final_claim = replace(claim, sources=tuple(SourceRef.model_validate(ref) for ref in refs))
        at = datetime.combine(today, datetime.min.time(), tzinfo=UTC).isoformat()
        if rule == 2:
            events.extend(
                [
                    {"event": "collected", "at": at, "claim": final_claim.to_dict()},
                    {
                        "event": "checked",
                        "at": at,
                        "target": final_claim.target.model_dump(),
                        "outcome": "cited",
                        "diff": [],
                    },
                ]
            )
        originals[path] = text.encode("utf-8")
        edits[path].extend(
            drop_refs(
                text, offset, mapping(node)["sources"], [ref in refs for ref in row["sources"]]
            )
        )
        raw["sources"] = refs
        expected[path] = document
    writes = {}
    for path, replacements in edits.items():
        text = originals[path].decode("utf-8")
        for start, end, replacement in sorted(replacements, reverse=True):
            text = text[:start] + replacement + text[end:]
        if yaml.load(yaml_body(path, text)[0], Loader=yaml.CSafeLoader) != expected[path]:
            raise ValueError(f"source edit changed unexpected data: {path}")
        writes[path] = text.encode("utf-8")
    for path, lines in (
        (
            root / "verification/queue/events.jsonl",
            [json.dumps(event, sort_keys=True, ensure_ascii=False) for event in events],
        ),
    ):
        if not lines:
            continue
        original = path.read_bytes() if path.exists() else b""
        if original and not original.endswith(b"\n"):
            raise ValueError(f"append-only log lacks a final newline: {path}")
        originals[path] = original
        writes[path] = original + ("\n".join(lines) + "\n").encode("utf-8")
    return changes, originals, writes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--source-cache", type=Path, required=True)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--write", action="store_true", help="apply the planned source-ref changes")
    args = parser.parse_args()
    retention.POLICY_PATH = args.policy.resolve()
    retention.cite_only_hosts.cache_clear()
    retention.cite_only_hosts()
    changes, originals, writes = plan(
        args.data_root.resolve(), CopyStore(args.source_cache.resolve()), args.as_of
    )
    if args.write:
        for path, original in originals.items():
            current = path.read_bytes() if path.exists() else b""
            if current != original:
                raise ValueError(f"data changed during planning: {path}")
        for path, data in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    counts = Counter(str(change["rule"]) for change in changes)
    grouped = {}
    for field in ("facet", "model"):
        groups = defaultdict(Counter)
        for change in changes:
            groups[change[field]][str(change["rule"])] += 1
        grouped["by_" + field] = {
            key: {rule: count[rule] for rule in ("1", "2", "3", "unknown")}
            for key, count in sorted(groups.items())
        }
    print(
        json.dumps(
            {
                "counts": {rule: counts[rule] for rule in ("1", "2", "3")},
                "unresolved": counts["unknown"],
                **grouped,
                "changes": changes,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
