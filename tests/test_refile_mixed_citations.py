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


def setup_data(tmp_path, *, retained_value=128000, facet="model.context_window", support="open",
               value=128000):
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
    row = fact("model", "lab/alpha", facet, value)
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


@pytest.mark.parametrize("support,refused,unresolved", [("open", 1, 0), ("cite", 0, 1)])
def test_earlier_support_with_later_mixed_winner(tmp_path, support, refused, unresolved):
    root, _, policy, card = setup_data(tmp_path, support=support)
    append_mixed_verification(root, card)
    before = files(root)
    result = invoke(root, tmp_path / "missing-copies", policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["unresolved"] == unresolved
    # Rule 1 would leave the card citing one source while the latest filed claim
    # (the mixed one) names two: the MODEL-546 drift. It refuses instead (MODEL-549).
    assert report["refused"] == refused
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
        # A newer mixed claim makes rule 2 file a claim, so the run must append.
        file_later_mixed_claim(root, card, datetime(2026, 10, 1, tzinfo=UTC))
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


def card_claim_disagreements(root):
    """The data-side rule (MODEL-546), written independently of the script.

    A card fact's source ids must equal those of its latest filed claim: the latest
    ``collected`` event, by ``at`` (no zone means UTC), equal instants in line order.
    Facts with no filed claim are exempt.
    """
    def at(event):
        moment = datetime.fromisoformat(event["at"])
        return moment if moment.tzinfo else moment.replace(tzinfo=UTC)

    events = [json.loads(line) for line in
              (root / "verification/queue/events.jsonl").read_text().splitlines() if line.strip()]
    claimed = {}
    for event in sorted(events, key=at):
        if event["event"] == "collected" and event["claim"]["target"]["kind"] == "fact":
            claimed[event["claim"]["target"]["id"]] = {
                ref["source_id"] for ref in event["claim"]["sources"]}
    wrong, checked = [], 0
    for path in sorted((root / "models").rglob("*.md")):
        front = yaml.safe_load(path.read_text().split("---", 2)[1])
        for row in front.get("facts") or []:
            fact_id = row.get("id") or f"{front['model_id']}#{row['facet']}"
            if fact_id not in claimed:
                continue
            checked += 1
            if {ref["source_id"] for ref in row["sources"]} != claimed[fact_id]:
                wrong.append(fact_id)
    return wrong, checked


def file_later_mixed_claim(root, card, at):
    """File the card's current (mixed) sources as a newer claim, with no check."""
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    claim = Claim.from_fact(Fact.model_validate(row), names=("Alpha",),
                            collector=Fact.model_validate(row).verification.collector)
    Queue(root / "verification").file(claim, at=at)


def test_rule_1_refuses_rather_than_leave_card_and_latest_claim_apart(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, support="open")
    # The retained-only check stands, but a later claim names both sources.
    file_later_mixed_claim(root, card, datetime(2026, 10, 1, tzinfo=UTC))
    assert card_claim_disagreements(root) == ([], 1)
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 0, "2": 0, "3": 0}
    assert report["refused"] == 1
    change = report["changes"][0]
    assert (change["rule"], change["would_be_rule"]) == ("refused", 1)
    assert "leaves 1 source(s), the latest filed claim names 2 (shared 1)" in change["reason"]
    # Counts only: the message names no source id and no hash.
    assert "open" not in change["reason"] and "sha256" not in change["reason"]
    assert report["by_facet"]["model.context_window"]["refused"] == 1
    assert files(root) == before
    assert card_claim_disagreements(root) == ([], 1)


def test_rule_2_claim_files_after_a_same_day_claim(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    # A claim filed later on the --as-of day must not outrank the refiled one.
    file_later_mixed_claim(root, card, datetime(2026, 10, 21, 12, 7, tzinfo=UTC))
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 1, "3": 0}
    assert card_claim_disagreements(root) == ([], 1)
    claim = Queue(root / "verification").filed()[("fact", "lab/alpha#model.context_window")]
    assert [ref.source_id for ref in claim.sources] == ["cite"]
    assert Queue(root / "verification").recrawl_requests() == []


def test_rule_2_refuses_when_the_queue_is_newer_than_as_of(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    file_later_mixed_claim(root, card, datetime(2026, 10, 22, tzinfo=UTC))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["refused"] == 1 and report["counts"]["2"] == 0
    assert files(root) == before


@pytest.mark.parametrize("support,retained_value,later", [
    ("open", 128000, None),
    ("open", 128000, datetime(2026, 10, 1, tzinfo=UTC)),
    ("cite", 64000, None),
    ("cite", 64000, datetime(2026, 10, 21, 18, 0, tzinfo=UTC)),
])
def test_data_rule_holds_over_the_script_output(tmp_path, support, retained_value, later):
    root, cache, policy, card = setup_data(
        tmp_path, retained_value=retained_value, support=support)
    if later is not None:
        file_later_mixed_claim(root, card, later)
    for _ in range(2):  # the write, then an idempotent second run
        result = invoke(root, cache, policy, "--write")
        assert result.returncode == 0, result.stderr
        wrong, checked = card_claim_disagreements(root)
        assert (wrong, checked) == ([], 1)


@pytest.fixture
def script(monkeypatch):
    """The script loaded in process, its retention policy restored afterwards."""
    import importlib.util

    from decision import retention

    spec = importlib.util.spec_from_file_location("refile_mixed_citations", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    monkeypatch.setattr(retention, "POLICY_PATH", retention.POLICY_PATH)
    yield module
    retention.cite_only_hosts.cache_clear()


def plan_in_process(script, root, cache, policy):
    from decision import retention

    retention.POLICY_PATH = policy
    retention.cite_only_hosts.cache_clear()
    return script.plan(root, CopyStore(cache), datetime(2026, 10, 21).date())


@pytest.mark.parametrize("support,retained_value", [("open", 128000), ("cite", 64000)])
def test_queue_changed_between_plan_and_write_is_refused(
    tmp_path, script, support, retained_value
):
    root, cache, policy, card = setup_data(
        tmp_path, retained_value=retained_value, support=support)
    if support == "cite":  # a newer mixed claim makes rule 2 file a claim
        file_later_mixed_claim(root, card, datetime(2026, 9, 30, tzinfo=UTC))
    planned = plan_in_process(script, root, cache, policy)
    assert planned.cards  # rule 1 changes only the card; rule 2 also appends
    assert bool(planned.append) == (support == "cite")
    # Another writer files a claim after the plan was made.
    file_later_mixed_claim(root, card, datetime(2026, 10, 1, tzinfo=UTC))
    before = files(root)
    with pytest.raises(ValueError, match="queue changed since planning"):
        script.apply(planned)
    assert files(root) == before


def test_queue_original_bytes_are_a_prefix_after_the_write(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    file_later_mixed_claim(root, card, datetime(2026, 10, 1, tzinfo=UTC))
    path = root / "verification/queue/events.jsonl"
    # CRLF lines must survive untouched: the write appends, it never rewrites.
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    original = path.read_bytes()
    inode = path.stat().st_ino
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    after = path.read_bytes()
    assert after.startswith(original) and len(after) > len(original)
    assert path.stat().st_ino == inode
    added = [json.loads(line) for line in after[len(original):].decode().splitlines()]
    assert [event["event"] for event in added] == ["collected", "checked"]


def test_card_write_failure_after_the_append_converges_on_rerun(
    tmp_path, script, monkeypatch, capsys
):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000, support="cite")
    file_later_mixed_claim(root, card, datetime(2026, 10, 1, tzinfo=UTC))
    original_card = card.read_bytes()
    args = ["--data-root", str(root), "--source-cache", str(cache), "--policy", str(policy),
            "--as-of", "2026-10-21", "--write"]
    with monkeypatch.context() as patch:
        fail_card_replace(patch)
        assert script.main(args) == 1
    err = capsys.readouterr().err
    assert "1 card file(s) were not written: 1 fact(s) unchanged, 1 of them" in err
    assert card.read_bytes() == original_card
    # Half-done: the claim names the cited source, the card still cites both.
    assert card_claim_disagreements(root) == (["lab/alpha#model.context_window"], 1)
    queue_after_append = (root / "verification/queue/events.jsonl").read_bytes()

    assert script.main(args) == 0
    assert json.loads(capsys.readouterr().out)["counts"] == {"1": 0, "2": 1, "3": 0}
    assert card_claim_disagreements(root) == ([], 1)
    # The rerun finished the card and filed nothing new.
    assert (root / "verification/queue/events.jsonl").read_bytes() == queue_after_append
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert [ref["source_id"] for ref in row["sources"]] == ["cite"]
    assert script.main(args) == 0
    assert json.loads(capsys.readouterr().out)["counts"] == {"1": 0, "2": 0, "3": 0}


def fail_card_replace(patch):
    """Fail the last step of a card write, after its new bytes reached a temp file."""
    replace_file = os.replace

    def failing(source, target, *args, **kwargs):
        if str(target).endswith(".md"):
            raise OSError("simulated card write failure")
        return replace_file(source, target, *args, **kwargs)

    patch.setattr(os, "replace", failing)


def test_same_length_queue_drift_is_refused_by_the_hash(tmp_path, script):
    root, cache, policy, card = setup_data(tmp_path, support="open")
    planned = plan_in_process(script, root, cache, policy)
    path = root / "verification/queue/events.jsonl"
    data = path.read_bytes()
    drifted = data.replace(b"2026-09-20T00:00:00", b"2026-09-21T00:00:00", 1)
    assert drifted != data and len(drifted) == len(data)
    path.write_bytes(drifted)
    before = files(root)
    with pytest.raises(ValueError, match="queue changed since planning"):
        script.apply(planned)
    assert files(root) == before


@pytest.mark.parametrize("value,filed", [(128000, 128000.0), (1, True)])
def test_rule_2_files_when_the_latest_claim_differs_only_in_value_type(tmp_path, value, filed):
    root, cache, policy, card = setup_data(
        tmp_path, retained_value=64000, support="cite", value=value)
    path = root / "verification/queue/events.jsonl"
    first = json.loads(path.read_text().splitlines()[0])
    # Exactly the claim rule 2 would file, but for the value's JSON type.
    assert first["claim"]["value"] == value
    later = {**first, "at": "2026-10-01T00:00:00+00:00",
             "claim": {**first["claim"], "value": filed}}
    with path.open("a") as stream:
        stream.write(json.dumps(later) + "\n")
    before = path.read_bytes()
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 1, "3": 0}
    added = [json.loads(line) for line in path.read_bytes()[len(before):].decode().splitlines()]
    assert [event["event"] for event in added] == ["collected", "checked"]
    assert type(added[0]["claim"]["value"]) is type(value)
    assert card_claim_disagreements(root) == ([], 1)


def test_card_write_failure_leaves_the_card_byte_identical(tmp_path, script, monkeypatch, capsys):
    root, cache, policy, card = setup_data(tmp_path, support="open")
    original = card.read_bytes()
    args = ["--data-root", str(root), "--source-cache", str(cache), "--policy", str(policy),
            "--as-of", "2026-10-21", "--write"]
    before = files(root)
    with monkeypatch.context() as patch:
        fail_card_replace(patch)
        assert script.main(args) == 1
    err = capsys.readouterr().err
    # Rule 1 only: nothing was appended, and the message must not say otherwise.
    assert "no queue line was appended" in err and "queue was appended" not in err
    assert card.read_bytes() == original
    assert files(root) == before  # no temp file left behind either


def test_rule_1_recovers_on_rerun_after_a_card_write_failure(
    tmp_path, script, monkeypatch, capsys
):
    root, cache, policy, card = setup_data(tmp_path, support="open")
    queue = (root / "verification/queue/events.jsonl").read_bytes()
    args = ["--data-root", str(root), "--source-cache", str(cache), "--policy", str(policy),
            "--as-of", "2026-10-21", "--write"]
    with monkeypatch.context() as patch:
        fail_card_replace(patch)
        assert script.main(args) == 1
    capsys.readouterr()
    assert script.main(args) == 0
    assert json.loads(capsys.readouterr().out)["counts"] == {"1": 1, "2": 0, "3": 0}
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert [ref["source_id"] for ref in row["sources"]] == ["open"]
    assert (root / "verification/queue/events.jsonl").read_bytes() == queue
    assert card_claim_disagreements(root) == ([], 1)
    assert script.main(args) == 0
    assert json.loads(capsys.readouterr().out)["counts"] == {"1": 0, "2": 0, "3": 0}


def test_the_data_root_plan_counts_by_the_private_datas_rule(tmp_path, script, monkeypatch):
    # MODEL-491, Codex reviews 4 and 7: with --private-data the plan's compiler and its history
    # check count verdicts by MODEL-491's rule; without it, on any --data-root, by main's. The
    # rule is never read from the environment.
    root, cache, policy, _card = setup_data(tmp_path, retained_value=64000, support="open")
    seen, real = [], script._Compiler

    def compiler(inputs, *args, **kwargs):
        seen.append(inputs.retire_rsp)
        return real(inputs, *args, **kwargs)

    monkeypatch.setattr(script, "_Compiler", compiler)
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    args = ["--data-root", str(root), "--source-cache", str(cache), "--policy", str(policy),
            "--as-of", "2026-10-21"]
    assert script.main(args) == 0
    assert seen and not any(seen)
    seen.clear()
    assert script.main([*args, "--private-data"]) == 0
    assert seen and all(seen)
    seen.clear()
    plan_in_process(script, root, cache, policy)  # the plan itself defaults to the public rule
    assert seen and not any(seen)
