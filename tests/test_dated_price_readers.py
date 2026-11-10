"""Dated prices verify their own model, table, row, and calendar boundary."""

from dataclasses import replace
from datetime import UTC, date, datetime
from html import escape

import pytest
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor, value_hash
from decision.sources import CopyStore, Source
from decision.verify import (
    Claim,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    verify,
)
from scripts import price_reread

URL = "https://ai.google.dev/gemini-api/docs/pricing"
SUBJECT = "google-gemini-api/google/gemini-4-argon/global/standard"
COLLECTOR = VerificationActor(agent="dated-price-collector", model_family="openai", method="read")
ARGON = """<main>
<div class="models-section"><div class="heading-group"><h2 id="gemini-4-argon">Gemini 4 Argon</h2>
<em><a href="/gemini-api/docs/models/gemini-4-argon">gemini-4-argon</a></em></div></div>
<p>Published prices.</p><div><devsite-selector><section><h3>Standard</h3>
<table><tr><th></th><th>Free Tier</th><th>Paid Tier, per 1M tokens in USD</th></tr>
<tr><td>Input price</td><td>Not available</td><td>$2.00 through November 30, 2026.<br>
$4.00 starting December 1, 2026.</td></tr>
</table></section></devsite-selector></div></main>"""
VERTEX = """<table><tr><th>Model</th><th>Type</th><th>Region</th>
<th>Price (/1M tokens) &lt;= 200K input tokens</th>
<th>Price (/1M tokens) &gt; 200K input tokens</th>
<th>Price (/1M tokens) &lt;= 200K cached input tokens</th>
<th>Price (/1M tokens) &gt; 200K cached input tokens</th></tr>
<tr><td>Gemini 3.7 Flash * through December 31, 2026</td>
<td>Input (text, image, video, audio)</td><td>Global</td>
<td>$0.75</td><td>$0.75</td><td>$0.075</td><td>$0.075</td></tr>
<tr><td></td><td>Text output (response and reasoning)</td><td>Global</td>
<td>$3.75</td><td>$3.75</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Gemini 3.7 Flash starting January 1, 2027</td>
<td>Input (text, image, video, audio)</td><td>Global</td>
<td>$1.50</td><td>$1.50</td><td>$0.15</td><td>$0.15</td></tr>
<tr><td></td><td>Text output (response and reasoning)</td><td>Global</td>
<td>$7.50</td><td>$7.50</td><td>N/A</td><td>N/A</td></tr></table>"""


@pytest.fixture(autouse=True)
def reviewed_fixture_context(monkeypatch):
    from decision.dated_prices import GEMINI_OWNERSHIP_TEMPLATES

    # Independent literal for this small fixture. Production admits only the
    # separately reviewed primary-source context, checked by the data replay.
    monkeypatch.setitem(
        GEMINI_OWNERSHIP_TEMPLATES,
        (URL, SUBJECT),
        "42905b0da1bb81cecf23ab46c82c435a55e9bb11ef2ccfeccd5d375f8783ada3",
    )


def setup_claim(
    tmp_path,
    html=ARGON,
    *,
    value=4,
    until=None,
    start="2026-12-01",
    subject=SUBJECT,
    names=("Gemini 4 Argon",),
    facet="offering.price.input",
    url=URL,
):
    store = CopyStore(tmp_path / "copies")
    ref = store.put(html.encode(), source_url="https://fixture.example/")
    source = Source.model_validate(
        {
            "id": "pricing",
            "url": url,
            "normaliser": "html-default",
            "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
        }
    )
    claim = Claim(
        target=TargetRef(kind="fact", id=subject + "#" + facet + "@scheduled"),
        subject=subject,
        names=names,
        field=facet,
        value=value,
        collector=COLLECTOR,
        unit="usd_per_1m_tokens",
        sources=(SourceRef(source_id="pricing", snapshot_ref=ref, cited_regions=["page"]),),
        conditions={"effective_from": start, "effective_until": until},
    )
    return claim, StoredRegions(store, {"pricing": source})


@pytest.mark.parametrize(
    ("value", "start", "until"), [(2, None, "2026-11-30"), (4, "2026-12-01", None)]
)
def test_dated_argon_rows_verify_and_bind_the_dates(tmp_path, value, start, until):
    claim, regions = setup_claim(tmp_path, value=value, start=start, until=until)
    result = verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17))
    assert result.outcome == "verified", result
    assert result.verification.target.value_hash == value_hash(
        {"value": value, "effective_from": start, "effective_until": until}
    )


@pytest.mark.parametrize(
    "change",
    [
        "missing_date",
        "wrong_date",
        "sibling",
        "wrong_tier",
        "duplicate",
        "wrong_row",
        "foreign_table",
    ],
)
def test_dated_argon_never_borrows_an_undated_or_foreign_price(tmp_path, change):
    html = ARGON
    if change == "missing_date":
        html = html.replace(" starting December 1, 2026.", "")
    elif change == "wrong_date":
        html = html.replace("starting December 1", "starting December 2")
    elif change == "sibling":
        html = html.replace("Gemini 4 Argon", "Gemini 4 Argon Pro")
    elif change == "wrong_tier":
        html = html.replace("Standard", "Batch")
    elif change == "duplicate":
        html = html.replace(
            "</table>", html[html.index("<tr><td>") : html.index("</table>")] + "</table>"
        )
    elif change == "wrong_row":
        html = html.replace("Input price", "Output price (including thinking tokens)")
    else:
        html = html.replace(
            "</devsite-selector>",
            "</devsite-selector><table><tr><td>Gemini 4 Argon</td>"
            "<td>$4.00 starting December 1, 2026.</td></tr></table>",
        )
        html = html.replace(
            "$4.00 starting December 1, 2026.", "$9.00 starting December 1, 2026.", 1
        )
    claim, regions = setup_claim(tmp_path, html)
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


@pytest.mark.parametrize("change", ["second_selector", "nested_model_heading", "nested_table"])
def test_argon_rejects_conflicting_or_nested_table_ownership(tmp_path, change):
    table = ARGON[ARGON.index("<table>") : ARGON.index("</table>") + len("</table>")]
    if change == "second_selector":
        html = ARGON.replace(
            "</main>",
            "<div><devsite-selector><section><h3>Standard</h3>"
            + table.replace("$4.00", "$9.00")
            + "</section></devsite-selector></div></main>",
        )
    elif change == "nested_model_heading":
        html = ARGON.replace(
            "<div><devsite-selector>", "<div><h3>Gemini 4 Argon Pro</h3><devsite-selector>"
        )
    else:
        start = table.index("<tr><td>")
        row = table[start : table.index("</table>")]
        html = ARGON.replace(
            row, "<tr><td><h3>Gemini 4 Argon Pro</h3><table>" + row + "</table></td></tr>"
        )
    claim, regions = setup_claim(tmp_path, html)
    result = verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17))
    assert result.outcome != "verified"


def test_quoted_table_text_does_not_cite_the_actual_table(tmp_path):
    from decision.normalise import NORMALISERS, _nodes_text, normalise_document

    document = normalise_document(ARGON.encode(), NORMALISERS["html-default"])
    table = next(node for node in document.root.elements() if node.tag == "table")
    quoted = "".join(
        "<p>" + escape(line) + "</p>" for line in _nodes_text([table], document.rules).splitlines()
    )
    html = ARGON.replace("<main>", '<main><div id="quoted-table">' + quoted + "</div>")
    claim, regions = setup_claim(tmp_path, html)
    source = regions.sources["pricing"].model_dump(mode="json")
    source["cited_regions"] = [{"id": "page", "locator": {"kind": "css", "value": "#quoted-table"}}]
    regions = StoredRegions(regions.store, {"pricing": Source.model_validate(source)})
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


def test_foreign_paragraph_caption_cannot_assign_argons_sibling_table(tmp_path):
    html = ARGON.replace(
        "<div><devsite-selector>", "<p>Caption: Gemini 4 Argon Pro</p><div><devsite-selector>"
    )
    claim, regions = setup_claim(tmp_path, html)
    result = verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17))
    assert result.outcome != "verified"


@pytest.mark.parametrize(
    "caption",
    [
        '<aside class="note">The prices belong to Sibling Beta.</aside>',
        '<p class="navigation">The prices belong to Sibling Beta.</p>',
        "<p hidden>The prices belong to Sibling Beta.</p>",
    ],
)
def test_ownership_hash_keeps_elements_the_text_normalizer_drops(tmp_path, caption):
    html = ARGON.replace("<div><devsite-selector>", caption + "<div><devsite-selector>")
    claim, regions = setup_claim(tmp_path, html)
    result = verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17))
    assert result.outcome != "verified"


@pytest.mark.parametrize(
    "attribute",
    [
        'href="/gemini-api/docs/models/gemini-4-argon"',
        'id="gemini-4-argon"',
        'class="models-section"',
    ],
)
def test_duplicate_attributes_cannot_hide_foreign_ownership(tmp_path, attribute):
    name = attribute.split("=", 1)[0]
    html = ARGON.replace(attribute, f'{name}="sibling-beta" ' + attribute, 1)
    claim, regions = setup_claim(tmp_path, html)
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


@pytest.mark.parametrize("marker", ['<div class="models-section">', "<main>"])
def test_ownership_caption_before_the_model_section_is_bound(tmp_path, marker):
    html = ARGON.replace(marker, "<p>These tables belong to Sibling Beta.</p>" + marker, 1)
    claim, regions = setup_claim(tmp_path, html)
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


@pytest.mark.parametrize(
    "change",
    [
        "prose",
        "caption",
        "link",
        "attribute",
        "header",
        "subject",
        "parent",
    ],
)
def test_gemini_requires_its_reviewed_complete_ownership_template(tmp_path, change):
    html = ARGON
    subject = SUBJECT
    if change == "prose":
        html = html.replace("Published prices.", "Published prices for a different model.")
    elif change == "caption":
        html = html.replace("<table>", "<table><caption>Gemini 4 Argon Pro</caption>")
    elif change == "link":
        html = html.replace(
            'href="/gemini-api/docs/models/gemini-4-argon"',
            'href="/gemini-api/docs/models/gemini-4-argon-pro"',
        )
    elif change == "attribute":
        html = html.replace(
            '<div class="models-section">', '<div class="models-section" data-model="other">'
        )
    elif change == "header":
        html = html.replace("Free Tier", "Paid Tier")
    elif change == "parent":
        html = html.replace("<main>", '<main data-model="other">')
    else:
        subject = SUBJECT.replace("/gemini-4-argon/", "/gemini-4-argon-pro/")
    claim, regions = setup_claim(tmp_path, html, subject=subject)
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


@pytest.mark.parametrize(
    ("facet", "value"), [("input", 1.5), ("output", 7.5), ("cached_input", 0.15)]
)
def test_vertex_exact_model_date_region_and_continuation_row(tmp_path, facet, value):
    claim, regions = setup_claim(
        tmp_path,
        VERTEX,
        value=value,
        start="2027-01-01",
        subject="google-vertex-ai/google/gemini-3-7-flash/global/standard",
        names=("Gemini 3.7 Flash",),
        facet="offering.price." + facet,
        url="https://cloud.google.com/vertex-ai/generative-ai/pricing",
    )
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        == "verified"
    )
    wrong = replace(claim, conditions={"effective_from": "2027-01-02", "effective_until": None})
    assert (
        verify(wrong, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


@pytest.mark.parametrize(
    ("model", "names"),
    [
        ("google/gemini-3-8-flash", ("Gemini 3.7 Flash",)),
        ("other-lab/not-a-gemini", ("Gemini 3.7 Flash",)),
        ("google/gemini-3-8-flash", ("Gemini 3.8 Flash", "Gemini 3.7 Flash")),
    ],
)
def test_vertex_canonical_model_cannot_borrow_another_catalogue_name(tmp_path, model, names):
    claim, regions = setup_claim(
        tmp_path, VERTEX, value=1.5, start="2027-01-01",
        subject=f"google-vertex-ai/{model}/global/standard", names=names,
        url="https://cloud.google.com/vertex-ai/generative-ai/pricing",
    )
    queue = Queue(tmp_path / "verification")
    queue.file(Claim.from_dict(claim.to_dict()), at=datetime(2026, 10, 17, tzinfo=UTC))
    claim = next(iter(queue.filed().values()))
    assert (
        verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17)).outcome
        != "verified"
    )


def test_weekly_reread_checks_future_row_and_proposes_a_change_without_writing(tmp_path):
    claim, regions = setup_claim(tmp_path)
    root = tmp_path / "repo"
    (root / "registry").mkdir(parents=True)
    source = regions.sources["pricing"]
    (root / "registry/sources.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "sources": [source.model_dump(mode="json")]})
    )
    path = root / "offerings/google-gemini-api/google/gemini-4-argon.yaml"
    path.parent.mkdir(parents=True)
    fact = {
        "id": claim.target.id,
        "subject": {"kind": "offering", "id": SUBJECT},
        "facet": claim.field,
        "state": "known",
        "value": 4,
        "effective_from": "2026-12-01",
        "sources": [s.model_dump() for s in claim.sources],
    }
    path.write_text(
        yaml.safe_dump(
            [
                {
                    "model": "google/gemini-4-argon",
                    "provider": "google-gemini-api",
                    "region": "global",
                    "tier": "standard",
                    "facts": [fact],
                }
            ],
            sort_keys=False,
        )
    )
    queue, log = Queue(root / "verification"), VerificationLog(root / "verification")
    queue.file(claim, at=datetime(2026, 10, 17, tzinfo=UTC))
    result = verify(claim, regions, deterministic_extractors(), today=date(2026, 10, 17))
    assert result.outcome == "verified"
    log.append(result.verification)

    class Fetcher:
        def __init__(self, html):
            self.html = html

        def fetch(self, url, **kwargs):
            from decision.sources import FetchResult

            return FetchResult(
                "ok", 200, body=self.html.encode(), content_type="text/html", charset="utf-8"
            )

    def reread(html, write=False):
        return price_reread.run(
            root=root,
            fetcher=Fetcher(html),
            store=regions.store,
            today=date(2026, 10, 18),
            write=write,
        )

    assert reread(ARGON).facts[0].status == price_reread.Status.UNCHANGED
    missing = ARGON.replace(" starting December 1, 2026.", "")
    assert reread(missing).facts[0].status != price_reread.Status.UNCHANGED
    before = path.read_text()
    report = reread(ARGON.replace("$4.00", "$5.00"), write=True)
    # MODEL-423: a changed price is proposed for review, never written.
    assert report.facts[0].status == price_reread.Status.NEEDS_REVIEW
    assert report.facts[0].new_value == 5
    assert path.read_text() == before
    updated = yaml.safe_load(path.read_text())[0]["facts"][0]
    assert (updated["value"], updated["effective_from"]) == (4, "2026-12-01")
    updated["effective_from"] = "2026-12-02"
    rows = yaml.safe_load(path.read_text())
    rows[0]["facts"][0] = updated
    path.write_text(yaml.safe_dump(rows, sort_keys=False))
    altered = reread(ARGON.replace("$4.00", "$5.00")).facts[0]
    assert altered.status == price_reread.Status.NOT_REREAD
    assert altered.reason == "the fact differs from its filed claim"


_VERTEX_SUBJECT = "google-vertex-ai/google/gemini-3-7-flash/global/standard"
_VERTEX_URL = "https://cloud.google.com/vertex-ai/generative-ai/pricing"
_VERTEX_HTML_HEADERS = [
    "Model",
    "Type",
    "Region",
    "Price (/1M tokens) &lt;= 200K input tokens",
    "Price (/1M tokens) &gt; 200K input tokens",
    "Price (/1M tokens) &lt;= 200K cached input tokens",
    "Price (/1M tokens) &gt; 200K cached input tokens",
]


def _vertex_price_row(region="Global"):
    return [
        "Gemini 3.7 Flash through December 31, 2026",
        "Input (text, image, video, audio)",
        region,
        "$0.75",
        "$0.99",
        "$0.075",
        "$0.099",
    ]


def _vertex_table(rows):
    head = "".join(f"<th>{cell}</th>" for cell in _VERTEX_HTML_HEADERS)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><tr>{head}</tr>{body}</table>"


def _read_vertex(html, facet):
    from decision.dated_prices import read_dated_prices
    from decision.normalise import NORMALISERS, Locator, normalise_document

    body = html.encode()
    document = normalise_document(body, NORMALISERS["html-default"])
    return read_dated_prices(
        document,
        Locator(kind="page", value=""),
        names=("Gemini 3.7 Flash",),
        subject=_VERTEX_SUBJECT,
        facet=facet,
        url=_VERTEX_URL,
        body=body,
    )


def _pin_price_clock(monkeypatch):
    """Keep 2026-11-09 as today so a 2026-12-31 synthetic price stays current."""
    import decision.snapshot as snapshot

    class Pinned(datetime):
        @classmethod
        def now(cls, tz=None):
            instant = cls(2026, 11, 9, 12, tzinfo=UTC)
            if tz is not None:
                return instant.astimezone(tz)
            return instant.replace(tzinfo=None)

    monkeypatch.setattr(snapshot, "datetime", Pinned)


def _decide_dated_readings(readings, kind, monkeypatch):
    from decision.contract import parse_spec
    from decision.engine import decide
    from decision.registry import facet
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
    from tests.snapshot_records import SOURCES, fact, model, offering, verification

    _pin_price_clock(monkeypatch)
    mid = "google/gemini-3-7-flash"
    provider = "google-vertex-ai"
    offering_id = f"{provider}/{mid}/global/standard"
    parsed_facet = "offering.price." + kind
    other_facet = "offering.price.input" if kind == "output" else "offering.price.output"
    facts = [fact("offering", offering_id, other_facet, 1.0, source="src-pricing")]
    for number, reading in enumerate(readings):
        value = float(reading.value)
        row = fact("offering", offering_id, parsed_facet, value, source="src-pricing")
        row["id"] += f"@synthetic-{number}"
        row["effective_from"] = reading.effective_from
        row["effective_until"] = reading.effective_until
        row["verification"] = verification(
            "fact",
            row["id"],
            value={
                "value": value,
                "effective_from": reading.effective_from,
                "effective_until": reading.effective_until,
            },
        )
        facts.append(row)
    other = "lab/comparator"
    other_id = f"{provider}/{other}/global/standard"
    fixed = [
        fact("offering", other_id, "offering.price." + side, 10.0, source="src-pricing")
        for side in ("input", "output")
    ]
    index = load_built_snapshot(
        build_snapshot(
            SnapshotInputs(
                models=[model(mid), model(other)],
                offerings=[
                    offering(mid, provider, facts=facts),
                    offering(other, provider, facts=fixed),
                ],
                sources=SOURCES,
            ),
            gate=False,
            as_of=date(2026, 11, 9),
        ),
        include_archive=True,
        source="synthetic parsed-price ingestion",
    )
    spec = parse_spec(
        {
            "spec_version": 1,
            "where": ["offering.provider = google-vertex-ai"],
            "optimize": {"min": "offering.cost_per_task"},
            "task_tokens": {"input": 1000, "output": 1000},
            "explain": "full",
        },
        facets=facet,
    )
    return index.fact(offering_id, parsed_facet), decide(spec, index, facets=facet)


def _assert_only_comparator_priced(parsed, decision):
    assert parsed.state == "unknown"
    assert parsed.value is None
    assert decision.status == "partial"
    assert len(decision.results) == 1
    assert decision.results[0].model == "lab/comparator"
    assert decision.results[0].rank == 1
    assert decision.results[0].cost_per_task == pytest.approx(0.02)
    assert [item.model for item in decision.may_qualify] == ["google/gemini-3-7-flash"]
    assert decision.may_qualify[0].unknown == ["offering.cost_per_task"]


def test_vertex_rejects_non_global_price_rows_for_global_offering(monkeypatch):
    """A Europe row on a global Vertex offering yields no dated price."""
    readings = _read_vertex(_vertex_table([_vertex_price_row("Europe")]), "offering.price.input")
    assert readings == []
    parsed, decision = _decide_dated_readings(readings, "input", monkeypatch)
    _assert_only_comparator_priced(parsed, decision)


def test_vertex_clears_owner_after_malformed_intervening_row(monkeypatch):
    """A malformed row clears the model and date before a blank-owner output row."""
    rows = [
        _vertex_price_row(),
        ["Foreign ownership boundary"],
        ["", "Text output (response and reasoning)", "Global", "$3.75", "$4.99", "N/A", "N/A"],
    ]
    readings = _read_vertex(_vertex_table(rows), "offering.price.output")
    assert readings == []
    parsed, decision = _decide_dated_readings(readings, "output", monkeypatch)
    _assert_only_comparator_priced(parsed, decision)


def test_vertex_rejects_multiple_eligible_pricing_tables(monkeypatch):
    """Two eligible Vertex pricing tables yield no dated price."""
    table = _vertex_table([_vertex_price_row()])
    readings = _read_vertex(table + table, "offering.price.input")
    assert readings == []
    parsed, decision = _decide_dated_readings(readings, "input", monkeypatch)
    _assert_only_comparator_priced(parsed, decision)


def test_vertex_reads_short_context_input_when_columns_differ(monkeypatch):
    """The short-context input price is 0.75 when the long-context column is 0.99."""
    row = _vertex_price_row()
    readings = _read_vertex(_vertex_table([row]), "offering.price.input")
    assert [reading.value for reading in readings] == ["0.75"]
    assert readings[0].effective_until == "2026-12-31"
    assert readings[0].effective_from is None
    assert readings[0].subject == "Gemini 3.7 Flash"
    parsed, decision = _decide_dated_readings(readings, "input", monkeypatch)
    assert parsed.state == "known"
    assert parsed.value == pytest.approx(0.75)
    assert decision.status == "answered"
    assert [(item.model, item.rank) for item in decision.results] == [
        ("google/gemini-3-7-flash", 1),
        ("lab/comparator", 2),
    ]
    # 1000 input tokens at 0.75 and 1000 output tokens at 1.0, per 1M tokens.
    assert decision.results[0].cost_per_task == pytest.approx(0.00175)
    assert decision.results[1].cost_per_task == pytest.approx(0.02)
    assert decision.may_qualify == []


def test_vertex_reads_short_context_cached_input_when_columns_differ():
    """The short-context cached input is 0.075 when the long-context column is 0.099."""
    row = _vertex_price_row()
    assert row[5] == "$0.075"
    assert row[6] == "$0.099"
    readings = _read_vertex(_vertex_table([row]), "offering.price.cached_input")
    assert [reading.value for reading in readings] == ["0.075"]
    assert readings[0].subject == "Gemini 3.7 Flash"
    assert readings[0].effective_until == "2026-12-31"
