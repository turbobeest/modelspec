"""MODEL-558: two readers confirm a filed value on a page whose host retains copies.

The rule-15 safeguards hold unchanged (two known lineages, blind prompt, every attempt logged,
no retry-shopping, quarantine first); the cite-only conditions are replaced by a classed
retaining host and the verified path winning. Every fixture is synthetic.
"""

import json
import socket

import pytest
import yaml
from decision.cited_change import (
    REFUSALS,
    RETAINED_RULE,
    RULE,
    cited_change,
    reread,
    retained_agreement,
)
from decision.cited_reader import ATTEMPTS_FILE, Reader, sha256
from decision.retention import _clear_caches

SUBJECT = "acme/widget-7b"
FACET = "model.input_modalities"
URL = "https://huggingface.co/acme/Widget-7B/resolve/main/README.md"
CITE_ONLY = "https://docs.acme.test/widget-7b"
UNCLASSED = "https://unclassed.acme.test/widget-7b"
PAGE = b"# Widget 7B\n\nWidget 7B reads text, images and video in one model. SECRET-PAGE-MARKER\n"
FILED = ["text", "image", "video"]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


def reader(rid, family, value=FILED):
    return Reader(rid, family, "1.0",
                  lambda prompt: f'<<<JSON {{"value": {json.dumps(value)}}} JSON>>>')


def pair(value=FILED, other=None):
    return [reader("codex", "gpt-5", value),
            reader("claude", "claude-sonnet-5", value if other is None else other)]


def serve(pages=None):
    pages = {URL: PAGE} if pages is None else pages
    calls = []

    def request(url):
        calls.append(url)
        page = pages[url]
        return page if isinstance(page, tuple) else (200, None, page)
    request.calls = calls
    return request


def source(sid, url, **kw):
    return dict(id=sid, url=url, kind="lab_documentation", publisher="acme", fetch="http",
                normaliser="text-default",
                cited_regions=[dict(id="model-spec", locator=dict(kind="page", value=""))], **kw)


class Data:
    def __init__(self, root, monkeypatch):
        self.root = root
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
        _clear_caches()
        self.sources = [source("readme", URL), source("docs", CITE_ONLY),
                        source("loose", UNCLASSED)]
        self.fact = dict(id=f"{SUBJECT}#{FACET}", facet=FACET, value=list(FILED), state="known",
                         sources=[dict(source_id="readme", snapshot_ref="sha256:" + "0" * 64,
                                       cited_regions=["model-spec"])])
        self.terms = {"huggingface.co": "restricts", "docs.acme.test": "forbids"}
        self.log_rows = []
        self.write()

    def write(self):
        (self.root / "models/acme").mkdir(parents=True, exist_ok=True)
        (self.root / "registry").mkdir(exist_ok=True)
        (self.root / "verification").mkdir(exist_ok=True)
        card = yaml.safe_dump({"display_name": "Widget 7B", "model_id": SUBJECT,
                               "facts": [self.fact]}, sort_keys=False)
        (self.root / "models/acme/widget-7b.md").write_text(f"---\n{card}---\nbody\n")
        (self.root / "registry/sources.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "sources": self.sources}))
        (self.root / "registry/source-terms.json").write_text(json.dumps(self.terms))
        (self.root / "verification/log.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in self.log_rows))
        _clear_caches()

    def attempts(self):
        path = self.root / ATTEMPTS_FILE
        return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def run(**kw):
    args = dict(subject=SUBJECT, facet=FACET, source_id="readme", readers=pair(), request=serve())
    args.update(kw)
    return retained_agreement(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS
    return out


# --- every condition holds ------------------------------------------------------------------------


def test_two_readers_confirm_the_filed_value_and_the_record_names_the_retained_rule(data):
    out = run()
    assert out.changed, (out.reason, out.detail)
    rec = out.record
    assert rec["value"] == FILED and rec["state"] == "known"
    assert rec["source"]["snapshot_ref"] == "sha256:" + sha256(PAGE)
    block = rec["derivation"]["cited_change"]
    assert block["rule"] == RETAINED_RULE != RULE and "MODEL-558" in block["decided_by"]
    assert block["previous_value"] == FILED and block["url"] == URL
    assert [r["family"] for r in block["readers"]] == ["gpt-5", "claude-sonnet-5"]
    assert all(r["prompt_sha256"] and r["manifest"] for r in block["readers"])
    assert "SECRET-PAGE-MARKER" not in json.dumps(rec)


def test_every_attempt_is_logged_without_page_text_under_the_shared_key(data):
    run()
    (entry,) = data.attempts()
    assert (entry["subject"], entry["facet"], entry["epoch"]) == (SUBJECT, FACET, "initial")
    assert entry["harness"] is True and entry["complete"] and entry["agreed"]
    assert "SECRET-PAGE-MARKER" not in json.dumps(entry)


# --- bypasses: the host and its hops --------------------------------------------------------------


def test_a_cite_only_page_is_refused_here_and_left_to_cited_change(data):
    refused("host_cite_only", source_id="docs", request=serve({CITE_ONLY: PAGE}))
    assert data.attempts() == []


def test_an_unclassed_host_is_never_requested(data):
    request = serve({UNCLASSED: PAGE})
    refused("host_unclassed", source_id="loose", request=request)
    assert request.calls == []


def test_an_unreadable_terms_register_refuses(data):
    (data.root / "registry/source-terms.json").write_text("not json")
    _clear_caches()
    refused("host_unclassed")


def test_a_redirect_to_a_cite_only_or_unclassed_host_is_never_requested(data):
    for target, reason in ((CITE_ONLY, "redirect_to_cite_only_host"),
                           (UNCLASSED, "redirect_to_unclassed_host")):
        request = serve({URL: (307, target, b"")})
        refused(reason, request=request)
        assert request.calls == [URL]


def test_a_same_host_redirect_is_followed_and_recorded(data):
    hop = "https://huggingface.co/api/resolve-cache/models/acme/Widget-7B/abc/README.md"
    out = run(request=serve({URL: (307, hop, b""), hop: PAGE}))
    assert out.changed and out.record["derivation"]["cited_change"]["resolved_urls"] == [hop]


def test_cited_change_still_refuses_a_retaining_host(data):
    out = cited_change(subject=SUBJECT, facet=FACET, source_id="readme", readers=pair(),
                       request=serve())
    assert out.reason == "host_not_cite_only"


# --- bypasses: first party, readers, blindness ----------------------------------------------------


def test_not_first_party_and_a_kind_the_facet_does_not_permit_are_refused(data):
    data.sources[0]["publisher"] = "someone-else"
    data.write()
    refused("not_first_party")
    data.sources[0].update(publisher="acme", kind="benchmark_author")
    data.write()
    refused("source_kind_not_permitted")


@pytest.mark.parametrize("readers,reason", [
    ([reader("codex", "gpt-5")], "reader_count"),
    ([reader("codex", "gpt-5"), reader("codex-2", "openai")], "reader_families_not_distinct"),
    ([reader("codex", "gpt-5"), reader("x", "unknown")], "reader_families_not_distinct"),
    ([reader("codex", "gpt-5"), reader("x", "deterministic")], "reader_families_not_distinct"),
])
def test_two_distinct_known_lineages_are_needed_before_any_read(data, readers, reason):
    request = serve()
    refused(reason, readers=readers, request=request)
    assert request.calls == [] and data.attempts() == []


def test_the_readers_get_the_blind_prompt_only(data):
    seen = []

    def ask(prompt):
        seen.append(prompt)
        return f'<<<JSON {{"value": {json.dumps(FILED)}}} JSON>>>'
    assert run(readers=[Reader("codex", "gpt-5", "1", ask),
                        Reader("claude", "claude-sonnet-5", "1", ask)]).changed
    assert len(set(seen)) == 1 and '"video"' not in seen[0].split("PAGE TEXT START")[0]


# --- confirmation only ----------------------------------------------------------------------------


def test_an_agreed_other_value_changes_nothing_and_is_logged(data):
    refused("value_differs", readers=pair(["text", "image"]))
    assert data.attempts()[-1]["agreed"] is True
    # The next read cannot shop for the filed value: the agreed other value blocks it.
    refused("prior_attempt_disagreed")


def test_an_agreed_absence_files_nothing(data):
    refused("no_value", readers=pair(None))
    refused("prior_attempt_disagreed")


def test_a_fact_not_filed_known_is_not_confirmed(data):
    data.fact.update(state="not_disclosed", value=None)
    data.write()
    refused("value_differs")


# --- no retry-shopping, across both paths ---------------------------------------------------------


def test_a_disagreement_blocks_every_later_attempt(data):
    refused("readers_disagree", readers=pair(FILED, ["text"]))
    refused("prior_attempt_disagreed")
    assert len(data.attempts()) == 1


def test_a_disagreement_logged_by_the_cite_only_path_blocks_this_one(data):
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"subject": SUBJECT, "facet": FACET, "epoch": "initial",
                                "url": CITE_ONLY, "complete": True, "harness": True,
                                "agreed": False}) + "\n")
    refused("prior_attempt_disagreed")


# --- quarantine and the verified path -------------------------------------------------------------


def test_a_quarantined_fact_is_refused_before_any_read(data):
    data.log_rows = [{"target": {"kind": "fact", "id": f"{SUBJECT}#{FACET}",
                                 "value_hash": "sha256:" + "a" * 64},
                      "collector": {"agent": "c", "model_family": "anthropic", "method": "m"},
                      "verifier": {"agent": "modelspec-verify", "model_family": "deterministic",
                                   "method": "key-value-match@1"},
                      "method": "key-value-match@1", "outcome": "mismatch", "date": "2026-11-01",
                      "diff": None}]
    data.write()
    request = serve()
    refused("quarantined", request=request)
    assert request.calls == [] and data.attempts() == []


def test_a_page_an_engine_reader_reads_takes_the_verified_path(data):
    data.fact.update(facet="model.context_window", value=32768,
                     id=f"{SUBJECT}#model.context_window")
    data.write()
    table = b"| | |\n|---|---|\n| **Context length** | 32,768 tokens |\n"
    out = refused("engine_reader_reads", facet="model.context_window",
                  readers=pair(32768), request=serve({URL: table}))
    assert "hf-readme-spec@1" in out.detail and data.attempts() == []
    # A page whose engine reading contradicts the filed value is the verified path's too.
    data.fact.update(value=8192)
    data.write()
    refused("engine_reader_reads", facet="model.context_window", readers=pair(8192),
            request=serve({URL: table}))


def test_a_page_every_engine_reader_abstains_on_is_left_to_the_readers(data):
    data.fact.update(facet="model.context_window", value=262144,
                     id=f"{SUBJECT}#model.context_window")
    data.write()
    table = b"| | |\n|---|---|\n| **Context Length** | 256K |\n"
    out = run(facet="model.context_window", readers=pair(262144), request=serve({URL: table}))
    assert out.changed, (out.reason, out.detail)


# --- the rolling re-read --------------------------------------------------------------------------


def file_record(data, record):
    """Write a record into the card, as the data writer does."""
    data.fact.update(sources=[record["source"]], derivation=record["derivation"])
    data.write()


def test_reread_of_a_retained_agreement_uses_the_retaining_gate(data):
    file_record(data, run().record)
    fact = {"subject": SUBJECT, "facet": FACET}
    assert reread(fact, source_id="readme", readers=pair(), request=serve()).outcome == "current"
    changed = PAGE + b"More text.\n"
    out = reread(fact, source_id="readme", readers=pair(), request=serve({URL: changed}))
    assert out.outcome == "confirmed" and out.record["derivation"]["cited_change"]["rule"] \
        == RETAINED_RULE
    file_record(data, out.record)  # the confirmed read starts a new epoch
    out = reread(fact, source_id="readme", readers=pair(["text"]),
                 request=serve({URL: changed + b"x"}))
    assert out.outcome == "flagged" and out.reason == "value_differs"


def test_reread_takes_the_block_and_epoch_from_the_filed_fact_not_the_caller(data):
    record = run().record
    # The caller hands in a block the card does not carry: the filed fact has none.
    fact = {"subject": SUBJECT, "facet": FACET, "derivation": record["derivation"]}
    out = reread(fact, source_id="readme", readers=pair(), request=serve())
    assert out.outcome == "flagged" and out.reason == "not_a_cited_change"


def test_the_rolling_reread_requests_a_retained_agreement_whose_page_text_changed(data):
    from datetime import date, timedelta

    from scripts import evidence_reread as script

    record = run().record
    data.fact.update(sources=[record["source"]], derivation=record["derivation"])
    data.write()

    def sweep(body):
        report = script.Report("x", True)
        script.cited_change_rereads(data.root, script.load_terms(data.root), report,
                                    request=serve({URL: body}),
                                    pacer=script.Pacer(0, sleep=lambda s: None),
                                    observed_at=date.today() + timedelta(days=8))
        return report

    assert sweep(PAGE).cited_change_rereads == []
    assert sweep(PAGE + b"More text.\n").cited_change_rereads == [f"{SUBJECT}#{FACET}"]
    # A cite-only rule block on a retaining host is still not re-read.
    data.fact["derivation"]["cited_change"]["rule"] = RULE
    data.write()
    assert sweep(PAGE + b"More text.\n").cited_change_rereads == []


def test_a_set_agreed_in_another_order_keeps_the_filed_order(data):
    out = run(readers=pair(["video", "text", "image"]))
    assert out.changed and out.record["value"] == FILED


# --- review fixes: incomplete answers, the attempt budget, epochs, the veto, origin class --------


def seed(data, **entry):
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(exist_ok=True)
    base = {"subject": SUBJECT, "facet": FACET, "epoch": "initial", "url": URL,
            "complete": False, "harness": True, "agreed": None, "readers": []}
    with path.open("a") as fh:
        fh.write(json.dumps({**base, **entry}) + "\n")


def failing(rid, family, value=None):
    calls = []

    def ask(prompt):
        calls.append(1)
        raise TimeoutError("slow")
    return Reader(rid, family, "1.0", ask)


def test_a_contradictory_answer_in_an_incomplete_attempt_blocks_a_later_agreement(data):
    seed(data, readers=[{"reader_id": "codex", "family": "gpt-5", "version": "1",
                         "value": ["text"]}])
    refused("prior_attempt_disagreed")


def test_two_incomplete_attempts_that_differ_block_before_any_read(data):
    for value in (["text"], ["text", "image"]):
        seed(data, readers=[{"reader_id": "codex", "family": "gpt-5", "version": "1",
                             "value": value}])
    request = serve()
    refused("prior_attempt_disagreed", request=request)
    assert request.calls == []


def test_an_incomplete_answer_that_matches_does_not_block(data):
    seed(data, readers=[{"reader_id": "codex", "family": "gpt-5", "version": "1",
                         "value": ["video", "text", "image"]}])
    assert run().changed


def test_the_attempt_budget_survives_a_rerun(data):
    readers = [reader("codex", "gpt-5"), failing("claude", "claude-sonnet-5")]
    refused("reader_failed", readers=readers)       # two incomplete attempts in one call
    assert len(data.attempts()) == 2
    refused("attempts_exhausted", readers=readers)  # a re-run gets one more, then stops
    assert len(data.attempts()) == 3
    request = serve()
    refused("attempts_exhausted", request=request)  # even with working readers
    assert request.calls == [] and len(data.attempts()) == 3


def test_a_direct_agreement_reads_in_the_filed_facts_epoch(data):
    record = run().record
    file_record(data, record)
    epoch = "reread:" + record["derivation"]["cited_change"]["text_sha256"]
    seed(data, epoch=epoch, complete=True, agreed=False)
    refused("prior_attempt_disagreed")              # the seeded disagreement is in its epoch
    assert all(e["epoch"] in {"initial", epoch} for e in data.attempts())


def test_the_engine_veto_reads_every_retaining_source_the_fact_cites(data):
    spec = "https://huggingface.co/acme/Widget-7B/raw/main/README.md"
    data.sources.append(source("spec", spec))
    data.fact.update(facet="model.context_window", value=32768,
                     id=f"{SUBJECT}#model.context_window")
    data.fact["sources"].append(dict(source_id="spec", snapshot_ref="sha256:" + "1" * 64,
                                     cited_regions=["model-spec"]))
    data.write()
    prose = b"# Widget 7B\n\nA long context model.\n"
    table = b"| | |\n|---|---|\n| **Context length** | 16,384 tokens |\n"
    out = refused("engine_reader_reads", facet="model.context_window", readers=pair(32768),
                  request=serve({URL: prose, spec: table}))
    assert "spec" in out.detail and data.attempts() == []
    # A cited retaining source that cannot be read fails closed.
    out = refused("engine_reader_reads", facet="model.context_window", readers=pair(32768),
                  request=serve({URL: prose, spec: (404, None, b"")}))
    assert "could not be read" in out.detail


def test_the_engine_veto_reads_through_stored_regions_so_a_pdf_takes_its_route(data, monkeypatch):
    import decision.verify as verify_module

    seen = []
    real = verify_module.verify

    def spy(claim, regions, extractors, *, today):
        seen.append(type(regions).__name__)
        return real(claim, regions, extractors, today=today)
    monkeypatch.setattr(verify_module, "verify", spy)
    assert run().changed
    assert seen and set(seen) == {"StoredRegions"}


def test_a_cited_page_on_a_cite_only_host_is_not_fetched_for_the_veto(data):
    data.fact["sources"].append(dict(source_id="docs", snapshot_ref="sha256:" + "1" * 64,
                                     cited_regions=["model-spec"]))
    data.write()
    request = serve()
    assert run(request=request).changed
    assert request.calls == [URL]


def test_the_origin_class_is_checked_before_any_reread_fetch(data):
    file_record(data, run().record)
    data.terms["huggingface.co"] = "forbids"          # the host is now cite-only
    data.write()
    request = serve()
    out = reread({"subject": SUBJECT, "facet": FACET}, source_id="readme", readers=pair(),
                 request=request)
    assert out.outcome == "flagged" and out.reason == "host_cite_only" and request.calls == []
    del data.terms["huggingface.co"]                   # the host now has no class
    data.write()
    out = reread({"subject": SUBJECT, "facet": FACET}, source_id="readme", readers=pair(),
                 request=request)
    assert out.reason == "host_unclassed" and request.calls == []


# --- review round 2 -------------------------------------------------------------------------------


def test_the_veto_reads_each_source_in_the_context_of_the_full_cited_set(data):
    # The config reader needs the README in its bindings; read alone it abstains, read with the
    # fact's full cited set it finds 131072, which disagrees with the filed 262144.
    cfg = "https://huggingface.co/acme/Widget-7B/resolve/0123abc/config.json"
    data.sources.append(dict(source("cfg", cfg), kind="weights_repository",
                             normaliser="json-default",
                             cited_regions=[dict(id="page", locator=dict(kind="page", value=""))]))
    data.fact.update(facet="model.context_window", value=262144,
                     id=f"{SUBJECT}#model.context_window")
    data.fact["sources"].append(dict(source_id="cfg", snapshot_ref="sha256:" + "1" * 64,
                                     cited_regions=["page"]))
    data.write()
    silent = b"# Widget 7B\n\nA text model for long documents.\n"
    config = json.dumps({"architectures": ["WidgetForCausalLM"], "model_type": "widget",
                         "num_attention_heads": 8, "max_position_embeddings": 131072}).encode()
    out = refused("engine_reader_reads", facet="model.context_window", readers=pair(262144),
                  request=serve({URL: silent, cfg: config}))
    assert "hf-config-context@1" in out.detail and data.attempts() == []


def test_the_rolling_reread_lists_a_retained_agreement_whose_origin_is_now_cite_only(data):
    from datetime import date, timedelta

    from scripts import evidence_reread as script

    file_record(data, run().record)
    data.terms["huggingface.co"] = "forbids"
    data.write()
    request = serve({URL: PAGE + b"More text.\n"})
    report = script.Report("x", True)
    script.cited_change_rereads(data.root, script.load_terms(data.root), report, request=request,
                                pacer=script.Pacer(0, sleep=lambda s: None),
                                observed_at=date.today() + timedelta(days=8))
    assert request.calls == [] and report.cited_change_rereads == []
    assert report.retained_now_cite_only == [f"{SUBJECT}#{FACET}"]
    assert report.to_dict()["retained_agreements_now_cite_only"] == [f"{SUBJECT}#{FACET}"]
