"""MODEL-544: the rule-15 gate takes offering facts, and an agreed not_disclosed change."""

import json
import socket
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from decision.cited_change import (
    MIN_SILENT_TEXT, OFFERING_CLAUSE, REFUSALS, cited_change, cited_change_facts, lookup, reread,
)
from decision.cited_reader import (
    ATTEMPTS_FILE, MAX_PAGE_CHARS, Reader, build_prompt, facet_definition, sha256,
)
from scripts import cited_offering as writer

SUBJECT = "openai/openai/gpt-x/global/standard"
FACT_ID = f"{SUBJECT}#offering.data.retention"
SOC2_ID = f"{SUBJECT}#offering.attestation.soc2"
URL = "https://developers.openai.com/api/docs/guides/your-data"
TRUST = "https://developers.openai.com/trust"
OTHER = "https://developers.openai.com/api/docs/other"
HF = "https://huggingface.co/openai/gpt-x"
FILLER = " ".join(f"Section {i} describes how the service handles requests." for i in range(30))
PAGE = f"<html><body>{FILLER} Abuse monitoring logs are kept for up to 30 days. SECRET-PAGE-MARKER</body></html>".encode()
SILENT = f"<html><body>{FILLER} SECRET-PAGE-MARKER</body></html>".encode()
HEADER = "# A comment the writer keeps.\n"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


def reader(rid, family, value):
    return Reader(rid, family, "1.0", lambda prompt: f'<<<JSON {{"value": {json.dumps(value)}}} JSON>>>')


def pair(value=30, other=None):
    return [reader("codex", "openai", value), reader("claude", "anthropic", value if other is None else other)]


def serve(pages=None):
    pages = {URL: PAGE, TRUST: SILENT} if pages is None else pages
    calls = []

    def request(url):
        calls.append(url)
        page = pages[url]
        return page if isinstance(page, tuple) else (200, None, page)
    request.calls = calls
    return request


def ref(source_id):
    return {"source_id": source_id, "snapshot_ref": "sha256:" + "0" * 64, "cited_regions": ["page"]}


class Data:
    def __init__(self, root: Path, monkeypatch):
        self.root = root
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
        page_region = [dict(id="page", locator=dict(kind="page", value=""))]
        self.sources = [
            dict(id="data", url=URL, kind="provider_documentation", publisher="openai",
                 fetch="conditional_http", normaliser="text-default", cited_regions=page_region),
            dict(id="trust", url=TRUST, kind="provider_trust_center", publisher="openai",
                 fetch="conditional_http", normaliser="text-default", cited_regions=page_region),
            dict(id="other", url=OTHER, kind="provider_documentation", publisher="openai",
                 fetch="conditional_http", normaliser="text-default", cited_regions=page_region),
            dict(id="hf", url=HF, kind="provider_documentation", publisher="openai",
                 fetch="conditional_http", normaliser="text-default", cited_regions=page_region),
        ]
        self.facts = [
            {"id": FACT_ID, "subject": {"kind": "offering", "id": SUBJECT},
             "facet": "offering.data.retention", "value": None, "state": "not_disclosed",
             "checked_sources": ["data"], "verification": None, "sources": [ref("data")]},
            {"id": SOC2_ID, "subject": {"kind": "offering", "id": SUBJECT},
             "facet": "offering.attestation.soc2", "value": "type_2", "state": "known",
             "checked_sources": ["trust"], "verification": None, "sources": [ref("trust")]},
        ]
        self.write()

    @property
    def offering_path(self):
        return self.root / "offerings/openai/openai/gpt-x.yaml"

    def write(self):
        (self.root / "models/openai").mkdir(parents=True, exist_ok=True)
        (self.root / "registry").mkdir(exist_ok=True)
        self.offering_path.parent.mkdir(parents=True, exist_ok=True)
        card = yaml.safe_dump({"display_name": "GPT X", "facts": []}, sort_keys=False)
        (self.root / "models/openai/gpt-x.md").write_text(f"---\n{card}---\nbody\n")
        rows = [{"model": "openai/gpt-x", "provider": "openai", "region": "global",
                 "tier": "standard", "facts": self.facts}]
        self.offering_path.write_text(HEADER + yaml.safe_dump(rows, sort_keys=False))
        (self.root / "registry/sources.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "sources": self.sources}))
        (self.root / "registry/providers.yaml").write_text(yaml.safe_dump(
            {"providers": [{"id": "openai", "name": "OpenAI API", "url": "https://platform.openai.com/"},
                           {"id": "google-vertex-ai", "name": "Vertex AI",
                            "url": "https://cloud.google.com/vertex-ai"}]}))

    def fact(self, fact_id=FACT_ID, **kw):
        next(f for f in self.facts if f["id"] == fact_id).update(kw)
        self.write()

    def log(self):
        path = self.root / ATTEMPTS_FILE
        return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []

    def events(self):
        path = self.root / "verification/queue/events.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def retention(**kw):
    args = dict(subject=SUBJECT, facet="offering.data.retention", source_id="data",
                readers=pair(), request=serve())
    args.update(kw)
    return cited_change(**args)


def soc2(**kw):
    args = dict(subject=SUBJECT, facet="offering.attestation.soc2", source_id="trust",
                readers=pair(None), request=serve(), accept_not_disclosed=True)
    args.update(kw)
    return cited_change(**args)


def refused(out, reason):
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS


def snapshot(data):
    """Every file under the data directory but the attempt log, byte for byte."""
    return {p.relative_to(data.root).as_posix(): p.read_bytes() for p in data.root.rglob("*")
            if p.is_file() and p.relative_to(data.root).as_posix() != ATTEMPTS_FILE}


# --- offering facts ------------------------------------------------------------------------------


def test_an_offering_fact_with_two_agreeing_readers_is_a_cited_change(data):
    out = retention()
    assert out.changed, (out.reason, out.detail)
    rec = out.record
    assert rec["subject"] == SUBJECT and rec["value"] == 30 and rec["state"] == "known"
    assert rec["resolution"] == "cited" and rec["source"]["snapshot_ref"] == "sha256:" + sha256(PAGE)
    block = rec["derivation"]["cited_change"]
    assert block["previous_value"] is None and block["previous_sources"] == ["data"]
    assert [r["family"] for r in block["readers"]] == ["openai", "anthropic"]
    assert "SECRET-PAGE-MARKER" not in json.dumps(rec)


def test_offering_readers_are_told_the_subject_is_an_offering(data):
    seen = []
    spy = Reader("codex", "openai", "1.0", lambda p: seen.append(p) or '<<<JSON {"value": 30} JSON>>>')
    assert retention(readers=[spy, reader("claude", "anthropic", 30)]).changed
    assert "GPT X, as OpenAI API serves it" in seen[0]
    assert OFFERING_CLAUSE.strip() in seen[0]
    found = lookup(SUBJECT, "offering.data.retention")
    assert found.kind == "offering" and found.names == ("GPT X",)
    assert found.definition == facet_definition("offering.data.retention") + OFFERING_CLAUSE


def test_a_planted_disagreement_on_an_offering_fact_files_nothing(data):
    before = snapshot(data)
    out = retention(readers=pair(30, 45))
    refused(out, "readers_disagree")
    assert snapshot(data) == before
    (entry,) = data.log()
    assert entry["complete"] and entry["agreed"] is False
    refused(retention(), "prior_attempt_disagreed")  # a later clean read cannot be used
    assert snapshot(data) == before


def test_the_writer_files_nothing_on_a_refusal(data):
    out = retention(readers=pair(30, 45))
    with pytest.raises(writer.WriteRefused):
        writer.apply(out, data_dir=data.root)
    assert not data.events()


def test_an_offering_fact_is_first_party_only_for_its_provider(data):
    data.sources[0]["publisher"] = "someone-else"
    data.write()
    refused(retention(), "not_first_party")
    data.sources[0].pop("publisher")
    data.write()
    refused(retention(), "not_first_party")


def test_the_retaining_host_and_kind_rules_hold_for_offerings(data):
    data.fact(sources=[ref("data"), ref("hf")])
    refused(retention(), "retaining_source_registered")
    data.fact(sources=[ref("data")])
    data.sources[0]["kind"] = "lab_documentation"
    data.write()
    refused(retention(), "source_kind_not_permitted")


def test_an_offering_lookup_fails_closed(data):
    refused(retention(subject="openai/openai/gpt-y/global/standard"), "registry_lookup_failed")
    refused(retention(subject="openai/openai/../../etc"), "registry_lookup_failed")
    refused(retention(facet="model.context_window"), "registry_lookup_failed")
    refused(cited_change(subject="openai/gpt-x", facet="offering.data.retention", source_id="data",
                         readers=pair(), request=serve()), "registry_lookup_failed")
    data.facts.append(dict(data.facts[0]))  # the fact twice is no fact
    data.write()
    refused(retention(), "registry_lookup_failed")


def test_the_writer_keeps_the_offering_reference_and_the_claim_on_one_copy(data):
    before = data.offering_path.read_text()
    out = retention()
    path = writer.apply(out, data_dir=data.root)
    assert path == data.offering_path
    after = path.read_text()
    assert after.startswith(HEADER)  # every other line is kept
    rows = yaml.safe_load(after)
    fact = next(f for f in rows[0]["facts"] if f["id"] == FACT_ID)
    assert fact["value"] == 30 and fact["state"] == "known"
    assert fact["derivation"]["cited_change"]["sha256"] == sha256(PAGE)
    assert fact["checked_sources"] == ["data"] and "verification" in fact
    other_before = next(f for f in yaml.safe_load(before)[0]["facts"] if f["id"] == SOC2_ID)
    assert next(f for f in rows[0]["facts"] if f["id"] == SOC2_ID) == other_before
    collected, checked = data.events()
    assert collected["event"] == "collected" and checked["event"] == "checked"
    assert checked["outcome"] == "cited" and checked["target"]["id"] == FACT_ID
    claim = collected["claim"]
    assert claim["target"] == {"kind": "fact", "id": FACT_ID} and claim["value"] == 30
    assert claim["unit"] == "days" and claim["names"] == ["GPT X"] and claim["state"] == "known"
    (ref_,), (claimed,) = fact["sources"], claim["sources"]
    # the MODEL-542 check: the same snapshot_ref and the same retrieved_at instant
    assert ref_["snapshot_ref"] == claimed["snapshot_ref"] == out.record["source"]["snapshot_ref"]
    assert datetime.fromisoformat(ref_["retrieved_at"].replace("Z", "+00:00")) \
        == datetime.fromisoformat(claimed["retrieved_at"].replace("Z", "+00:00"))
    assert "SECRET-PAGE-MARKER" not in after + json.dumps(data.events())
    # no quarantine is lifted: nothing is written to the verification log
    assert not (data.root / "verification/log.jsonl").exists()
    assert not (data.root / "verification/supersessions.jsonl").exists()


def test_the_rewrite_refuses_to_touch_another_fact():
    text = HEADER + yaml.safe_dump([{"model": "m", "facts": [
        {"id": "a", "value": 1}, {"id": "b", "value": 2}]}], sort_keys=False)
    after = writer.rewrite(text, "a", {"id": "a", "value": 3})
    writer.check_rewrite(text, after, "a", {"id": "a", "value": 3})
    with pytest.raises(writer.WriteRefused):
        writer.check_rewrite(text, after.replace("value: 2", "value: 9"), "a", {"id": "a", "value": 3})
    with pytest.raises(writer.WriteRefused):
        writer.rewrite(text, "missing", {"id": "missing"})


def test_a_cited_offering_fact_is_listed_for_the_rolling_reread(data):
    writer.apply(retention(), data_dir=data.root)
    listed = cited_change_facts(data.root)
    assert [(f["subject"], f["facet"], f["source_id"]) for f in listed] == [
        (SUBJECT, "offering.data.retention", "data")]
    fact = lookup(SUBJECT, "offering.data.retention").fact | {"subject": SUBJECT}
    out = reread(fact, source_id="data", readers=[], request=serve())
    assert out.outcome == "current"


# --- not_disclosed -------------------------------------------------------------------------------


def test_not_disclosed_files_when_both_readers_find_the_page_silent(data):
    out = soc2()
    assert out.changed, (out.reason, out.detail)
    rec = out.record
    assert rec["value"] is None and rec["state"] == "not_disclosed" and rec["resolution"] == "cited"
    block = rec["derivation"]["cited_change"]
    assert block["previous_value"] == "type_2"
    assert [(r["value"], r["finding"]) for r in block["readers"]] == [(None, "not_stated")] * 2
    writer.apply(out, data_dir=data.root)
    fact = next(f for f in yaml.safe_load(data.offering_path.read_text())[0]["facts"]
                if f["id"] == SOC2_ID)
    assert fact["value"] is None and fact["state"] == "not_disclosed"
    claim = data.events()[0]["claim"]
    assert claim["value"] is None and claim["state"] == "not_disclosed"


def test_one_reader_dissenting_from_silence_files_nothing(data):
    before = snapshot(data)
    refused(soc2(readers=pair(None, "type_2")), "readers_disagree")
    refused(soc2(), "prior_attempt_disagreed")
    assert snapshot(data) == before


def test_silence_is_no_change_unless_the_caller_asks(data):
    refused(soc2(accept_not_disclosed=False), "no_value")


def test_silence_on_a_page_too_short_or_truncated_proves_nothing(data):
    refused(soc2(request=serve({TRUST: b"<html><body>Loading...</body></html>"})), "page_too_short")
    assert len(FILLER) >= MIN_SILENT_TEXT
    long = ("<html><body>" + "word " * (MAX_PAGE_CHARS // 4) + "</body></html>").encode()
    refused(soc2(request=serve({TRUST: long})), "page_truncated")


def test_silence_on_one_page_is_not_silence_on_another_the_fact_cites(data):
    data.fact(SOC2_ID, checked_sources=["trust", "other"])
    refused(soc2(), "other_source_unread")


def test_silence_after_an_agreed_value_is_a_conflict(data):
    (data.root / "verification").mkdir(parents=True, exist_ok=True)
    (data.root / ATTEMPTS_FILE).write_text(json.dumps({
        "subject": SUBJECT, "facet": "offering.attestation.soc2", "url": OTHER, "epoch": "initial",
        "complete": True, "harness": True, "agreed": True, "agreed_value": "type_2"}) + "\n")
    refused(soc2(), "prior_attempt_disagreed")


def test_a_value_after_agreed_silence_is_a_conflict(data):
    assert soc2().changed
    refused(soc2(readers=pair("type_1")), "prior_attempt_disagreed")


def test_not_disclosed_filed_already_is_unchanged(data):
    data.fact(SOC2_ID, value=None, state="not_disclosed")
    refused(soc2(), "value_unchanged")


def test_a_reread_confirms_a_cited_not_disclosed_fact(data):
    writer.apply(soc2(), data_dir=data.root)
    fact = lookup(SUBJECT, "offering.attestation.soc2").fact | {"subject": SUBJECT}
    changed = SILENT.replace(b"Section 1 ", b"Section one ")
    out = reread(fact, source_id="trust", readers=pair(None),
                 request=serve({TRUST: changed}))
    assert out.outcome == "confirmed" and out.record["state"] == "not_disclosed"


# --- card facts are as they were -----------------------------------------------------------------


def test_a_card_prompt_is_the_registry_definition_alone(data):
    prompt = build_prompt(url=URL, facet_id="model.context_window", subject_name="GPT X",
                          page_bytes=PAGE)
    assert OFFERING_CLAUSE.strip() not in prompt
    assert facet_definition("model.context_window") in prompt
