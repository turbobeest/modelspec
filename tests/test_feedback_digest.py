"""MODEL-221: the weekly digest turns a staged negative cluster into one draft."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
for _path in (REPO_ROOT / "scripts" / "feedback", REPO_ROOT / "api" / "worker" / "src"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import access_kv  # noqa: E402
import digest  # noqa: E402
import export  # noqa: E402
import feedback_service as fb  # noqa: E402

UNTIL = date(2026, 10, 5)


def _stage(tmp_path: Path) -> Path:
    """Feedback as the Worker stores it: sent through `submit`, read back out of KV."""
    kv = access_kv.MemoryKV()
    store = fb.Store(enabled=True, kv=kv, pepper=b"p" * 32)
    bodies = [
        # The cluster: three "confusing" on the coding template, two decisions,
        # one repeated note, one note carrying an email address.
        {"rating": "confusing", "client": "page", "page": "/decide/", "template": "coding",
         "decision_id": "dec_aaaaaaaaaaaa", "note": "Which band do I pick?"},
        {"rating": "confusing", "client": "agent", "template": "coding",
         "decision_id": "dec_bbbbbbbbbbbb", "note": "which band do I   pick?"},
        {"rating": "confusing", "client": "page", "page": "/decide/", "template": "coding",
         "decision_id": "dec_aaaaaaaaaaaa", "note": "ping me at jo@example.com"},
        # Below the threshold: one "untrustworthy".
        {"rating": "untrustworthy", "client": "cli", "decision_id": "dec_cccccccccccc"},
        # Positive: counted, never drafted.
        {"rating": "reliable", "client": "page", "page": "/method/"},
        {"rating": "trustworthy", "client": "mcp"},
    ]
    now = datetime(2026, 10, 3, 12, tzinfo=UTC)
    for i, body in enumerate(bodies):
        outcome = asyncio.run(fb.submit(raw=json.dumps(body).encode(), address=f"198.51.100.{i}",
                                        origin=None, allowed_origins=frozenset(), store=store,
                                        now=now + timedelta(minutes=i)))
        assert outcome.status == 202
    # Last month's feedback falls outside the window.
    old = asyncio.run(fb.submit(raw=json.dumps({"rating": "confusing", "client": "page",
                                                "template": "coding"}).encode(),
                                address="198.51.100.99", origin=None,
                                allowed_origins=frozenset(), store=store,
                                now=now - timedelta(days=30)))
    assert old.status == 202

    def run(args):
        if args[:3] == ["kv", "key", "list"]:
            return json.dumps([{"name": k} for k in kv.data if k.startswith(fb.RECORD_PREFIX)])
        return kv.data[args[3]]

    out = tmp_path / "export.jsonl"
    assert export.export("ns", out, run=run) == 7
    return out


def test_a_staged_cluster_becomes_one_new_draft_with_its_decision_ids(tmp_path) -> None:
    records = _stage(tmp_path)
    summary = digest.run(records, tmp_path / "week1", tmp_path / "ledger.json", until=UNTIL)
    assert summary["records"] == 6 and summary["new"] == 1 and summary["update"] == 0

    (draft,) = json.loads((tmp_path / "week1" / "drafts.json").read_text())
    assert draft["action"] == "new"
    assert draft["cluster_key"] == "confusing|template:coding"
    assert draft["title"] == "Feedback: 3 × confusing on the coding template"
    assert draft["decision_ids"] == ["dec_aaaaaaaaaaaa", "dec_bbbbbbbbbbbb"]
    assert draft["labels"] == ["feedback", "feedback:confusing"]
    # Deduplicated notes, and the email scrubbed by the Worker before storage.
    assert draft["description"].count("band do I") == 1
    assert "jo@example.com" not in draft["description"]
    assert "[email]" in draft["description"]

    md = (tmp_path / "week1" / "digest.md").read_text()
    assert "| confusing | 3 |" in md and "| reliable | 1 |" in md and "| unreliable | 0 |" in md
    assert "| coding | 3 |" in md
    assert "`untrustworthy|client:cli`: 1 (below threshold)" in md


def test_the_same_cluster_next_week_is_an_update_not_a_second_issue(tmp_path) -> None:
    records = _stage(tmp_path)
    ledger = tmp_path / "ledger.json"
    digest.run(records, tmp_path / "week1", ledger, until=UNTIL)
    state = json.loads(ledger.read_text())
    state["confusing|template:coding"]["issue"] = "MODEL-999"
    ledger.write_text(json.dumps(state))

    later = tmp_path / "later.jsonl"
    rows = [json.loads(line) for line in records.read_text().splitlines()]
    moved = [{**r, "received_on": "2026-10-10"} for r in rows if r["rating"] == "confusing"]
    moved.append({**moved[0], "decision_id": "dec_dddddddddddd"})
    later.write_text("".join(json.dumps(r) + "\n" for r in moved))
    summary = digest.run(later, tmp_path / "week2", ledger, until=date(2026, 10, 12))
    assert summary["new"] == 0 and summary["update"] == 1
    (draft,) = json.loads((tmp_path / "week2" / "drafts.json").read_text())
    assert draft["action"] == "update" and draft["issue"] == "MODEL-999"
    assert draft["new_decision_ids"] == ["dec_dddddddddddd"]
    assert "dec_dddddddddddd" in json.loads(ledger.read_text())[
        "confusing|template:coding"]["decision_ids"]


def test_feedback_text_is_never_written_into_the_repository(tmp_path) -> None:
    records = _stage(tmp_path)
    with pytest.raises(digest.DigestError, match="inside the public ModelSpec repository"):
        digest.run(records, REPO_ROOT / "docs" / "feedback" / "out", None, until=UNTIL)
    with pytest.raises(digest.DigestError, match="inside the public ModelSpec repository"):
        digest.run(records, tmp_path / "ok", REPO_ROOT / "ledger.json", until=UNTIL)
    with pytest.raises(digest.DigestError, match="inside the public ModelSpec repository"):
        export.export("ns", REPO_ROOT / "export.jsonl", run=lambda args: "[]")


def test_a_record_that_is_not_the_stored_shape_is_refused(tmp_path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({"rating": "confusing", "ip": "203.0.113.7"}) + "\n")
    with pytest.raises(digest.DigestError, match="not a stored record"):
        digest.load(bad)


def test_no_workflow_runs_the_digest() -> None:
    """Public CI logs are public; the digest reads private feedback text."""
    for workflow in (REPO_ROOT / ".github" / "workflows").glob("*.y*ml"):
        text = workflow.read_text(encoding="utf-8")
        assert "scripts/feedback/" not in text, workflow.name
