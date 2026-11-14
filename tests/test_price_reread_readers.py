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


def test_a_table_with_no_batch_column_and_the_models_row_confirms_not_disclosed(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("input", "known", 4.0),
                                        ("batch_input", "not_disclosed", None),
                                        ("batch_output", "not_disclosed", None)])
    root, _ = estate
    report = reread(estate, NO_BATCH, write=True)

    for kind in ("batch_input", "batch_output"):
        confirmed = result(report, kind)
        assert confirmed.status is Status.UNCHANGED
        assert confirmed.reason == "still not disclosed"
        assert confirmed.verification is not None
        assert confirmed in report.facts and confirmed not in report.alerts
    assert report.counts()["unchanged"] == 3 and report.counts()["unreadable"] == 0
    assert report.alerts == []
    latest = VerificationLog(root / "verification").latest()
    undisclosed = latest[("fact", f"{SUBJECT}#offering.price.batch_input")]
    assert undisclosed.date == TODAY and undisclosed.outcome == "verified"
    assert undisclosed.target.value_hash == value_hash(None)


def test_a_batch_value_now_stated_on_the_row_is_a_disclosed_alert_and_writes_nothing(
        tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    root, _ = estate
    files = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}

    report = reread(estate, WITH_BATCH_VALUE, write=True)

    stated = result(report, "batch_input")
    assert stated.status is Status.NEEDS_REVIEW and stated in report.alerts
    assert stated.reason.startswith("disclosed: page now states a value")
    assert stated.new_value in (None, 2, 2.0) and stated.old_value is None
    assert report.changes == []
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == files


def test_an_explicit_not_available_cell_is_not_confirmed_for_not_disclosed(tmp_path) -> None:
    """The page states the price is unavailable; that is ``not_offered``, not undisclosed."""
    estate = build(tmp_path, WITH_BATCH_NA, [("batch_input", "not_disclosed", None)])
    report = reread(estate, WITH_BATCH_NA)
    stated = result(report, "batch_input")
    assert stated.status is Status.UNREADABLE and stated in report.alerts


def test_not_offered_with_an_explicit_not_available_cell_keeps_todays_outcome(tmp_path) -> None:
    """A ``not_offered`` fact is re-read like any filed fact. Only ``not_disclosed`` gained a
    confirmation, so the same page still reads unreadable for it."""
    estate = build(tmp_path, WITH_BATCH_NA, [("batch_input", "not_offered", None)])
    report = reread(estate, WITH_BATCH_NA)
    assert result(report, "batch_input").status is Status.UNREADABLE


def test_not_offered_without_the_column_is_not_confirmed(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_offered", None)])
    report = reread(estate, NO_BATCH)
    assert result(report, "batch_input").status is Status.UNREADABLE


def test_an_unknown_fact_is_not_re_read(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("input", "known", 4.0)])
    root, _ = estate
    text = (root / OFFERING_FILE).read_text()
    (root / OFFERING_FILE).write_text(text.replace("state: known", "state: unknown")
                                      .replace("value: 4.0", "value: null"))
    assert price_reread.tracked_facts(root) == []


@pytest.mark.parametrize("page", [OTHER_MODEL_ONLY, LOOSER_NAME_ONLY],
                         ids=["row-missing", "row-of-a-looser-name"])
def test_a_missing_model_row_never_confirms(tmp_path, page: str) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    report = reread(estate, page)
    assert result(report, "batch_input").status is Status.UNREADABLE


@pytest.mark.parametrize("page", [NO_TABLE, ONE_LINE_TABLE, ROW_WITHOUT_PRICES,
                                  SECOND_TABLE_HAS_BATCH],
                         ids=["no-table", "no-header-row", "no-other-price-on-the-row",
                              "model-also-in-a-table-with-a-batch-column"])
def test_a_table_that_did_not_read_never_confirms(tmp_path, page: str) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    report = reread(estate, page)
    unread = result(report, "batch_input")
    assert unread.status is Status.UNREADABLE and unread in report.alerts


def test_a_page_that_did_not_fetch_is_unreachable_not_confirmed(tmp_path) -> None:
    estate = build(tmp_path, NO_BATCH, [("batch_input", "not_disclosed", None)])
    report = reread(estate, None)
    assert result(report, "batch_input").status is Status.UNREACHABLE


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


def test_the_vertex_reader_matches_the_row_type_exactly() -> None:
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
