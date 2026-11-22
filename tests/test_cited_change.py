"""MODEL-531: a cite-only page may change a value when two readers of different families agree."""

from dataclasses import replace
from datetime import date

import pytest

from decision.cited_change import (
    REFUSALS, CitedSource, ReaderAnswer, RegisteredSource, cited_change, cited_change_block,
    reread, reread_required,
)

FACET = "model.context_window"
SHA = "a" * 64
SHA2 = "b" * 64
URL = "https://docs.x.ai/docs/models/grok-x"


@pytest.fixture(autouse=True)
def _public_list_only(monkeypatch):
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)


def src(**kw):
    base = dict(source_id="s1", url=URL, kind="lab_documentation", read_date=date(2026, 11, 20),
                sha256=SHA, publisher="xai")
    return CitedSource(**{**base, **kw})


def ans(rid="codex", family="openai", value=262144, **kw):
    return ReaderAnswer(rid, family, kw.pop("version", "1.0"), value, kw.pop("blind", True))


def run(**kw):
    args = dict(subject="xai/grok-x", facet=FACET, filed_value=131072, source=src(),
                answers=[ans(), ans("grok", "xai", 262144)],
                registered_sources=[RegisteredSource("s1", URL)], owners=("xai",))
    args.update(kw)
    return cited_change(**args)


def test_all_conditions_hold_writes_cited_record():
    out = run()
    assert out.changed and out.reason is None
    rec = out.record
    assert rec["value"] == 262144 and rec["resolution"] == "cited" and rec["state"] == "known"
    assert rec["source"]["snapshot_ref"] == "sha256:" + SHA
    block = rec["cited_change"]
    assert block["sha256"] == SHA and block["url"] == URL and block["read_date"] == "2026-11-20"
    assert [r["family"] for r in block["readers"]] == ["openai", "xai"]
    assert all(r["reader_id"] and r["version"] for r in block["readers"])
    assert "text" not in str(rec).lower().replace("context", "")


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason and out.record is None
    assert reason in REFUSALS


def test_refuse_host_retains_copies():
    u = "https://huggingface.co/x/y"
    refused("host_not_cite_only", source=src(url=u), registered_sources=[])


def test_refuse_malformed_url():
    refused("host_unreadable", source=src(url="https://"))


def test_refuse_redirect_to_retaining_host():
    refused("host_not_cite_only", source=src(resolved_urls=("https://huggingface.co/a",)))


def test_refuse_kind_not_permitted_for_facet():
    refused("source_kind_not_permitted", source=src(kind="provider_terms"))


def test_refuse_not_first_party():
    refused("not_first_party", source=src(kind="weights_repository"))
    refused("not_first_party", source=src(publisher="someone-else"))


def test_refuse_reader_count():
    refused("reader_count", answers=[ans()])
    refused("reader_count", answers=[ans(), ans("grok", "xai"), ans("q", "qwen")])


def test_refuse_reader_metadata_missing():
    refused("reader_metadata_missing", answers=[ans(), ans("grok", "xai", version="")])
    refused("reader_metadata_missing", answers=[ans(), ans("", "xai")])


def test_refuse_reader_not_blind():
    refused("reader_not_blind", answers=[ans(), ans("grok", "xai", blind=False)])


def test_refuse_same_family():
    refused("reader_families_not_distinct", answers=[ans(), ans("codex2", "gpt-5")])
    refused("reader_families_not_distinct", answers=[ans(), ans("x", "unknown")])
    refused("reader_families_not_distinct", answers=[ans(), ans("x", "deterministic")])


def test_refuse_disagreement():
    refused("readers_disagree", answers=[ans(), ans("grok", "xai", 1000000)])


def test_refuse_no_value_and_invalid_value():
    refused("no_value", answers=[ans(value=None), ans("grok", "xai", None)])
    refused("value_invalid", answers=[ans(value="big"), ans("grok", "xai", "big")])


def test_refuse_excerpt_sized_string():
    long = "x" * 500
    out = cited_change(subject="xai/grok-x", facet="origin.lab_jurisdiction", filed_value=["US"],
                       source=src(kind="lab_documentation"),
                       answers=[ans(value=[long]), ans("grok", "xai", [long])],
                       registered_sources=[], owners=("xai",))
    assert out.reason == "value_invalid"


def test_refuse_unchanged_value():
    refused("value_unchanged", filed_value=262144)


def test_refuse_retaining_source_registered():
    refused("retaining_source_registered",
            registered_sources=[RegisteredSource("s1", URL),
                                RegisteredSource("hf", "https://huggingface.co/x/y")])
    refused("retaining_source_unreadable",
            registered_sources=[RegisteredSource("bad", "https://")])


def test_refuse_bad_sha_date_and_facet():
    refused("bad_sha256", source=src(sha256="abc"))
    refused("bad_read_date", source=src(read_date=date(2999, 1, 1)))
    refused("unknown_facet", facet="no.such.facet")


def test_set_values_compare_unordered():
    out = cited_change(subject="xai/grok-x", facet="origin.lab_jurisdiction", filed_value=["US"],
                       source=src(), answers=[ans(value=["US", "GB"]), ans("grok", "xai", ["GB", "US"])],
                       registered_sources=[], owners=("xai",))
    assert out.changed


# --- the re-read ---------------------------------------------------------------------------------


def fact():
    return {"subject": "xai/grok-x", "facet": FACET, "value": 262144,
            "derivation": {"cited_change": run().record["cited_change"]}}


def test_reread_triggers_only_on_sha_change_of_cited_change_fact():
    assert not reread_required(fact(), SHA)
    assert reread_required(fact(), SHA2)
    assert not reread_required({"subject": "a", "facet": FACET, "value": 1}, SHA2)
    assert cited_change_block({"derivation": None}) is None


def read(f, answers, source=None):
    return reread(f, source=source or src(sha256=SHA2), answers=answers,
                  registered_sources=[RegisteredSource("s1", URL)], owners=("xai",))


def test_reread_unchanged_sha_needs_no_read():
    assert reread(fact(), source=src(), answers=[], registered_sources=[]).outcome == "current"


def test_reread_changed_sha_confirms_with_two_readers():
    out = read(fact(), [ans(), ans("grok", "xai")])
    assert out.outcome == "confirmed" and out.record["cited_change"]["sha256"] == SHA2


def test_reread_changed_sha_new_value():
    out = read(fact(), [ans(value=5), ans("grok", "xai", 5)])
    assert out.outcome == "changed" and out.record["value"] == 5


def test_reread_changed_sha_one_reader_or_disagreement_flags():
    one = read(fact(), [ans()])
    assert one.outcome == "flagged" and one.reason == "reader_count"
    dis = read(fact(), [ans(), ans("grok", "xai", 7)])
    assert dis.outcome == "flagged" and dis.reason == "readers_disagree" and dis.record is None


def test_reread_of_plain_fact_flags():
    assert reread({"facet": FACET}, source=src(), answers=[], registered_sources=[]).reason == "not_a_cited_change"
