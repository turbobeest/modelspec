"""Re-file mixed guaranteed facts offline; dry-run unless --write is supplied.

The policy and retained-copy directory are explicit inputs. No pages are fetched.
Only source references change; the engine derives citation assurance from them.
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
from decision.model import Fact, SourceRef
from decision.sources import CopyStore, load_sources
from decision.verify import Queue, StoredRegions, deterministic_extractors, verify


IDENTIFIERS = {"offering.api_model_id", "offering.router_slug"}


def mapping(node):
    return {key.value: value for key, value in node.value}


def documents(root):
    """Yield data and YAML locations without normalizing unrelated file bytes."""
    paths = sorted((root / "models").glob("*/*.md"))
    paths += sorted((root / "offerings").glob("**/*.yaml"))
    for path in paths:
        text = path.read_bytes().decode("utf-8")
        offset = 0
        body = text
        if path.suffix == ".md":
            lines = text.splitlines(keepends=True)
            if not lines or lines[0].strip() != "---":
                raise ValueError(f"missing front matter: {path}")
            end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
            offset = len(lines[0])
            body = "".join(lines[1:end])
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
                record = {"id": f"{subject}#{row['facet']}",
                          "subject": {"kind": kind, "id": subject}, **row}
                yield path, text, offset, record, row_node, model


def drop_refs(text, offset, source_node, keep):
    """Delete only unwanted source items, keeping surviving block YAML verbatim."""
    if source_node.flow_style:
        refs = yaml.safe_load(yaml.serialize(source_node))
        return [(offset + source_node.start_mark.index, offset + source_node.end_mark.index,
                 json.dumps([ref for ref, kept in zip(refs, keep) if kept]))]
    edits = []
    for node, kept in zip(source_node.value, keep):
        if kept:
            continue
        start = text.rfind("\n", 0, offset + node.start_mark.index) + 1
        end = offset + node.end_mark.index - node.end_mark.column
        edits.append((start, end, ""))
    return edits


def plan(root, store, today):
    sources = load_sources(root / "registry/sources.yaml")
    urls = {sid: str(source.url) for sid, source in sources.items()}
    regions = StoredRegions(store, sources, cache_documents=True)
    filed = Queue(root / "verification").filed()
    changes = []
    edits, originals, events, verifications = defaultdict(list), {}, [], []
    for path, text, offset, row, node, model in documents(root):
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
        fact = Fact.model_validate({**row, "verification": None})
        old = filed[("fact", row["id"])]
        # Filed values can be older than the card. Keep reader hints, but always
        # ask the verifier about the current fact and its current references.
        claim = replace(old, subject=fact.subject.id, field=fact.facet, value=fact.value,
                        sources=tuple(fact.sources),
                        conditions={key: getattr(fact, key).isoformat() if getattr(fact, key) else None
                                    for key in ("effective_from", "effective_until")}
                        if fact.effective_from or fact.effective_until else {})
        retained = [ref for ref, state in zip(row["sources"], states) if state != "cited"]
        checked = replace(claim, sources=tuple(SourceRef.model_validate(ref) for ref in retained))
        result = verify(checked, regions, deterministic_extractors(), today=today)
        if result.outcome == "verified" and result.verification is not None:
            rule, refs = 1, retained
            verifications.append(result.verification.model_dump_json())
        else:
            rule = 2
            refs = [ref for ref, state in zip(row["sources"], states) if state == "cited"]
            fact_citation({**row, "sources": refs}, urls, store)
        changes.append({"id": row["id"], "facet": row["facet"], "model": model, "rule": rule,
                        "retained_outcome": result.outcome})
        final_claim = replace(claim, sources=tuple(SourceRef.model_validate(ref) for ref in refs))
        at = datetime.combine(today, datetime.min.time(), tzinfo=UTC).isoformat()
        events.extend([
            {"event": "collected", "at": at, "claim": final_claim.to_dict()},
            {"event": "checked", "at": at, "target": final_claim.target.model_dump(),
             "outcome": "verified" if rule == 1 else "cited", "diff": []},
        ])
        originals[path] = text.encode("utf-8")
        edits[path].extend(drop_refs(text, offset, mapping(node)["sources"],
                                    [ref in refs for ref in row["sources"]]))
    writes = {}
    for path, replacements in edits.items():
        text = originals[path].decode("utf-8")
        for start, end, replacement in sorted(replacements, reverse=True):
            text = text[:start] + replacement + text[end:]
        writes[path] = text.encode("utf-8")
    for path, lines in (
        (root / "verification/log.jsonl", verifications),
        (root / "verification/queue/events.jsonl",
         [json.dumps(event, sort_keys=True, ensure_ascii=False) for event in events]),
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
        args.data_root.resolve(), CopyStore(args.source_cache.resolve()), args.as_of)
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
        grouped["by_" + field] = {key: {rule: count[rule] for rule in ("1", "2", "3")}
                                 for key, count in sorted(groups.items())}
    print(json.dumps({"counts": {rule: counts[rule] for rule in ("1", "2", "3")},
                      **grouped, "changes": changes}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
