"""MODEL-481: the price re-read confirms an undisclosed price and reads one cell per fact.

Every case replays a fixture page through the real ``scripts.price_reread.run`` and the real
readers. Providers, models and prices are invented.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from decision.model import (
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore, FetchResult
from decision.verify import Claim, OfferingPriceExtractor, Queue, VerificationLog
from scripts import price_reread
from scripts.price_reread import Status

TODAY = date(2026, 11, 13)
AT = datetime(2026, 11, 13, 7, 41, tzinfo=UTC)
COLLECTOR = VerificationActor(agent="fixture-collector", model_family="anthropic",
                              method="primary-source-read@2026-11-01")
URL = "https://pricing.example/models"
OFFERING_FILE = "offerings/examplecloud/acme/alpha.yaml"
SUBJECT = "examplecloud/acme/alpha/global/standard"
SOURCES = """\
schema_version: 1
sources:
- id: example-pricing
  url: https://pricing.example/models
  fetch: conditional_http
  normaliser: html-default
  cited_regions:
  - id: page
    locator: {kind: page, value: ''}
"""

# Azure-shaped: price labels inside one cell, a Pricing column and two more columns.
ALPHA = "Acme Alpha Global"
NO_BATCH = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Cached Input: $0.40 Output: $20</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Acme Gamma Global</td><td>Input: $1 Output: $5</td><td>N/A</td><td>N/A</td></tr>
</table></body></html>"""
WITH_BATCH_VALUE = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Pricing with Batch API (1M Tokens)</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>Input: $2 Output: $10</td></tr>
</table></body></html>"""
WITH_BATCH_NA = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Pricing with Batch API (1M Tokens)</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>N/A</td></tr>
</table></body></html>"""
OTHER_MODEL_ONLY = """<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>Acme Gamma Global</td><td>Input: $1 Output: $5</td><td>N/A</td><td>N/A</td></tr>
</table></body></html>"""
LOOSER_NAME_ONLY = """<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>Acme Alpha Mini Global</td><td>Input: $1 Output: $5</td><td>N/A</td><td>N/A</td></tr>
</table></body></html>"""
NO_TABLE = "<html><body><h1>Pricing</h1><p>Acme Alpha Global is available.</p></body></html>"
ONE_LINE_TABLE = f"""<html><body><table>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td></tr>
</table></body></html>"""
ROW_WITHOUT_PRICES = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>{ALPHA}</td><td>Contact sales</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Acme Gamma Global</td><td>Input: $1 Output: $5</td><td>N/A</td><td>N/A</td></tr>
</table></body></html>"""
# The model also appears in a second table of another width, which carries a Batch column.
SECOND_TABLE_HAS_BATCH = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>N/A</td><td>N/A</td></tr>
</table><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Pricing with Batch API (1M Tokens)</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>Input: $2 Output: $10</td></tr>
</table></body></html>"""


ASYNC_COLUMN = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Asynchronous (1M Tokens)</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>Input: $2 Output: $10</td></tr>
</table></body></html>"""
FOOTNOTE = NO_BATCH.replace("</table>", "</table><p>Batch API requests are billed at 50% off.</p>")
CACHING_COLUMN = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Prompt caching (1M Tokens)</th></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>Cached Input: $0.40</td></tr>
</table></body></html>"""
FIRST_TABLE_ONLY = f"""<html><body><table>
<tr><th>Model</th><th>Pricing (1M Tokens)</th><th>Flex</th><th>Priority</th></tr>
<tr><td>Acme Gamma Global</td><td>Input: $1 Output: $5</td><td>N/A</td><td>N/A</td></tr>
<tr><td>{ALPHA}</td><td>Input: $4 Output: $20</td><td>N/A</td><td>N/A</td></tr>
</table></body></html>"""


class Fetcher:
    def __init__(self, body: bytes | None) -> None:
        self.body = body

    def fetch(self, url: str, **_: object) -> FetchResult:
        if self.body is None:
            return FetchResult("unreachable", 503, error="HTTP 503")
        return FetchResult("ok", 200, body=self.body, content_type="text/html; charset=utf-8",
                           charset="utf-8")


def build(tmp_path: Path, page: str, facts: list[tuple[str, str, Any]],
          *, names: tuple[str, ...] = (ALPHA,)) -> tuple[Path, CopyStore]:
    """A catalogue whose facts were filed and verified against ``page``."""
    root = tmp_path / "repo"
    store = CopyStore(tmp_path / "copies")
    ref = store.put(page.encode(), source_url="https://fixture.example/")
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(SOURCES)
    entries = []
    for kind, state, value in facts:
        entries.append({
            "id": f"{SUBJECT}#offering.price.{kind}",
            "subject": {"kind": "offering", "id": SUBJECT},
            "facet": f"offering.price.{kind}", "value": value, "state": state,
            "sources": [{"source_id": "example-pricing", "snapshot_ref": ref,
                         "cited_regions": ["page"]}],
        })
    (root / OFFERING_FILE).parent.mkdir(parents=True)
    (root / OFFERING_FILE).write_text(yaml.safe_dump([
        {"model": "acme/alpha", "provider": "examplecloud", "region": "global",
         "tier": "standard", "facts": entries}]))
    queue, log = Queue(root / "verification"), VerificationLog(root / "verification")
    for entry in entries:
        queue.file(Claim(
            target=TargetRef(kind="fact", id=entry["id"]), subject=SUBJECT, names=names,
            field=entry["facet"], value=entry["value"], unit="usd_per_1m_tokens",
            label=entry["facet"].removeprefix("offering.price.").replace("_", " ").title(),
            collector=COLLECTOR,
            sources=tuple(SourceRef.model_validate(s) for s in entry["sources"]),
        ), at=datetime(2026, 11, 6, 14, tzinfo=UTC))
        log.append(Verification(
            target=VerificationTarget(kind="fact", id=entry["id"],
                                      value_hash=value_hash(entry["value"])),
            collector=COLLECTOR, verifier=OfferingPriceExtractor.actor,
            method="offering-price-table@1", outcome="verified", date=date(2026, 11, 6)))
    return root, store


def reread(estate: tuple[Path, CopyStore], page: str | None, *, write: bool = False
           ) -> price_reread.Report:
    root, store = estate
    body = None if page is None else page.encode()
    return price_reread.run(root=root, fetcher=Fetcher(body), store=store, today=TODAY,
                            write=write, at=AT)


def result(report: price_reread.Report, kind: str) -> price_reread.FactResult:
    fact_id = f"{SUBJECT}#offering.price.{kind}"
    return next(f for f in report.facts if f.fact_id == fact_id)


# --- fault 1: a price filed not_disclosed ---------------------------------------------------------

NEUTRAL = Status.NOT_DISCLOSED_NO_VALUE


def untouched(root: Path) -> dict[Path, bytes]:
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def assert_claims_nothing(report: price_reread.Report, fact: price_reread.FactResult,
                          root: Path, before: dict[Path, bytes]) -> None:
    assert fact.status is NEUTRAL
    assert fact.verification is None
    assert fact not in report.alerts and fact not in report.changes
    assert report.counts()["not_disclosed_no_value"] >= 1
    after = untouched(root)
    changed = {p.name for p in before if after[p] != before[p]}
    assert changed <= {"log.jsonl"}  # only another fact's dated reconfirmation
    latest = VerificationLog(root / "verification").latest()[("fact", fact.fact_id)]
    assert latest.date == date(2026, 11, 6)


def test_nothing_to_read_for_a_not_disclosed_price_is_neutral_and_writes_nothing(
        tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("input", "known", 4.0),
                                        ("batch_input", "not_disclosed", None),
                                        ("batch_output", "not_disclosed", None)])
    root, _ = estate
    before = untouched(root)
    report = reread(estate, NO_BATCH, write=True)

    for kind in ("batch_input", "batch_output"):
        assert_claims_nothing(report, result(report, kind), root, before)
        assert "example-pricing#page" in result(report, kind).reason
    assert result(report, "input").status is Status.UNCHANGED
    counts = report.counts()
    assert counts["unchanged"] == 1 and counts["unreadable"] == 0
    assert counts["not_disclosed_no_value"] == 2 and report.alerts == []
    body = price_reread.render_report(report)
    assert "### Not disclosed, nothing to read" in body
    assert "example-pricing#page" in body
    assert report.to_dict()["not_disclosed_no_value"][0]["sources"] == ["example-pricing"]
    assert len(price_reread.alert_comment(report.to_dict(), "https://run.example/1")
               .split("| Source |")[1].splitlines()) == 4  # header rule, no source rows


def test_a_batch_value_now_stated_on_the_row_is_a_disclosed_alert_and_writes_nothing(
        tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    root, _ = estate
    files = untouched(root)

    report = reread(estate, WITH_BATCH_VALUE, write=True)

    stated = result(report, "batch_input")
    assert stated.status is Status.NEEDS_REVIEW and stated in report.alerts
    assert stated.reason.startswith("disclosed: page now states a value")
    assert report.changes == []
    assert untouched(root) == files


def test_an_explicit_not_available_cell_is_reviewed_without_the_disclosed_prefix(
        tmp_path) -> None:
    estate = build(tmp_path, WITH_BATCH_NA, [("batch_input", "not_disclosed", None)])
    root, _ = estate
    before = untouched(root)
    report = reread(estate, WITH_BATCH_NA)
    stated = result(report, "batch_input")
    assert stated.status is Status.NEEDS_REVIEW and stated in report.alerts
    assert "not available" in stated.reason and "not_offered" in stated.reason
    assert not stated.reason.startswith("disclosed")
    assert untouched(root) == before


def test_not_offered_with_an_explicit_not_available_cell_keeps_todays_outcome(tmp_path) -> None:
    estate = build(tmp_path, WITH_BATCH_NA, [("batch_input", "not_offered", None)])
    assert result(reread(estate, WITH_BATCH_NA), "batch_input").status is Status.UNREADABLE


def test_not_offered_without_the_column_keeps_todays_outcome(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_offered", None)])
    assert result(reread(estate, NO_BATCH), "batch_input").status is Status.UNREADABLE


def test_an_unknown_fact_is_not_re_read(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("input", "known", 4.0)])
    root, _ = estate
    text = (root / OFFERING_FILE).read_text()
    (root / OFFERING_FILE).write_text(text.replace("state: known", "state: unknown")
                                      .replace("value: 4.0", "value: null"))
    assert price_reread.tracked_facts(root) == []


@pytest.mark.parametrize("page", [OTHER_MODEL_ONLY, LOOSER_NAME_ONLY, NO_TABLE, ONE_LINE_TABLE,
                                  ROW_WITHOUT_PRICES],
                         ids=["row-missing", "row-of-a-looser-name", "no-table",
                              "no-header-row", "no-other-price-on-the-row"])
def test_a_page_that_did_not_read_stays_unreadable(tmp_path, page: str) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    report = reread(estate, page)
    unread = result(report, "batch_input")
    assert unread.status is Status.UNREADABLE and unread in report.alerts


@pytest.mark.parametrize("page,kind", [
    (ASYNC_COLUMN, "batch_input"), (FOOTNOTE, "batch_input"),
    (CACHING_COLUMN, "cached_input"), (SECOND_TABLE_HAS_BATCH, "batch_input"),
    (FIRST_TABLE_ONLY, "batch_input")],
    ids=["asynchronous-column", "footnote-sentence", "prompt-caching-column",
         "second-table", "partial-render"])
def test_the_wrong_confirmations_of_round_one_claim_nothing(tmp_path, page: str, kind: str
                                                            ) -> None:
    estate = build(tmp_path, NO_BATCH, [(kind, "not_disclosed", None)])
    root, _ = estate
    before = untouched(root)
    report = reread(estate, page)
    fact = result(report, kind)
    assert fact.status is not Status.UNCHANGED and fact.verification is None
    assert fact.status in {NEUTRAL, Status.NEEDS_REVIEW}
    assert untouched(root) == before


def test_a_page_that_did_not_fetch_is_unreachable(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    assert result(reread(estate, None), "batch_input").status is Status.UNREACHABLE


def test_a_known_batch_price_whose_column_is_gone_stays_unreadable(tmp_path) -> None:
    estate = build(tmp_path, WITH_BATCH_VALUE, [("batch_input", "known", 2.0)])
    report = reread(estate, NO_BATCH)
    gone = result(report, "batch_input")
    assert gone.status is Status.UNREADABLE and gone in report.alerts


# --- fault 2: one cell per fact -------------------------------------------------------------------


def vertex(*rows: str) -> str:
    body = "".join(rows)
    return ("<html><body><table><tr><th>Model</th><th>Type</th><th>Price (/1M tokens)</th></tr>"
            + body + "</table></body></html>")


BETA = "Acme Beta"


def first(model: str, kind: str, price: str) -> str:
    return f"<tr><td>{model}</td><td>{kind}</td><td>{price}</td></tr>"


def more(kind: str, price: str) -> str:
    return f"<tr><td></td><td>{kind}</td><td>{price}</td></tr>"


DIFFERENT = vertex(first(BETA, "Input", "$5.00"), more("Output", "$25.00"),
                   more("Batch Input", "$2.50"), more("Batch Output", "$12.50"))


@pytest.mark.parametrize("kind,filed", [("input", 5.0), ("output", 25.0),
                                        ("batch_input", 2.5), ("batch_output", 12.5)])
def test_each_fact_reads_only_its_own_row(tmp_path, kind: str, filed: float) -> None:
    estate = build(tmp_path, DIFFERENT, [(kind, "known", filed)], names=(BETA,))
    report = reread(estate, DIFFERENT)
    assert result(report, kind).status is Status.UNCHANGED


@pytest.mark.parametrize("kind,other_price", [("output", 12.5), ("batch_output", 25.0)])
def test_a_price_equal_to_the_other_rows_cell_is_never_unchanged(
        tmp_path, kind: str, other_price: float) -> None:
    estate = build(tmp_path, DIFFERENT, [(kind, "known", other_price)], names=(BETA,))
    report = reread(estate, DIFFERENT)
    wrong = result(report, kind)
    assert wrong.status is not Status.UNCHANGED
    assert wrong.status is Status.NEEDS_REVIEW and wrong in report.alerts


def test_a_row_printed_twice_with_equal_cells_still_reads(tmp_path) -> None:
    page = vertex(first(BETA, "Input", "$5.00"), more("Output", "$25.00"),
                  more("Batch Output", "$12.50"), more("Batch Output", "$12.50"))
    estate = build(tmp_path, page, [("batch_output", "known", 12.5)], names=(BETA,))
    assert result(reread(estate, page), "batch_output").status is Status.UNCHANGED


def test_a_row_printed_twice_with_different_cells_is_unreadable(tmp_path) -> None:
    page = vertex(first(BETA, "Input", "$5.00"), more("Output", "$25.00"),
                  more("Batch Output", "$12.50"), more("Batch Output", "$11.00"))
    estate = build(tmp_path, page, [("batch_output", "known", 12.5)], names=(BETA,))
    report = reread(estate, page)
    twice = result(report, "batch_output")
    assert twice.status is Status.UNREADABLE and twice in report.alerts
    assert "disagree" in twice.reason


EXTENDED = vertex(
    first(BETA, "Input (text, image, video, audio)", "$5.00"),
    more("Text output (response and reasoning)", "$25.00"),
    more("Batch input (text)", "$2.50"),
    more("Batch output (text)", "$12.50"),
    more("Cache hit", "$0.50"))


@pytest.mark.parametrize("kind,filed", [("input", 5.0), ("output", 25.0),
                                        ("batch_input", 2.5), ("batch_output", 12.5),
                                        ("cached_input", 0.5)])
def test_a_label_that_extends_the_type_reads_its_own_kind(tmp_path, kind: str,
                                                          filed: float) -> None:
    estate = build(tmp_path, EXTENDED, [(kind, "known", filed)], names=(BETA,))
    assert result(reread(estate, EXTENDED), kind).status is Status.UNCHANGED


@pytest.mark.parametrize("kind,other", [("input", 25.0), ("output", 5.0),
                                        ("batch_input", 5.0), ("batch_output", 25.0)])
def test_an_extended_label_never_reads_another_kinds_row(tmp_path, kind: str,
                                                         other: float) -> None:
    estate = build(tmp_path, EXTENDED, [(kind, "known", other)], names=(BETA,))
    assert result(reread(estate, EXTENDED), kind).status is Status.NEEDS_REVIEW


def test_two_extended_rows_that_disagree_are_unreadable(tmp_path) -> None:
    page = vertex(first(BETA, "Input (text)", "$5.00"), more("Input (audio)", "$9.00"),
                  more("Output", "$25.00"))
    estate = build(tmp_path, page, [("input", "known", 5.0)], names=(BETA,))
    twice = result(reread(estate, page), "input")
    assert twice.status is Status.UNREADABLE and "disagree" in twice.reason


def test_the_vertex_reader_returns_one_cell_for_one_kind() -> None:
    claim = Claim(
        target=TargetRef(kind="fact", id="x#offering.price.output"), subject=SUBJECT,
        names=(BETA,), field="offering.price.output", label="Output", value=25.0,
        unit="usd_per_1m_tokens", collector=COLLECTOR,
        sources=(SourceRef(source_id="pricing", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["prices"]),))
    text = ("Model | Type | Price (/1M tokens)\n"
            "Acme Beta | Input | $5.00\n| Output | $25.00\n| Batch Output | $12.50\n")
    readings = OfferingPriceExtractor().extract(claim, text)
    assert [r.value for r in readings] == ["$25.00"]


# --- the column-header scan: a header that names the kind and no other ---------------------------


def scan(*cells: str, headers: str) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers.split("|"))
    body = "".join(f"<td>{c}</td>" for c in cells)
    return f"<html><body><table><tr>{head}</tr><tr>{body}</tr></table></body></html>"


SCAN_HEADERS = ("Model|Cache write input tokens|Cache read input tokens|Input tokens|"
                "Output tokens|Input tokens batch")
SCAN = scan(BETA, "$6", "$0.50", "$5", "$25", "$2.50", headers=SCAN_HEADERS)


@pytest.mark.parametrize("kind,filed", [("input", 5.0), ("output", 25.0),
                                        ("cached_input", 0.5), ("batch_input", 2.5)])
def test_the_header_scan_reads_only_the_header_that_names_the_kind(tmp_path, kind: str,
                                                                    filed: float) -> None:
    estate = build(tmp_path, SCAN, [(kind, "known", filed)], names=(BETA,))
    assert result(reread(estate, SCAN), kind).status is Status.UNCHANGED


def test_the_header_scan_never_takes_a_cache_write_column_for_input(tmp_path) -> None:
    estate = build(tmp_path, SCAN, [("input", "known", 6.0)], names=(BETA,))
    assert result(reread(estate, SCAN), "input").status is Status.NEEDS_REVIEW


def test_two_headers_for_one_kind_with_different_cells_are_unreadable(tmp_path) -> None:
    page = scan(BETA, "$5", "$4", "$25", headers="Model|Input tokens|Input tokens (reserved)|"
                "Output tokens")
    estate = build(tmp_path, page, [("input", "known", 5.0)], names=(BETA,))
    twice = result(reread(estate, page), "input")
    assert twice.status is Status.UNREADABLE and "disagree" in twice.reason


# --- cached input never reads the plain input price ---------------------------------------------


def with_cache(label: str | None) -> str:
    rows = [first(BETA, "Input (text)", "$5.00"), more("Output", "$25.00")]
    if label:
        rows.append(more(label, "$0.50"))
    return vertex(*rows)


@pytest.mark.parametrize("label", ["Cache hit", "Cache read", "Cache Hit / Cache read",
                                   "Cached input", "Prompt caching"])
def test_cached_input_reads_the_cache_rows_own_price(tmp_path, label: str) -> None:
    page = with_cache(label)
    own = build(tmp_path / "own", page, [("cached_input", "known", 0.5)], names=(BETA,))
    assert result(reread(own, page), "cached_input").status is Status.UNCHANGED
    plain = build(tmp_path / "plain", page, [("cached_input", "known", 5.0)], names=(BETA,))
    assert result(reread(plain, page), "cached_input").status is Status.NEEDS_REVIEW


@pytest.mark.parametrize("label", [None, "Cache write", "Cache write input", "Cache miss"])
def test_cached_input_with_no_cache_row_reads_nothing(tmp_path, label: str | None) -> None:
    page = with_cache(label)
    known = build(tmp_path / "known", page, [("cached_input", "known", 5.0)], names=(BETA,))
    gone = result(reread(known, page), "cached_input")
    assert gone.status is Status.UNREADABLE and gone in reread(known, page).alerts
    undisclosed = build(tmp_path / "nd", page, [("cached_input", "not_disclosed", None)],
                        names=(BETA,))
    report = reread(undisclosed, page)
    assert result(report, "cached_input").status is NEUTRAL


def test_a_cached_column_on_the_input_row_still_prices_cached_input(tmp_path) -> None:
    page = ("<html><body><table><tr><th>Model</th><th>Type</th><th>Price (/1M tokens)</th>"
            "<th>Cached price (/1M tokens)</th></tr>"
            f"<tr><td>{BETA}</td><td>Input</td><td>$5.00</td><td>$0.50</td></tr>"
            "<tr><td></td><td>Output</td><td>$25.00</td><td>N/A</td></tr></table></body></html>")
    estate = build(tmp_path, page, [("cached_input", "known", 0.5)], names=(BETA,))
    assert result(reread(estate, page), "cached_input").status is Status.UNCHANGED
