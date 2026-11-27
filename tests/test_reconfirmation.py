"""MODEL-572: an agreed, unchanged cited-fact read files its record and read date.

The gate (``cited_change(allow_unchanged=True)``), the snapshot build and the site loader decide
through one test (``decision.reconfirmation.reconfirmation_problem``). Bypass tests: same family,
a disagreement present, a held fact, a licence value change attempted, a ruled or blocked fact,
and a record edited after the gate wrote it. Every page, hash and attempt is synthetic.
"""

from __future__ import annotations

import copy
import json
import socket

import pytest
import yaml
from decision.cited_change import REFUSALS, cited_change, fact_epoch
from decision.cited_reader import ATTEMPTS_FILE
from decision.reconfirmation import MARK, filed, is_reconfirmation, reconfirmation_problem

from tests import test_cited_change as gate
from tests.test_cited_change import FACET, SUBJECT, URL, pair, reader, seed, serve


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


@pytest.fixture
def data(tmp_path, monkeypatch):
    return gate.Data(tmp_path / "data", monkeypatch)


FILED = 131072
LICENCE = "licence.commercial_use"
#: A terms page long enough to show silence, that states no commercial-use term.
SILENT = ("<html><body><h1>Terms</h1>" + "<p>These terms govern the account, billing and "
          "support of the service. Notices go to the address on the invoice.</p>" * 8
          + "</body></html>").encode()


def run(**kw):
    args = dict(subject=SUBJECT, facet=FACET, source_id="s1", readers=pair(FILED),
                request=serve(), allow_unchanged=True)
    args.update(kw)
    return cited_change(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS
    return out


def licence(data, value=None, state="not_disclosed"):
    """The fact as an owner's correction leaves it: a licence fact with no block."""
    data.source(kind="provider_terms")
    data.fact.update(facet=LICENCE, value=value, state=state)
    data.write()


def licence_run(values=None, **kw):
    return run(facet=LICENCE, request=serve({URL: SILENT}), accept_not_disclosed=True,
               readers=pair(values), **kw)


def problem(data, fact):
    """The one test, with the logs and registry the build reads from the data directory."""
    from datetime import UTC, datetime

    from decision.owner_ruling import read_json_lines
    from decision.quarantine_clearing import AttemptLog
    from decision.snapshot import _Compiler

    verdicts = _Compiler._verification_log(read_json_lines(data.root / "verification/log.jsonl"))
    urls = {s["id"]: s["url"] for s in data.sources}
    return reconfirmation_problem(fact, SUBJECT, log=AttemptLog.read(data.root / ATTEMPTS_FILE),
                                  verdicts=verdicts, sources=urls,
                                  cutoff=datetime.now(UTC).date())


def file_record(data, record):
    fact = filed(data.fact, record)
    data.fact.clear()
    data.fact.update(fact)
    data.write()


# --- the gate ------------------------------------------------------------------------------------


def test_an_agreement_on_the_filed_value_files_its_record_and_date(data):
    out = run()
    assert out.changed and out.record["value"] == FILED and out.record["state"] == "known"
    block = out.record["derivation"]["cited_change"]
    assert block[MARK] is True and block["previous_state"] == "known"
    assert block["previous_value"] == FILED and block["read_date"]
    fact = filed(data.fact, out.record)
    assert is_reconfirmation(fact) and problem(data, fact) is None
    assert data.log()[-1]["agreed"] is True


def test_without_the_flag_the_unchanged_value_still_files_nothing(data):
    out = cited_change(subject=SUBJECT, facet=FACET, source_id="s1", readers=pair(FILED),
                       request=serve())
    assert out.reason == "value_unchanged" and out.record is None


def test_a_not_disclosed_licence_fact_is_reconfirmed_on_a_silent_page(data):
    licence(data)
    out = licence_run()
    assert out.changed and out.record["state"] == "not_disclosed" and out.record["value"] is None
    block = out.record["derivation"]["cited_change"]
    assert block[MARK] is True and block["previous_state"] == "not_disclosed"
    assert {r["finding"] for r in block["readers"]} == {"not_stated"}
    assert problem(data, filed(data.fact, out.record)) is None


def test_a_licence_fact_meets_the_normal_paths_silence_rules(data):
    licence(data)
    refused("page_too_short", facet=LICENCE, accept_not_disclosed=True, readers=pair(None))
    refused("no_value", facet=LICENCE, request=serve({URL: SILENT}), readers=pair(None))


@pytest.mark.parametrize("families", [("gpt-5", "gpt-5"), ("openai", "codex")])
def test_same_family_readers_are_refused_before_any_read(data, families):
    refused("reader_families_not_distinct",
            readers=[reader("a", families[0], FILED), reader("b", families[1], FILED)])
    assert data.log() == []


def test_a_disagreement_in_the_epoch_blocks_the_reconfirmation(data):
    refused("readers_disagree", readers=[reader("codex", "gpt-5", FILED),
                                         reader("grok", "xai", 262144)])
    refused("prior_attempt_disagreed")


def test_a_logged_disagreement_blocks_before_any_read(data):
    seed(data, harness=True, agreed=False)
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1


def test_an_earlier_agreement_on_another_value_blocks(data):
    seed(data, harness=True, agreed=True, agreed_value=262144)
    refused("prior_attempt_disagreed")


def test_a_held_fact_is_refused_before_any_read(data):
    from tests.snapshot_records import verification

    path = data.root / "verification/log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(verification("fact", f"{SUBJECT}#{FACET}", "mismatch",
                                            value=FILED)) + "\n")
    refused("quarantined")
    assert data.log() == []


@pytest.mark.parametrize("filed, agreed", [
    ((None, "not_disclosed"), "permitted"),
    (("permitted", "known"), None),
    (("permitted", "known"), "prohibited"),
])
def test_a_licence_value_change_is_refused_and_files_nothing(data, filed, agreed):
    licence(data, *filed)
    before = (data.root / "models/xai/grok-x.md").read_text()
    refused("value_differs", facet=LICENCE, request=serve({URL: SILENT}),
            accept_not_disclosed=True, readers=pair(agreed))
    assert (data.root / "models/xai/grok-x.md").read_text() == before


def test_a_known_value_change_is_refused_and_files_nothing(data):
    refused("value_differs", readers=pair(262144))


def test_a_fact_with_a_block_is_left_to_the_rolling_reread(data):
    file_record(data, cited_change(subject=SUBJECT, facet=FACET, source_id="s1",
                                   readers=pair(262144), request=serve()).record)
    assert fact_epoch(data.fact) != "initial"
    before = len(data.log())
    refused("reconfirmation_not_admitted", readers=pair(262144))
    assert len(data.log()) == before


def test_a_ruled_fact_or_a_clearing_is_refused_before_any_read(data):
    refused("reconfirmation_not_admitted", clear_quarantine=True)
    data.fact["derivation"] = {"owner_ruling": {"ruled_by": "x"}}
    data.write()
    refused("reconfirmation_not_admitted")
    assert data.log() == []


# --- the one test, as the build asks it ----------------------------------------------------------


def _filed(data):
    return filed(data.fact, run().record)


@pytest.mark.parametrize("edit", [
    lambda f: f.update(value=262144),
    lambda f: f.update(state="not_disclosed", value=None),
    lambda f: f["derivation"]["cited_change"]["readers"][1].update(value=262144),
    lambda f: f["derivation"]["cited_change"]["readers"][1].update(family="gpt-5"),
    lambda f: f["derivation"]["cited_change"]["readers"].pop(),
    lambda f: f["derivation"]["cited_change"].update(rule="two-readers-retained-agreement@1"),
    lambda f: f["derivation"]["cited_change"].update(clearing_epoch="initial"),
    lambda f: f["derivation"].update(owner_ruling={"ruled_by": "x"}),
    lambda f: f["sources"].append(dict(f["sources"][0], source_id="hf")),
    lambda f: f["derivation"]["cited_change"].update(read_date="2020-01-01"),
])
def test_an_edited_reconfirmation_fails_the_test(data, edit):
    fact = _filed(data)
    assert problem(data, fact) is None
    edited = copy.deepcopy(fact)
    edit(edited)
    assert problem(data, edited) is not None


def test_an_edited_licence_reconfirmation_fails_the_test(data):
    licence(data)
    fact = filed(data.fact, licence_run().record)
    assert problem(data, fact) is None
    for edit in ({"value": "permitted", "state": "known"}, {"value": "permitted"}):
        assert problem(data, {**fact, **edit}) is not None
    readers = copy.deepcopy(fact)
    for r in readers["derivation"]["cited_change"]["readers"]:
        r.pop("finding")
    assert problem(data, readers) is not None


def _build(data):
    from decision.snapshot import build_snapshot, collect_repo, load_built_snapshot
    from pipeline.load import load_models

    (data.root / "benchmarks").mkdir(exist_ok=True)
    card = yaml.safe_dump({"display_name": "Grok X", "model_id": SUBJECT, "facts": [data.fact]},
                          sort_keys=False)
    (data.root / "models/xai/grok-x.md").write_text(f"---\n{card}---\nbody\n")
    index = load_built_snapshot(build_snapshot(collect_repo(data.root)))
    (card,) = load_models(data.root)
    return index, card


def test_the_build_and_the_site_serve_a_reconfirmation_and_withhold_an_edited_one(data,
                                                                                   monkeypatch):
    file_record(data, run().record)
    index, card = _build(data)
    shown = index.fact(SUBJECT, FACET)
    assert shown.state == "known" and shown.value == FILED
    record = index.record(shown.record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    (cited,) = card.cited_facts
    assert cited["value"] == FILED and card.withheld_facets == ()
    # A value edited under the block: out of the build, withheld on the site.
    data.fact["value"] = 262144
    data.write()
    index, card = _build(data)
    assert index.fact(SUBJECT, FACET).state != "known"
    assert card.cited_facts == [] and card.withheld_facets == (FACET,)
    # It is the one test that keeps it out: without it the edited value would be served.
    import decision.reconfirmation as rule

    monkeypatch.setattr(rule, "reconfirmation_problem", lambda *a, **k: None)
    index, card = _build(data)
    assert index.fact(SUBJECT, FACET).value == 262144 and card.withheld_facets == ()


# --- the writer ----------------------------------------------------------------------------------


def test_the_writer_files_a_card_reconfirmation_and_its_claim(data):
    from scripts.cited_offering import WriteRefused, apply

    out = run()
    before = (data.root / "models/xai/grok-x.md").read_text()
    apply(out, data_dir=data.root)
    after = (data.root / "models/xai/grok-x.md").read_text()
    front = yaml.safe_load(after.split("---", 2)[1])
    (fact,) = front["facts"]
    assert fact["value"] == FILED and problem(data, fact) is None
    assert after.endswith("---\nbody\n") and before != after
    events = [json.loads(x) for x in
              (data.root / "verification/queue/events.jsonl").read_text().splitlines()]
    assert [e["event"] for e in events] == ["collected", "checked"]
    assert events[0]["claim"]["target"]["id"] == f"{SUBJECT}#{FACET}"
    assert events[0]["claim"]["sources"] == fact["sources"]
    # A plain change to a card fact is not written here.
    data.fact.clear()
    data.fact.update(dict(facet=FACET, value=FILED, state="known", checked_sources=[],
                          sources=[dict(source_id="s1", snapshot_ref="sha256:" + "0" * 64,
                                        cited_regions=["page"])]))
    data.write()
    (data.root / ATTEMPTS_FILE).unlink()
    change = cited_change(subject=SUBJECT, facet=FACET, source_id="s1", readers=pair(262144),
                          request=serve())
    assert change.changed
    with pytest.raises(WriteRefused):
        apply(change, data_dir=data.root)


# --- review round (Codex): stale writes, the logged line, provenance, the hold ------------------


@pytest.mark.parametrize("change", [
    lambda f: f.update(value=262144),
    lambda f: f.update(state="not_disclosed", value=None),
    lambda f: f.update(derivation={"cited_change": {"rule": "x"}}),
    lambda f: f.update(checked_sources=["hf"]),
])
def test_a_stale_reconfirmation_never_overwrites_a_newer_fact(data, change):
    from scripts.cited_offering import WriteRefused, apply

    out = run()
    change(data.fact)
    data.write()
    before = (data.root / "models/xai/grok-x.md").read_text()
    with pytest.raises(WriteRefused, match="changed since the gate read it"):
        apply(out, data_dir=data.root)
    assert (data.root / "models/xai/grok-x.md").read_text() == before
    assert not (data.root / "verification/queue/events.jsonl").exists()


def test_the_served_value_is_the_logged_agreements_not_the_facts_own_fields(data):
    fact = _filed(data)
    assert problem(data, fact) is None
    # A forgery that is consistent with itself: value, prior value and both answers edited.
    forged = copy.deepcopy(fact)
    forged["value"] = 262144
    block = forged["derivation"]["cited_change"]
    block["previous_value"] = 262144
    for r in block["readers"]:
        r["value"] = 262144
    assert problem(data, forged) is not None
    # The logged line itself: gone, or edited, admits nothing.
    lines = (data.root / ATTEMPTS_FILE).read_text().splitlines()
    (data.root / ATTEMPTS_FILE).write_text(lines[-1].replace("131072", "131073") + "\n")
    assert problem(data, fact) is not None
    (data.root / ATTEMPTS_FILE).write_text("")
    assert problem(data, fact) is not None


def test_a_later_disagreement_in_the_epoch_undoes_the_reconfirmation(data):
    fact = _filed(data)
    seed(data, harness=True, agreed=False)
    assert problem(data, fact) is not None


def test_every_source_the_fact_cited_stays_in_its_provenance(data):
    from scripts.cited_offering import apply

    other = "https://docs.x.ai/docs/models/grok-x-limits"
    data.sources.append(dict(data.sources[0], id="s2", url=other))
    data.sources.append(dict(data.sources[0], id="s3", url=other + "-more"))
    data.fact["sources"].append(dict(source_id="s3", snapshot_ref="sha256:" + "2" * 64,
                                     cited_regions=["page"]))
    data.fact["checked_sources"] = ["s2"]
    data.write()
    apply(run(), data_dir=data.root)
    front = yaml.safe_load((data.root / "models/xai/grok-x.md").read_text().split("---", 2)[1])
    (fact,) = front["facts"]
    assert [s["source_id"] for s in fact["sources"]] == ["s1"]
    assert fact["checked_sources"] == ["s2", "s1", "s3"]
    assert problem(data, fact) is None
    events = [json.loads(x) for x in
              (data.root / "verification/queue/events.jsonl").read_text().splitlines()]
    assert events[0]["claim"]["sources"] == fact["sources"]


@pytest.mark.parametrize("outcome", ["unreachable", "mismatch"])
def test_a_later_unresolved_verdict_holds_the_fact_on_the_site_as_in_the_build(data, outcome):
    from tests.snapshot_records import verification

    file_record(data, run().record)
    index, card = _build(data)
    assert index.fact(SUBJECT, FACET).value == FILED and card.withheld_facets == ()
    path = data.root / "verification/log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(verification("fact", f"{SUBJECT}#{FACET}", outcome,
                                            value=FILED)) + "\n")
    index, card = _build(data)
    assert index.fact(SUBJECT, FACET).state != "known"
    assert card.cited_facts == [] and card.withheld_facets == (FACET,)
