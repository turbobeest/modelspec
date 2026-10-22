"""Audit the private repair; emit counts and byte-preservation checks only."""

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

import yaml

from decision import retention
from decision.citation import ref_states
from decision.sources import load_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--engine-pin", required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.data_root

    def git(*argv):
        return subprocess.run(["git", "-C", str(root), *argv], check=True,
                              capture_output=True).stdout

    def before(name):
        return git("show", f"{args.base}:{name}")

    retention.POLICY_PATH = args.policy
    retention.cite_only_hosts.cache_clear()
    urls = {sid: str(source.url)
            for sid, source in load_sources(root / "registry/sources.yaml").items()}
    plan = json.loads(args.plan.read_text())
    changes = {row["id"]: row for row in plan["changes"]}
    seen, counts, removed = set(), Counter(), Counter()
    for path in sorted((root / "models").glob("*/*.md")):
        name = path.relative_to(root).as_posix()
        original, current = before(name), path.read_bytes()
        old_parts, new_parts = original.split(b"---", 2), current.split(b"---", 2)
        old, new = yaml.safe_load(old_parts[1]), yaml.safe_load(new_parts[1])
        assert old_parts[0::2] == new_parts[0::2], name
        for left, right in zip(old.get("facts", []), new.get("facts", []), strict=True):
            identity = f"{old['model_id']}#{left['facet']}"
            entry = changes.get(identity)
            rule = entry["rule"] if entry else "unchanged"
            if entry:
                seen.add(identity)
                counts[str(rule)] += 1
            if rule in (1, 2):
                states = ref_states(left, urls)
                expected = [ref for ref, state in zip(left["sources"], states)
                            if (state == "cited") == (rule == 2)]
                assert right["sources"] == expected, identity
                removed[str(rule)] += len(left["sources"]) - len(expected)
                left["sources"] = expected
            assert left == right, identity
        assert old == new, name
    assert seen == set(changes)
    log = "verification/log.jsonl"
    assert before(log) == (root / log).read_bytes()
    queue = "verification/queue/events.jsonl"
    old_queue, new_queue = before(queue), (root / queue).read_bytes()
    assert new_queue.startswith(old_queue)
    appended = [json.loads(line) for line in new_queue[len(old_queue):].splitlines()]
    assert len(appended) == counts["2"] * 2
    for collected, checked in zip(appended[::2], appended[1::2], strict=True):
        claim = collected["claim"]
        assert collected["event"] == "collected"
        assert changes[claim["target"]["id"]]["rule"] == 2
        assert checked["event"] == "checked" and checked["outcome"] == "cited"
        assert checked["target"] == claim["target"] and checked["diff"] == []
        path = root / "models" / (claim["subject"] + ".md")
        card = yaml.safe_load(path.read_bytes().split(b"---", 2)[1])
        row = next(row for row in card["facts"] if row["facet"] == claim["field"])
        assert claim["value"] == row["value"] and claim["sources"] == row["sources"]
    assert (root / ".engine-pin").read_text().strip() == args.engine_pin
    changed_files = git("diff", "--name-only", args.base).decode().splitlines()
    assert all(name.startswith("models/") or name in {queue, ".engine-pin"}
               for name in changed_files)
    report = {
        "counts": dict(sorted(counts.items())), "removed_refs_by_rule": dict(removed),
        "changed_model_files": sum(name.startswith("models/") for name in changed_files),
        "verification_log_byte_identical": True, "queue_prefix_byte_identical": True,
        "appended_collected_events": len(appended) // 2,
        "appended_cited_checks": len(appended) // 2,
        "values_states_other_fields_and_bodies_unchanged": True,
        "unknown_facts_unchanged": counts["unknown"], "no_code_added_under_data_paths": True,
        "engine_pin": args.engine_pin, "by_facet": plan["by_facet"],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
