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


ALPHA, BETA = claim("lab/alpha"), claim("lab/beta")


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A data checkout where only lab/alpha's fact still has a data row."""
    (tmp_path / "models").mkdir()
    monkeypatch.setattr(verify, "data_row_targets", lambda root: {("fact", ALPHA.target.id)})
    queue = verify.Queue(tmp_path / "verification")
    queue.file(ALPHA, at=AT)
    queue.file(BETA, at=AT)
    return tmp_path


def lines(root):
    return (root / "verification" / "queue" / "events.jsonl").read_text(encoding="utf-8").splitlines()


def test_retired_claim_is_not_filed_pending_or_recrawled(root):
    queue = verify.Queue(root / "verification")
    before = lines(root)
    queue.retire(BETA.target, at=AT + timedelta(seconds=1), reason="no_data_row")
    after = lines(root)
    assert after[:len(before)] == before and len(after) == len(before) + 1
    assert json.loads(after[-1]) == {
        "event": "retired", "at": (AT + timedelta(seconds=1)).isoformat(),
        "target": {"kind": "fact", "id": BETA.target.id}, "reason": "no_data_row"}
    assert set(queue.filed()) == {("fact", ALPHA.target.id)}
    pending, unknown = queue.pending()
    assert [c.target.id for c in pending] == [ALPHA.target.id] and unknown == []
    assert queue.recrawl_requests() == []


def test_a_later_collected_files_a_retired_target_again(root):
    queue = verify.Queue(root / "verification")
    queue.retire("fact:" + BETA.target.id, at=AT + timedelta(seconds=1), reason="no_data_row")
    queue.file(claim("lab/beta", value=256000), at=AT + timedelta(seconds=2))
    assert queue.filed()[("fact", BETA.target.id)].value == 256000


@pytest.mark.parametrize("targets,reason", [
    ([BETA.target], "page said so"),                      # not a fixed reason code
    ([ALPHA.target], "no_data_row"),                      # a data row still holds it
    ([TargetRef(kind="fact", id="lab/gamma#model.context_window")], "no_data_row"),  # unfiled
    ([BETA.target, ALPHA.target], "no_data_row"),         # one bad target refuses all
    ([BETA.target, BETA.target], "no_data_row"),          # named twice
    ([], "no_data_row"),                                  # nothing named
])
def test_queue_retire_refuses_and_appends_nothing(root, targets, reason):
    before = lines(root)
    with pytest.raises(ValueError):
        verify.Queue(root / "verification").retire(targets, at=AT, reason=reason)
    assert lines(root) == before


def test_queue_retire_refuses_outside_a_data_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, "data_row_targets", lambda root: set())
    queue = verify.Queue(tmp_path / "verification")
    queue.file(BETA, at=AT)
    with pytest.raises(ValueError, match="models directory"):
        queue.retire(BETA.target, at=AT, reason="no_data_row")


def test_queue_retire_checks_the_checkout_it_writes_to(root, tmp_path_factory, monkeypatch):
    """Rows come from the queue's own checkout: another root is refused (MODEL-557)."""
    other = tmp_path_factory.mktemp("other")
    (other / "models").mkdir()
    seen = []
    monkeypatch.setattr(verify, "data_row_targets", lambda r: seen.append(r) or set())
    queue = verify.Queue(root / "verification")
    before = lines(root)
    with pytest.raises(ValueError, match="not the checkout"):
        queue.retire(ALPHA.target, at=AT, reason="no_data_row", root=other)
    assert lines(root) == before and seen == []
    queue.retire(BETA.target, at=AT, reason="no_data_row", root=root)
    assert seen == [root.resolve()]


def test_queue_retire_refuses_a_queue_outside_verification(root):
    with pytest.raises(ValueError, match="verification"):
        verify.Queue(root / "elsewhere").retire(BETA.target, at=AT, reason="no_data_row")


def test_accuracy_draws_skip_a_retired_claim(root):
    queue = verify.Queue(root / "verification")
    path = root / "verification" / "queue" / "events.jsonl"
    assert len(accuracy._latest_collected_claims(path)) == 2
    queue.retire(BETA.target, at=AT + timedelta(seconds=1), reason="no_data_row")
    assert [c.target.id for c in accuracy._latest_collected_claims(path)] == [ALPHA.target.id]
    queue.file(BETA, at=AT + timedelta(seconds=2))
    assert len(accuracy._latest_collected_claims(path)) == 2


def test_accuracy_orders_events_as_the_queue_does(root):
    """A backdated retirement on a later line never hides a newer claim (MODEL-557)."""
    path = root / "verification" / "queue" / "events.jsonl"
    queue = verify.Queue(root / "verification")
    queue.file(claim("lab/beta", value=256000), at=AT + timedelta(minutes=5))
    # Appended after the newer claim, but dated before it.
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "retired", "at": (AT + timedelta(minutes=1)).isoformat(),
                             "target": {"kind": "fact", "id": BETA.target.id},
                             "reason": "no_data_row"}) + "\n")
    drawn = {c.target.id: c.value for c in accuracy._latest_collected_claims(path)}
    assert drawn[BETA.target.id] == 256000
    assert queue.filed()[("fact", BETA.target.id)].value == 256000
    # A claim line dated earlier than one above it is still the older claim.
    queue.file(claim("lab/alpha", value=1), at=AT - timedelta(days=1))
    drawn = {c.target.id: c.value for c in accuracy._latest_collected_claims(path)}
    assert drawn[ALPHA.target.id] == ALPHA.value == queue.filed()[("fact", ALPHA.target.id)].value


def test_script_dry_run_writes_nothing(root, capsys):
    before = lines(root)
    assert retire_claims.main(["--root", str(root), "--target", "fact:" + BETA.target.id]) == 0
    assert lines(root) == before
    assert "would be retired" in capsys.readouterr().out


def test_script_writes_one_retired_event_per_target(root):
    before = lines(root)
    assert retire_claims.main(["--root", str(root), "--write", "--target",
                               "fact:" + BETA.target.id]) == 0
    after = lines(root)
    assert after[:len(before)] == before and len(after) == len(before) + 1
    assert json.loads(after[-1])["event"] == "retired"


@pytest.mark.parametrize("ref", [
    "fact:" + ALPHA.target.id,               # a data row still holds it
    "fact:lab/gamma#model.context_window",   # no filed claim
    "lab/beta#model.context_window",          # not a verification ref
])
def test_script_refuses_the_whole_run(root, ref, capsys):
    before = lines(root)
    assert retire_claims.main(["--root", str(root), "--write", "--target",
                               "fact:" + BETA.target.id, "--target", ref]) == 1
    assert lines(root) == before
    assert "nothing written" in capsys.readouterr().err
