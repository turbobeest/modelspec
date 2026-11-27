"""MODEL-551: the owner's ruling past a recorded rule-15 disagreement, and its bypasses.

Synthetic data only: a planted offering on a cite-only host, attempts made through the
real gate with stub readers, and a snapshot built from synthetic records.
"""

import json
import shutil
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
    blocks_rule_15,
    disagreed,
    fact_epoch,
    ruling_problem,
    split_status,
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
    ref,
    refused,
    serve,
)


@pytest.fixture(autouse=True)
def legacy_log(monkeypatch):
    """Each test's own attempt log is its pinned legacy prefix (``tests.legacy_pin``)."""
    from tests.legacy_pin import pin_whole_log

    pin_whole_log(monkeypatch)


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
    """One real readers_disagree attempt through the gate, which fetches the page itself with
    its own transport (stubbed), so the attempt records ``own_fetch``."""
    import decision.cited_change as gate_module

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(gate_module, "_http_once", serve())
        if facet == RETENTION:
            out = cited_change(subject=SUBJECT, facet=RETENTION, source_id="data",
                               readers=pair(30, "unbounded"), **kw)
        else:
            out = cited_change(subject=SUBJECT, facet=SOC2, source_id="trust",
                               readers=[reader("codex", "openai", "type_2"),
                                        reader("claude", "anthropic", None)],
                               accept_not_disclosed=True, **kw)
    refused(out, "readers_disagree")


def own_gate(**kw):
    """The gate, fetching the page itself with its own transport (stubbed): ``own_fetch``."""
    import decision.cited_change as gate_module

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(gate_module, "_http_once", serve())
        return _gate(request=None, **kw)


def read_in(epoch, readers):
    """A real harness read logged in ``epoch`` (``decision.cited_reader.read_page``). The gate
    reads only in the filed fact's own epoch (MODEL-558), so an attempt in another epoch, as a
    past re-read left it, is made through the harness, not by naming an epoch to the gate."""
    from decision.cited_change import lookup
    from decision.cited_reader import read_page
    from tests.test_cited_offering import PAGE

    found = lookup(SUBJECT, RETENTION)
    return read_page(subject=SUBJECT, url=URL, facet_id=RETENTION,
                     subject_name=found.subject_name, page_bytes=PAGE, readers=readers,
                     epoch=epoch, definition=found.definition, own_fetch=True)


def enter_epoch(data, text_sha):
    """Put the filed fact in the re-read epoch ``reread:<text_sha>``, as a re-read of a changed
    page does: the fact's cited-change block names the text hash the readers read."""
    rows = yaml.safe_load(data.offering_path.read_text())
    for row in rows:
        for fact in row.get("facts") or []:
            if fact.get("id") == FACT_ID:
                derivation = dict(fact.get("derivation") or {})
                derivation["cited_change"] = {**(derivation.get("cited_change") or {}),
                                              "text_sha256": text_sha}
                fact["derivation"] = derivation
    data.offering_path.write_text(HEADER + yaml.safe_dump(rows, sort_keys=False))
    return "reread:" + text_sha


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


def claims(data):
    from decision.owner_ruling import latest_ruling_claims

    return latest_ruling_claims(data.root / "verification/queue/events.jsonl")


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
    assert fact["derivation"]["owner_ruling"] == line
    assert set(fact["derivation"]) == {"owner_ruling"}  # no earlier state is stored
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
    assert admits(fact, SUBJECT, rulings=rulings(data), attempts=attempts(data),
                  sources=urls(data), claims=claims(data))


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
    # The gate will not read in an epoch that is not the filed fact's own.
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                  readers=pair(30, "unbounded"), request=serve(), allow_unchanged=False,
                  epoch="reread:" + "b" * 64), "epoch_not_current")
    read_in("reread:" + "b" * 64, pair(30, "unbounded"))  # a past re-read's disagreement
    assert attempts(data)[-1]["agreed"] is False
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
    keep = dict(rulings=rulings(data), attempts=attempts(data), sources=urls(data),
                claims=claims(data))
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
    keep = dict(rulings=rulings(data), attempts=attempts(data), sources=urls(data),
                claims=claims(data))
    assert not admits({**ruled, "id": f"{SUBJECT}#renamed"}, SUBJECT, **keep)
    assert not admits({**ruled, "facet": SOC2}, SUBJECT, **keep)


def test_a_hand_added_value_with_no_ruling_line_is_not_admitted(data):
    disagree()
    file(data)
    ruled = offering_fact(data)
    keep = dict(attempts=attempts(data), sources=urls(data), claims=claims(data))
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
    assert ruling_problem(forged, attempts=keep["attempts"], sources=keep["sources"])[0] \
        == "no_disagreement"
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
    keep = dict(attempts=attempts(data), sources=urls(data), claims=claims(data))
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


def _readers(*values, families=("openai", "anthropic"), ids=("a", "b")):
    return [{"reader_id": i, "family": f, "version": "1", "value": v}
            for i, f, v in zip(ids, families, values)]


def test_disagreed_reads_only_a_real_rule_15_split():
    base = {"complete": True, "agreed": False, "harness": True, "page_sha256": "1" * 64,
            "prompt_sha256": "2" * 64, "readers": _readers(30, "unbounded")}
    assert disagreed(base, RETENTION)
    assert not disagreed({**base, "agreed": True}, RETENTION)
    assert not disagreed({**base, "complete": False}, RETENTION)
    assert not disagreed({**base, "readers": _readers(30, 30.0)}, RETENTION)
    assert not disagreed({**base, "readers": _readers(30)}, RETENTION)


# A seeded split (marked ``seeded``, ``harness`` false) is one the owner may rule past
# (MODEL-491); the gate blocks on it for good, as on a harness split.
RULABLE_SPLITS = [{"seeded": True, "harness": False},
                  {"seeded": True, "harness": False, "prompt_sha256": None}]
# Lines that look complete and not agreed but are not well formed: the gate fails closed and
# blocks on each, and no ruling resolves any (``split_status`` is "malformed").
MALFORMED_SPLITS = [
    {"harness": False},  # no seeded mark
    {"prompt_sha256": None},  # a harness line without the prompt hash its writer records
    {"seeded": True},  # seeded and harness at once
    {"complete": "false", "agreed": None, "readers": None, "harness": None},  # a forged string
    {"complete": 1}, {"agreed": None}, {"agreed": 0},
    {"readers": _readers(30, "unbounded", families=("openai", "openai"))},
    {"readers": _readers(30, "unbounded", families=("openai", "codex"))},  # one lineage
    {"readers": _readers(30, "unbounded", families=("unknown", "anthropic"))},
    {"readers": _readers(30, "unbounded", ids=("a", "a"))},
    {"readers": [{"value": 30}, {"value": "unbounded"}]},  # no identities
    {"readers": _readers(30, 30.0)},  # the gate's comparison tells them apart: no split
    {"readers": [*_readers(30, "unbounded"), {"reader_id": "c", "family": "google",
                                             "version": "1", "value": 1}]},
    {"page_sha256": "short"}, {"page_sha256": None}, {"at": None}, {"at": "2026-10-11T09:00:00"},
]


@pytest.mark.parametrize("change", RULABLE_SPLITS)
def test_a_fact_ruling_resolves_a_well_formed_seeded_split(change):
    attempt = {**_attempt(), **change}
    assert split_status(attempt, FACET) == "split" and blocks_rule_15(attempt)
    assert not disagreed(attempt, FACET)  # the MODEL-569 board test still refuses it
    ruling = _ruling(attempt)
    assert _build(_ruled_fact(ruling), [ruling], [attempt]).fact(MID, FACET).state == "known"


@pytest.mark.parametrize("change", MALFORMED_SPLITS)
def test_a_malformed_split_blocks_the_gate_but_no_ruling_resolves_it(change):
    attempt = {**_attempt(), **change}
    assert blocks_rule_15(attempt) and split_status(attempt, FACET) == "malformed"
    ruling = _ruling(attempt)
    assert _build(_ruled_fact(ruling), [ruling], [attempt]).fact(MID, FACET).state == "unknown"


@pytest.mark.parametrize("change", [{"complete": False}, {"complete": None}, {"agreed": True},
                                    {"agreed": 1}])
def test_a_line_the_gate_does_not_count_is_no_split(change):
    attempt = {**_attempt(), **change}
    assert not blocks_rule_15(attempt) and split_status(attempt, FACET) is None
    ruling = _ruling(attempt)
    assert _build(_ruled_fact(ruling), [ruling], [attempt]).fact(MID, FACET).state == "unknown"


AFTER_OWN_FETCH = "2026-11-27T03:00:00+00:00"  # after OWN_FETCH_SINCE


def test_a_harness_split_since_own_fetch_needs_the_gates_own_fetch():
    from decision.cited_reader import epoch_root

    # Ruled on 2026-11-27, so read and ruled in the facet's first epoch in force then (E6).
    first = epoch_root(FACET, "2026-11-27")
    caller_bytes = {**_attempt(epoch=first), "at": AFTER_OWN_FETCH}  # a caller's transport
    assert blocks_rule_15(caller_bytes) and split_status(caller_bytes, FACET) == "malformed"
    own = {**caller_bytes, "own_fetch": True}
    assert split_status(own, FACET) == "split"
    assert split_status({**caller_bytes, "own_fetch": "true"}, FACET) == "malformed"
    before = _attempt()  # logged before the harness recorded own_fetch: the earlier rule
    assert "own_fetch" not in before and split_status(before, FACET) == "split"
    for attempt, state in ((caller_bytes, "unknown"), (own, "known")):
        ruling = _ruling(attempt, ruled_at="2026-11-27", epoch=first)
        row, claim = _ruled_fact(ruling), _claim(ruling)
        row["sources"][0]["retrieved_at"] = claim["sources"][0]["retrieved_at"] = AFTER_OWN_FETCH
        assert _build(row, [ruling], [attempt], claims={f"{MID}#{FACET}": claim},
                      as_of=date(2026, 11, 27)).fact(MID, FACET).state == state


def test_a_split_read_through_a_callers_transport_blocks_but_cannot_be_ruled_on(data):
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data",
                         readers=pair(30, "unbounded"), request=serve()), "readers_disagree")
    assert "own_fetch" not in attempts(data)[-1]
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                         request=serve()), "prior_attempt_disagreed")
    refuses(data, "no_disagreement")


def _seed(epoch="initial", subject=SUBJECT, **kw):
    line = {"subject": subject, "facet": RETENTION, "epoch": epoch, "url": URL,
            "complete": True, "agreed": False, "harness": False, "seeded": True,
            "page_sha256": "a" * 64, "prompt_sha256": None,
            "at": "2026-11-01T00:00:00+00:00", "readers": _readers(30, "unbounded")}
    line.update(kw)
    log_attempt(line)
    return line


def test_a_seeded_split_blocks_the_gate_and_the_owner_rules_past_it(data):
    seeded = _seed()
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                         request=serve()), "prior_attempt_disagreed")
    file(data)
    [line] = rulings(data)
    assert line["resolves"] == [attempt_id(seeded)]
    fact = offering_fact(data)
    assert fact["value"] == 30 and fact["sources"][0]["snapshot_ref"] == "sha256:" + "a" * 64
    # The epoch still blocks the readers after the ruling.
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                         request=serve()), "prior_attempt_disagreed")


def test_a_seeded_split_of_another_fact_or_another_subject_is_no_split_here(data):
    other = _seed(subject=OTHER_SUBJECT)
    refuses(data, "no_disagreement")
    refuses(data, "no_disagreement", resolves=[attempt_id(other)])
    soc2_split = {"subject": SUBJECT, "facet": SOC2, "epoch": "initial", "url": URL,
                  "complete": True, "agreed": False, "page_sha256": "a" * 64,
                  "at": "2026-11-01T00:00:00+00:00", "readers": _readers(30, "unbounded")}
    log_attempt(soc2_split)
    refuses(data, "no_disagreement", resolves=[attempt_id(soc2_split)])


def test_a_seeded_split_in_a_stale_epoch_is_refused(data):
    stale = _seed(epoch="reread:" + "b" * 64)
    refuses(data, "no_disagreement")  # the fact is in the initial epoch
    refuses(data, "no_disagreement", resolves=[attempt_id(stale)])
    refuses(data, "epoch_not_current", epoch="reread:" + "b" * 64)


def test_a_seeded_line_that_pins_no_copy_still_blocks_but_names_no_copy(data):
    _seed(page_sha256=None, at=None)
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                         request=serve()), "prior_attempt_disagreed")
    refuses(data, "no_disagreement")


def test_a_forged_string_complete_line_blocks_the_gate_and_the_filer_refuses_it(data):
    forged = {"subject": SUBJECT, "facet": RETENTION, "epoch": "initial", "url": URL,
              "complete": "false", "page_sha256": "a" * 64, "at": "2026-11-01T00:00:00+00:00"}
    log_attempt(forged)
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                         request=serve()), "prior_attempt_disagreed")  # fails closed
    refuses(data, "no_disagreement")
    refuses(data, "no_disagreement", resolves=[attempt_id(forged)])


EXTRA = {"source_id": "other", "snapshot_ref": "sha256:" + "c" * 64, "cited_regions": ["page"],
         "retrieved_at": "2026-11-02T00:00:00+00:00"}


def _claim_before(data, sources, at="2026-11-02T01:00:00+00:00"):
    """The fact's claim as it stood before the ruling, as an earlier filing left it."""
    path = data.root / "verification/queue/events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    claim = {"target": {"kind": "fact", "id": FACT_ID}, "subject": SUBJECT, "field": RETENTION,
             "value": None, "state": "not_disclosed", "sources": sources,
             "collector": {"agent": "a-builder", "model_family": "anthropic", "method": "read"}}
    with path.open("a") as handle:
        handle.write(json.dumps({"event": "collected", "at": at, "claim": claim}) + "\n")
        handle.write(json.dumps({"event": "checked", "at": at, "outcome": "cited", "diff": [],
                                 "target": {"kind": "fact", "id": FACT_ID}}) + "\n")


def test_a_ruling_may_cite_a_cite_only_page_the_fact_cited_before_beyond_the_read_one(data):
    data.fact(sources=[ref("data"), EXTRA], checked_sources=["data", "other"])
    _claim_before(data, [ref("data"), EXTRA])
    _seed()
    refuses(data, "source_mismatch", source_ids=["data", "trust"])  # not a source of this fact
    refuses(data, "source_mismatch", source_ids=["other"])  # the read page must be cited
    file(data, source_ids=["data", "other"])
    refs = {r["source_id"]: r for r in offering_fact(data)["sources"]}
    assert refs["other"]["snapshot_ref"] == EXTRA["snapshot_ref"]
    assert refs["data"]["snapshot_ref"] == "sha256:" + "a" * 64


def test_an_extra_page_the_earlier_claim_does_not_cite_is_refused(data):
    # The fact names the page and its pin, but the claim it stood on before the ruling did not.
    data.fact(sources=[ref("data"), EXTRA], checked_sources=["data", "other"])
    _claim_before(data, [ref("data")])
    _seed()
    refuses(data, "source_mismatch", source_ids=["data", "other"])


def test_an_extra_page_with_no_zoned_read_time_is_refused(data):
    extra = {k: v for k, v in EXTRA.items() if k != "retrieved_at"}
    data.fact(sources=[ref("data"), extra], checked_sources=["data", "other"])
    _claim_before(data, [ref("data"), extra])
    _seed()
    refuses(data, "source_mismatch", source_ids=["data", "other"])


def _extra_case(prior_sources):
    attempt = _attempt()
    ruling = _ruling(attempt, source_ids=["src-cite", "src-extra"])
    pin = {"source_id": "src-extra", "snapshot_ref": "sha256:" + "d" * 64,
           "retrieved_at": AT, "cited_regions": ["page"]}
    row = _ruled_fact(ruling)
    row["sources"].append(pin)
    claim = _claim(ruling)
    claim["sources"].append(pin)  # the page and its pin, added to the ruled fact and its claim
    prior = {**claim, "collector": {"agent": "a-builder", "model_family": "anthropic",
                                    "method": "read"}, "value": None, "state": "not_disclosed",
             "sources": prior_sources(pin)}
    fid = f"{MID}#{FACET}"
    history = {fid: [_event("collected", "2026-10-11T09:00:00+00:00", prior),
                     _event("checked", "2026-10-11T09:00:00+00:00"),
                     _event("collected", f"{ruling['ruled_at']}T09:00:00+00:00", claim),
                     _event("checked", f"{ruling['ruled_at']}T09:00:00+00:00")]}
    return _build(row, [ruling], [attempt], claims={fid: claim}, history=history,
                  extra_sources={"src-extra": CITE + "/extra"}).fact(MID, FACET).state


def test_the_build_pins_an_extra_page_from_the_claim_before_the_ruling():
    assert _extra_case(lambda pin: [pin]) == "known"


def test_a_page_and_pin_added_to_the_ruled_fact_and_its_claim_alone_do_not_stand():
    assert _extra_case(lambda pin: []) == "unknown"  # the fact did not cite it before
    other_pin = lambda pin: [{**pin, "snapshot_ref": "sha256:" + "e" * 64}]  # noqa: E731
    assert _extra_case(other_pin) == "unknown"  # it cited another copy


# --- duplicate keys, in any spelling -------------------------------------------------------------


def test_a_repeated_json_key_in_any_spelling_is_refused(tmp_path):
    from decision.owner_ruling import read_lines

    path = tmp_path / "x.jsonl"
    for line in ('{"ruled_by": "alice", "ruled_by": "jamie"}',
                 '{"ruled_by": "alice", "ruled\\u005fby": "jamie"}',
                 '{"a": {"b": 1, "\\u0062": 2}}'):
        path.write_text(line + "\n")
        with pytest.raises(ValueError):
            read_lines(path)


def test_the_filer_refuses_a_repeated_key_in_the_rulings_attempts_or_fact_file(data):
    disagree()
    rulings_path = data.root / RULINGS_FILE
    rulings_path.write_text('{"subject": "x", "subj\\u0065ct": "y"}\n')
    refuses(data, "malformed")
    rulings_path.unlink()
    attempts_path = data.root / ATTEMPTS_FILE
    good = attempts_path.read_text()
    attempts_path.write_text(good + '{"agreed": true, "agr\\u0065ed": false}\n')
    refuses(data, "malformed")
    attempts_path.write_text(good)
    text = data.offering_path.read_text()
    assert "    state: not_disclosed\n" in text
    data.offering_path.write_text(text.replace("    state: not_disclosed\n",
                                               "    state: not_disclosed\n    state: known\n"))
    refuses(data, "malformed")


# --- the epoch is rule 15's, and a ruling stands only while it is the latest change -------------


REREAD = "reread:" + "a" * 64


def _change_attempt(page="3" * 64, prompt="4" * 64, text="a" * 64):
    """The agreed harness attempt that made a cited change, as the gate logs it."""
    return {**_attempt(), "agreed": True, "agreed_value": 128000, "page_sha256": page,
            "text_sha256": text, "prompt_sha256": prompt, "at": "2026-10-01T08:00:00+00:00",
            "readers": _readers(128000, 128000)}


def _change_block(page="3" * 64, prompt="4" * 64, text="a" * 64):
    return {"rule": "two-readers-cited-change@3", "sha256": page, "text_sha256": text,
            "read_date": "2026-10-01", "previous_value": 1, "url": CITE,
            "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 128000,
                         "prompt_sha256": prompt, "manifest": {"fields": ["url"]}},
                        {"reader_id": "b", "family": "anthropic", "version": "1",
                         "value": 128000, "prompt_sha256": prompt, "manifest": {}}]}


def test_a_ruling_block_cannot_choose_its_epoch():
    attempt = _attempt(epoch=REREAD)
    ruling = _ruling(attempt, epoch=REREAD)
    # the block names the re-read epoch, but the fact is in ``initial`` by rule 15
    assert _build(_ruled_fact(ruling), [ruling], [attempt]).fact(MID, FACET).state == "unknown"


@pytest.mark.parametrize("fake", [
    {}, {"page": "9" * 64}, {"prompt": "5" * 64},
])
def test_a_fabricated_cited_change_block_does_not_choose_the_epoch(fake):
    """``text_sha256`` names the epoch only on a block the attempt log shows the gate made."""
    attempt = _attempt(epoch=REREAD)
    ruling = _ruling(attempt, epoch=REREAD)
    row = _ruled_fact(ruling)
    row["derivation"]["cited_change"] = _change_block(**fake)
    logged = [] if not fake else [_change_attempt()]
    assert _build(row, [ruling], [attempt, *logged]).fact(MID, FACET).state == "unknown"
    # the block the gate made, with its agreed attempt logged, puts the fact in that epoch
    row["derivation"]["cited_change"] = _change_block()
    assert _build(row, [ruling], [attempt, _change_attempt()]).fact(MID, FACET).value == 262144


def test_a_block_with_the_right_raw_hashes_but_a_forged_text_hash_is_refused():
    """The epoch is named by ``text_sha256``, so the log must bind it too."""
    forged = "f" * 64
    attempt = _attempt(epoch=f"reread:{forged}")
    ruling = _ruling(attempt, epoch=f"reread:{forged}")
    row = _ruled_fact(ruling)
    row["derivation"]["cited_change"] = _change_block(text=forged)  # page and prompt are real
    assert _build(row, [ruling], [attempt, _change_attempt()]).fact(MID, FACET).state == "unknown"
    # an attempt logged before the log kept the text hash binds nothing named by one
    legacy = {k: v for k, v in _change_attempt(text=forged).items() if k != "text_sha256"}
    assert _build(row, [ruling], [attempt, legacy]).fact(MID, FACET).state == "unknown"
    # the gate's own attempt, text hash and all, does
    assert _build(row, [ruling], [attempt, _change_attempt(text=forged)]).fact(
        MID, FACET).value == 262144


def test_the_gate_logs_the_text_hash_the_epoch_is_named_by(data):
    from decision.cited_reader import text_sha256
    from tests.test_cited_offering import PAGE

    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data",
                         readers=pair(30, "unbounded"), request=serve()), "readers_disagree")
    assert attempts(data)[-1]["text_sha256"] == text_sha256(PAGE)


def test_the_filer_refuses_a_fabricated_cited_change_block(data):
    data.fact(derivation={"cited_change": {"sha256": "9" * 64, "text_sha256": "a" * 64,
                                           "readers": [{"prompt_sha256": "1" * 64}]}})
    # The fabricated block names the epoch, so the gate reads there (it is the fact's own).
    refused(own_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                     readers=pair(30, "unbounded"), allow_unchanged=False,
                     epoch="reread:" + "a" * 64), "readers_disagree")
    refuses(data, "epoch_not_current", epoch="reread:" + "a" * 64)


def test_a_record_of_a_ruled_reread_fact_is_that_of_a_plain_cited_fact():
    """Nothing the ruling or the kept cited-change block holds is served."""
    attempt = _attempt(epoch=REREAD)
    ruling = _ruling(attempt, epoch=REREAD)
    row = _ruled_fact(ruling)
    row["derivation"]["cited_change"] = _change_block()
    ruled = _build(row, [ruling], [attempt, _change_attempt()])
    plain_row = {k: v for k, v in row.items() if k != "derivation"}
    plain = _build(plain_row, [], [])
    a, b = ruled.fact(MID, FACET), plain.fact(MID, FACET)
    assert (a.state, a.value) == (b.state, b.value) == ("known", 262144)
    assert dict(ruled.record(a.record_id)) == dict(plain.record(b.record_id))
    served = json.dumps(dict(ruled.record(a.record_id)))
    assert "derivation" not in served and "prompt_sha256" not in served


def test_an_agreed_attempt_the_gate_refused_does_not_supersede_a_ruling(data):
    disagree()
    file(data)
    # a later agreed read in a new epoch that the gate refuses (the value is the ruled one)
    ruled_text = data.offering_path.read_text()
    epoch = enter_epoch(data, "d" * 64)
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(30),
                  request=serve(), allow_unchanged=False, epoch=epoch),
            "value_unchanged")
    data.offering_path.write_text(ruled_text)  # the fact stays as ruled
    assert attempts(data)[-1]["agreed"] is True
    assert admits(offering_fact(data), SUBJECT, rulings=rulings(data), attempts=attempts(data),
                  sources=urls(data), claims=claims(data))


def test_a_ruling_copied_back_after_an_admitted_change_does_not_stand(data):
    from scripts import cited_offering as writer

    disagree()
    file(data)
    ruled_text = data.offering_path.read_text()
    ruled = offering_fact(data)
    # an admitted change in a new epoch: it passed the gate and was applied, with its claim
    epoch = enter_epoch(data, "e" * 64)
    out = _gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                request=serve(), allow_unchanged=False, epoch=epoch)
    writer.apply(out, data_dir=data.root)
    assert offering_fact(data)["value"] == 45
    data.offering_path.write_text(ruled_text)  # the ruled fact copied back by hand
    keep = dict(rulings=rulings(data), attempts=attempts(data), sources=urls(data))
    assert not admits(offering_fact(data), SUBJECT, claims=claims(data), **keep)
    assert admits(ruled, SUBJECT, claims={FACT_ID: _filed_ruling_claim(data)}, **keep)


def _filed_ruling_claim(data):
    return next(e["claim"] for e in data.events() if e["event"] == "collected"
                and e["claim"]["collector"]["agent"] == "owner-ruling")


def test_a_later_ruling_supersedes_an_earlier_one():
    attempt = _attempt()
    ruling = _ruling(attempt)
    second = {**_attempt(epoch="reread:" + "c" * 64), "at": "2026-10-16T08:00:00+00:00"}
    newer = _ruling(second, epoch="reread:" + "c" * 64, value=300000, ruled_at="2026-10-17")
    # the fact's latest claim is the newer ruling's, so the earlier one copied back fails
    assert _build(_ruled_fact(ruling), [ruling, newer], [attempt, second],
                  claims={f"{MID}#{FACET}": _claim(newer)}).fact(MID, FACET).state == "unknown"
    assert _build(_ruled_fact(ruling), [ruling, newer], [attempt, second]).fact(
        MID, FACET).value == 262144  # while its own claim is the latest, it stands


# --- the build applies the filer's quarantine test to every value -------------------------------


@pytest.mark.parametrize("value", [128000, 262144, 1])
def test_the_build_keeps_out_a_ruled_fact_with_an_unresolved_verdict_on_any_value(value):
    from tests.snapshot_records import verification

    attempt = _attempt()
    ruling = _ruling(attempt)
    log = [verification("fact", f"{MID}#{FACET}", "mismatch", day="2026-10-14", value=value)]
    assert _build(_ruled_fact(ruling), [ruling], [attempt], log).fact(MID, FACET).state \
        == "unknown"
    resolved = [*log, verification("fact", f"{MID}#{FACET}", "verified", day="2026-10-15",
                                   value=value)]
    assert _build(_ruled_fact(ruling), [ruling], [attempt], resolved).fact(MID, FACET).state \
        == "known"


# --- values compare exactly ----------------------------------------------------------------------


def test_values_compare_exactly_with_their_types():
    attempt = _attempt()
    ruling = _ruling(attempt)
    assert _build(_ruled_fact(ruling, value=262144.0), [ruling], [attempt]).fact(
        MID, FACET).state == "unknown"
    near = _ruling(attempt, value=262144.0000001)
    assert _build(_ruled_fact(ruling, value=262144.0000001), [ruling | {"value": 262144}],
                  [attempt]).fact(MID, FACET).state == "unknown"
    assert ruling_problem(near, attempts=[attempt], sources={"src-cite": CITE},
                          legacy={attempt_id(attempt)}) is None


# --- a ruling in a re-read epoch keeps the fact there; apply re-checks the logs -----------------


def test_a_ruling_in_a_reread_epoch_keeps_the_reread_metadata(data):
    from decision.cited_change import cited_change_block
    from scripts import cited_offering as writer

    writer.apply(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data",
                              readers=pair(30), request=serve()), data_dir=data.root)
    epoch = fact_epoch(offering_fact(data))
    assert epoch.startswith("reread:")
    refused(own_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                     readers=[reader("codex", "openai", 45), reader("claude", "anthropic", 46)],
                     allow_unchanged=False, epoch=epoch), "readers_disagree")
    refuses(data, "no_disagreement")  # the initial epoch agreed: nothing to rule on there
    file(data, epoch=epoch, value=45)
    fact = offering_fact(data)
    assert cited_change_block(fact) is not None and fact["derivation"]["owner_ruling"]["epoch"] \
        == epoch
    assert fact_epoch(fact) == epoch  # readers are not sent back to ``initial``
    assert admits(fact, SUBJECT, rulings=rulings(data), attempts=attempts(data),
                  sources=urls(data), claims=claims(data))
    # and the epoch still blocks readers after the ruling
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(47),
                  request=serve(), allow_unchanged=False, epoch=epoch), "prior_attempt_disagreed")


def test_apply_rechecks_the_attempt_and_verification_logs(data):
    disagree()
    result = filer.plan(data_dir=data.root, **args())
    with (data.root / ATTEMPTS_FILE).open("a") as handle:
        handle.write(json.dumps({"subject": "other/x", "facet": RETENTION}) + "\n")
    before = state(data)
    with pytest.raises(filer.Refused) as caught:
        filer.apply(result)
    assert caught.value.reason == "changed_since_planning" and state(data) == before
    result = filer.plan(data_dir=data.root, **args())
    plant(data, FACT_ID, "mismatch", None)  # a verdict lands after planning
    before = state(data)
    with pytest.raises(filer.Refused) as caught:
        filer.apply(result)
    assert caught.value.reason == "changed_since_planning" and state(data) == before


# --- gate integration ----------------------------------------------------------------------------


def test_after_a_ruling_the_epoch_still_blocks_readers_and_a_new_epoch_is_normal(data):
    disagree()
    file(data)
    # the same epoch: a later agreement on another value is still blocked
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                         request=serve()), "prior_attempt_disagreed")
    # naming another epoch does not move the gate there
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                  request=serve(), allow_unchanged=False, epoch="reread:" + "e" * 64),
            "epoch_not_current")
    # a fresh agreement in a new epoch (the fact's own, after a re-read) follows the normal
    # rules and supersedes the ruling
    ruled_text = data.offering_path.read_text()
    epoch = enter_epoch(data, "e" * 64)
    out = _gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                request=serve(), allow_unchanged=False, epoch=epoch)
    assert out.changed and out.record["value"] == 45 and out.record["state"] == "known"
    assert "owner_ruling" not in out.record["derivation"]
    # and a disagreement in yet another new epoch blocks only it
    data.offering_path.write_text(ruled_text)
    other = enter_epoch(data, "f" * 64)
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data",
                  readers=[reader("codex", "openai", 45), reader("claude", "anthropic", 46)],
                  request=serve(), allow_unchanged=False, epoch=other), "readers_disagree")
    assert [a["epoch"] for a in attempts(data) if not a.get("agreed")][-1] == other
    data.offering_path.write_text(ruled_text)
    refused(cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                         request=serve()), "prior_attempt_disagreed")  # initial: still blocked


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


def _claim(ruling):
    """The claim the filer files for a ruling, as the queue holds it."""
    return {"target": {"kind": "fact", "id": f"{MID}#{FACET}"}, "subject": MID,
            "field": FACET, "value": ruling["value"], "state": ruling["state"],
            "collector": {"agent": "owner-ruling", "model_family": "deterministic",
                          "method": "owner-ruling@1"},
            "sources": [{"source_id": "src-cite", "snapshot_ref": f"sha256:{PAGE_SHA}",
                         "cited_regions": ["page"], "retrieved_at": AT}]}


def _build(row, rulings, attempts, log=(), claims=None, source_cache=None,
           as_of=date(2026, 10, 19), history=None, extra_sources=None):
    """By default the fact's latest claim is its own ruling block's, as after a filing."""
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
    from tests.snapshot_records import SOURCES, model

    block = (row.get("derivation") or {}).get("owner_ruling")
    if claims is None:
        claims = {f"{MID}#{FACET}": _claim(block)} if block else {}
    if history is None:  # as after a filing: the claim line filed and checked on the ruling day
        history = {fid: [_event("collected", f"{block['ruled_at']}T09:00:00+00:00", claim),
                         _event("checked", f"{block['ruled_at']}T09:00:00+00:00")]
                   for fid, claim in claims.items()} if block else {}
    inputs = SnapshotInputs(models=[model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE, **(extra_sources or {})},
                            owner_rulings=list(rulings), cited_attempts=list(attempts),
                            verifications=list(log), owner_ruling_claims=claims,
                            owner_ruling_history=history,
                            # The test's own log is its legacy prefix (``tests.legacy_pin``).
                            owner_ruling_legacy=frozenset(attempt_id(a) for a in attempts))
    return load_built_snapshot(build_snapshot(inputs, as_of=as_of,
                                              source_cache=source_cache))


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
    from decision.cited_reader import epoch_root

    log_attempt({"subject": CARD_SUBJECT, "facet": "model.context_window",
                 "epoch": epoch_root("model.context_window"),  # a plain fact's epoch now (E6)
                 "url": URL, "complete": True, "agreed": False, "agreed_value": None,
                 "harness": True, "page_sha256": "7" * 64, "prompt_sha256": "6" * 64,
                 "at": "2026-11-01T00:00:00+00:00",
                 "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 1},
                             {"reader_id": "b", "family": "anthropic", "version": "1",
                              "value": 2}]})
    file(data, subject=CARD_SUBJECT, facet="model.context_window", value=262144,
         epoch=epoch_root("model.context_window"))
    text = (data.root / CARD).read_text()
    assert text.endswith("---\n" + body)
    after = yaml.safe_load(text.split("---", 2)[1])
    ruled, other = after["facts"]
    assert (ruled["value"], ruled["sources"][0]["snapshot_ref"]) == (262144, "sha256:" + "7" * 64)
    assert other == front["facts"][1] and after["display_name"] == "GPT X"
    [collected, _] = data.events()
    assert collected["claim"]["target"]["id"] == f"{CARD_SUBJECT}#model.context_window"
    assert {s["source_id"] for s in collected["claim"]["sources"]} == {"data"}


# --- the site path: the same admission and served form -------------------------------------------


def _site_tree(root, *, claim=True, ruling_kw=None):
    """A card with a ruled cite-only fact, its logs and its claim, for ``load_models``."""
    attempt = _attempt(epoch=REREAD)
    ruling = _ruling(attempt, epoch=REREAD, **(ruling_kw or {}))
    row = _ruled_fact(ruling)
    row["derivation"]["cited_change"] = _change_block()  # a ruled re-read fact keeps it
    row.pop("id"), row.pop("subject")
    front = {"model_id": MID, "display_name": "Alpha", "provider": "lab",
             "model_type": "llm-chat", "facts": [row],
             "modalities": {"text": {"context_window": 128000}}}
    path = root / f"models/{MID}.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    (root / "registry").mkdir()
    (root / "registry/sources.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "sources": [{"id": "src-cite", "url": CITE}]}))
    (root / "verification/queue").mkdir(parents=True)
    (root / RULINGS_FILE).write_text(json.dumps(ruling, sort_keys=True) + "\n")
    (root / ATTEMPTS_FILE).write_text(json.dumps(attempt, sort_keys=True) + "\n"
                                      + json.dumps(_change_attempt()) + "\n")
    events = [{"event": "collected", "at": "2026-10-12T00:00:00+00:00",
               "claim": _claim(ruling)},
              {"event": "checked", "at": "2026-10-12T00:00:00+00:00", "outcome": "cited",
               "diff": [], "target": {"kind": "fact", "id": f"{MID}#{FACET}"}}] if claim else []
    (root / "verification/queue/events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events))
    return front


def _site_export(root):
    from pipeline import export
    from pipeline.load import Catalogue, load_models

    build = export.Build("b" * 40, "2026-10-19T12:00:00+00:00", date(2026, 10, 19))
    models = load_models(root)
    out = root / "export"
    export.write(out, models, [], Catalogue(build.as_of), build)
    return models[0], json.loads((out / f"models/{MID}.json").read_text())


def test_both_paths_refuse_a_verification_row_that_repeats_outcome(tmp_path):
    """MODEL-554: a ruled card makes the site read the verification log too; a row that says
    ``mismatch`` and then ``verified`` (escaped) is refused there and by the snapshot."""
    from decision.snapshot import collect_repo
    from pipeline.load import LoadError, load_models

    _site_tree(tmp_path)
    row = json.dumps({"target": {"kind": "fact", "id": f"{MID}#{FACET}", "value_hash": "x"},
                      "outcome": "mismatch", "date": "2026-10-12"})
    (tmp_path / "verification/log.jsonl").write_text(
        row[:-1] + ', "outc\\u006fme": "verified"}\n')
    for path in (load_models, collect_repo):  # the snapshot reads cards through load_models
        # The counts-only message every path gives: the file, the line and the count.
        with pytest.raises(LoadError, match=r"log\.jsonl: line 1: a JSON object repeats a key "
                                            r"\(1 line\(s\) repeat a key\)$"):
            path(tmp_path)


def test_the_site_export_publishes_a_ruled_fact_without_its_internals(tmp_path):
    _site_tree(tmp_path)
    model, result = _site_export(tmp_path)
    [published] = [f for f in result["card"]["facts"] if f["facet"] == FACET]
    assert published["value"] == 262144 and published["citation"]["status"] == "cited"
    assert published["verification"] is None and "derivation" not in published
    text = json.dumps(result)
    assert "owner_ruling" not in text and "cited_change" not in text \
        and "prompt_sha256" not in text
    assert result["cited_facts"] == [published] and model.cited_facts == [published]


@pytest.mark.parametrize("case", ["no_claim", "non_owner"])
def test_a_ruling_that_does_not_stand_is_withheld_on_the_site_path(tmp_path, case):
    kw = {"no_claim": dict(claim=False), "non_owner": dict(ruling_kw={"ruled_by": "alice"})}
    _site_tree(tmp_path, **kw[case])
    model, result = _site_export(tmp_path)
    assert model.withheld_facets == (FACET,) and not model.cited_facts
    assert all(f["facet"] != FACET for f in result["card"]["facts"])
    assert "owner_ruling" not in json.dumps(result) and "cited_facts" not in result


def test_a_configured_copy_store_decides_a_ruled_fact_alike_on_both_paths(tmp_path, monkeypatch):
    """A store whose citation record for the fact's copy is unreadable makes the snapshot
    refuse the fact (``invalid_citation``); the site, configured the same way, withholds it."""
    from decision.sources import CopyStore, configured_copy_store

    root = tmp_path / "data"
    front = _site_tree(root)
    attempt = _attempt(epoch=REREAD)
    ruling = _ruling(attempt, epoch=REREAD)
    row = {**front["facts"][0], "id": f"{MID}#{FACET}", "subject": {"kind": "model", "id": MID}}
    attempts_ = [attempt, _change_attempt()]
    cache = tmp_path / "cache"
    monkeypatch.delenv("MODELSPEC_SOURCE_CACHE", raising=False)
    assert configured_copy_store() is None
    assert _build(row, [ruling], attempts_).fact(MID, FACET).value == 262144
    model, _ = _site_export(root)
    assert model.withheld_facets == () and model.cited_facts
    # the same store, configured once for both paths
    record = CopyStore(cache).path(f"sha256:{PAGE_SHA}").with_suffix(".citation.json")
    record.parent.mkdir(parents=True)
    record.write_text("{not json")
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(cache))
    store = configured_copy_store()
    assert store is not None and store.root == cache
    assert _build(row, [ruling], attempts_, source_cache=store).fact(MID, FACET).state \
        == "unknown"
    shutil.rmtree(root / "export")
    model, result = _site_export(root)
    assert model.withheld_facets == (FACET,) and not model.cited_facts
    assert all(f["facet"] != FACET for f in result["card"]["facts"])


def _event(kind, at, claim=None, outcome="cited"):
    if kind == "collected":
        return {"event": "collected", "at": at, "claim": claim}
    return {"event": "checked", "at": at, "target": {"kind": "fact", "id": f"{MID}#{FACET}"},
            "outcome": outcome, "diff": []}


def _plain_claim(value, at_ref="0" * 64):
    return {"target": {"kind": "fact", "id": f"{MID}#{FACET}"}, "subject": MID, "field": FACET,
            "value": value, "state": "known",
            "collector": {"agent": "cited-change-gate", "model_family": "deterministic",
                          "method": "two-readers-cited-change@3"},
            "sources": [{"source_id": "src-cite", "snapshot_ref": f"sha256:{at_ref}",
                         "cited_regions": ["page"]}]}


def test_a_build_dated_before_the_ruling_withholds_the_fact():
    """Later knowledge never enters an earlier snapshot, and nothing is restored."""
    attempt = _attempt()
    ruling = _ruling(attempt)  # ruled, filed and checked 2026-10-12
    assert _build(_ruled_fact(ruling), [ruling], [attempt], as_of=date(2026, 10, 1)).fact(
        MID, FACET).state == "unknown"
    assert _build(_ruled_fact(ruling), [ruling], [attempt], as_of=date(2026, 10, 12)).fact(
        MID, FACET).value == 262144  # on the day, the live checks admit it
    # a forged earlier value in the ruling record is never served
    row = _ruled_fact(ruling)
    row["derivation"]["owner_ruling_previous"] = {"value": 999999, "state": "known",
                                                  "sources": row["sources"]}
    assert _build(row, [ruling], [attempt], as_of=date(2026, 10, 1)).fact(
        MID, FACET).state == "unknown"
    # a ruling dated after the UTC day is refused whatever the as_of
    future = (datetime.now(UTC).date() + timedelta(days=2)).isoformat()
    ahead = _ruling(attempt, ruled_at=future)
    assert _build(_ruled_fact(ahead), [ahead], [attempt]).fact(MID, FACET).state == "unknown"
    assert _build(_ruled_fact(ahead), [ahead], [attempt],
                  as_of=date(2030, 1, 1)).fact(MID, FACET).state == "unknown"


def test_a_backdated_ruling_is_withheld_until_its_claim_is_filed_and_checked():
    attempt = _attempt()  # read 2026-10-10
    ruling = _ruling(attempt, ruled_at="2026-10-11")
    fid = f"{MID}#{FACET}"
    history = {fid: [_event("collected", "2026-10-14T09:00:00+00:00", _claim(ruling)),
                     _event("checked", "2026-10-15T09:00:00+00:00")]}

    def on(day, events=history):
        return _build(_ruled_fact(ruling), [ruling], [attempt], as_of=day,
                      history=events).fact(MID, FACET)

    assert on(date(2026, 10, 12)).state == "unknown"  # dated before its claim existed
    assert on(date(2026, 10, 14)).state == "unknown"  # filed, not yet checked
    assert on(date(2026, 10, 15)).value == 262144
    unchecked = {fid: history[fid][:1]}
    assert on(date(2026, 10, 19), unchecked).state == "unknown"  # never checked
    later = {fid: [*history[fid], _event("collected", "2026-10-16T09:00:00+00:00",
                                         _plain_claim(1))]}
    assert on(date(2026, 10, 19), later).state == "unknown"  # a newer claim, ruling's is not


def test_a_withheld_ruled_fact_names_no_source_in_its_gap():
    from decision import registry
    from decision.snapshot import SnapshotInputs, _compile
    from tests.snapshot_records import SOURCES, model

    attempt = _attempt()
    ruling = _ruling(attempt)
    inputs = SnapshotInputs(models=[model(MID, facts=[_ruled_fact(ruling)])],
                            sources={**SOURCES, "src-cite": CITE}, owner_rulings=[ruling],
                            cited_attempts=[attempt])
    compiled = _compile(inputs, registry.default(), None, date(2026, 10, 1), False, None)
    reason, urls = compiled.rejected[(MID, FACET)]
    assert reason == "invalid_citation" and urls == ()
    assert CITE not in json.dumps([str(g) for g in compiled.gaps([MID])])


def test_a_historical_site_export_does_not_know_a_later_ruling(tmp_path):
    """The site path withholds a ruled fact from a build dated before the ruling, as the
    snapshot does, and admits it on the day."""
    _site_tree(tmp_path)
    from pipeline import export
    from pipeline.load import Catalogue, load_models

    build = export.Build("b" * 40, "2026-10-01T12:00:00+00:00", date(2026, 10, 1))
    models = load_models(tmp_path, as_of=date(2026, 10, 1))
    out = tmp_path / "export"
    export.write(out, models, [], Catalogue(build.as_of), build)
    result = json.loads((out / f"models/{MID}.json").read_text())
    assert models[0].withheld_facets == (FACET,) and not models[0].cited_facts
    assert all(f["facet"] != FACET for f in result["card"]["facts"])
    assert load_models(tmp_path, as_of=date(2026, 10, 12))[0].withheld_facets == ()


def test_a_past_cutoff_ruled_fact_with_an_invalid_citation_names_no_source_in_its_gap():
    """The cutoff check runs before the citation is read: a registered source with an invalid
    citation hash would otherwise reject the fact with its URL in the gap record."""
    from decision import registry
    from decision.snapshot import SnapshotInputs, _compile
    from tests.snapshot_records import SOURCES, model

    attempt = _attempt()
    ruling = _ruling(attempt)
    row = _ruled_fact(ruling)
    row["sources"][0]["snapshot_ref"] = "sha256:not-a-hash"  # registered source, bad hash
    inputs = SnapshotInputs(models=[model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE}, owner_rulings=[ruling],
                            cited_attempts=[attempt])
    compiled = _compile(inputs, registry.default(), None, date(2026, 10, 1), False, None)
    reason, urls = compiled.rejected[(MID, FACET)]
    assert reason == "invalid_citation" and urls == ()
    assert CITE not in json.dumps([str(g) for g in compiled.gaps([MID])])
