"""MODEL-531: a cite-only page may change a value when two readers of different families agree."""

import json
import socket
import inspect
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from decision import cited_change as gate
from decision.cited_change import (
    KNOWN_FAMILIES, REFUSALS, _check_readers, cited_change, cited_change_block,
    cited_change_facts, lookup, reread, reread_due, reread_required,
)
from decision.cited_reader import (
    ATTEMPTS_FILE, Reader, ReaderAnswer, ReaderError, attempts, build_prompt, input_manifest,
    parse_answer, read_page, sha256, text_sha256,
)

FACET = "model.context_window"
SUBJECT = "xai/grok-x"
URL = "https://docs.x.ai/docs/models/grok-x"
HF = "https://huggingface.co/xai/grok-x"
PAGE = b"<html><body>Grok X token limit 262144 SECRET-PAGE-MARKER</body></html>"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


def reader(rid, family, value=262144, version="1.0"):
    return Reader(rid, family, version, lambda prompt: f'<<<JSON {{"value": {json.dumps(value)}}} JSON>>>')


def failing(rid, family):
    def ask(prompt):
        raise TimeoutError("slow")
    return Reader(rid, family, "1.0", ask)


def pair(value=262144, a=("codex", "gpt-5"), b=("grok", "xai"), version="1.0"):
    return [reader(a[0], a[1], value, version), reader(b[0], b[1], value, version)]


def serve(pages=None):
    """The HTTP transport: URL -> (status, Location, body). Records every URL requested."""
    pages = {URL: PAGE} if pages is None else pages
    calls = []

    def request(url):
        calls.append(url)
        page = pages[url]
        return page if isinstance(page, tuple) else (200, None, page)
    request.calls = calls
    return request


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

    def log(self):
        path = self.root / ATTEMPTS_FILE
        return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def run(**kw):
    args = dict(subject=SUBJECT, facet=FACET, source_id="s1", readers=pair(), request=serve())
    args.update(kw)
    return cited_change(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS


def today():
    return datetime.now(UTC).date().isoformat()


# --- every condition holds -----------------------------------------------------------------------


def test_all_conditions_hold_writes_cited_record_with_manifests(data):
    out = run()
    assert out.changed and out.reason is None
    rec = out.record
    assert rec["value"] == 262144 and rec["resolution"] == "cited" and rec["state"] == "known"
    assert rec["source"]["snapshot_ref"] == "sha256:" + sha256(PAGE)
    assert datetime.fromisoformat(rec["source"]["retrieved_at"]).tzinfo is not None
    assert set(rec["source"]) == {"source_id", "snapshot_ref", "retrieved_at", "cited_regions"}
    block = rec["derivation"]["cited_change"]
    assert "cited_change" not in rec
    assert block["sha256"] == sha256(PAGE) and block["url"] == URL and block["read_date"] == today()
    assert block["previous_sources"] == ["s1"] and block["resolved_urls"] == []
    assert [r["family"] for r in block["readers"]] == ["gpt-5", "xai"]
    for r in block["readers"]:
        assert r["reader_id"] and r["version"] and r["prompt_sha256"]
        assert r["manifest"]["fields"] == ["url", "facet", "facet_definition", "subject_name", "page"]
    assert "SECRET-PAGE-MARKER" not in json.dumps(rec)


def test_no_public_path_accepts_answers_pages_hashes_or_manifests():
    for fn in (cited_change, reread):
        names = set(inspect.signature(fn).parameters)
        assert not names & {"answers", "page_bytes", "manifest", "prompt_sha256", "read_at"}, names
    assert "readers" in inspect.signature(cited_change).parameters


def test_the_record_round_trips_into_a_valid_fact(data):
    from decision import registry
    from decision.model import Fact

    record = run().record
    fact = {"id": "x", "subject": {"kind": "model", "id": SUBJECT}, "facet": FACET,
            "value": record["value"], "state": "known", "sources": [record["source"]],
            "derivation": record["derivation"]}
    assert Fact.model_validate(fact, context={"registry": registry}).derivation


def test_prompt_holds_only_the_four_inputs(data):
    prompt = build_prompt(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=PAGE)
    assert "131072" not in prompt and "262144" in prompt
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
    refused("registry_lookup_failed")
    monkeypatch.delenv("MODELSPEC_DATA_DIR")
    refused("registry_lookup_failed")


# --- condition 1: the host, and the redirects at the gate ----------------------------------------


def test_refuse_host_retains_copies(data):
    refused("host_not_cite_only", source_id="hf", request=serve({HF: PAGE}))


def test_refuse_malformed_url(data):
    data.source(url="https://")
    refused("host_unreadable")


def test_the_gate_follows_a_redirect_only_to_cite_only_hosts_and_records_the_hops(data):
    other = "https://docs.x.ai/docs/models/grok-x-moved"
    request = serve({URL: (301, "/docs/models/grok-x-moved", b""), other: PAGE})
    out = run(request=request)
    assert out.changed and request.calls == [URL, other]
    assert out.record["derivation"]["cited_change"]["resolved_urls"] == [other]


def test_the_gate_refuses_a_redirect_to_a_retaining_host_and_never_requests_it(data):
    request = serve({URL: (302, HF, b""), HF: PAGE})
    refused("redirect_to_retaining_host", request=request)
    assert request.calls == [URL]
    assert not data.log()  # no reader was asked


def test_the_gate_refuses_an_unreadable_page_and_a_redirect_loop(data):
    refused("page_unreadable", request=serve({URL: (404, None, b"")}))
    refused("page_unreadable", request=serve({URL: (200, None, b"")}))
    refused("page_unreadable", request=serve({URL: (301, URL, b"")}))

    def boom(url):
        raise OSError("down")
    refused("page_unreadable", request=boom)
    refused("host_unreadable", request=serve({URL: (301, "https://docs.x.ai:99999/x", b"")}))


def test_the_page_bytes_come_only_from_the_gates_fetch(data):
    seen = []
    spy = Reader("codex", "gpt-5", "1.0", lambda p: seen.append(p) or '<<<JSON {"value": 5} JSON>>>')
    spy2 = Reader("grok", "xai", "1.0", lambda p: '<<<JSON {"value": 5} JSON>>>')
    assert run(readers=[spy, spy2], request=serve({URL: b"<html>only this page 5</html>"})).changed
    assert "only this page 5" in seen[0] and "SECRET-PAGE-MARKER" not in seen[0]


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


# --- condition 3: two readers, distinct known families -------------------------------------------


def test_refuse_reader_count(data):
    refused("reader_count", readers=pair()[:1])
    refused("reader_count", readers=pair() + [reader("q", "qwen")])


def test_refuse_reader_metadata_missing(data):
    refused("reader_metadata_missing", readers=pair(version=""))
    refused("reader_metadata_missing", readers=[reader("", "gpt-5"), reader("g", "xai")])


@pytest.mark.parametrize("family", ["gpt-5", "openai", "unknown", "other", "unrecorded",
                                    "deterministic", "foobar-lab", "Unlisted-Family"])
def test_refuse_a_family_that_is_not_a_distinct_known_lineage(data, family):
    refused("reader_families_not_distinct", readers=pair(b=("x", family)))


def test_known_families_are_the_lineages(data):
    assert {"openai", "anthropic", "xai"} <= KNOWN_FAMILIES
    assert run(readers=pair(a=("codex", "openai"), b=("claude", "anthropic"))).changed


def test_refuse_same_reader_id(data):
    refused("reader_families_not_distinct", readers=pair(a=("same", "gpt-5"), b=("same", "xai")))


def forged(data):
    """Answers as a caller could forge them: only the private defence in depth sees these."""
    answers = read_page(subject=SUBJECT, url=URL, facet_id=FACET, subject_name="Grok X",
                        page_bytes=PAGE, readers=pair())
    return answers, gate._facet(FACET)


def check(answers, facet, page=PAGE):
    return _check_readers(answers, facet, url=URL, subject_name="Grok X", page_bytes=page)


def test_defence_in_depth_against_forged_answers(data):
    (a, b), facet = forged(data)
    assert check([a, b], facet) is None
    missing = ReaderAnswer(b.reader_id, b.family, b.version, b.value)
    assert check([a, missing], facet).reason == "reader_input_missing"
    leaked = build_prompt(url=URL, facet_id=FACET, subject_name="Grok X", page_bytes=PAGE) \
        + "\nFiled value: 131072"
    with_leak = ReaderAnswer(b.reader_id, b.family, b.version, b.value, sha256(leaked), b.manifest)
    assert check([a, with_leak], facet).reason == "reader_input_not_blind"
    extra = {**b.manifest, "fields": [*b.manifest["fields"], "filed_value"]}
    assert check([a, ReaderAnswer(b.reader_id, b.family, b.version, b.value, b.prompt_sha256,
                                  extra)], facet).reason == "reader_input_not_blind"
    assert check([a, b], facet, page=b"<html>another page</html>").reason == "reader_input_not_blind"


def test_refuse_disagreement(data):
    refused("readers_disagree", readers=[reader("codex", "gpt-5", 1), reader("grok", "xai", 2)])


def test_refuse_no_value(data):
    refused("no_value", readers=pair(value=None))


def test_refuse_invalid_value(data):
    refused("value_invalid", readers=pair(value="big"))


def test_refuse_excerpt_sized_string(data):
    data.fact.update(facet="origin.lab_jurisdiction", value=["US"])
    data.write()
    long = "x" * 500
    refused("value_invalid", facet="origin.lab_jurisdiction", readers=pair(value=[long]))


def test_set_values_compare_unordered(data):
    data.fact.update(facet="origin.lab_jurisdiction", value=["US"])
    data.write()
    assert run(facet="origin.lab_jurisdiction", readers=[
        reader("a", "gpt-5", ["US", "GB"]), reader("b", "xai", ["GB", "US"])]).changed


def test_refuse_unchanged_value(data):
    refused("value_unchanged", readers=pair(value=131072))


# --- no retry-shopping: the attempt log ----------------------------------------------------------


def test_every_attempt_is_logged_without_page_text(data):
    run()
    (entry,) = data.log()
    assert entry["harness"] is True and entry["complete"] and entry["agreed"] and entry["agreed_value"] == 262144
    assert entry["page_sha256"] == sha256(PAGE) and entry["prompt_sha256"] and entry["at"]
    assert [r["reader_id"] for r in entry["readers"]] == ["codex", "grok"]
    assert {"family", "version", "value"} <= set(entry["readers"][0])
    assert "SECRET-PAGE-MARKER" not in json.dumps(entry)


def test_an_agreement_after_a_disagreement_is_refused(data):
    refused("readers_disagree", readers=[reader("codex", "gpt-5", 1), reader("grok", "xai", 2)])
    refused("prior_attempt_disagreed")  # a clean second read agrees, and still cannot be used
    assert len(data.log()) == 2 - 1  # the second attempt never read: the gate refused first
    assert attempts(SUBJECT, FACET)[0]["agreed"] is False


def test_a_second_attempt_after_an_agreement_must_return_the_same_value(data):
    assert run().changed
    assert run().changed
    refused("prior_attempt_disagreed", readers=pair(value=999))


def test_an_incomplete_attempt_is_logged_and_does_not_count(data):
    refused("reader_failed", readers=[failing("codex", "gpt-5"), reader("grok", "xai")])
    assert [e["complete"] for e in data.log()] == [False, False]  # one retry, both logged
    assert run().changed  # an incomplete attempt is no first complete attempt


def seed(data, **kw):
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(exist_ok=True)
    entry = {"subject": SUBJECT, "facet": FACET, "url": URL, "epoch": "initial", "complete": True,
             "seeded": True, **kw}
    with path.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


def test_a_seeded_disagreement_blocks_but_a_seeded_agreement_authorises_nothing(data):
    seed(data, harness=False, agreed=True, agreed_value=262144)
    assert run().changed  # a seeded agreement does not block; the live attempt must itself agree
    assert [e.get("seeded") for e in data.log()] == [True, None]


def test_a_disagreement_on_any_page_blocks_the_facet(data):
    seed(data, harness=False, agreed=False, url="https://docs.x.ai/docs/another-page")
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1  # no reader was asked


def test_disagree_then_seeded_agree_then_live_disagree_then_live_agree_is_refused(data):
    refused("readers_disagree", readers=[reader("codex", "gpt-5", 1), reader("grok", "xai", 2)])
    seed(data, harness=False, agreed=True, agreed_value=262144)
    refused("prior_attempt_disagreed", readers=[reader("codex", "gpt-5", 1), reader("grok", "xai", 2)])
    refused("prior_attempt_disagreed")
    assert not any(e.get("agreed") and not e.get("seeded") for e in data.log())


def test_a_live_agreement_after_a_disagreeing_seed_from_unproven_reads_is_refused(data):
    seed(data, harness=False, agreed=False)
    refused("prior_attempt_disagreed")


def test_a_later_agreed_attempt_on_another_page_must_return_the_same_value(data):
    seed(data, harness=True, agreed=True, agreed_value=999, url="https://docs.x.ai/docs/another-page")
    refused("prior_attempt_disagreed")


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


def test_a_retaining_source_of_another_kind_is_not_for_this_facet(data):
    data.source("hf", kind="licence_text")
    data.fact["checked_sources"] = ["hf"]
    data.write()
    assert run().changed
    data.source("hf", kind="weights_repository")
    refused("retaining_source_registered")


def test_previous_sources_are_still_considered_on_later_reads(data):
    data.fact["checked_sources"] = ["hf"]
    data.redirects = {"hf": {"to": URL, "status": 301, "checked": today()}}
    data.write()
    record = run().record
    assert record["derivation"]["cited_change"]["previous_sources"] == ["s1", "hf"]
    # the card now cites only s1, but remembers hf; the redirect entry later goes stale
    data.fact = {"facet": FACET, "value": record["value"], "state": "known",
                 "sources": [record["source"]], "checked_sources": [], "derivation": record["derivation"]}
    data.redirects = {"hf": {"to": URL, "status": 301, "checked": "2020-01-01"}}
    data.write()
    refused("retaining_source_registered", readers=pair(value=7))


@pytest.mark.parametrize("entry,honoured", [
    ({"to": URL, "checked": "TODAY"}, True),
    ({"to": URL, "checked": "OLD"}, False),
    ({"to": "https://docs.x.ai/docs/not-registered", "checked": "TODAY"}, False),
    ({"to": URL, "checked": "FUTURE"}, False),
    ({"to": URL}, False),
    ({"to": URL, "checked": "garbage"}, False),
    ("not a mapping", False),
])
def test_a_redirect_entry_counts_only_for_a_registered_cite_only_target_checked_this_week(
        data, entry, honoured):
    if isinstance(entry, dict) and "checked" in entry:
        entry["checked"] = {"TODAY": today(), "OLD": (datetime.now(UTC) - timedelta(days=8)).date().isoformat(),
                            "FUTURE": (datetime.now(UTC) + timedelta(days=3)).date().isoformat()
                            }.get(entry["checked"], entry["checked"])
    data.fact["checked_sources"] = ["hf"]
    data.redirects = {"hf": entry}
    data.write()
    if honoured:
        assert run().changed
    else:
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
    assert not reread_required(fact, PAGE)
    assert reread_required(fact, PAGE + b" changed")
    assert not reread_required({"subject": SUBJECT, "facet": FACET, "value": 1}, PAGE)
    assert lookup(SUBJECT, FACET).fact["derivation"]["cited_change"]["sha256"] == sha256(PAGE)


def test_byte_churn_is_not_a_change_but_a_text_change_is(data):
    fact = cited_card(data, run().record)
    assert fact["derivation"]["cited_change"]["text_sha256"] == text_sha256(PAGE)
    churned = PAGE.replace(b"<html>", b"<html><script>var t=987654321;</script><!-- 2026-11-23T01:02 -->")
    assert sha256(churned) != sha256(PAGE) and not reread_required(fact, churned)
    assert not reread_required(fact, PAGE.replace(b"<body>", b"<body>\n   "))  # whitespace folds
    assert reread_required(fact, PAGE.replace(b"262144", b"524288"))
    assert reread_required({"derivation": {"cited_change": {"sha256": "x"}}}, PAGE)  # no text hash


def test_a_reread_is_due_only_after_seven_days_since_the_read_and_the_last_request(data):
    fact = cited_card(data, run().record)
    changed = PAGE + b" new"
    now = datetime.now(UTC)
    assert not reread_due(fact, changed, now=now)  # read today
    assert not reread_due(fact, PAGE, now=now + timedelta(days=30))  # nothing changed
    assert reread_due(fact, changed, now=now + timedelta(days=8))
    assert not reread_due(fact, changed, now=now + timedelta(days=8),
                          last_request=now + timedelta(days=3))
    assert reread_due(fact, changed, now=now + timedelta(days=11), last_request=now + timedelta(days=3))


def reread_with(fact, page, readers=None):
    return reread(fact, source_id="s1", readers=readers or pair(), request=serve({URL: page}))


def test_reread_unchanged_page_needs_no_read(data):
    fact = cited_card(data, run().record)
    out = reread_with(fact, PAGE, readers=[])
    assert out.outcome == "current"


def test_reread_changed_sha_confirms_or_changes_with_two_readers(data):
    fact = cited_card(data, run().record)
    page = PAGE + b" v2"
    out = reread_with(fact, page)
    assert out.outcome == "confirmed" and out.record["derivation"]["cited_change"]["sha256"] == sha256(page)
    # a second read at the same recorded hash must return the same value as the first agreed one
    other = reread_with(fact, page + b" v3", readers=pair(value=5))
    assert other.outcome == "flagged" and other.reason == "prior_attempt_disagreed"


def test_reread_changed_sha_new_value_with_a_fresh_epoch(data):
    fact = cited_card(data, run().record)
    out = reread_with(fact, PAGE + b" v2", readers=pair(value=5))
    assert out.outcome == "changed" and out.record["value"] == 5


def test_reread_changed_sha_one_reader_or_disagreement_flags(data):
    fact = cited_card(data, run().record)
    page = PAGE + b" v2"
    one = reread_with(fact, page, readers=pair()[:1])
    assert one.outcome == "flagged" and one.reason == "reader_count"
    dis = reread_with(fact, page + b"!", readers=[reader("a", "gpt-5", 1), reader("b", "xai", 2)])
    assert dis.outcome == "flagged" and dis.reason == "readers_disagree" and dis.record is None


def test_reread_of_plain_fact_flags(data):
    out = reread({"subject": SUBJECT, "facet": FACET}, source_id="s1", readers=[])
    assert out.reason == "not_a_cited_change"


# --- the rolling re-read script ------------------------------------------------------------------


def sweep_script(data):
    from scripts import evidence_reread as script

    (data.root / "registry/source-terms.json").write_text(json.dumps({"huggingface.co": "restricts"}))
    return script


def sweep(script, data, body, days, dry_run=True):
    from datetime import date

    report = script.Report("x", dry_run)
    script.cited_change_rereads(data.root, script.load_terms(data.root), report,
                                request=serve({URL: body}), pacer=script.Pacer(0, sleep=lambda s: None),
                                observed_at=date.today() + timedelta(days=days), dry_run=dry_run)
    return report


def test_the_rolling_reread_flags_a_cited_change_fact_whose_page_text_changed(data):
    script = sweep_script(data)
    cited_card(data, run().record)
    assert sweep(script, data, PAGE, 8).cited_change_rereads == []
    churned = PAGE.replace(b"<html>", b"<html><script>var t=1;</script>")
    assert sweep(script, data, churned, 8).cited_change_rereads == [], "byte churn is no change"
    report = sweep(script, data, PAGE + b" new", 8)
    assert report.cited_change_rereads == [f"{SUBJECT}#{FACET}"]
    assert report.to_dict()["cited_change_rereads_required"] == [f"{SUBJECT}#{FACET}"]
    assert sweep(script, data, PAGE + b" new", 3).cited_change_rereads == [], "read less than 7 days ago"


def test_the_rolling_reread_asks_at_most_once_in_seven_days(data):
    script = sweep_script(data)
    cited_card(data, run().record)
    changed = PAGE + b" new"
    assert sweep(script, data, changed, 8, dry_run=False).cited_change_rereads
    assert (data.root / script.REREAD_REQUESTS).is_file()
    assert sweep(script, data, changed, 12, dry_run=False).cited_change_rereads == []
    assert sweep(script, data, changed, 16, dry_run=False).cited_change_rereads
    lines = (data.root / script.REREAD_REQUESTS).read_text().splitlines()
    assert len(lines) == 2


def test_a_dry_run_logs_no_reread_request(data):
    script = sweep_script(data)
    cited_card(data, run().record)
    assert sweep(script, data, PAGE + b" new", 8).cited_change_rereads
    assert not (data.root / script.REREAD_REQUESTS).exists()


def test_the_rolling_reread_run_reports_it(data, tmp_path):
    script = sweep_script(data)
    cited_card(data, run().record)
    report = script.run(data.root, observed_at=datetime.now(UTC).date() + timedelta(days=8), dry_run=True,
                        store_root=tmp_path / "cache", request=lambda url: (200, None, PAGE + b"!"),
                        pacer=script.Pacer(0, sleep=lambda s: None))
    assert report.cited_change_rereads == [f"{SUBJECT}#{FACET}"]
    assert not [p for p in (tmp_path / "cache").rglob("*") if p.is_file()], "no page bytes kept"


def refresh(data, status, location, *, dry_run=False):
    script = sweep_script(data)
    report = script.Report("2026-11-23", dry_run)
    script.refresh_redirects(data.root, script.load_terms(data.root), report,
                             observed_at=datetime(2026, 11, 23).date(), dry_run=dry_run,
                             request=lambda url: (status, location, b""),
                             pacer=script.Pacer(0, sleep=lambda s: None))
    return report, json.loads((data.root / "registry/source-redirects.json").read_text())


def test_the_rolling_reread_keeps_a_redirect_entry_only_while_the_source_still_redirects_there(data):
    data.redirects = {"hf": {"to": URL, "status": 301, "checked": "2026-11-01"}}
    data.write()
    report, entries = refresh(data, 301, URL)
    assert report.redirects_kept == ["hf"] and entries["hf"]["checked"] == "2026-11-23"
    report, entries = refresh(data, 301, "https://docs.x.ai/docs/else")
    assert report.redirects_dropped == ["hf"] and entries == {}


def test_the_rolling_reread_drops_a_redirect_entry_when_the_source_answers_200_or_fails(data):
    data.redirects = {"hf": {"to": URL, "status": 301, "checked": "2026-11-01"}}
    data.write()
    report, entries = refresh(data, 200, None)
    assert report.redirects_dropped == ["hf"] and entries == {}


def test_a_dry_run_leaves_the_redirect_file_alone(data):
    data.redirects = {"hf": {"to": URL, "status": 301, "checked": "2026-11-01"}}
    data.write()
    _, entries = refresh(data, 200, None, dry_run=True)
    assert entries["hf"]["checked"] == "2026-11-01"
