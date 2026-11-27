"""MODEL-491: the gate tags every fact read it logs, under the line's hash.

``read_page`` writes ``kind`` into the attempt line before it is logged: ``refused`` when a reader
gave no usable answer, ``split`` when the two readers disagreed, ``silent`` when both agreed the
page states nothing, and, on a retaining page, ``confirmation`` or ``correction`` as before. A
split or silent line carries the fact's filed value on cite-only pages too, and an agreed
cite-only line stays as it was. The tags move and serve nothing (``line_kind`` knows only the
retained kinds), and the line's hash covers them. Every record here is synthetic.
"""

from __future__ import annotations

import json

import pytest
from decision.cited_change import cited_change
from decision.cited_reader import ATTEMPTS_FILE, Reader
from decision.quarantine_clearing import AttemptLog, line_hash, line_kind

from tests import test_retained_agreement as gate

SPLIT, SILENT, AGREED = (None, ["text"]), (None, None), ("filed", "filed")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    import socket

    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


@pytest.fixture
def data(tmp_path, monkeypatch):
    return gate.Data(tmp_path / "data", monkeypatch)


def readers(answers):
    a, b = (gate.FILED if v == "filed" else v for v in answers)
    return [gate.reader("codex", "gpt-5", a), gate.reader("claude", "claude-sonnet-5", b)]


def failing():
    return [Reader("codex", "gpt-5", "1.0", lambda prompt: "no answer"),
            gate.reader("claude", "claude-sonnet-5")]


def cite_only(data, pair):
    data.fact["sources"] = [dict(source_id="docs", snapshot_ref="sha256:" + "0" * 64,
                                 cited_regions=["model-spec"])]
    data.write()
    return cited_change(subject=gate.SUBJECT, facet=gate.FACET, source_id="docs", readers=pair,
                        request=gate.serve({gate.CITE_ONLY: gate.PAGE}))


def raw_lines(data):
    return (data.root / ATTEMPTS_FILE).read_text().splitlines()


@pytest.mark.parametrize("answers, kind, reason", [(SPLIT, "split", "readers_disagree"),
                                                   (SILENT, "silent", "no_value")])
def test_the_retaining_gate_tags_a_split_or_silent_read(data, answers, kind, reason):
    gate.refused(reason, readers=readers(answers))
    (line,) = data.attempts()
    assert line["kind"] == kind and line["filed_value"] == gate.FILED


def test_the_retaining_gate_tags_a_refused_read(data):
    gate.refused("reader_failed", readers=failing())
    lines = data.attempts()
    assert lines and all(x["kind"] == "refused" and x["complete"] is False for x in lines)


def test_the_retaining_gate_still_tags_a_confirmation(data):
    assert gate.run().changed
    assert data.attempts()[-1]["kind"] == "confirmation"


@pytest.mark.parametrize("answers, kind", [(SPLIT, "split"), (SILENT, "silent")])
def test_the_cite_only_gate_tags_a_split_or_silent_read_with_its_filed_value(data, answers,
                                                                             kind):
    cite_only(data, readers(answers))
    (line,) = data.attempts()
    assert line["kind"] == kind and line["filed_value"] == gate.FILED


def test_the_cite_only_gate_tags_a_refused_read_without_a_filed_value(data):
    cite_only(data, failing())
    lines = data.attempts()
    assert lines and all(x["kind"] == "refused" and "filed_value" not in x for x in lines)


def test_an_agreed_cite_only_read_is_logged_as_before(data):
    cite_only(data, readers(AGREED))
    (line,) = data.attempts()
    assert "kind" not in line and "filed_value" not in line


@pytest.mark.parametrize("answers", [SPLIT, SILENT])
def test_the_lines_hash_covers_its_tag(data, answers):
    gate.refused("readers_disagree" if answers == SPLIT else "no_value", readers=readers(answers))
    (raw,) = raw_lines(data)
    line = json.loads(raw)
    log = AttemptLog([raw])
    assert log.by_hash[line_hash(raw)][0]["kind"] == line["kind"]
    # The same line with its tag removed or changed is another line, with another hash.
    for other in ({k: v for k, v in line.items() if k != "kind"}, {**line, "kind": "silent"
                                                                   if answers == SPLIT
                                                                   else "split"}):
        respelled = json.dumps(other, sort_keys=True, ensure_ascii=False)
        assert line_hash(respelled) != line_hash(raw)
        assert line_hash(respelled) not in log.by_hash


@pytest.mark.parametrize("kind", ["split", "silent", "refused"])
def test_the_new_tags_move_and_serve_nothing(kind):
    assert line_kind({"kind": kind}, gate.FACET) is None



# --- the legacy prefix: untagged reads logged before the tags, pinned on raw bytes by path --------

ATTEMPTS = "verification/cited-attempts.jsonl"


def _line(**kw):
    base = {"subject": gate.SUBJECT, "facet": gate.FACET, "epoch": "initial", "complete": True,
            "harness": True, "agreed": False, "agreed_value": None, "readers": []}
    return json.dumps({**base, **kw}, sort_keys=True)


LEGACY_SPLIT = _line()
LEGACY_SILENT = _line(agreed=True)
LEGACY_AGREED = _line(agreed=True, agreed_value=gate.FILED)
LEGACY_INCOMPLETE = _line(complete=False, agreed=None, error="ReaderError")
PREFIX = [LEGACY_SPLIT, LEGACY_SILENT, LEGACY_AGREED, LEGACY_INCOMPLETE]
PREFIX_BYTES = "".join(x + "\n" for x in PREFIX).encode()


def _pins(data=PREFIX_BYTES, path=ATTEMPTS):
    import hashlib

    return {path: (len(data), hashlib.sha256(data).hexdigest())}


def _legacy(data, path=ATTEMPTS, pins=None):
    from decision.hold_evidence import legacy_lines

    return legacy_lines(path, data, pins or _pins())


def test_the_pin_is_a_length_and_a_digest_bound_to_the_attempt_logs_path():
    from decision.hold_evidence import LEGACY_PREFIXES

    assert set(LEGACY_PREFIXES) == {ATTEMPTS}
    ((length, digest),) = LEGACY_PREFIXES.values()
    assert length > 0 and len(digest) == 64 and int(digest, 16) >= 0


def test_an_untagged_read_inside_the_prefix_shows_its_hold():
    from decision.hold_evidence import hold_kind

    appended = _line(epoch="reread:x")
    legacy = _legacy(PREFIX_BYTES + (appended + "\n").encode())
    assert legacy == tuple(PREFIX)
    log = AttemptLog([*PREFIX, appended])
    assert hold_kind(log, LEGACY_SPLIT, legacy=legacy) == "split"
    assert hold_kind(log, LEGACY_SILENT, legacy=legacy) == "silent"
    # An agreed value or an incomplete attempt shows no hold, inside the prefix or not.
    assert hold_kind(log, LEGACY_AGREED, legacy=legacy) is None
    assert hold_kind(log, LEGACY_INCOMPLETE, legacy=legacy) is None


def test_an_untagged_line_appended_after_the_prefix_shows_nothing():
    from decision.hold_evidence import hold_kind

    appended = _line(epoch="reread:y")
    tagged = _line(epoch="reread:z", kind="split")
    data = PREFIX_BYTES + (appended + "\n" + tagged + "\n").encode()
    legacy = _legacy(data)
    log = AttemptLog([*PREFIX, appended, tagged])
    assert hold_kind(log, appended, legacy=legacy) is None
    assert hold_kind(log, tagged, legacy=legacy) == "split"  # past the prefix, only the tag counts
    assert hold_kind(log, _line(epoch="not-in-log"), legacy=legacy) is None


@pytest.mark.parametrize("change", ["byte", "crlf", "blank_line", "no_final_lf", "dropped_line",
                                    "reordered", "short_file", "renamed"])
def test_any_prefix_difference_makes_no_line_legacy(change):
    data, path = PREFIX_BYTES, ATTEMPTS
    if change == "byte":
        data = data.replace(b'"initial"', b'"initiaL"', 1)
    elif change == "crlf":  # the same lines with Windows line ends
        data = data.replace(b"\n", b"\r\n")
    elif change == "blank_line":
        data = (PREFIX[0] + "\n\n" + "".join(x + "\n" for x in PREFIX[1:])).encode()
    elif change == "no_final_lf":
        data = data[:-1]
    elif change == "dropped_line":
        data = "".join(x + "\n" for x in PREFIX[:2] + PREFIX[3:]).encode()
    elif change == "reordered":
        data = "".join(x + "\n" for x in [PREFIX[1], PREFIX[0], *PREFIX[2:]]).encode()
    elif change == "short_file":
        data = "".join(x + "\n" for x in PREFIX[:2]).encode()
    else:  # the same bytes at another path
        path = "verification/cited-attempts-old.jsonl"
    assert _legacy(data + b'{"later": true}\n', path=path) == ()


def test_a_legacy_line_never_serves_or_moves_a_record():
    import inspect

    import decision.quarantine_clearing as qc
    import decision.retained_correction as rc

    # line_kind, the only tag that moves or serves, ignores the legacy prefix and the hold tags.
    for raw in PREFIX:
        assert line_kind(json.loads(raw), gate.FACET) is None
    for kind in ("split", "silent", "refused", "refusal"):
        assert line_kind({"kind": kind}, gate.FACET) is None
    # The prefix and hold tags are read by hold evidence alone: never by the clearing, move or
    # correction rules.
    for module in (qc, rc):
        source = inspect.getsource(module)
        assert "hold_evidence" not in source and "hold_kind" not in source


# --- an owner's ruling rests only on a tagged or a pinned legacy split --------------------------

def _split_attempt(**kw):
    line = {"subject": gate.SUBJECT, "facet": gate.FACET, "epoch": "initial", "complete": True,
            "agreed": False, "agreed_value": None, "harness": True,
            "page_sha256": "3" * 64, "prompt_sha256": "4" * 64, "own_fetch": True,
            "at": "2026-11-28T08:00:00+00:00",
            "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 1},
                        {"reader_id": "b", "family": "anthropic", "version": "1", "value": 2}]}
    return {**line, **kw}


def test_a_ruling_split_is_gate_tagged_or_in_the_legacy_prefix():
    from decision.hold_evidence import legacy_ids
    from decision.owner_ruling import is_split, split_status

    facet = "model.context_window"
    untagged = _split_attempt(facet=facet)
    tagged = _split_attempt(facet=facet, kind="split")
    assert split_status(untagged, facet) == "split"
    assert not is_split(untagged, facet)  # an untagged split past the prefix: no ruling
    assert is_split(tagged, facet)
    legacy = legacy_ids([json.dumps(untagged, sort_keys=True)])
    assert is_split(untagged, facet, legacy=legacy)
    other = _split_attempt(facet=facet, at="2026-11-28T09:00:00+00:00")
    assert not is_split(other, facet, legacy=legacy)


# --- a refusal before any read: one tagged line in its own log, never a read --------------------

def refusals(data):
    from decision.hold_evidence import REFUSALS_FILE

    path = data.root / REFUSALS_FILE
    return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


def test_a_refusal_before_any_read_logs_a_tagged_refusal_line(data):
    from decision.hold_evidence import REFUSAL_FIELDS, REFUSAL_RULE
    from decision.model import value_hash

    request = gate.serve()
    gate.refused("host_unclassed", source_id="loose", request=request)
    assert request.calls == [] and data.attempts() == []
    (line,) = refusals(data)
    assert set(line) == set(REFUSAL_FIELDS)
    assert line["kind"] == "refusal" and line["rule"] == REFUSAL_RULE
    assert line["reason"] == "host_unclassed" and line["source_id"] == "loose"
    assert line["fact_id"] == f"{gate.SUBJECT}#{gate.FACET}" and line["epoch"] == "initial"
    assert line["value_hash"] == value_hash(gate.FILED) and line["fetched"] is False


def test_a_refusal_line_is_not_a_read_or_a_retry(data):
    gate.refused("host_unclassed", source_id="loose", request=gate.serve())
    gate.refused("host_unclassed", source_id="loose", request=gate.serve())
    assert len(refusals(data)) == 2 and data.attempts() == []
    assert gate.run().changed  # the refusals block nothing: the next read confirms
    assert data.attempts()[-1]["kind"] == "confirmation"


def test_a_cite_only_refusal_before_any_read_is_logged_too(data):
    request = gate.serve({gate.CITE_ONLY: gate.PAGE})
    out = cited_change(subject=gate.SUBJECT, facet=gate.FACET, source_id="readme",
                       readers=readers(AGREED), request=request)
    assert out.outcome == "refused" and data.attempts() == []
    assert [x["reason"] for x in refusals(data)] == [out.reason]


@pytest.mark.parametrize("pair, reason", [(SPLIT, "readers_disagree"), (SILENT, "no_value")])
def test_a_refusal_after_a_read_logs_no_refusal_line(data, pair, reason):
    gate.refused(reason, readers=readers(pair))
    assert len(data.attempts()) == 1 and refusals(data) == []


def test_a_reader_failure_is_a_read_not_a_refusal_line(data):
    gate.refused("reader_failed", readers=failing())
    assert data.attempts() and refusals(data) == []


def test_a_refusal_for_no_fact_logs_nothing(data):
    out = cited_change(subject=gate.SUBJECT, facet="not.a_facet", source_id="readme",
                       readers=readers(AGREED), request=gate.serve())
    assert out.outcome == "refused" and refusals(data) == []


def test_a_refusal_after_a_fetch_but_before_a_read_says_it_fetched(data):
    page = (302, gate.CITE_ONLY, b"")
    gate.refused("redirect_to_cite_only_host", request=gate.serve({gate.URL: page}))
    assert data.attempts() == []
    (line,) = refusals(data)
    assert line["reason"] == "redirect_to_cite_only_host" and line["fetched"] is True


def test_an_unrelated_append_does_not_suppress_a_refusal_line(data, monkeypatch):
    # Another writer appends to the shared attempt log while this call runs: the call still
    # knows it read nothing, so its refusal line is written.
    import decision.cited_change as cc

    real = cc.quarantine_rows

    def appending(*a, **kw):
        path = data.root / ATTEMPTS_FILE
        with path.open("a") as fh:
            fh.write(_line(subject="other/model") + "\n")
        return real(*a, **kw)

    monkeypatch.setattr(cc, "quarantine_rows", appending)
    gate.refused("host_unclassed", source_id="loose", request=gate.serve())
    assert [x["reason"] for x in refusals(data)] == ["host_unclassed"]


def test_a_read_that_ends_in_a_refusal_writes_its_attempt_line_only(data):
    # The call itself knows it read: a refused read logs its attempt line and no refusal line.
    gate.refused("readers_disagree", readers=readers(SPLIT))
    (line,) = data.attempts()
    assert line["kind"] == "split" and refusals(data) == []


def test_ruling_inputs_take_the_legacy_splits_from_the_logs_raw_bytes(tmp_path, monkeypatch):
    import hashlib

    import decision.hold_evidence as he
    from decision.owner_ruling import RULINGS_FILE, attempt_id, read_ruling_inputs

    root = tmp_path / "data"
    (root / "verification").mkdir(parents=True)
    (root / RULINGS_FILE).write_text(json.dumps({"subject": "x"}) + "\n")
    first, later = _split_attempt(), _split_attempt(at="2026-11-28T09:00:00+00:00")
    prefix = (json.dumps(first, sort_keys=True) + "\n").encode()
    (root / ATTEMPTS).write_bytes(prefix + (json.dumps(later, sort_keys=True) + "\n").encode())
    monkeypatch.setattr(he, "LEGACY_PREFIXES",
                        {ATTEMPTS: (len(prefix), hashlib.sha256(prefix).hexdigest())})
    inputs = read_ruling_inputs(root, verdicts=False)
    assert inputs.legacy == {attempt_id(first)}  # the appended untagged split is not legacy
    # The same log written with Windows line ends pins nothing.
    (root / ATTEMPTS).write_bytes(prefix.replace(b"\n", b"\r\n"))
    assert read_ruling_inputs(root, verdicts=False).legacy == frozenset()
