"""MODEL-531: a cite-only page may change a value when two readers of different families agree."""

import json
import socket
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from decision.cited_change import (
    KNOWN_FAMILIES, REFUSALS, cited_change, cited_change_block, cited_change_facts, lookup,
    reread, reread_required,
)
from decision.cited_reader import (
    Reader, ReaderAnswer, ReaderError, build_prompt, input_manifest, parse_answer, read_page, sha256,
)

FACET = "model.context_window"
SUBJECT = "xai/grok-x"
URL = "https://docs.x.ai/docs/models/grok-x"
HF = "https://huggingface.co/xai/grok-x"
PAGE = b"<html><body>Grok X token limit 262144 SECRET-PAGE-MARKER</body></html>"
READ_AT = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


def reader(rid, family, value=262144, version="1.0"):
    return Reader(rid, family, version, lambda prompt: f'<<<JSON {{"value": {json.dumps(value)}}} JSON>>>')


class Data:
    def __init__(self, root: Path, monkeypatch):
        self.root = root
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
        self.sources = [
            dict(id="s1", url=URL, kind="lab_documentation", publisher="xai", fetch="conditional_http",
                 normaliser="text-default", cited_regions=[dict(id="page", locator=dict(kind="page", value=""))]),
            dict(id="hf", url=HF, kind="lab_documentation", publisher="xai", fetch="conditional_http",
                 normaliser="text-default", cited_regions=[dict(id="page", locator=dict(kind="page", value=""))]),
        ]
        self.fact = dict(facet=FACET, value=131072, state="known",
                         sources=[dict(source_id="s1", snapshot_ref="sha256:" + "0" * 64,
                                       cited_regions=["page"])], checked_sources=[])
        self.redirects = None
        self.write()

    def write(self):
        (self.root / "models/xai").mkdir(parents=True, exist_ok=True)
        (self.root / "registry").mkdir(exist_ok=True)
        card = yaml.safe_dump({"display_name": "Grok X", "facts": [self.fact]}, sort_keys=False)
        (self.root / "models/xai/grok-x.md").write_text(f"---\n{card}---\nbody\n")
        (self.root / "registry/sources.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "sources": self.sources}))
        if self.redirects is not None:
            (self.root / "registry/source-redirects.json").write_text(json.dumps(self.redirects))

    def source(self, sid="s1", **kw):
        next(s for s in self.sources if s["id"] == sid).update(kw)
        self.write()


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def answers(value=262144, page=PAGE, a=("codex", "gpt-5"), b=("grok", "xai")):
    return read_page(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=page,
                     readers=[reader(a[0], a[1], value), reader(b[0], b[1], value)])


def run(**kw):
    args = dict(subject=SUBJECT, facet=FACET, source_id="s1", read_at=READ_AT, page_bytes=PAGE,
                answers=answers())
    args.update(kw)
    return cited_change(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS


# --- every condition holds -----------------------------------------------------------------------


def test_all_conditions_hold_writes_cited_record_with_manifests(data):
    out = run()
    assert out.changed and out.reason is None
    rec = out.record
    assert rec["value"] == 262144 and rec["resolution"] == "cited" and rec["state"] == "known"
    assert rec["source"]["snapshot_ref"] == "sha256:" + sha256(PAGE)
    assert rec["source"]["retrieved_at"] == "2026-11-20T12:00:00+00:00"
    block = rec["derivation"]["cited_change"]
    assert "cited_change" not in rec
    assert block["sha256"] == sha256(PAGE) and block["url"] == URL and block["read_date"] == "2026-11-20"
    assert [r["family"] for r in block["readers"]] == ["gpt-5", "xai"]
    for r in block["readers"]:
        assert r["reader_id"] and r["version"] and r["prompt_sha256"]
        assert r["manifest"]["fields"] == ["url", "facet", "facet_definition", "subject_name", "page"]
        assert "filed_value" not in json.dumps(r["manifest"])
    assert "SECRET-PAGE-MARKER" not in json.dumps(rec)


def test_prompt_holds_only_the_four_inputs(data):
    prompt = build_prompt(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=PAGE)
    assert "131072" not in prompt and "262144" in prompt  # the page's own number, never the filed one
    assert input_manifest(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=PAGE)["fields"]
    with pytest.raises(ReaderError):
        parse_answer("no markers")
    with pytest.raises(ReaderError):
        parse_answer('<<<JSON {"value": 1, "extra": 2} JSON>>>')


# --- lookup --------------------------------------------------------------------------------------


def test_refuse_when_the_registry_lookup_fails(data, monkeypatch):
    refused("registry_lookup_failed", source_id="nope")
    refused("registry_lookup_failed", subject="xai/missing")
    refused("registry_lookup_failed", subject="../etc/passwd")
    refused("unknown_facet", facet="no.such.facet")
    data.fact["facet"] = "model.max_output_tokens"
    data.write()
    refused("registry_lookup_failed")  # the card has no such fact for this facet
    monkeypatch.delenv("MODELSPEC_DATA_DIR")
    refused("registry_lookup_failed")


# --- condition 1: the host -----------------------------------------------------------------------


def test_refuse_host_retains_copies(data):
    refused("host_not_cite_only", source_id="hf")


def test_refuse_malformed_url(data):
    data.source(url="https://")
    refused("host_unreadable")


# --- condition 2: kind and first party -----------------------------------------------------------


def test_refuse_kind_not_permitted_for_facet(data):
    data.source(kind="provider_terms")
    refused("source_kind_not_permitted")


def test_refuse_not_first_party(data):
    data.source(kind="weights_repository")
    refused("not_first_party")
    data.source(kind="lab_documentation", publisher="someone-else")
    refused("not_first_party")
    data.sources[0].pop("publisher")
    data.write()
    refused("not_first_party")


# --- condition 3: two readers, distinct known families, blind ------------------------------------


def test_refuse_reader_count(data):
    refused("reader_count", answers=answers()[:1])
    refused("reader_count", answers=answers() * 2)


def test_refuse_reader_metadata_missing(data):
    a, b = answers()
    refused("reader_metadata_missing", answers=[a, ReaderAnswer(b.reader_id, b.family, "", b.value,
                                                                b.prompt_sha256, b.manifest)])
    refused("reader_metadata_missing", answers=[a, ReaderAnswer("", b.family, b.version, b.value,
                                                                b.prompt_sha256, b.manifest)])


@pytest.mark.parametrize("family", ["gpt-5", "openai", "unknown", "other", "unrecorded",
                                    "deterministic", "foobar-lab", "Unlisted-Family"])
def test_refuse_a_family_that_is_not_a_distinct_known_lineage(data, family):
    refused("reader_families_not_distinct", answers=answers(a=("codex", "gpt-5"), b=("x", family)))


def test_known_families_are_the_lineages(data):
    assert {"openai", "anthropic", "xai"} <= KNOWN_FAMILIES
    assert run(answers=answers(a=("codex", "openai"), b=("claude", "anthropic"))).changed


def test_refuse_same_reader_id(data):
    refused("reader_families_not_distinct", answers=answers(a=("same", "gpt-5"), b=("same", "xai")))


def test_refuse_missing_input_records(data):
    a, b = answers()
    refused("reader_input_missing", answers=[a, ReaderAnswer(b.reader_id, b.family, b.version, b.value)])
    refused("reader_input_missing", answers=[a, ReaderAnswer(b.reader_id, b.family, b.version, b.value,
                                                             b.prompt_sha256, None)])


def test_refuse_a_reader_shown_the_filed_value_or_the_other_answer(data):
    a, b = answers()
    leaked = build_prompt(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=PAGE) \
        + "\nFiled value: 131072"
    refused("reader_input_not_blind", answers=[a, ReaderAnswer(
        b.reader_id, b.family, b.version, b.value, sha256(leaked), b.manifest)])
    extra = {**b.manifest, "fields": [*b.manifest["fields"], "filed_value"],
             "input_sha256": {**b.manifest["input_sha256"], "filed_value": sha256("131072")}}
    refused("reader_input_not_blind", answers=[a, ReaderAnswer(
        b.reader_id, b.family, b.version, b.value, b.prompt_sha256, extra)])
    refused("reader_input_not_blind", answers=[a, ReaderAnswer(
        b.reader_id, b.family, b.version, b.value, b.prompt_sha256,
        {**b.manifest, "input_sha256": {**b.manifest["input_sha256"], "page": sha256("x")}})])


def test_refuse_readers_that_read_other_bytes_than_the_page_given(data):
    refused("reader_input_not_blind", answers=answers(page=b"<html>another page</html>"))


def test_refuse_disagreement(data):
    a, _ = answers()
    _, b = answers(value=1000000)
    refused("readers_disagree", answers=[a, b])


def test_refuse_no_value_and_invalid_value(data):
    refused("no_value", answers=answers(value=None))
    refused("value_invalid", answers=answers(value="big"))


def test_refuse_excerpt_sized_string(data):
    data.fact.update(facet="origin.lab_jurisdiction", value=["US"])
    data.write()
    long = "x" * 500
    refused("value_invalid", facet="origin.lab_jurisdiction", answers=read_page(
        url=URL, facet_id="origin.lab_jurisdiction", subject_name="Grok X", page_bytes=PAGE,
        readers=[reader("a", "gpt-5", [long]), reader("b", "xai", [long])]))


def test_set_values_compare_unordered(data):
    data.fact.update(facet="origin.lab_jurisdiction", value=["US"])
    data.write()
    got = read_page(url=URL, facet_id="origin.lab_jurisdiction", subject_name="Grok X",
                    page_bytes=PAGE, readers=[reader("a", "gpt-5", ["US", "GB"]),
                                              reader("b", "xai", ["GB", "US"])])
    assert run(facet="origin.lab_jurisdiction", answers=got).changed


def test_refuse_unchanged_value(data):
    refused("value_unchanged", answers=answers(value=131072))


def test_refuse_bad_read_date(data):
    refused("bad_read_date", read_at=datetime(2026, 11, 20))
    refused("bad_read_date", read_at=datetime.now(UTC) + timedelta(days=2))


# --- condition 5: a retaining source wins (looked up, not supplied) ------------------------------


def test_refuse_retaining_source_registered_for_the_subject_and_facet(data):
    data.fact["sources"].append(dict(source_id="hf", snapshot_ref="sha256:" + "1" * 64,
                                     cited_regions=["page"]))
    data.write()
    refused("retaining_source_registered")


def test_refuse_a_checked_retaining_source_and_unreadable_and_unregistered(data):
    data.fact["checked_sources"] = ["hf"]
    data.write()
    refused("retaining_source_registered")
    data.source("hf", url="https://")
    refused("retaining_source_unreadable")
    data.fact["checked_sources"] = ["ghost"]
    data.write()
    refused("registry_lookup_failed")


def test_a_retaining_source_that_now_redirects_to_a_cite_only_host_is_not_a_path(data):
    data.fact["checked_sources"] = ["hf"]
    data.redirects = {"hf": {"to": "https://docs.x.ai/docs/other"}}
    data.write()
    assert run().changed
    data.redirects = {"hf": {"to": "https://example.org/other"}}
    data.write()
    refused("retaining_source_registered")


def test_a_retaining_source_of_another_kind_is_not_for_this_facet(data):
    data.source("hf", kind="licence_text")  # not a permitted kind for context_window
    data.fact["checked_sources"] = ["hf"]
    data.write()
    assert run().changed
    data.source("hf", kind="weights_repository")  # permitted: it is a path for this facet
    refused("retaining_source_registered")


# --- the re-read: runtime path, record exactly as cited_change returns it ------------------------


def cited_card(data, record):
    data.fact = {"facet": record["facet"], "value": record["value"], "state": "known",
                 "sources": [record["source"]], "checked_sources": [], "derivation": record["derivation"]}
    data.write()
    return data.fact | {"subject": SUBJECT}


def test_runtime_record_is_found_and_reread_triggers_on_a_changed_sha(data):
    record = run().record
    assert cited_change_block({"derivation": record["derivation"]}) is not None
    fact = cited_card(data, record)
    assert [(f["subject"], f["facet"]) for f in cited_change_facts(data.root)] == [(SUBJECT, FACET)]
    assert not reread_required(fact, sha256(PAGE))
    assert reread_required(fact, sha256(PAGE + b" changed"))
    assert not reread_required({"subject": SUBJECT, "facet": FACET, "value": 1}, "f" * 64)
    assert lookup(SUBJECT, FACET).fact["derivation"]["cited_change"]["sha256"] == sha256(PAGE)


def reread_with(fact, page, **kw):
    kw.setdefault("answers", answers(page=page, value=kw.pop("value", 262144)))
    return reread(fact, source_id="s1", read_at=READ_AT, page_bytes=page, **kw)


def test_reread_unchanged_page_needs_no_read(data):
    fact = cited_card(data, run().record)
    assert reread(fact, source_id="s1", read_at=READ_AT, page_bytes=PAGE, answers=[]).outcome == "current"


def test_reread_changed_sha_confirms_or_changes_with_two_readers(data):
    fact = cited_card(data, run().record)
    page = PAGE + b" v2"
    out = reread_with(fact, page)
    assert out.outcome == "confirmed" and out.record["derivation"]["cited_change"]["sha256"] == sha256(page)
    out = reread_with(fact, page, value=5)
    assert out.outcome == "changed" and out.record["value"] == 5


def test_reread_changed_sha_one_reader_or_disagreement_flags(data):
    fact = cited_card(data, run().record)
    page = PAGE + b" v2"
    one = reread_with(fact, page, answers=answers(page=page)[:1])
    assert one.outcome == "flagged" and one.reason == "reader_count"
    a, _ = answers(page=page)
    _, b = answers(page=page, value=7)
    dis = reread_with(fact, page, answers=[a, b])
    assert dis.outcome == "flagged" and dis.reason == "readers_disagree" and dis.record is None


def test_reread_of_plain_fact_flags(data):
    out = reread({"subject": SUBJECT, "facet": FACET}, source_id="s1", read_at=READ_AT,
                 page_bytes=PAGE, answers=[])
    assert out.reason == "not_a_cited_change"


# --- the rolling re-read script ------------------------------------------------------------------


def test_the_rolling_reread_flags_a_cited_change_fact_whose_page_hash_changed(data, tmp_path):
    from scripts import evidence_reread as script

    cited_card(data, run().record)
    (data.root / "registry/source-terms.json").write_text("{}")
    calls = []

    def serve(body):
        def request(url):
            calls.append(url)
            return 200, None, body
        return request

    def sweep(body):
        report = script.Report("2026-11-23", True)
        script.cited_change_rereads(data.root, script.load_terms(data.root), report,
                                    request=serve(body), pacer=script.Pacer(0, sleep=lambda s: None))
        return report

    assert sweep(PAGE).cited_change_rereads == []
    report = sweep(PAGE + b" new")
    assert report.cited_change_rereads == [f"{SUBJECT}#{FACET}"]
    assert report.to_dict()["cited_change_rereads_required"] == [f"{SUBJECT}#{FACET}"]
    assert set(calls) == {URL}


def test_the_rolling_reread_run_reports_it(data, tmp_path):
    from scripts import evidence_reread as script

    cited_card(data, run().record)
    (data.root / "registry/source-terms.json").write_text("{}")
    report = script.run(data.root, observed_at=READ_AT.date() + timedelta(days=3), dry_run=True,
                        store_root=tmp_path / "cache", request=lambda url: (200, None, PAGE + b"!"),
                        pacer=script.Pacer(0, sleep=lambda s: None))
    assert report.cited_change_rereads == [f"{SUBJECT}#{FACET}"]
    assert not [p for p in (tmp_path / "cache").rglob("*") if p.is_file()], "no page bytes kept"
