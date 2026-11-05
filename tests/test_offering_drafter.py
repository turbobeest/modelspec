"""New-card prices are independently read before entering a draft offering."""

import json
from datetime import UTC, date, datetime

import pytest
import yaml

from decision.sources import CopyStore, FetchResult

TODAY = date(2026, 11, 4)
MODEL = "google/fixture-model"
URL = "https://ai.google.dev/gemini-api/docs/pricing"
PRICES = (b"<table><tr><th>Model</th><th>Input price per 1M tokens</th>"
          b"<th>Output price per 1M tokens</th></tr>"
          b"<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>")


def catalogue(tmp_path, *, model=MODEL, url=URL, version="fixture-model"):
    root = tmp_path / "data"
    path = root / "models" / f"{model}.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\n" + yaml.safe_dump({
        "model_id": model, "display_name": "Fixture Model", "version": version,
        "model_type": "llm", "status": "active", "sources": {"provider_docs_url": url},
        "cost": {"input": 999, "output": 999},
    }) + "---\nIncomplete new card.\n")
    (root / "registry").mkdir()
    (root / "registry/source-terms.json").write_text(json.dumps({
        "ai.google.dev": "restricts", "docs.x.ai": "forbids",
    }))
    return root


class Pages:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def fetch(self, url):
        self.calls.append(url)
        body = self.pages.get(url)
        return FetchResult("ok" if body else "unreachable", body=body or b"",
                           status=200 if body else 404, resolved_urls=(url,),
                           retrieved_at=datetime(2026, 11, 4, tzinfo=UTC))


def draft(root, tmp_path, fetcher=None, model=MODEL):
    from scripts.offering_drafter import draft_offering

    return draft_offering(root=root, model_id=model, fetcher=fetcher or Pages({URL: PRICES}),
                          store=CopyStore(tmp_path / "copies"), today=TODAY)


def test_offering_writes_before_model_admission_with_independent_receipts(tmp_path):
    from decision.model import load_offerings
    from decision.verify import Queue, VerificationLog

    root = catalogue(tmp_path)
    card = root / "models" / f"{MODEL}.md"
    before = card.read_bytes()
    packet = draft(root, tmp_path)
    packet.write(root)
    path = root / "offerings/google-gemini-api/google/fixture-model.yaml"
    offering, = load_offerings(path)
    assert {f.facet: f.value for f in offering.facts} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert card.read_bytes() == before
    assert not (root / "premier").exists()
    receipts = VerificationLog(root / "verification").latest()
    assert len(receipts) == 2
    assert all(v.independent and v.outcome == "verified" for v in receipts.values())
    assert len(Queue(root / "verification").filed()) == 2
    written = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    packet.write(root)
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == written


def test_unverified_price_stays_absent_with_a_reason(tmp_path):
    root = catalogue(tmp_path)
    packet = draft(root, tmp_path, Pages({}))
    packet.write(root)
    assert not list(root.glob("offerings/**/*.yaml"))
    assert {g.facet for g in packet.gaps} >= {"offering.price.input", "offering.price.output"}
    assert all(g.reason for g in packet.gaps)
    assert "999" not in json.dumps(packet.to_dict())


def test_existing_offering_is_never_rewritten(tmp_path):
    root = catalogue(tmp_path)
    path = root / "offerings/google-gemini-api/google/fixture-model.yaml"
    path.parent.mkdir(parents=True)
    path.write_text("# Existing human-reviewed record.\n[]\n")
    before = path.read_bytes()
    packet = draft(root, tmp_path)
    packet.write(root)
    assert path.read_bytes() == before
    assert any("existing" in g.reason for g in packet.gaps)


def test_models_dev_costs_are_never_a_price_source(tmp_path):
    root = catalogue(tmp_path, url="https://models.dev/google/fixture-model")
    fetcher = Pages({"https://models.dev/google/fixture-model": PRICES})
    packet = draft(root, tmp_path, fetcher)
    assert "https://models.dev/google/fixture-model" not in fetcher.calls
    assert packet.offering is None


def test_cite_only_keeps_hash_and_url_without_price_or_page_bytes(tmp_path):
    url = "https://docs.x.ai/docs/models"
    root = catalogue(tmp_path, model="xai/fixture-model", url=url)
    packet = draft(root, tmp_path, Pages({url: PRICES}), model="xai/fixture-model")
    packet.write(root)
    assert packet.offering is None
    assert any("cite-only" in g.reason for g in packet.gaps)
    assert any(s.get("snapshot_ref", "").startswith("sha256:") for s in packet.sources)
    assert all(s["url"] == url for s in packet.sources)
    assert all(PRICES not in p.read_bytes() for p in tmp_path.rglob("*") if p.is_file())


def test_unreadable_http_uses_rendered_read_before_paid_fallback(tmp_path):
    root = catalogue(tmp_path)

    class Rendered(Pages):
        def render(self, url):
            self.calls.append("render:" + url)
            return Pages({URL: PRICES}).fetch(url)

        def fallback(self, url):
            raise AssertionError("verified rendered price must not spend credits")

    fetcher = Rendered({URL: b"<html>JavaScript shell</html>"})
    packet = draft(root, tmp_path, fetcher)
    assert {f["facet"]: f["value"] for f in packet.offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert fetcher.calls == [URL, "render:" + URL]


def test_existing_citation_receipt_is_not_rewritten(tmp_path):
    from decision.sources import fingerprint_bytes

    url = "https://docs.x.ai/docs/models"
    root = catalogue(tmp_path, model="xai/fixture-model", url=url)
    store = CopyStore(tmp_path / "copies")
    ref = fingerprint_bytes(PRICES)
    store.record_citation(ref, source_url=url, retrieved_at=datetime(2026, 1, 1, tzinfo=UTC))
    path = store.path(ref).with_suffix(".citation.json")
    before = path.read_bytes()
    draft(root, tmp_path, Pages({url: PRICES}), model="xai/fixture-model")
    assert path.read_bytes() == before


def test_corrupt_existing_copy_is_not_replaced(tmp_path):
    from decision.sources import fingerprint_bytes

    root = catalogue(tmp_path)
    path = CopyStore(tmp_path / "copies").path(fingerprint_bytes(PRICES))
    path.parent.mkdir(parents=True)
    path.write_bytes(b"existing corrupt record")
    packet = draft(root, tmp_path)
    assert path.read_bytes() == b"existing corrupt record"
    assert packet.offering is None
    assert any("existing" in g.reason for g in packet.gaps)


def test_disagreeing_first_party_prices_do_not_enter_offering(tmp_path):
    model_url = "https://ai.google.dev/gemini-api/docs/models/fixture-model"
    root = catalogue(tmp_path, url=model_url)
    packet = draft(root, tmp_path, Pages({URL: PRICES, model_url: PRICES.replace(b"$2", b"$3")}))
    assert {f["facet"]: f["value"] for f in packet.offering["facts"]} == {
        "offering.price.output": 8,
    }
    assert any(g.facet == "offering.price.input" and "conflicting" in g.reason
               for g in packet.gaps)


@pytest.mark.parametrize("row_name", ["Fixture Model Ultra", "Mini Fixture Model"])
@pytest.mark.parametrize("grouped", [False, True], ids=["flat", "grouped"])
def test_substring_model_row_leaves_prices_unwritten(tmp_path, row_name, grouped):
    root = catalogue(tmp_path)
    if grouped:
        body = (b"<table><tr><th>Model</th><th>Base tokens</th></tr>"
                b"<tr><th>Name</th><th>Input</th><th>Output</th></tr>"
                b"<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>")
    else:
        body = PRICES
    body = body.replace(b"Fixture Model", row_name.encode()).replace(b"$2", b"$5").replace(b"$8", b"$9")
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering is None
    assert not list(root.glob("offerings/**/*.yaml"))
    assert {g.facet for g in packet.gaps} >= {"offering.price.input", "offering.price.output"}
    assert all(g.reason for g in packet.gaps)


@pytest.mark.parametrize("other_first", [False, True])
def test_price_table_with_both_models_keeps_only_the_exact_row(tmp_path, other_first):
    root = catalogue(tmp_path)
    other = b"<tr><td>Fixture Model Ultra</td><td>$5</td><td>$9</td></tr>"
    body = (PRICES.replace(b"<tr><td>", other + b"<tr><td>", 1) if other_first
            else PRICES.replace(b"</table>", other + b"</table>"))
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    assert {fact["facet"]: fact["value"] for fact in offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }


@pytest.mark.parametrize("row_name", ["FIXTURE MODEL", "fixture-model", "Fixture.Model"])
def test_normalized_exact_model_row_still_writes_verified_prices(tmp_path, row_name):
    from decision.verify import VerificationLog

    root = catalogue(tmp_path)
    packet = draft(root, tmp_path, Pages({URL: PRICES.replace(b"Fixture Model", row_name.encode())}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    assert {fact["facet"]: fact["value"] for fact in offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    receipts = VerificationLog(root / "verification").latest()
    assert len(receipts) == 2
    assert all(record.independent and record.outcome == "verified" for record in receipts.values())


@pytest.mark.parametrize("row_name", ["Fixture Model Ultra", "Mini Fixture Model"])
def test_model_page_fallback_cannot_draft_a_sibling_price(tmp_path, row_name):
    root = catalogue(tmp_path)
    body = ("<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>"
            f"<tr><td>{row_name}</td><td>$5</td><td>$9</td></tr></table>"
            "<p>Prices are listed per million tokens.</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering is None
    assert not list(root.glob("offerings/**/*.yaml"))
    assert {g.facet for g in packet.gaps} >= {"offering.price.input", "offering.price.output"}


@pytest.mark.parametrize("other_first", [False, True])
def test_model_page_fallback_keeps_exact_prices_without_sibling_conflicts(tmp_path, other_first):
    root = catalogue(tmp_path)
    own = "<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr>"
    other = "<tr><td>Fixture Model Ultra</td><td>$5</td><td>$9</td></tr>"
    body = ("<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>"
            + (other + own if other_first else own + other)
            + "</table><p>Prices are listed per million tokens.</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    assert {fact["facet"]: fact["value"] for fact in offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert not any("conflicting" in gap.reason for gap in packet.gaps)


@pytest.mark.parametrize("heading", ["Fixture Model Ultra", "Mini Fixture Model"])
@pytest.mark.parametrize("earlier_exact", [False, True])
def test_model_page_heading_cannot_assign_sibling_prices(tmp_path, heading, earlier_exact):
    root = catalogue(tmp_path)
    prefix = "<h1>Fixture Model</h1>" if earlier_exact else ""
    body = (prefix + f"<h1>{heading}</h1>"
            "<p>Input</p><p>$5</p><p>Output</p><p>$9</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering is None
    assert not list(root.glob("offerings/**/*.yaml"))


@pytest.mark.parametrize("heading, version", [
    ("FIXTURE--Model", "fixture-model"),
    ("Fixture Model Global", "Fixture Model Global"),
])
def test_model_page_exact_heading_or_declared_alias_drafts_prices(tmp_path, heading, version):
    root = catalogue(tmp_path, version=version)
    body = (f"<h1>{heading}</h1>"
            "<p>Input</p><p>$2</p><p>Output</p><p>$8</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    assert {fact["facet"]: fact["value"] for fact in offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }


@pytest.mark.parametrize("name, version, expected_cached", [
    ("Fixture Model Ultra", "fixture-model", None),
    ("FIXTURE--Model", "fixture-model", 0.2),
    ("Fixture Model Global", "Fixture Model Global", 0.2),
])
def test_model_page_cached_prose_requires_exact_name_or_declared_alias(
        tmp_path, name, version, expected_cached):
    root = catalogue(tmp_path, version=version)
    body = ("<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>"
            "<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>"
            f"<p>{name} caching gives a discount ($0.20 USD per million tokens).</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    prices = {fact["facet"]: fact["value"] for fact in offering["facts"]}
    assert prices["offering.price.input"] == 2
    assert prices["offering.price.output"] == 8
    if expected_cached is None:
        assert "offering.price.cached_input" not in prices
        assert any(g.facet == "offering.price.cached_input" for g in packet.gaps)
    else:
        assert prices["offering.price.cached_input"] == expected_cached


@pytest.mark.parametrize("earlier_exact", [False, True])
@pytest.mark.parametrize("heading_tag", ["h2", "p"])
def test_inverse_price_labels_do_not_draft_a_sibling(tmp_path, earlier_exact, heading_tag):
    root = catalogue(tmp_path)
    prefix = "<h1>Fixture Model</h1>" if earlier_exact else ""
    body = (prefix + f"<{heading_tag}>Fixture Model Ultra</{heading_tag}>"
            "<p>$5 input</p><p>$9 output</p>").encode()
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering is None
    assert not list(root.glob("offerings/**/*.yaml"))
    assert {gap.facet for gap in packet.gaps} >= {
        "offering.price.input", "offering.price.output",
    }


def test_inverse_price_labels_keep_exact_model_without_sibling_conflicts(tmp_path):
    root = catalogue(tmp_path)
    body = (b"<h1>Fixture Model</h1><p>$2 input</p><p>$8 output</p>"
            b"<h2>Fixture Model Ultra</h2><p>$5 input</p><p>$9 output</p>")
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering_path is not None
    offering, = yaml.safe_load((root / packet.offering_path).read_text())
    assert {fact["facet"]: fact["value"] for fact in offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert not any("conflicting" in gap.reason for gap in packet.gaps)


def test_priority_section_does_not_draft_standard_prices(tmp_path):
    root = catalogue(tmp_path)
    body = (b"<h1>Fixture Model</h1><h2>Priority</h2>"
            b"<p>Input</p><p>$5</p><p>Output</p><p>$9</p>")
    packet = draft(root, tmp_path, Pages({URL: body}))
    packet.write(root)
    assert packet.offering is None
    assert not list(root.glob("offerings/**/*.yaml"))
