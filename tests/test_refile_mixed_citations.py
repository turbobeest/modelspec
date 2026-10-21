"""Offline source-ref repairs through the opt-in command and snapshot admission."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from decision.model import Fact, Source
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from decision.sources import CopyStore
from decision.verify import Claim, Queue
from tests.snapshot_records import fact

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/refile_mixed_citations.py"


def setup_data(tmp_path, *, retained_value=128000, facet="model.context_window"):
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
    claim = Claim.from_fact(
        Fact.model_validate(row),
        names=("Alpha",),
        label="context window",
        collector=Fact.model_validate(row).verification.collector,
    )
    Queue(root / "verification").file(claim, at=datetime(2026, 10, 18, tzinfo=UTC))
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


@pytest.mark.parametrize("retained_value,rule,source", [(128000, 1, "open"), (64000, 2, "cite")])
def test_write_preserves_values_bytes_and_admission_and_is_idempotent(
    tmp_path, retained_value, rule, source
):
    root, cache, policy, card = setup_data(tmp_path, retained_value=retained_value)
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
        assert record["verification"]["verifier"]["model_family"] == "deterministic"
    after = files(root)
    again = invoke(root, cache, policy, "--write")
    assert again.returncode == 0, again.stderr
    assert json.loads(again.stdout)["counts"] == {"1": 0, "2": 0, "3": 0}
    assert files(root) == after


def rewrite_card(card, update):
    data = yaml.safe_load(card.read_text().split("---")[1])
    update(data)
    card.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\nBody.\n")


def test_stale_queue_value_cannot_verify_current_fact(tmp_path):
    root, cache, policy, card = setup_data(tmp_path)
    rewrite_card(card, lambda data: data["facts"][0].update(value=256000, verification=None))
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"] == {"1": 0, "2": 1, "3": 0}
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert row["value"] == 256000
    assert [ref["source_id"] for ref in row["sources"]] == ["cite"]


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


def test_unreachable_retained_copy_uses_undated_citation_without_reading_its_bytes(tmp_path):
    root, cache, policy, card = setup_data(tmp_path)

    def update(data):
        data["facts"][0]["sources"][0]["snapshot_ref"] = "sha256:" + "b" * 64
        data["facts"][0]["sources"][1].pop("retrieved_at")

    rewrite_card(card, update)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["counts"] == {"1": 0, "2": 1, "3": 0}
    assert report["changes"][0]["retained_outcome"] == "unreachable"
    row = yaml.safe_load(card.read_text().split("---")[1])["facts"][0]
    assert "retrieved_at" not in row["sources"][0]


@pytest.mark.parametrize("damage", ["invalid_citation", "unresolved_source", "unterminated_log"])
def test_invalid_input_prevents_all_writes(tmp_path, damage):
    root, cache, policy, card = setup_data(tmp_path)
    if damage == "invalid_citation":
        rewrite_card(card, lambda data: data["facts"][0]["sources"][1].update(cited_regions=[]))
    elif damage == "unresolved_source":
        rewrite_card(card, lambda data: data["facts"][0]["sources"][0].update(source_id="missing"))
    else:
        path = root / "verification/log.jsonl"
        path.write_bytes(path.read_bytes().rstrip(b"\r\n"))
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode != 0
    assert files(root) == before


def test_inline_source_mappings_are_removed_and_second_run_is_empty(tmp_path):
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000)
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
    root, cache, policy, card = setup_data(tmp_path, retained_value=64000)
    data = yaml.safe_load(card.read_text().split("---")[1])
    data["unrelated_sources"] = data["facts"][0]["sources"]
    card.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\nBody.\n")
    before = files(root)
    result = invoke(root, cache, policy, "--write")
    assert result.returncode != 0
    assert files(root) == before
