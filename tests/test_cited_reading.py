"""A cite-only board reading is changed by two readers of different families (rule 15, readings)."""

import json
import socket
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

import inspect

from decision import cited_change as gate
from decision.cited_change import (
    ABSENCE_GAP, REFUSALS, cited_change_readings, cited_reading, pending_absences, reading_epoch,
)
from decision.cited_reader import ATTEMPTS_FILE, Reader, attempts

SUBJECT = "acme/orbit-9"
BENCH = "boardbench_1"
URL = "https://cursor.com/cursorbench"
RETAIN = "https://huggingface.co/datasets/acme/boardbench"
READING = {"model_id_as_evaluated": "Orbit 9 (max)", "effort": "max", "harness": None}
PAGE = b"<html><body><table><tr><td>Orbit 9 Max</td><td>51.2%</td></tr></table>PAGEMARK</body></html>"
GONE = b"<html><body><table><tr><td>Rival 1</td><td>40.0%</td></tr></table></body></html>"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


def rd(rid, family, value):
    return Reader(rid, family, "1.0", lambda prompt: f'<<<JSON {{"value": {json.dumps(value)}}} JSON>>>')


def pair(value=51.2, second=None):
    return [rd("claude", "anthropic", value), rd("local", "mistral", value if second is None else second)]


def serve(page=PAGE):
    def request(url):
        return 200, None, page
    return request


class Data:
    def __init__(self, root: Path, monkeypatch):
        self.root = root
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
        self.sources = [
            dict(id="board", url=URL, kind="benchmark_author", publisher="cursor", fetch="http",
                 normaliser="text-default", cited_regions=[dict(id="rows", locator=dict(kind="page", value=""))]),
            dict(id="hf", url=RETAIN, kind="benchmark_author", publisher="cursor", fetch="http",
                 normaliser="text-default", cited_regions=[dict(id="rows", locator=dict(kind="page", value=""))]),
        ]
        self.row = dict(benchmark_id=BENCH, model_id_as_evaluated="Orbit 9 (max)", score=46.6,
                        effort="max", harness=None, observed_at="2026-10-19",
                        sources=[dict(source_id="board", snapshot_ref="sha256:" + "0" * 64,
                                      cited_regions=["rows"])])
        self.bench = {"id": BENCH, "metric": {"name": "Board score", "unit": "%", "max_score": 100},
                      "owner_id": "cursor", "publisher": {"org": "Cursor", "url": "https://cursor.com/cursorbench"},
                      "sources": [{"url": URL}]}
        self.vendors = [dict(id="cursor", name="Cursor", url="https://cursor.com/")]
        self.write()

    def write(self):
        for d in ("models/acme", "registry", "benchmarks"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        card = yaml.safe_dump({"display_name": "Orbit 9", "benchmarks": {"scores": {}, "evidence": [self.row]}}, sort_keys=False)
        (self.root / "models/acme/orbit-9.md").write_text(f"---\n{card}---\n")
        (self.root / f"benchmarks/{BENCH}.md").write_text(f"---\n{yaml.safe_dump(self.bench)}---\n")
        (self.root / "registry/sources.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "sources": self.sources}))
        (self.root / "registry/providers.yaml").write_text(
            yaml.safe_dump({"providers": [], "subscription_vendors": self.vendors}))
        (self.root / "registry/labs.yaml").write_text(yaml.safe_dump({"labs": []}))

    def log(self):
        path = self.root / ATTEMPTS_FILE
        return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def run(**kw):
    args = dict(subject=SUBJECT, benchmark_id=BENCH, reading=READING, source_id="board",
                readers=pair(), request=serve())
    args.update(kw)
    return cited_reading(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS


def test_two_readers_agree_so_the_score_changes_as_cited(data):
    out = run()
    assert out.changed and out.record["value"] == 51.2
    rec = out.record
    assert rec["resolution"] == "cited" and rec["benchmark_id"] == BENCH and "facet" not in rec
    block = rec["derivation"]["cited_change"]
    assert block["previous_value"] == 46.6 and len(block["readers"]) == 2
    assert {r["family"] for r in block["readers"]} == {"anthropic", "mistral"}
    assert "PAGEMARK" not in json.dumps(rec) and "PAGEMARK" not in json.dumps(data.log())
    assert rec["clears_not_published_since"] is False


def test_the_prompt_names_the_row_not_the_filed_score(data):
    seen = []
    spy = Reader("claude", "anthropic", "1", lambda p: seen.append(p) or '<<<JSON {"value": 51.2} JSON>>>')
    run(readers=[spy, rd("local", "mistral", 51.2)])
    assert "Orbit 9 (max)" in seen[0] and "46.6" not in seen[0]


def test_a_publisher_that_does_not_own_the_board_is_refused(data):
    data.sources[0]["publisher"] = "acme"          # the subject's lab is not the board's owner
    data.vendors.append(dict(id="acme", name="Acme", url="https://acme.example/"))
    data.write()
    refused("not_first_party")


def test_a_source_with_no_publisher_is_refused(data):
    del data.sources[0]["publisher"]
    data.write()
    refused("not_first_party")


def test_a_non_owner_on_the_same_host_is_refused(data):
    data.sources[0]["publisher"] = "other"         # another registry id, a path on the same host
    data.vendors.append(dict(id="other", name="Other", url="https://cursor.com/other"))
    data.write()
    refused("not_first_party")


def test_a_benchmark_page_with_no_owner_is_refused(data):
    del data.bench["owner_id"]
    data.write()
    refused("not_first_party")


def test_an_owner_whose_registry_host_is_not_the_source_host_is_refused(data):
    data.vendors[0]["url"] = "https://other.example/"
    data.write()
    refused("not_first_party")


def test_a_non_author_source_kind_is_refused(data):
    data.sources[0]["kind"] = "lab_documentation"
    data.write()
    refused("source_kind_not_permitted")


def test_a_retaining_host_source_is_refused(data):
    data.row["sources"].append(dict(source_id="hf", snapshot_ref="sha256:" + "1" * 64,
                                    cited_regions=["rows"]))
    data.write()
    refused("retaining_source_registered")


def test_a_retaining_source_in_checked_sources_previous_sources_or_the_page_is_refused(data):
    data.row["checked_sources"] = ["hf"]
    data.write()
    refused("retaining_source_registered")
    del data.row["checked_sources"]
    data.row["derivation"] = {"cited_change": {"previous_sources": ["hf"]}}
    data.write()
    refused("retaining_source_registered")
    del data.row["derivation"]
    data.bench["sources"].append({"url": RETAIN})
    data.write()
    refused("retaining_source_registered")


def test_a_redirect_to_a_retaining_host_is_refused_and_not_requested(data):
    calls = []

    def request(url):
        calls.append(url)
        return 302, "https://huggingface.co/x", b""
    refused("redirect_to_retaining_host", request=request)
    assert calls == [URL]


def test_a_reader_input_that_is_not_the_blind_prompt_is_refused(data, monkeypatch):
    real = gate.read_page

    def tampered(**kw):
        answers = real(**kw)
        bad = dict(answers[0].manifest, template="other")
        return [type(answers[0])(a.reader_id, a.family, a.version, a.value, a.prompt_sha256, bad)
                for a in answers]
    monkeypatch.setattr(gate, "read_page", tampered)
    refused("reader_input_not_blind")


def test_a_prior_agreement_on_another_value_is_refused(data):
    assert run(readers=pair(51.2)).changed
    refused("prior_attempt_disagreed", readers=pair(52.0))


def test_now_cannot_be_injected():
    assert "now" not in inspect.signature(cited_reading).parameters
    with pytest.raises(TypeError):
        cited_reading(subject=SUBJECT, benchmark_id=BENCH, reading=READING, source_id="board",
                      readers=pair(), now=datetime.now(UTC))


def test_a_naive_time_in_the_log_is_refused_not_raised(data):
    run(readers=pair(None), request=serve(GONE))
    log = data.log()
    log[0]["at"] = "2026-11-01T00:00:00"
    (data.root / ATTEMPTS_FILE).write_text("".join(json.dumps(x) + "\n" for x in log))
    refused("bad_read_date", readers=pair(None), request=serve(GONE))


def test_readers_that_disagree_are_refused_and_block_a_retry(data):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    assert [a["agreed"] for a in data.log()] == [False]
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1


def test_two_readers_of_one_family_are_refused(data):
    refused("reader_families_not_distinct", readers=[rd("a", "anthropic", 51.2), rd("b", "anthropic", 51.2)])
    assert data.log() == []


def test_the_same_score_is_not_a_change(data):
    refused("value_unchanged", readers=pair(46.6))


def test_a_row_must_match_exactly_one_reading(data):
    refused("reading_not_found", reading={**READING, "effort": "low"})
    data.root.joinpath("x").mkdir(exist_ok=True)
    data.rowcopy = dict(data.row)
    card = yaml.safe_dump({"display_name": "Orbit 9", "benchmarks": {"scores": {}, "evidence": [data.row, dict(data.row)]}})
    (data.root / "models/acme/orbit-9.md").write_text(f"---\n{card}---\n")
    refused("reading_ambiguous")


def test_a_score_outside_the_board_range_is_refused(data):
    refused("value_invalid", readers=pair(151.2))


def test_a_cleared_row_reappears_with_its_mark_cleared(data):
    data.row["not_published_since"] = "2026-11-01"
    data.write()
    assert run().record["clears_not_published_since"] is True


def test_a_reappearing_row_with_an_unchanged_score_still_clears_the_mark(data):
    data.row["not_published_since"] = "2026-11-01"
    data.write()
    out = run(readers=pair(46.6))
    assert out.changed and out.record["clears_not_published_since"] is True
    assert out.record["value"] == 46.6


# --- no longer published --------------------------------------------------------------------------


def _absent(**kw):
    return run(readers=pair(None), request=serve(GONE), **kw)


def _age(data, index, delta):
    """Move a logged attempt back in time, as a later run would find it."""
    log = data.log()
    log[index]["at"] = (datetime.now(UTC) - delta).replace(microsecond=0).isoformat()
    (data.root / ATTEMPTS_FILE).write_text("".join(json.dumps(x) + "\n" for x in log))
    return log[index]["at"]


def test_one_absent_read_is_pending_and_marks_nothing(data):
    out = _absent()
    assert out.outcome == "absence_pending" and not out.changed and not out.marked
    assert out.record["reads"] == 1 and "not_published_since" not in out.record
    assert len(data.log()) == 1


def test_a_second_read_inside_24_hours_stays_pending(data):
    _absent()
    _age(data, 0, timedelta(hours=23))
    assert _absent().outcome == "absence_pending"


def test_two_absent_reads_24_hours_apart_mark_the_row(data):
    _absent()
    first = _age(data, 0, ABSENCE_GAP + timedelta(minutes=1))
    out = _absent()
    assert out.marked and out.record["not_published_since"] == first[:10]
    assert out.record["reads"] == 2 and "value" not in out.record


def test_a_model_that_reappears_clears_the_pending_absence(data):
    _absent()
    _age(data, 0, timedelta(days=2))
    assert run(readers=pair(51.2)).changed       # it is listed again
    assert pending_absences(attempts(SUBJECT, "benchmark:" + BENCH, reading_epoch(READING))) == []
    assert _absent().outcome == "absence_pending"   # a new absence starts a new count


def test_readers_split_on_presence_do_not_mark_absence(data):
    refused("readers_disagree", readers=pair(None, 51.2), request=serve(GONE))


def test_the_log_keeps_no_page_text(data):
    _absent()
    assert "Rival" not in json.dumps(data.log())


# --- the harness writes through the refresh writer ------------------------------------------------


def _card(data, extra=""):
    row = (
        "  - benchmark_id: boardbench_1\n    model_id_as_evaluated: Orbit 9 (max)\n    score: 46.6\n"
        "    unit: percent\n    source_url: https://cursor.com/cursorbench\n"
        "    source_kind: benchmark_author\n    evidence_date: '2026-10-19'\n    date_type: evaluated\n"
        "    verified_at: '2026-10-19'\n    benchmark_version: Board 1\n"
        "    configuration: Board read 2026-10-19.\n    limitations: x\n"
        "    id: acme/orbit-9#boardbench_1#aaaaaaaaaaaa\n    measured_by: benchmark_author\n"
        "    effort: max\n    harness: null\n    sources:\n    - source_id: board\n"
        f"      snapshot_ref: sha256:{'0' * 64}\n      cited_regions:\n      - rows\n"
        f"    observed_at: '2026-10-19'\n{extra}")
    (data.root / "models/acme/orbit-9.md").write_text(
        f"---\ndisplay_name: Orbit 9\nmodel_id: acme/orbit-9\nbenchmarks:\n  scores: {{}}\n  evidence:\n{row}deployment:\n  x: 1\n---\n")


def test_the_harness_writes_a_changed_score_and_a_mark_through_the_writer(data):
    from scripts import cited_reading

    data.bench["metric"]["unit"] = "percent"
    data.write()
    _card(data)
    counts = cited_reading.run(data.root, BENCH, "board", pair(), request=serve())
    assert counts == {"cited_change": 1}
    row = yaml.safe_load((data.root / "models/acme/orbit-9.md").read_text().split("---", 2)[1])["benchmarks"]["evidence"][0]
    assert row["score"] == 51.2 and row["observed_at"] == datetime.now(UTC).date().isoformat()
    assert row["sources"][0]["snapshot_ref"].startswith("sha256:") and "not_published_since" not in row
    assert row["id"] != "acme/orbit-9#boardbench_1#aaaaaaaaaaaa"
    block = row["derivation"]["cited_change"]
    assert block["rule"] == gate.RULE and block["sha256"] and block["read_date"] and block["url"] == URL
    assert [r["family"] for r in block["readers"]] == ["anthropic", "mistral"]
    assert all(r["prompt_sha256"] and r["manifest"] for r in block["readers"])
    assert "PAGEMARK" not in (data.root / "models/acme/orbit-9.md").read_text()
    # the rolling re-read sees the reading
    found = cited_change_readings(data.root)
    assert [f["target"].split("#")[0] for f in found] == [SUBJECT]
    assert found[0]["reading"] == READING
    # a second reading's absence: age the first absent read, then mark
    t = datetime.now(UTC)
    log = data.log()
    log[0]["at"] = (t - timedelta(days=5)).replace(microsecond=0).isoformat()
    (data.root / ATTEMPTS_FILE).write_text("".join(json.dumps(x) + "\n" for x in log))
    for at in (t - timedelta(days=2), None):
        cited_reading.run(data.root, BENCH, "board", pair(None), request=serve(GONE))
        if at:
            log = data.log()
            log[-1]["at"] = at.replace(microsecond=0).isoformat()
            (data.root / ATTEMPTS_FILE).write_text("".join(json.dumps(x) + "\n" for x in log))
    row = yaml.safe_load((data.root / "models/acme/orbit-9.md").read_text().split("---", 2)[1])["benchmarks"]["evidence"][0]
    assert row["not_published_since"] == (t - timedelta(days=2)).date().isoformat()
    assert row["score"] == 51.2


def test_a_cost_in_the_configuration_keeps_its_own_read_day():
    from scripts.cited_reading import dated_cost

    text = "Board read 2026-11-23; max effort; $11.95 a task."
    out = dated_cost(text, "2026-10-19")
    assert out == "Board read 2026-11-23; max effort; $11.95 a task (cost read 2026-10-19)."
    assert dated_cost(out, "2026-11-23") == out
