"""New-card prices are independently read before entering a draft offering."""

import json
from datetime import UTC, date, datetime

import yaml

from decision.sources import CopyStore, FetchResult

TODAY = date(2026, 11, 4)
MODEL = "google/fixture-model"
URL = "https://ai.google.dev/gemini-api/docs/pricing"
PRICES = (b"<table><tr><th>Model</th><th>Input price per 1M tokens</th>"
          b"<th>Output price per 1M tokens</th></tr>"
          b"<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>")


def catalogue(tmp_path, *, model=MODEL, url=URL):
    root = tmp_path / "data"
    path = root / "models" / f"{model}.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\n" + yaml.safe_dump({
        "model_id": model, "display_name": "Fixture Model", "version": "fixture-model",
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
