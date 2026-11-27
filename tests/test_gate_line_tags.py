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



# --- the legacy prefix: untagged reads logged before the tags, for a hold only --------------------

def _line(**kw):
    base = {"subject": gate.SUBJECT, "facet": gate.FACET, "epoch": "initial", "complete": True,
            "harness": True, "agreed": False, "agreed_value": None, "readers": []}
    return json.dumps({**base, **kw}, sort_keys=True)


LEGACY_SPLIT = _line()
LEGACY_SILENT = _line(agreed=True)
LEGACY_AGREED = _line(agreed=True, agreed_value=gate.FILED)
LEGACY_INCOMPLETE = _line(complete=False, agreed=None, error="ReaderError")
PREFIX = [LEGACY_SPLIT, LEGACY_SILENT, LEGACY_AGREED, LEGACY_INCOMPLETE]


def _pin(lines):
    import hashlib

    data_ = "".join(x + "\n" for x in lines).encode()
    return len(data_), hashlib.sha256(data_).hexdigest()


def test_the_pinned_prefix_is_a_length_and_a_digest():
    from decision.hold_evidence import LEGACY_ATTEMPTS

    length, digest = LEGACY_ATTEMPTS
    assert length > 0 and len(digest) == 64 and int(digest, 16) >= 0


def test_an_untagged_read_inside_the_prefix_shows_its_hold():
    from decision.hold_evidence import hold_kind, legacy_count

    pin = _pin(PREFIX)
    log = AttemptLog([*PREFIX, _line(epoch="reread:x")])
    assert legacy_count(log.lines, pin) == 4
    assert hold_kind(log, LEGACY_SPLIT, pinned=pin) == "split"
    assert hold_kind(log, LEGACY_SILENT, pinned=pin) == "silent"
    # An agreed value or an incomplete attempt shows no hold, inside the prefix or not.
    assert hold_kind(log, LEGACY_AGREED, pinned=pin) is None
    assert hold_kind(log, LEGACY_INCOMPLETE, pinned=pin) is None


def test_an_untagged_line_appended_after_the_prefix_shows_nothing():
    from decision.hold_evidence import hold_kind

    pin = _pin(PREFIX)
    appended = _line(epoch="reread:y")
    tagged = _line(epoch="reread:z", kind="split")
    log = AttemptLog([*PREFIX, appended, tagged])
    assert hold_kind(log, appended, pinned=pin) is None
    assert hold_kind(log, tagged, pinned=pin) == "split"  # past the prefix, only the tag counts
    assert hold_kind(log, _line(epoch="not-in-log"), pinned=pin) is None


@pytest.mark.parametrize("change", ["byte", "dropped_line", "reordered", "short_log"])
def test_a_changed_prefix_makes_no_line_legacy(change):
    from decision.hold_evidence import hold_kind, legacy_count

    pin = _pin(PREFIX)
    lines = list(PREFIX)
    if change == "byte":
        lines[2] = lines[2].replace('"initial"', '"initiaL"')
    elif change == "dropped_line":
        lines.pop(2)
    elif change == "reordered":
        lines[0], lines[1] = lines[1], lines[0]
    else:
        lines = lines[:2]
    log = AttemptLog(lines)
    assert legacy_count(log.lines, pin) == 0
    assert hold_kind(log, LEGACY_SPLIT, pinned=pin) is None
    assert hold_kind(log, LEGACY_SILENT, pinned=pin) is None


def test_a_legacy_line_never_serves_or_moves_a_record():
    import inspect

    import decision.quarantine_clearing as qc
    import decision.retained_correction as rc

    # line_kind, the only tag that moves or serves, ignores the legacy prefix and the hold tags.
    for raw in PREFIX:
        assert line_kind(json.loads(raw), gate.FACET) is None
    # The prefix and hold tags are read by hold evidence alone: never by the clearing, move or
    # correction rules.
    for module in (qc, rc):
        source = inspect.getsource(module)
        assert "hold_evidence" not in source and "hold_kind" not in source


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
    assert line["value_hash"] == value_hash(gate.FILED)


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
