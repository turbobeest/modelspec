"""MODEL-551: the owner's ruling past a recorded rule-15 disagreement, and its bypasses.

Synthetic data only: a planted offering on a cite-only host, attempts made through the
real gate with stub readers, and a snapshot built from synthetic records.
"""

import json
import socket
from datetime import UTC, date, datetime, timedelta

import pytest
import yaml

from decision.cited_change import _gate, cited_change
from decision.cited_reader import ATTEMPTS_FILE, log_attempt
from decision.owner_ruling import (
    FIELDS,
    OWNERS,
    RULINGS_FILE,
    admits,
    attempt_id,
    disagreed,
    fact_epoch,
    ruling_problem,
)
from scripts import file_owner_ruling as filer
from tests.test_cited_offering import (
    FACT_ID,
    HEADER,
    SOC2_ID,
    SUBJECT,
    URL,
    Data,
    pair,
    plant,
    reader,
    refused,
    serve,
)

RETENTION = "offering.data.retention"
SOC2 = "offering.attestation.soc2"
OTHER_SUBJECT = "openai/openai/gpt-x/eu/standard"
TODAY = datetime.now(UTC).date().isoformat()


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def disagree(facet=RETENTION, **kw):
    """One real readers_disagree attempt through the gate."""
    if facet == RETENTION:
        out = cited_change(subject=SUBJECT, facet=RETENTION, source_id="data",
                           readers=pair(30, "unbounded"), request=serve(), **kw)
    else:
        out = cited_change(subject=SUBJECT, facet=SOC2, source_id="trust",
                           readers=[reader("codex", "openai", "type_2"),
                                    reader("claude", "anthropic", None)], request=serve(),
                           accept_not_disclosed=True, **kw)
    refused(out, "readers_disagree")


def args(**kw):
    base = dict(subject=SUBJECT, facet=RETENTION, value=30, state="known", ruled_by="jamie",
                ruled_at=TODAY, ticket="MODEL-1", source_ids=["data"],
                basis="day counts near retention wording: 1, equal to the value")
    base.update(kw)
    return base


def file(data, **kw):
    result = filer.plan(data_dir=data.root, **args(**kw))
    filer.apply(result)
    return result


def refuses(data, reason, **kw):
    before = state(data)
    with pytest.raises(filer.Refused) as caught:
        file(data, **kw)
    assert caught.value.reason == reason, (caught.value.reason, caught.value.detail)
    assert state(data) == before  # nothing written
    return caught.value


def state(data):
    paths = [RULINGS_FILE, "verification/queue/events.jsonl", ATTEMPTS_FILE,
             "verification/log.jsonl", "offerings/openai/openai/gpt-x.yaml"]
    return {p: (data.root / p).read_bytes() if (data.root / p).exists() else None for p in paths}


def rulings(data):
    path = data.root / RULINGS_FILE
    return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


def offering_fact(data, fact_id=FACT_ID):
    rows = yaml.safe_load(data.offering_path.read_text())
    return next(f for r in rows for f in r["facts"] if f["id"] == fact_id)


def urls(data):
    return {s["id"]: s["url"] for s in data.sources}


def attempts(data):
    return data.log()


# --- the filer, when every condition holds -------------------------------------------------------


def test_a_ruling_files_the_line_the_claim_and_the_fact_from_one_reference(data):
    disagree()
    file(data)
    [line] = rulings(data)
    assert set(line) == set(FIELDS) and line["ruled_by"] in OWNERS
    [attempt] = attempts(data)
    assert line["resolves"] == [attempt_id(attempt)] and line["source_ids"] == ["data"]
    fact = offering_fact(data)
    assert (fact["value"], fact["state"]) == (30, "known")
    assert fact["derivation"] == {"owner_ruling": line}
    [ref] = fact["sources"]
    assert ref["snapshot_ref"] == f"sha256:{attempt['page_sha256']}"
    collected, checked = data.events()
    assert collected["event"] == "collected" and checked["outcome"] == "cited"
    claim = collected["claim"]
    assert claim["target"] == {"kind": "fact", "id": FACT_ID} and claim["value"] == 30
    [claimed] = claim["sources"]
    assert claimed["snapshot_ref"] == ref["snapshot_ref"]
    assert datetime.fromisoformat(claimed["retrieved_at"].replace("Z", "+00:00")) == \
        datetime.fromisoformat(str(ref["retrieved_at"]).replace("Z", "+00:00"))
    # every other byte of the offering file is kept: its comment and the other fact
    text = data.offering_path.read_text()
    assert text.startswith(HEADER)
    assert offering_fact(data, SOC2_ID)["value"] == "type_2"
    assert fact_epoch(fact) == "initial"
    # no verification record and no attempt are written
    assert not (data.root / "verification/log.jsonl").exists() and len(attempts(data)) == 1
    assert admits(fact, SUBJECT, rulings=rulings(data), attempts=attempts(data), sources=urls(data))


def test_a_not_disclosed_ruling_and_the_soc2_kind(data):
    disagree(SOC2)
    file(data, facet=SOC2, value=None, state="not_disclosed", source_ids=["trust"])
    fact = offering_fact(data, SOC2_ID)
    assert (fact["value"], fact["state"]) == (None, "not_disclosed")
    assert fact["sources"][0]["source_id"] == "trust"


def test_the_dry_run_cli_writes_nothing_and_prints_no_page_text(data, capsys):
    disagree()
    before = state(data)
    code = filer.main(["--data-dir", str(data.root), "--subject", SUBJECT, "--facet", RETENTION,
                       "--value", "30", "--state", "known", "--ruled-by", "jamie",
                       "--ruled-at", TODAY, "--ticket", "MODEL-1", "--source", "data",
                       "--basis", "counts only"])
    out = capsys.readouterr().out
    assert code == 0 and json.loads(out)["outcome"] == "planned"
    assert "SECRET-PAGE-MARKER" not in out and state(data) == before


# --- the bypasses --------------------------------------------------------------------------------


def test_a_ruling_with_no_disagreement_is_refused(data):
    refuses(data, "no_disagreement")
    # an agreed attempt is not a disagreement either
    assert cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                        request=serve()).changed
    refuses(data, "no_disagreement")


def test_an_incomplete_attempt_is_not_a_disagreement(data):
    log_attempt({"subject": SUBJECT, "facet": RETENTION, "epoch": "initial", "url": URL,
                 "complete": False, "agreed": None, "page_sha256": "a" * 64,
                 "at": "2026-11-01T00:00:00+00:00", "readers": [{"value": 30}]})
    refuses(data, "no_disagreement")


def test_a_disagreement_in_another_epoch_is_refused(data):
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                  readers=pair(30, "unbounded"), request=serve(), allow_unchanged=False,
                  epoch="reread:" + "b" * 64), "readers_disagree")
    refuses(data, "no_disagreement")  # the ruling is for the initial epoch
    refuses(data, "epoch_not_current", epoch="reread:" + "b" * 64)  # the fact is not there
    other = attempt_id(attempts(data)[0])
    refuses(data, "no_disagreement", resolves=[other])  # named explicitly, still another epoch


@pytest.mark.parametrize("who", ["alice", "Jamie", "jamie ", "", "orchestrator"])
def test_a_non_owner_ruling_is_refused(data, who):
    disagree()
    refuses(data, "not_owner", ruled_by=who)


def test_a_ruling_needs_a_ticket(data):
    disagree()
    refuses(data, "no_ticket", ticket="")
    refuses(data, "no_ticket", ticket="see chat")


def test_a_quarantined_fact_is_refused_and_the_message_says_why(data):
    disagree()
    plant(data, FACT_ID, "mismatch", None)
    refusal = refuses(data, "quarantined")
    assert "owner's open question" in refusal.detail


@pytest.mark.parametrize("kw", [
    dict(value="thirty"), dict(value=[30]), dict(value=True), dict(value=None),
    dict(value=30, state="not_disclosed"), dict(value=30, state="unknown"),
    dict(facet=SOC2, value="type_3", source_ids=["trust"]),
])
def test_a_value_of_the_wrong_type_is_refused(data, kw):
    disagree()
    disagree(SOC2)
    refuses(data, "value_invalid", **kw)


def test_a_ruling_for_subject_a_is_not_a_ruling_for_subject_b(data):
    disagree()
    data.facts.append({"id": f"{OTHER_SUBJECT}#{RETENTION}",
                       "subject": {"kind": "offering", "id": OTHER_SUBJECT},
                       "facet": RETENTION, "value": None, "state": "not_disclosed",
                       "sources": [{"source_id": "data", "snapshot_ref": "sha256:" + "0" * 64,
                                    "cited_regions": ["page"]}]})
    rows = [{"model": "openai/gpt-x", "provider": "openai", "region": "global",
             "tier": "standard", "facts": data.facts[:2]},
            {"model": "openai/gpt-x", "provider": "openai", "region": "eu",
             "tier": "standard", "facts": data.facts[2:]}]
    data.offering_path.write_text(HEADER + yaml.safe_dump(rows, sort_keys=False))
    a_attempt = attempt_id(attempts(data)[0])
    refuses(data, "no_disagreement", subject=OTHER_SUBJECT)
    refuses(data, "no_disagreement", subject=OTHER_SUBJECT, resolves=[a_attempt])
    # the build: A's ruled fact copied onto B, or moved there with A's stored id, admits nothing
    file(data)
    ruled = offering_fact(data)
    keep = dict(rulings=rulings(data), attempts=attempts(data), sources=urls(data))
    assert admits(ruled, SUBJECT, **keep)
    copied = {**ruled, "id": f"{OTHER_SUBJECT}#{RETENTION}",
              "subject": {"kind": "offering", "id": OTHER_SUBJECT}}
    assert not admits(copied, OTHER_SUBJECT, **keep)
    assert not admits(ruled, OTHER_SUBJECT, **keep)  # moved, stored id kept


def test_a_renamed_or_moved_fact_id_is_refused(data):
    disagree()
    old = f"openai/openai/gpt-x/old-region/standard#{RETENTION}"
    data.fact(id=old)
    refuses(data, "fact_id_mismatch")
    data.fact(old, id=FACT_ID, subject={"kind": "offering", "id": OTHER_SUBJECT})
    refuses(data, "fact_id_mismatch")


def test_a_ruled_fact_under_a_renamed_id_is_not_admitted(data):
    disagree()
    file(data)
    ruled = offering_fact(data)
    keep = dict(rulings=rulings(data), attempts=attempts(data), sources=urls(data))
    assert not admits({**ruled, "id": f"{SUBJECT}#renamed"}, SUBJECT, **keep)
    assert not admits({**ruled, "facet": SOC2}, SUBJECT, **keep)


def test_a_hand_added_value_with_no_ruling_line_is_not_admitted(data):
    disagree()
    file(data)
    ruled = offering_fact(data)
    keep = dict(attempts=attempts(data), sources=urls(data))
    assert not admits(ruled, SUBJECT, rulings=[], **keep)  # block, no line
    assert not admits({**ruled, "value": 31}, SUBJECT, rulings=rulings(data), **keep)
    assert not admits({**ruled, "state": "not_disclosed", "value": None}, SUBJECT,
                      rulings=rulings(data), **keep)
    # a block edited by hand to another value no longer is the filed line
    edited = json.loads(json.dumps(ruled))
    edited["derivation"]["owner_ruling"]["value"] = 31
    edited["value"] = 31
    assert not admits(edited, SUBJECT, rulings=rulings(data), **keep)
    # a ruling line added by hand that resolves no logged attempt is no ruling
    forged = {**rulings(data)[0], "resolves": ["sha256:" + "c" * 64]}
    assert ruling_problem(forged, **keep)[0] == "no_disagreement"
    # a hand-edited source copy is not the copy the readers read
    moved = json.loads(json.dumps(ruled))
    moved["sources"][0]["snapshot_ref"] = "sha256:" + "d" * 64
    assert not admits(moved, SUBJECT, rulings=rulings(data), **keep)


def test_a_duplicate_ruling_is_refused(data):
    disagree()
    file(data)
    refuses(data, "duplicate_ruling")  # the same ruling again: applied already
    refuses(data, "duplicate_ruling", value=31)  # another ruling on the same key
    # two lines for one key admit neither
    line = rulings(data)[0]
    keep = dict(attempts=attempts(data), sources=urls(data))
    assert not admits(offering_fact(data), SUBJECT, rulings=[line, line], **keep)


def test_append_only_a_changed_file_since_planning_writes_nothing(data):
    disagree()
    (data.root / RULINGS_FILE).write_text(json.dumps({"other": 1}) + "\n")
    junk = {RULINGS_FILE: json.dumps({"x": 1}) + "\n",
            "verification/queue/events.jsonl": json.dumps(
                {"event": "checked", "at": "2026-01-01T00:00:00+00:00", "outcome": "cited",
                 "diff": [], "target": {"kind": "fact", "id": "other#x"}}) + "\n",
            "offerings/openai/openai/gpt-x.yaml": "# changed\n"}
    for path, line in junk.items():
        result = filer.plan(data_dir=data.root, **args())
        target = data.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a") as handle:
            handle.write(line)
        before = state(data)
        with pytest.raises(filer.Refused) as caught:
            filer.apply(result)
        assert caught.value.reason == "changed_since_planning"
        assert state(data) == before


def test_append_only_earlier_lines_are_kept_and_a_stopped_write_finishes(data, monkeypatch):
    disagree()
    disagree(SOC2)
    earlier = json.dumps({"kept": True}, sort_keys=True) + "\n"
    (data.root / RULINGS_FILE).write_text(earlier)
    events = data.root / "verification/queue/events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    events.write_text("")
    attempts_before = (data.root / ATTEMPTS_FILE).read_bytes()
    # the ruling line lands, then the write stops before the claim and the fact
    monkeypatch.setattr(filer, "write_atomic", lambda *a: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(OSError):
        file(data)
    assert len(rulings(data)) == 2 and len(data.events()) == 2
    monkeypatch.undo()
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(data.root))
    file(data)  # the rerun finishes: no second line, no second claim
    assert (data.root / RULINGS_FILE).read_text().startswith(earlier)
    assert len(rulings(data)) == 2 and len(data.events()) == 2
    assert offering_fact(data)["value"] == 30
    file(data, facet=SOC2, value="type_2", source_ids=["trust"])
    assert len(rulings(data)) == 3 and (data.root / RULINGS_FILE).read_text().startswith(earlier)
    assert (data.root / ATTEMPTS_FILE).read_bytes() == attempts_before


def test_the_claim_is_the_latest_even_after_a_later_dated_event(data):
    disagree()
    events = data.root / "verification/queue/events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    soon = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    events.write_text(json.dumps({"event": "checked", "at": soon, "outcome": "cited", "diff": [],
                                  "target": {"kind": "fact", "id": FACT_ID}}) + "\n")
    file(data)
    collected = [e for e in data.events() if e["event"] == "collected"]
    assert datetime.fromisoformat(collected[-1]["at"]) >= datetime.fromisoformat(soon)


def test_a_future_dated_queue_event_is_refused(data):
    disagree()
    events = data.root / "verification/queue/events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    later = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    events.write_text(json.dumps({"event": "checked", "at": later, "outcome": "cited", "diff": [],
                                  "target": {"kind": "fact", "id": FACT_ID}}) + "\n")
    refuses(data, "queue_ahead")


@pytest.mark.parametrize("kw", [
    dict(basis=""), dict(basis="x" * 401), dict(basis="see https://example.com"),
    dict(basis="two\nlines"),
])
def test_the_basis_is_short_one_line_and_carries_no_url(data, kw):
    disagree()
    refuses(data, "basis_invalid", **kw)


def test_a_ruling_date_before_the_attempt_or_in_the_future_is_refused(data):
    disagree()
    refuses(data, "bad_ruling_date", ruled_at="2020-01-01")
    refuses(data, "bad_ruling_date", ruled_at=(date.today() + timedelta(days=3)).isoformat())
    refuses(data, "bad_ruling_date", ruled_at="25 Nov")


def test_the_sources_must_be_the_pages_the_readers_read(data):
    disagree()
    refuses(data, "source_mismatch", source_ids=["trust"])
    refuses(data, "source_mismatch", source_ids=["data", "trust"])
    refuses(data, "source_mismatch", source_ids=["hf"])  # a retaining host


def test_disagreed_reads_only_a_complete_split():
    base = {"complete": True, "agreed": False,
            "readers": [{"value": 30}, {"value": "unbounded"}]}
    assert disagreed(base, RETENTION)
    assert not disagreed({**base, "agreed": True}, RETENTION)
    assert not disagreed({**base, "complete": False}, RETENTION)
    assert not disagreed({**base, "readers": [{"value": 30}, {"value": 30.0}]}, RETENTION)
    assert not disagreed({**base, "readers": [{"value": 30}]}, RETENTION)


# --- gate integration ----------------------------------------------------------------------------


def test_after_a_ruling_the_epoch_still_blocks_readers_and_a_new_epoch_is_normal(data):
    disagree()
    file(data)
    # the same epoch: a later agreement on another value is still blocked
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                         request=serve()), "prior_attempt_disagreed")
    # a fresh agreement in a new epoch follows the normal rules and supersedes the ruling
    out = _gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                request=serve(), allow_unchanged=False, epoch="reread:" + "e" * 64)
    assert out.changed and out.record["value"] == 45 and out.record["state"] == "known"
    assert "owner_ruling" not in out.record["derivation"]
    # and a disagreement in that new epoch blocks only it
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                  readers=[reader("codex", "openai", 45), reader("claude", "anthropic", 46)],
                  request=serve(), allow_unchanged=False,
                  epoch="reread:" + "f" * 64), "readers_disagree")


# --- the build: a valid ruling admits that epoch's value, served as any cited fact ---------------


CITE = "https://www.perplexity.ai/pro"
MID, FACET = "lab/alpha", "model.context_window"
PAGE_SHA = "9" * 64
AT = "2026-10-10T08:00:00+00:00"


def _attempt(subject=MID, facet=FACET, epoch="initial", values=(128000, 262144)):
    return {"subject": subject, "facet": facet, "epoch": epoch, "url": CITE, "complete": True,
            "agreed": False, "agreed_value": None, "harness": True, "page_sha256": PAGE_SHA,
            "prompt_sha256": "8" * 64, "at": AT,
            "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": values[0]},
                        {"reader_id": "b", "family": "anthropic", "version": "1",
                         "value": values[1]}]}


def _ruling(attempt, **kw):
    line = {"subject": MID, "facet": FACET, "epoch": "initial", "value": 262144, "state": "known",
            "ruled_by": "jamie", "ruled_at": "2026-10-12", "ticket": "MODEL-1",
            "source_ids": ["src-cite"], "resolves": [attempt_id(attempt)],
            "basis": "token counts near the context wording: 1, equal to the value"}
    line.update(kw)
    return line


def _ruled_fact(ruling, **kw):
    from tests.snapshot_records import fact

    row = fact("model", MID, FACET, ruling["value"], source="src-cite", outcome=None)
    row["sources"] = [{"source_id": "src-cite", "snapshot_ref": f"sha256:{PAGE_SHA}",
                       "retrieved_at": AT, "cited_regions": ["page"]}]
    row["derivation"] = {"owner_ruling": dict(ruling)}
    row.update(kw)
    return row


def _build(row, rulings, attempts):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
    from tests.snapshot_records import SOURCES, model

    inputs = SnapshotInputs(models=[model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE},
                            owner_rulings=list(rulings), cited_attempts=list(attempts))
    return load_built_snapshot(build_snapshot(inputs, as_of=date(2026, 10, 19)))


def test_the_build_admits_a_ruled_fact_as_an_ordinary_cited_fact():
    attempt = _attempt()
    ruling = _ruling(attempt)
    index = _build(_ruled_fact(ruling), [ruling], [attempt])
    shown = index.fact(MID, FACET)
    assert shown.state == "known" and shown.value == 262144
    record = index.record(shown.record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    assert "derivation" not in record  # the ruling is internal: nothing outward names it
    assert "owner_ruling" not in json.dumps(record)


@pytest.mark.parametrize("case", [
    "no_line", "other_subject", "other_facet", "other_epoch", "non_owner", "agreed_attempt",
    "hand_value", "two_lines", "retained_source", "before_attempt",
])
def test_the_build_keeps_out_a_ruled_fact_whose_ruling_does_not_stand(case):
    attempt = _attempt()
    ruling = _ruling(attempt)
    row, rulings, attempts = _ruled_fact(ruling), [ruling], [attempt]
    if case == "no_line":
        rulings = []
    elif case == "other_subject":
        other = _attempt(subject="lab/beta")
        rulings = [_ruling(other, subject="lab/beta")]
        attempts = [other]
        row = _ruled_fact(rulings[0])
    elif case == "other_facet":
        other = _attempt(facet="licence.user_cap", values=("unbounded", 5))
        rulings = [_ruling(other, facet="licence.user_cap", value="unbounded")]
        attempts = [attempt, other]
        row["derivation"]["owner_ruling"] = rulings[0]
    elif case == "other_epoch":
        other = _attempt(epoch="reread:" + "a" * 64)
        rulings = [_ruling(other, epoch="reread:" + "a" * 64)]
        attempts = [other]
        row = _ruled_fact(rulings[0] | {"epoch": "initial"})
    elif case == "non_owner":
        rulings = [_ruling(attempt, ruled_by="alice")]
        row = _ruled_fact(rulings[0])
    elif case == "agreed_attempt":
        agreed = _attempt(values=(262144, 262144)) | {"agreed": True, "agreed_value": 262144}
        attempts = [agreed]
        rulings = [_ruling(agreed)]
        row = _ruled_fact(rulings[0])
    elif case == "hand_value":
        row = _ruled_fact(ruling, value=300000)
    elif case == "two_lines":
        rulings = [ruling, ruling]
    elif case == "retained_source":
        row["sources"][0]["source_id"] = "src-lab-docs"
    elif case == "before_attempt":
        rulings = [_ruling(attempt, ruled_at="2026-10-01")]
        row = _ruled_fact(rulings[0])
    index = _build(row, rulings, attempts)
    assert index.fact(MID, FACET).state == "unknown"


def test_a_fact_with_no_ruling_block_is_untouched_by_the_rulings():
    from tests.snapshot_records import fact

    attempt = _attempt()
    row = fact("model", MID, FACET, 128000, source="src-cite", outcome=None)
    index = _build(row, [_ruling(attempt)], [attempt])
    assert index.fact(MID, FACET).value == 128000


def test_without_the_block_each_kept_out_fact_would_enter_so_the_ruling_check_is_what_holds():
    from tests.snapshot_records import fact

    attempt = _attempt()
    row = _ruled_fact(_ruling(attempt), value=300000)
    assert _build(row, [], [attempt]).fact(MID, FACET).state == "unknown"
    row.pop("derivation")
    assert _build(row, [], [attempt]).fact(MID, FACET).value == 300000  # rule 14, as before
    assert fact("model", MID, FACET, 1, source="src-cite", outcome=None).get("derivation") is None


# --- a card fact ---------------------------------------------------------------------------------


CARD_SUBJECT = "openai/gpt-x"
CARD = "models/openai/gpt-x.md"


def test_a_card_fact_is_ruled_with_its_front_matter_and_body_kept(data):
    front = {"model_id": CARD_SUBJECT, "display_name": "GPT X", "facts": [
        {"facet": "model.context_window", "value": 128000, "state": "known",
         "sources": [{"source_id": "data", "snapshot_ref": "sha256:" + "0" * 64,
                      "cited_regions": ["page"]}]},
        {"facet": "model.weights_openness", "value": "closed_weights", "state": "known",
         "sources": [{"source_id": "data", "snapshot_ref": "sha256:" + "0" * 64,
                      "cited_regions": ["page"]}]}]}
    body = "\n# GPT X\n\nProse the writer keeps.\n"
    (data.root / CARD).write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body)
    log_attempt({"subject": CARD_SUBJECT, "facet": "model.context_window", "epoch": "initial",
                 "url": URL, "complete": True, "agreed": False, "agreed_value": None,
                 "harness": True, "page_sha256": "7" * 64, "at": "2026-11-01T00:00:00+00:00",
                 "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 1},
                             {"reader_id": "b", "family": "anthropic", "version": "1",
                              "value": 2}]})
    file(data, subject=CARD_SUBJECT, facet="model.context_window", value=262144)
    text = (data.root / CARD).read_text()
    assert text.endswith("---\n" + body)
    after = yaml.safe_load(text.split("---", 2)[1])
    ruled, other = after["facts"]
    assert (ruled["value"], ruled["sources"][0]["snapshot_ref"]) == (262144, "sha256:" + "7" * 64)
    assert other == front["facts"][1] and after["display_name"] == "GPT X"
    [collected, _] = data.events()
    assert collected["claim"]["target"]["id"] == f"{CARD_SUBJECT}#model.context_window"
    assert {s["source_id"] for s in collected["claim"]["sources"]} == {"data"}
