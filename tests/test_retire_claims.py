"""MODEL-557: a retired claim leaves the queue's filed set and the data-fidelity draws."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor
from scripts import accuracy, retire_claims
from tests.snapshot_records import fact

AT = datetime(2026, 11, 25, 12, tzinfo=UTC)


def claim(subject="lab/alpha", field="model.context_window", value=128000):
    row = fact("model", subject, field, value, outcome=None)
    return verify.Claim(
        target=TargetRef(kind="fact", id=row["id"]),
        subject=subject, names=("Alpha",), field=field, value=value,
        collector=VerificationActor(agent="collector", model_family="collector", method="read"),
        sources=(SourceRef.model_validate(row["sources"][0]),),
    )


def lines(root):
    return (root / "queue" / "events.jsonl").read_text(encoding="utf-8").splitlines()


def test_retired_claim_is_not_filed_pending_or_recrawled(tmp_path):
    queue = verify.Queue(tmp_path)
    kept, gone = claim("lab/alpha"), claim("lab/beta")
    queue.file(kept, at=AT)
    queue.file(gone, at=AT)
    before = lines(tmp_path)
    queue.retire(gone.target, at=AT + timedelta(seconds=1), reason="no_data_row")
    after = lines(tmp_path)
    assert after[:len(before)] == before and len(after) == len(before) + 1
    assert json.loads(after[-1]) == {
        "event": "retired", "at": (AT + timedelta(seconds=1)).isoformat(),
        "target": {"kind": "fact", "id": gone.target.id}, "reason": "no_data_row"}
    assert set(queue.filed()) == {("fact", kept.target.id)}
    pending, unknown = queue.pending()
    assert [c.target.id for c in pending] == [kept.target.id] and unknown == []
    assert queue.recrawl_requests() == []


def test_a_later_collected_files_a_retired_target_again(tmp_path):
    queue = verify.Queue(tmp_path)
    queue.file(claim(), at=AT)
    queue.retire("fact:" + claim().target.id, at=AT + timedelta(seconds=1), reason="no_data_row")
    queue.file(claim(value=256000), at=AT + timedelta(seconds=2))
    assert queue.filed()[("fact", claim().target.id)].value == 256000


def test_retire_refuses_an_unknown_reason(tmp_path):
    with pytest.raises(ValueError):
        verify.Queue(tmp_path).retire(claim().target, at=AT, reason="page said so")
    assert not (tmp_path / "queue" / "events.jsonl").exists()


def test_accuracy_draws_skip_a_retired_claim(tmp_path):
    queue = verify.Queue(tmp_path)
    queue.file(claim("lab/alpha"), at=AT)
    queue.file(claim("lab/beta"), at=AT)
    path = tmp_path / "queue" / "events.jsonl"
    assert len(accuracy._latest_collected_claims(path)) == 2
    queue.retire(claim("lab/beta").target, at=AT + timedelta(seconds=1), reason="no_data_row")
    assert [c.target.id for c in accuracy._latest_collected_claims(path)] == [
        claim("lab/alpha").target.id]
    queue.file(claim("lab/beta"), at=AT + timedelta(seconds=2))
    assert len(accuracy._latest_collected_claims(path)) == 2


@pytest.fixture
def data(tmp_path, monkeypatch):
    queue = verify.Queue(tmp_path / "verification")
    queue.file(claim("lab/alpha"), at=AT)
    queue.file(claim("lab/beta"), at=AT)
    monkeypatch.setattr(retire_claims, "data_rows",
                        lambda root: {("fact", claim("lab/alpha").target.id)})
    return tmp_path


def test_script_dry_run_writes_nothing(data, capsys):
    before = lines(data / "verification")
    assert retire_claims.main(["--root", str(data), "--target",
                               "fact:" + claim("lab/beta").target.id]) == 0
    assert lines(data / "verification") == before
    assert "would be retired" in capsys.readouterr().out


def test_script_writes_one_retired_event_per_target(data):
    before = lines(data / "verification")
    assert retire_claims.main(["--root", str(data), "--write", "--target",
                               "fact:" + claim("lab/beta").target.id]) == 0
    after = lines(data / "verification")
    assert after[:len(before)] == before and len(after) == len(before) + 1
    assert json.loads(after[-1])["event"] == "retired"


@pytest.mark.parametrize("ref", [
    "fact:" + claim("lab/alpha").target.id,  # a data row still holds it
    "fact:lab/gamma#model.context_window",   # no filed claim
    "lab/beta#model.context_window",          # not a verification ref
])
def test_script_refuses_the_whole_run(data, ref, capsys):
    before = lines(data / "verification")
    assert retire_claims.main(["--root", str(data), "--write", "--target",
                               "fact:" + claim("lab/beta").target.id, "--target", ref]) == 1
    assert lines(data / "verification") == before
    assert "nothing written" in capsys.readouterr().err
