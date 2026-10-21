"""Offline source-ref repairs through the opt-in command and snapshot admission."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from decision.model import Fact, Source, fact_verification_value, value_hash
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from decision.sources import CopyStore
from decision.verify import Claim, Queue, Result
from tests.snapshot_records import fact

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/refile_mixed_citations.py"


def setup_data(tmp_path, *, retained_value=128000, facet="model.context_window", support="open"):
    root = tmp_path / "data"
    store = CopyStore(tmp_path / "copies")
    retained = store.put(
        (
            "<table><tr><th>Model</th><th>Context window</th></tr>"
            f"<tr><td>Alpha</td><td>{retained_value}</td></tr></table>"
        ).encode(),
        source_url="https://retained.example/models",
    )
    sources = [
        Source(
            id=sid,
            url=url,
            normaliser="html-default",
            kind="lab_documentation",
            cited_regions=[{"id": "page", "locator": {"kind": "page", "value": ""}}],
        ).model_dump(mode="json")
        for sid, url in (
            ("open", "https://retained.example/models"),
            ("cite", "https://docs.x.ai/models"),
        )
    ]
    registry = root / "registry"
    registry.mkdir(parents=True)
    (registry / "sources.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "sources": sources})
    )
    row = fact("model", "lab/alpha", facet, 128000)
    row["sources"] = [
        {"source_id": "open", "snapshot_ref": retained, "cited_regions": ["page"]},
        {
            "source_id": "cite",
            "snapshot_ref": "sha256:" + "a" * 64,
            "cited_regions": ["page"],
            "retrieved_at": "2026-10-18T12:00:00+00:00",
        },
    ]
    card = root / "models/lab/alpha.md"
    card.parent.mkdir(parents=True)
    card.write_bytes(
        (
            "---\n"
            + yaml.safe_dump(
                {
                    "model_id": "lab/alpha",
                    "display_name": "Alpha",
                    "facts": [row],
                },
                sort_keys=False,
            )
            + "---\nKeep this body and its spacing.  \n"
        )
        .replace("\n", "\r\n")
        .encode()
    )
    historical = {**row, "sources": [ref for ref in row["sources"] if ref["source_id"] == support]}
    claim = Claim.from_fact(
        Fact.model_validate(historical),
        names=("Alpha",),
        label="context window",
        collector=Fact.model_validate(row).verification.collector,
    )
    queue = Queue(root / "verification")
    queue.file(claim, at=datetime(2026, 9, 20, tzinfo=UTC))
    queue.checked(Result(claim.target, "verified"), at=datetime(2026, 9, 20, tzinfo=UTC))
    log = root / "verification/log.jsonl"
    log.write_bytes((json.dumps(row["verification"]) + "\r\n").encode())
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"schema_version": 1, "cite_only_hosts": ["x.ai"]}))
    return root, store.root, policy, card


def invoke(root, cache, policy, *extra):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--data-root",
            str(root),
            "--source-cache",
            str(cache),
            "--policy",
            str(policy),
            "--as-of",
            "2026-10-21",
            *extra,
        ],
        env={**os.environ, "PYTHONPATH": str(SCRIPT.parents[1])},
        capture_output=True,
        text=True,
    )


def files(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_dry_run_verifies_retained_refs_without_writing(tmp_path):
    root, cache, policy, _ = setup_data(tmp_path)
    before = files(tmp_path)
    result = invoke(root, cache, policy)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 1, "2": 0, "3": 0}
    assert report["changes"][0]["rule"] == 1
    assert files(tmp_path) == before


def test_missing_retained_copy_preserves_existing_retained_verification(tmp_path):
    root, _, policy, card = setup_data(tmp_path)
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    historical = {**row, "sources": [row["sources"][0]]}
    claim = Claim.from_fact(
        Fact.model_validate(historical), names=("Alpha",), label="context window",
        collector=Fact.model_validate(row).verification.collector,
    )
    events = root / "verification/queue/events.jsonl"
    events.write_text("\n".join(json.dumps(event) for event in [
        {"event": "collected", "at": "2026-09-20T12:00:00+00:00", "claim": claim.to_dict()},
        {"event": "checked", "at": "2026-09-20T12:01:00+00:00",
         "target": claim.target.model_dump(), "outcome": "verified", "diff": []},
    ]) + "\n")
    before_log = (root / "verification/log.jsonl").read_bytes()
    result = invoke(root, tmp_path / "missing-copies", policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 1, "2": 0, "3": 0}
    repaired = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert repaired["sources"] == historical["sources"]
    assert (root / "verification/log.jsonl").read_bytes() == before_log
    snapshot = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[{"id": "lab/alpha", "lifecycle": "active", "facts": [repaired]}],
        sources={"open": "https://retained.example/models", "cite": "https://docs.x.ai/models"},
        verifications=[json.loads(line) for line in before_log.splitlines()],
    )))
    admitted = snapshot.fact("lab/alpha", "model.context_window")
    assert (admitted.state, admitted.value) == ("known", 128000)
    record = snapshot.record(admitted.record_id)
    assert record["verification"] == row["verification"]
    assert "citation" not in record


@pytest.mark.parametrize("retained_value,rule,source", [(128000, 1, "open"), (64000, 2, "cite")])
def test_write_preserves_values_bytes_and_admission_and_is_idempotent(
    tmp_path, retained_value, rule, source
):
    root, cache, policy, card = setup_data(tmp_path, retained_value=retained_value, support=source)
    before = files(root)
    original = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"][str(rule)] == 1
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert {k: v for k, v in row.items() if k != "sources"} == {
        k: v for k, v in original.items() if k != "sources"
    }
    assert row["sources"] == [ref for ref in original["sources"] if ref["source_id"] == source]
    assert card.read_bytes().endswith(b"---\r\nKeep this body and its spacing.  \r\n")
    assert b"\n" not in card.read_bytes().replace(b"\r\n", b"")
    for name in ("verification/log.jsonl", "verification/queue/events.jsonl"):
        assert (root / name).read_bytes().startswith(before[name])
    records = [
        json.loads(line) for line in (root / "verification/log.jsonl").read_text().splitlines()
    ]
    snapshot = load_built_snapshot(
        build_snapshot(
            SnapshotInputs(
                models=[{"id": "lab/alpha", "lifecycle": "active", "facts": [row]}],
                sources={
                    "open": "https://retained.example/models",
                    "cite": "https://docs.x.ai/models",
                },
                verifications=records,
            )
        )
    )
    admitted = snapshot.fact("lab/alpha", "model.context_window")
    assert (admitted.state, admitted.value) == ("known", 128000)
    record = snapshot.record(admitted.record_id)
    if rule == 2:
        assert record["citation"]["status"] == "cited"
        assert record["verification"] is None
        assert (root / "verification/log.jsonl").read_bytes() == before["verification/log.jsonl"]
    else:
        assert "citation" not in record
        assert record["verification"] == original["verification"]
        assert (root / "verification/log.jsonl").read_bytes() == before["verification/log.jsonl"]
    after = files(root)
    again = invoke(root, cache, policy, "--write")
    assert again.returncode == 0, again.stderr
    assert json.loads(again.stdout)["counts"] == {"1": 0, "2": 0, "3": 0}
    assert files(root) == after


def rewrite_card(card, update):
    data = yaml.safe_load(card.read_text().split("---")[1])
    update(data)
    card.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\nBody.\n")


def append_mixed_verification(root, card, *, day="2026-10-20"):
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    record = {**row["verification"], "date": day, "outcome": "verified",
              "verifier": {**row["verification"]["verifier"], "model_family": "family-b"}}
    record.pop("diff", None)
    with (root / "verification/log.jsonl").open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    claim = Claim.from_fact(Fact.model_validate(row), names=("Alpha",),
                            collector=Fact.model_validate(row).verification.collector)
    queue = Queue(root / "verification")
    at = datetime.fromisoformat(day + "T12:00:00+00:00")
    queue.file(claim, at=at)
    queue.checked(Result(claim.target, "verified"), at=at)


@pytest.mark.parametrize("support,rule,unresolved", [("open", 1, 0), ("cite", None, 1)])
def test_earlier_support_with_later_mixed_winner(tmp_path, support, rule, unresolved):
    root, _, policy, card = setup_data(tmp_path, support=support)
    append_mixed_verification(root, card)
    before = files(root)
    result = invoke(root, tmp_path / "missing-copies", policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["unresolved"] == unresolved
    if rule:
        assert report["counts"] == {"1": 1, "2": 0, "3": 0}
        assert (root / "verification/log.jsonl").read_bytes() == before["verification/log.jsonl"]
        assert (root / "verification/queue/events.jsonl").read_bytes() == before[
            "verification/queue/events.jsonl"
        ]
    else:
        assert report["counts"] == {"1": 0, "2": 0, "3": 0}
        assert files(root) == before


def test_retained_copy_contents_cannot_override_historical_support(tmp_path):
    root, cache, policy, _ = setup_data(tmp_path, retained_value=64000, support="open")
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 1, "2": 0, "3": 0}
    assert (root / "verification/log.jsonl").read_bytes() == before["verification/log.jsonl"]


def test_unmatched_checks_cannot_attribute_log_records(tmp_path):
    root, cache, policy, _ = setup_data(tmp_path)
    path = root / "verification/queue/events.jsonl"
    path.write_text(path.read_text().splitlines()[0] + "\n")
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["unresolved"] == 1
    assert files(root) == before


def test_repeated_cited_checks_preserve_unambiguous_winning_side(tmp_path):
    root, cache, policy, _ = setup_data(tmp_path, support="cite")
    path = root / "verification/queue/events.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    older = json.loads(json.dumps(events))
    older[0]["claim"]["sources"][0]["snapshot_ref"] = "sha256:" + "b" * 64
    path.write_text("\n".join(json.dumps(event) for event in [*older, *events]) + "\n")
    log = root / "verification/log.jsonl"
    log.write_bytes(log.read_bytes() * 2)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 1, "3": 0}


@pytest.mark.parametrize("damage", [
    "inline_mismatch", "logged_mismatch", "same_family", "wrong_field", "wrong_subject",
])
def test_invalidated_or_misfiled_history_cannot_prove_retained_support(tmp_path, damage):
    root, cache, policy, card = setup_data(tmp_path)
    log = root / "verification/log.jsonl"
    record = json.loads(log.read_text())
    if damage in {"inline_mismatch", "logged_mismatch"}:
        failed = {**record, "date": "2026-10-01", "outcome": "mismatch", "diff": "value differs"}
        if damage == "inline_mismatch":
            rewrite_card(card, lambda data: data["facts"][0].update(verification=failed))
        else:
            with log.open("a") as stream:
                stream.write(json.dumps(failed) + "\n")
    elif damage == "same_family":
        record["verifier"]["model_family"] = record["collector"]["model_family"]
        log.write_text(json.dumps(record) + "\n")
    else:
        path = root / "verification/queue/events.jsonl"
        events = [json.loads(line) for line in path.read_text().splitlines()]
        events[0]["claim"]["field" if damage == "wrong_field" else "subject"] = (
            "model.max_output_tokens" if damage == "wrong_field" else "lab/other"
        )
        path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    # The latest winner confirms the value, but does not identify its source.
    rewrite_card(card, lambda data: data["facts"][0].update(verification=record))
    append_mixed_verification(root, card)
    if damage == "inline_mismatch":
        rewrite_card(card, lambda data: data["facts"][0].update(verification=failed))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["unresolved"] == 1
    assert files(root) == before


def test_stale_queue_value_cannot_verify_current_fact(tmp_path):
    root, cache, policy, card = setup_data(tmp_path)
    rewrite_card(card, lambda data: data["facts"][0].update(value=256000, verification=None))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 0, "3": 0}
    assert json.loads(result.stdout)["unresolved"] == 1
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert row["value"] == 256000
    assert files(root) == before


@pytest.mark.parametrize("facet", ["offering.api_model_id", "offering.router_slug"])
def test_mixed_identifiers_are_reported_and_untouched(tmp_path, facet):
    root, cache, policy, card = setup_data(tmp_path)
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    subject = "sambanova/lab/alpha/global/standard"
    row.update(
        facet=facet,
        id=f"{subject}#{facet}",
        value="alpha",
        verification=None,
        subject={"kind": "offering", "id": subject},
    )
    rewrite_card(card, lambda data: data.update(facts=[]))
    offering = root / "offerings/sambanova/lab/alpha.yaml"
    offering.parent.mkdir(parents=True)
    offering.write_text(
        yaml.safe_dump(
            [
                {
                    "model": "lab/alpha",
                    "provider": "sambanova",
                    "region": "global",
                    "tier": "standard",
                    "facts": [row],
                }
            ]
        )
    )
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 0, "3": 1}
    assert files(root) == before


@pytest.mark.parametrize("dates", [
    {"effective_from": "2026-10-01"},
    {"effective_until": "2026-10-31"},
])
def test_verified_dated_price_requires_complete_schedule_and_stays_unchanged(tmp_path, dates):
    root, cache, policy, card = setup_data(tmp_path)
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    subject = "sambanova/lab/alpha/global/standard"
    row.update(
        facet="offering.price.input", id=f"{subject}#offering.price.input",
        subject={"kind": "offering", "id": subject}, value=3.5, **dates,
    )
    row["verification"]["target"].update(
        id=row["id"], value_hash=value_hash(fact_verification_value(row)),
    )
    validated = Fact.model_validate(row)
    claim = Claim.from_fact(
        validated.model_copy(update={"sources": [validated.sources[0]]}),
        names=("Alpha",), collector=validated.verification.collector,
    )
    queue = Queue(root / "verification")
    queue.path.write_text("")
    at = datetime(2026, 9, 20, tzinfo=UTC)
    queue.file(claim, at=at)
    queue.checked(Result(claim.target, "verified"), at=at)
    (root / "verification/log.jsonl").write_text(json.dumps(row["verification"]) + "\n")
    rewrite_card(card, lambda data: data.update(facts=[]))
    offering = root / "offerings/sambanova/lab/alpha.yaml"
    offering.parent.mkdir(parents=True)
    offering.write_text(yaml.safe_dump([{
        "model": "lab/alpha", "provider": "sambanova", "region": "global",
        "tier": "standard", "facts": [row],
    }]))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 0, "2": 0, "3": 0}
    assert report["unresolved"] == 1
    assert "complete offering schedule" in report["changes"][0]["reason"]
    assert files(root) == before


def test_changed_retained_hash_leaves_unknown_support_unchanged(tmp_path):
    root, cache, policy, card = setup_data(tmp_path)

    def update(data):
        data["facts"][0]["sources"][0]["snapshot_ref"] = "sha256:" + "b" * 64
        data["facts"][0]["sources"][1].pop("retrieved_at")

    rewrite_card(card, update)
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 0, "2": 0, "3": 0}
    assert report["unresolved"] == 1
    assert files(root) == before


def test_checked_queue_event_clears_changed_copy_overrides(tmp_path):
    root, cache, policy, card = setup_data(tmp_path)
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    original_a = row["sources"][0]
    original_b = {**original_a, "source_id": "open-b", "snapshot_ref": "sha256:" + "c" * 64}
    current_a = {**original_a, "snapshot_ref": "sha256:" + "b" * 64}
    current_b = {**original_b, "snapshot_ref": "sha256:" + "d" * 64}
    registry_path = root / "registry/sources.yaml"
    registered = yaml.safe_load(registry_path.read_text())
    registered["sources"].append({
        **registered["sources"][0], "id": "open-b", "url": "https://retained.example/features",
    })
    registry_path.write_text(yaml.safe_dump(registered))
    historical = Fact.model_validate({**row, "sources": [original_a, original_b]})
    claim = Claim.from_fact(
        historical, names=("Alpha",), collector=historical.verification.collector,
    )
    target = claim.target.model_dump()
    events = [
        {"event": "collected", "at": "2026-09-20T12:00:00+00:00", "claim": claim.to_dict()},
        {"event": "changed", "at": "2026-09-20T12:01:00+00:00", "target": target,
         "copies": {"open": current_a["snapshot_ref"]}},
        {"event": "checked", "at": "2026-09-20T12:02:00+00:00", "target": target,
         "outcome": "verified", "diff": []},
        {"event": "changed", "at": "2026-09-21T12:01:00+00:00", "target": target,
         "copies": {"open-b": current_b["snapshot_ref"]}},
        {"event": "checked", "at": "2026-09-21T12:02:00+00:00", "target": target,
         "outcome": "verified", "diff": []},
    ]
    (root / "verification/queue/events.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n"
    )
    with (root / "verification/log.jsonl").open("a") as stream:
        stream.write(json.dumps({**row["verification"], "date": "2026-09-21"}) + "\n")
    rewrite_card(card, lambda data: data["facts"][0].update(
        sources=[current_a, current_b, row["sources"][1]],
    ))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 0, "2": 0, "3": 0}
    assert report["unresolved"] == 1
    assert files(root) == before


@pytest.mark.parametrize("damage", ["invalid_citation", "unresolved_source", "unterminated_log"])
def test_invalid_input_prevents_all_writes(tmp_path, damage):
    root, cache, policy, card = setup_data(
        tmp_path, support="cite" if damage == "unterminated_log" else "open"
    )
    if damage == "invalid_citation":
        rewrite_card(card, lambda data: data["facts"][0]["sources"][1].update(cited_regions=[]))
    elif damage == "unresolved_source":
        rewrite_card(card, lambda data: data["facts"][0]["sources"][0].update(source_id="missing"))
    else:
        path = root / "verification/queue/events.jsonl"
        path.write_bytes(path.read_bytes().rstrip(b"\r\n"))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode != 0
    assert files(root) == before


def test_inline_source_mappings_are_removed_and_second_run_is_empty(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    text = card.read_text()
    data = yaml.safe_load(text.split("---")[1])
    old = data["facts"][0]["sources"]
    start = text.index("  sources:\n") + len("  sources:\n")
    end = text.index("  verification:", start)
    card.write_text(
        text[:start] + "".join("  - " + json.dumps(ref) + "\n" for ref in old) + text[end:]
    )
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert row["sources"] == [old[1]]
    again = invoke(root, cache, policy, "--write")
    assert again.returncode == 0, again.stderr
    assert json.loads(again.stdout)["counts"] == {"1": 0, "2": 0, "3": 0}


def test_aliased_sources_are_refused_without_changing_other_records(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    data = yaml.safe_load(card.read_text().split("---")[1])
    data["unrelated_sources"] = data["facts"][0]["sources"]
    card.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\nBody.\n")
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode != 0
    assert files(root) == before
