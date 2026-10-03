"""MODEL-217: the weekly price and plan re-read, replayed on fixture pages."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from decision import verify as verify_module
from decision.model import (
    DETERMINISTIC,
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore, FetchResult
from decision.verify import (
    Claim,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    is_quarantined,
    load_sources,
)
from decision.verify import run as verify_run
from scripts import price_reread
from scripts.price_reread import (
    BRANCH,
    RECONFIRM_BRANCH,
    Status,
    check_value_only,
    render_report,
    rewrite_fact,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = Path(__file__).parent / "fixtures" / "price_reread"
TODAY = date(2026, 10, 6)
AT = datetime(2026, 10, 6, 7, 41, tzinfo=UTC)
COLLECTOR = VerificationActor(agent="claude-fixture-collector", model_family="anthropic",
                              method="primary-source-read@2026-09-29")
PLANS_URL = "https://plans.example/pricing"
API_URL = "https://api.example/pricing"
RENDERED_URL = "https://rendered.example/pricing"

SOURCES = """\
schema_version: 1
sources:
- id: example-plans
  url: https://plans.example/pricing
  fetch: conditional_http
  normaliser: html-default
  cited_regions:
  - id: page
    locator: {kind: page, value: ''}
- id: example-api-pricing
  url: https://api.example/pricing
  fetch: conditional_http
  normaliser: html-default
  cited_regions:
  - id: page
    locator: {kind: page, value: ''}
- id: example-rendered
  url: https://rendered.example/pricing
  fetch: rendered
  normaliser: html-default
  cited_regions:
  - id: page
    locator: {kind: page, value: ''}
"""

# The two layouts real files use: flow-style subjects (MODEL-201/205) and block style.
PLANS = """\
# A comment the rewrite must keep.
- kind: subscription
  provider: example
  plan: pro
  name: Example Pro
  facts:
  - id: example/subscription/pro#offering.subscription.price
    subject: {kind: offering, id: example/subscription/pro}
    facet: offering.subscription.price
    state: known
    value: 20
    sources:
    - source_id: example-plans
      snapshot_ref: {plans}
      cited_regions: [page]
  - id: example/subscription/pro#offering.subscription.billing_period
    subject: {kind: offering, id: example/subscription/pro}
    facet: offering.subscription.billing_period
    state: known
    value: monthly
    sources:
    - source_id: example-plans
      snapshot_ref: {plans}
      cited_regions: [page]
- kind: subscription
  provider: example
  plan: max
  name: Example Max
  facts:
  - id: example/subscription/max#offering.subscription.price
    subject: {kind: offering, id: example/subscription/max}
    facet: offering.subscription.price
    state: known
    value: 100
    sources:
    - source_id: example-plans
      snapshot_ref: {plans}
      cited_regions: [page]
  - id: example/subscription/max#offering.subscription.coverage_quote
    subject: {kind: offering, id: example/subscription/max}
    facet: offering.subscription.coverage_quote
    state: unknown
    value: null
"""

API = """\
- model: example/example-large
  provider: example
  region: global
  tier: standard
  facts:
  - id: example/example/example-large/global/standard#offering.price.input
    subject:
      kind: offering
      id: example/example/example-large/global/standard
    facet: offering.price.input
    value: 3.0
    state: known
    sources:
    - source_id: example-api-pricing
      snapshot_ref: {api}
      cited_regions:
      - page
  - id: example/example/example-large/global/standard#offering.price.output
    subject:
      kind: offering
      id: example/example/example-large/global/standard
    facet: offering.price.output
    value: 15.0
    state: known
    sources:
    - source_id: example-api-pricing
      snapshot_ref: {api}
      cited_regions:
      - page
"""

RENDERED = """\
- kind: subscription
  provider: rendered
  plan: pro
  name: Rendered Pro
  facts:
  - id: rendered/subscription/pro#offering.subscription.price
    subject: {kind: offering, id: rendered/subscription/pro}
    facet: offering.subscription.price
    state: known
    value: 20
    sources:
    - source_id: example-rendered
      snapshot_ref: {plans}
      cited_regions: [page]
"""

PLAN_FILE = "offerings/subscriptions/example.yaml"
API_FILE = "offerings/example/example/example-large.yaml"
PRO_PRICE = "example/subscription/pro#offering.subscription.price"
LARGE_INPUT = "example/example/example-large/global/standard#offering.price.input"


def page(name: str) -> bytes:
    return (PAGES / name).read_bytes()


class ReplayFetcher:
    """Serves each URL's pages in order, repeating the last one; records every fetch."""

    def __init__(self, pages: dict[str, list[bytes | None]]) -> None:
        self.pages = {url: list(bodies) for url, bodies in pages.items()}
        self.fetched: list[str] = []

    def fetch(self, url: str, **_: object) -> FetchResult:
        self.fetched.append(url)
        bodies = self.pages[url]
        body = bodies.pop(0) if len(bodies) > 1 else bodies[0]
        if body is None:
            return FetchResult("unreachable", 503, error="HTTP 503")
        return FetchResult("ok", 200, body=body, content_type="text/html; charset=utf-8",
                           charset="utf-8")


@pytest.fixture
def estate(tmp_path: Path) -> tuple[Path, CopyStore]:
    """A catalogue whose facts were collected, filed and verified from the fixture pages."""
    root = tmp_path / "repo"
    store = CopyStore(tmp_path / "copies")
    refs = {"plans": store.put(page("plans.html")), "api": store.put(page("api-pricing.html"))}
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(SOURCES)
    for rel, text in ((PLAN_FILE, PLANS), (API_FILE, API),
                      ("offerings/subscriptions/rendered.yaml", RENDERED)):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text.replace("{plans}", refs["plans"])
                                .replace("{api}", refs["api"]))

    queue, log = Queue(root / "verification"), VerificationLog(root / "verification")
    names = {"example/subscription/pro": "Example Pro", "example/subscription/max": "Example Max",
             # Its retained copy is the plans fixture, read before the page went rendered.
             "rendered/subscription/pro": "Example Pro",
             "example/example/example-large/global/standard": "Example Large"}
    labels = {"offering.price.input": "Input", "offering.price.output": "Output"}
    for tracked in price_reread.tracked_facts(root):
        fact = tracked.fact
        subject = fact["subject"]["id"]
        unit = "usd_per_1m_tokens" if fact["facet"].startswith("offering.price.") else None
        queue.file(Claim(
            target=TargetRef(kind="fact", id=fact["id"]), subject=subject,
            names=(names[subject],), field=fact["facet"], value=fact["value"], unit=unit,
            label=labels.get(fact["facet"]), collector=COLLECTOR,
            sources=tuple(SourceRef.model_validate(s) for s in fact["sources"]),
        ), at=datetime(2026, 9, 29, 14, tzinfo=UTC))
    regions = StoredRegions(store, load_sources(root / "registry" / "sources.yaml"))
    setup = verify_run(queue, log, regions, deterministic_extractors(), today=date(2026, 9, 29))
    assert setup.counts["verified"] == 6, setup.to_dict()
    return root, store


def reread(estate, plans: list[bytes | None], api: list[bytes | None] | None = None, *,
           write: bool = False) -> tuple[price_reread.Report, ReplayFetcher]:
    root, store = estate
    fetcher = ReplayFetcher({PLANS_URL: plans, API_URL: api or [page("api-pricing.html")]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=TODAY,
                              write=write, at=AT)
    return report, fetcher


def by_id(report: price_reread.Report) -> dict[str, price_reread.FactResult]:
    return {f.fact_id: f for f in report.facts}


def test_an_unchanged_page_logs_a_dated_reconfirmation_and_edits_no_offering(estate) -> None:
    root, _ = estate
    before = {p: p.read_text() for p in (root / "offerings").glob("**/*.yaml")}
    queue_before = (root / "verification" / "queue" / "events.jsonl").read_text()
    report, fetcher = reread(estate, [page("plans.html")], write=True)

    assert report.counts() == {"unchanged": 5, "changed": 0, "needs_review": 0,
                               "unreadable": 0, "unreachable": 0, "not_reread": 1}
    assert report.alerts == [] and report.changes == []
    assert {p: p.read_text() for p in before} == before
    assert (root / "verification" / "queue" / "events.jsonl").read_text() == queue_before
    assert RENDERED_URL not in fetcher.fetched

    latest = VerificationLog(root / "verification").latest()
    reconfirmed = {key[1]: v for key, v in latest.items() if v.date == TODAY}
    assert sorted(reconfirmed) == sorted(report.to_dict()["reconfirmed"])
    assert len(reconfirmed) == 5
    assert all(v.outcome == "verified" and v.verifier.model_family == DETERMINISTIC
               and v.collector == COLLECTOR for v in reconfirmed.values())
    assert reconfirmed[PRO_PRICE].target.value_hash == value_hash(20)


def test_a_changed_plan_price_is_rewritten_verified_and_reported(estate) -> None:
    root, store = estate
    before = (root / PLAN_FILE).read_text()
    report, _ = reread(estate, [page("plans-price-change.html")], write=True)

    [change] = report.changes
    new_ref = store.put(page("plans-price-change.html"))
    assert (change.fact_id, change.old_value, change.new_value) == (PRO_PRICE, 20, 25)
    assert change.copies["example-plans"][1] == new_ref
    # The billing period on the same page still reads "monthly".
    assert by_id(report)[f"{PRO_PRICE.split('#')[0]}#offering.subscription.billing_period"] \
        .status is Status.UNCHANGED

    after = (root / PLAN_FILE).read_text()
    changed = [(a, b) for a, b in zip(before.splitlines(), after.splitlines(), strict=True)
               if a != b]
    assert changed == [
        ("    value: 20", "    value: 25"),
        (f"      snapshot_ref: {change.copies['example-plans'][0]}",
         f"      snapshot_ref: {new_ref}"),
    ]
    fact = next(f for o in yaml.safe_load(after) for f in o["facts"] if f["id"] == PRO_PRICE)
    assert fact["value"] == 25 and fact["state"] == "known"

    latest = VerificationLog(root / "verification").latest()[("fact", PRO_PRICE)]
    assert latest.outcome == "verified"
    assert latest.target.value_hash == value_hash(25)
    assert latest.collector.agent == "modelspec-price-reread"
    assert latest.verifier.agent == "modelspec-verify"
    assert latest.verifier.model_family == DETERMINISTIC
    assert not is_quarantined(f"fact:{PRO_PRICE}", directory=root / "verification")
    assert Queue(root / "verification").filed()[("fact", PRO_PRICE)].value == 25

    body = render_report(report)
    assert f"| `{PRO_PRICE}` | 20 | 25 |" in body
    assert "-$20/month" in body and "+$25/month" in body


def test_a_changed_pay_per_use_price_keeps_its_type(estate) -> None:
    root, _ = estate
    report, _ = reread(estate, [page("plans.html")], [page("api-pricing-change.html")],
                       write=True)

    [change] = report.changes
    assert (change.fact_id, change.old_value, change.new_value) == (LARGE_INPUT, 3.0, 2.5)
    text = (root / API_FILE).read_text()
    assert "    value: 2.5\n" in text and "    value: 15.0\n" in text
    assert VerificationLog(root / "verification").latest()[("fact", LARGE_INPUT)] \
        .target.value_hash == value_hash(2.5)


def test_an_unreadable_layout_raises_an_alert_and_never_guesses(estate) -> None:
    root, _ = estate
    before = (root / PLAN_FILE).read_text()
    report, _ = reread(estate, [page("plans-redesign.html")], write=True)

    alerted = {f.fact_id: f.status for f in report.alerts}
    assert set(alerted) == {
        PRO_PRICE,
        "example/subscription/pro#offering.subscription.billing_period",
        "example/subscription/max#offering.subscription.price",
    }
    assert set(alerted.values()) == {Status.UNREADABLE}
    assert report.changes == []
    assert (root / PLAN_FILE).read_text() == before
    assert "### Needs a person" in render_report(report)
    assert report.to_dict()["alerts"][0]["status"] == "unreadable"


def test_a_script_shell_is_fetched_again_before_it_alerts(estate) -> None:
    report, fetcher = reread(estate, [page("plans-shell.html"), page("plans.html")])
    assert report.alerts == []
    assert fetcher.fetched.count(PLANS_URL) == 2

    report, _ = reread(estate, [page("plans-shell.html")])
    assert {f.status for f in report.alerts} == {Status.UNREADABLE}
    assert "characters of text" in report.alerts[0].reason


def test_an_unreachable_page_alerts_after_one_more_try(estate) -> None:
    report, fetcher = reread(estate, [None, page("plans.html")])
    assert report.alerts == [] and fetcher.fetched.count(PLANS_URL) == 2

    report, _ = reread(estate, [None])
    assert {f.status for f in report.alerts} == {Status.UNREACHABLE}
    assert report.alerts[0].reason == "HTTP 503"


def test_rendered_and_quarantined_facts_are_listed_not_reread(estate) -> None:
    root, _ = estate
    report, _ = reread(estate, [page("plans.html")])
    reasons = {f.fact_id: f.reason for f in report.facts if f.status is Status.NOT_REREAD}
    assert reasons == {"rendered/subscription/pro#offering.subscription.price":
                       "the page needs a rendered fetch"}


def test_the_guard_refuses_a_rewrite_of_another_fact(estate) -> None:
    root, _ = estate
    text = (root / PLAN_FILE).read_text()
    change = price_reread.FactResult(
        PRO_PRICE, "offering.subscription.price", PLAN_FILE, ("example-plans",),
        Status.CHANGED, "known", 20, new_value=25)
    rewritten = rewrite_fact(text, change)
    check_value_only(text, rewritten, [change])

    tampered = rewritten.replace("    value: 100", "    value: 90")
    with pytest.raises(ValueError, match="changed without a re-read change"):
        check_value_only(text, tampered, [change])


def test_price_pull_requests_are_never_auto_merged() -> None:
    automerge = (ROOT / ".github" / "workflows" / "automerge.yml").read_text()
    workflow = (ROOT / ".github" / "private-writers" / "price-reread.yml").read_text()
    assert f"github.head_ref != '{BRANCH}'" in automerge
    assert f"branch: {BRANCH}" in workflow
    assert "gh pr merge" not in workflow
    # The log-only reconfirmation branch is the one this job lets auto-merge.
    assert f"branch: {RECONFIRM_BRANCH}" in workflow
    assert RECONFIRM_BRANCH not in automerge


def test_a_runner_store_keeps_only_cited_and_fetched_copies(estate) -> None:
    root, store = estate
    stray = store.put(b"a page no fact cites")
    report, _ = reread(estate, [page("plans-price-change.html")], write=True)

    [change] = report.changes
    old_plans, new_plans = change.copies["example-plans"]
    assert price_reread.retain_only(store, root, report) == 1
    assert not store.has(stray)
    # Example Max still cites the old copy; Example Pro now cites the new one.
    assert store.has(old_plans) and store.has(new_plans)
    assert store.has(report.sources["example-api-pricing"].copy_ref)


QUOTED = """\
- kind: subscription
  provider: example
  plan: pro
  name: Example Pro
  facts:
  - id: example/subscription/pro#offering.subscription.coverage_quote
    subject: {kind: offering, id: example/subscription/pro}
    facet: offering.subscription.coverage_quote
    state: known
    value: 'Opus | No | Yes

      Sonnet | Yes | Yes'
    sources:
    - source_id: example-plans
      snapshot_ref: sha256:1111111111111111111111111111111111111111111111111111111111111111
      cited_regions: [page]
  - id: example/subscription/pro#offering.subscription.price
    subject: {kind: offering, id: example/subscription/pro}
    facet: offering.subscription.price
    state: known
    value: 20
    sources:
    - source_id: example-plans
      snapshot_ref: sha256:1111111111111111111111111111111111111111111111111111111111111111
      cited_regions: [page]
"""


@pytest.mark.parametrize("new", ["Opus | Yes | Yes", "Opus | Yes | Yes\n\nSonnet | No | Yes"])
def test_a_multi_paragraph_quoted_value_is_replaced_whole(new: str) -> None:
    fid = "example/subscription/pro#offering.subscription.coverage_quote"
    new_ref = "sha256:" + "2" * 64
    change = price_reread.FactResult(
        fid, "offering.subscription.coverage_quote", PLAN_FILE, ("example-plans",),
        Status.CHANGED, "known", "Opus | No | Yes\nSonnet | Yes | Yes", new_value=new,
        copies={"example-plans": ("sha256:" + "1" * 64, new_ref)})
    rewritten = rewrite_fact(QUOTED, change)
    check_value_only(QUOTED, rewritten, [change])

    facts = {f["id"]: f for o in yaml.safe_load(rewritten) for f in o["facts"]}
    assert facts[fid]["value"] == new
    assert facts[fid]["sources"][0]["snapshot_ref"] == new_ref
    assert facts[PRO_PRICE]["value"] == 20
    # The three lines of the old value became one; nothing around them moved.
    old, out = QUOTED.splitlines(), rewritten.splitlines()
    assert out[:9] == old[:9] and out[10:12] == old[12:14] and out[13:] == old[15:]


def test_a_refused_rewrite_becomes_an_alert_and_writes_nothing(estate, monkeypatch) -> None:
    root, _ = estate
    before = (root / PLAN_FILE).read_text()
    log_before = (root / "verification" / "log.jsonl").read_text()

    def tamper(text: str, change: price_reread.FactResult) -> str:
        return text.replace("    value: 100", "    value: 90")

    monkeypatch.setattr(price_reread, "rewrite_fact", tamper)
    report, _ = reread(estate, [page("plans-price-change.html")], write=True)

    assert report.changes == []
    [alert] = [f for f in report.alerts if f.fact_id == PRO_PRICE]
    assert alert.status is Status.NEEDS_REVIEW
    assert "the rewrite guard refused it" in alert.reason
    assert (root / PLAN_FILE).read_text() == before
    log_after = (root / "verification" / "log.jsonl").read_text()
    new_records = [json.loads(line) for line in log_after[len(log_before):].splitlines()]
    assert all(r["target"]["id"] != PRO_PRICE for r in new_records)


def test_page_text_cannot_close_the_diff_fence() -> None:
    report = price_reread.Report(TODAY, diffs={"example-plans": ["+```", "+# injected"]})
    body = render_report(report)
    assert "````diff\n+```\n+# injected\n````" in body


MISTRAL = VerificationActor(agent="ollama", model_family="mistral", method="llm-extract:mistral")
LARGE_OUTPUT = "example/example/example-large/global/standard#offering.price.output"


def _llm_verified(root: Path, fact_id: str, value: object) -> None:
    """Log that an LLM reader last verified ``value`` for this fact."""
    VerificationLog(root / "verification").append(Verification(
        target=VerificationTarget(kind="fact", id=fact_id, value_hash=value_hash(value)),
        collector=COLLECTOR, verifier=MISTRAL, method=MISTRAL.method, outcome="verified",
        date=date(2026, 9, 29)))


def test_an_llm_verified_value_the_readers_confirm_is_reconfirmed(estate) -> None:
    """MODEL-235: a value a Mistral reader verified is reconfirmed deterministically."""
    root, _ = estate
    _llm_verified(root, LARGE_INPUT, 3.0)
    report, _ = reread(estate, [page("plans.html")], write=True)

    assert by_id(report)[LARGE_INPUT].status is Status.UNCHANGED
    latest = VerificationLog(root / "verification").latest()[("fact", LARGE_INPUT)]
    assert (latest.date, latest.verifier.model_family) == (TODAY, DETERMINISTIC)


def test_an_llm_verified_value_read_otherwise_alerts_and_is_never_written(estate) -> None:
    root, _ = estate
    _llm_verified(root, LARGE_INPUT, 3.0)
    before = (root / API_FILE).read_text()
    report, _ = reread(estate, [page("plans.html")], [page("api-pricing-change.html")],
                       write=True)

    result = by_id(report)[LARGE_INPUT]
    assert result.status is Status.NEEDS_REVIEW
    assert result.reason == ("last verified by an LLM reader (mistral); "
                             "a deterministic reader now reads 2.5")
    assert report.changes == []
    assert (root / API_FILE).read_text() == before


def test_an_llm_verified_value_the_readers_cannot_read_is_not_an_alert(estate) -> None:
    root, _ = estate
    _llm_verified(root, LARGE_INPUT, 3.0)
    # The API page now serves no price table at all.
    report, _ = reread(estate, [page("plans.html")], [page("plans.html")])

    result = by_id(report)[LARGE_INPUT]
    assert result.status is Status.NOT_REREAD
    assert result.reason == ("last verified by an LLM reader (mistral); "
                             "the deterministic readers cannot read it")
    # The deterministically verified output price on the same page does alert.
    assert by_id(report)[LARGE_OUTPUT].status is Status.UNREADABLE


def test_a_value_the_page_did_not_state_is_reviewed_not_written(estate) -> None:
    """MODEL-235: a price that was not disclosed and now reads as one goes to a person."""
    root, store = estate
    text = (root / API_FILE).read_text()
    (root / API_FILE).write_text(text.replace("    value: 15.0\n    state: known",
                                              "    value: null\n    state: not_disclosed"))
    queue = Queue(root / "verification")
    old = queue.filed()[("fact", LARGE_OUTPUT)]
    queue.file(replace(old, value=None), at=AT)
    VerificationLog(root / "verification").append(Verification(
        target=VerificationTarget(kind="fact", id=LARGE_OUTPUT, value_hash=value_hash(None)),
        collector=COLLECTOR, verifier=verify_module.OfferingPriceExtractor.actor,
        method="offering-price-table@1", outcome="verified", date=date(2026, 9, 29)))
    before = (root / API_FILE).read_text()

    report, _ = reread(estate, [page("plans.html")], write=True)

    result = by_id(report)[LARGE_OUTPUT]
    assert result.status is Status.NEEDS_REVIEW
    assert result.reason.startswith("was not_disclosed; a reader now reads 15:")
    assert (root / API_FILE).read_text() == before


def test_overdue_offering_is_fetched_and_reconfirmed(estate):
    root, store = estate
    fetcher = ReplayFetcher({PLANS_URL: [page('plans.html')], API_URL: [page('api-pricing.html')]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store,
                              today=date(2026, 10, 20), write=True, at=AT)
    assert API_URL in fetcher.fetched
    assert LARGE_INPUT in report.overdue
    assert next(f.status for f in report.facts if f.fact_id == LARGE_INPUT) is Status.UNCHANGED
    assert VerificationLog(root / 'verification').latest()[('fact', LARGE_INPUT)].date == date(2026, 10, 20)
    assert report.to_dict()['max_read_age_days'] == 7


def test_overdue_price_without_filed_claim_alerts(estate):
    root, store = estate
    Queue(root / 'verification').path.unlink()
    fetcher = ReplayFetcher({})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=date(2026, 10, 20))
    assert LARGE_INPUT in {fact.fact_id for fact in report.alerts}
    assert fetcher.fetched == []
