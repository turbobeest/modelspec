"""The responsive /pricing/ page is generated from the billing contract."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from pipeline import pricing
from pipeline.export import Build

REPO_ROOT = Path(__file__).resolve().parent.parent
TIERS_PATH = REPO_ROOT / "api/worker/tiers.json"


def _build() -> Build:
    return Build(commit="0" * 40, built_at="2026-09-17T00:00:00Z",
                 as_of=date(2026, 9, 17))


def _page(tiers: dict | None = None) -> str:
    return pricing.page(tiers or json.loads(TIERS_PATH.read_text()), build=_build())


def _payload(page: str) -> dict:
    match = re.search(r'<script id="pricing-data" type="application/json">(.*?)</script>', page)
    assert match
    return json.loads(match.group(1))


def test_pricing_page_is_built_with_assets_and_indexing_metadata(tmp_path: Path) -> None:
    result = pricing.write(tmp_path, REPO_ROOT, _build())
    page = tmp_path / "pricing" / "index.html"
    assert page.is_file()
    assert (tmp_path / "pricing-assets" / "pricing.css").is_file()
    assert (tmp_path / "pricing-assets" / "pricing.js").is_file()
    assert result == {"path": "/pricing/", "sitemap_paths": ["/pricing/"]}
    html = page.read_text()
    assert '<link rel="canonical" href="https://modelspec.dev/pricing/">' in html
    assert '<meta name="description"' in html
    assert pricing.TITLE in html


def test_all_prices_credits_weights_and_x402_rate_come_from_tiers_json() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    html = _page(tiers)
    data = _payload(html)
    prices = tiers["billing"]["prices"]
    assert data["plans"] == [
        {"name": row["name"], "credits": row["credits"], "usd": row["usd"]}
        for row in prices.values() if row["kind"] == "plan"]
    assert data["packs"] == [
        {"credits": row["credits"], "usd": row["usd"]}
        for row in prices.values() if row["kind"] == "pack"]
    assert data["weights"] == {
        "decide": tiers["credits"]["weights"]["decide.summary"],
        "decideFull": tiers["credits"]["weights"]["decide.full"],
        "rank": tiers["credits"]["weights"]["rank"],
        "check": tiers["credits"]["weights"]["policy-check"],
    }
    packs = [row for row in prices.values() if row["kind"] == "pack"]
    smallest = min(packs, key=lambda row: row["credits"])
    assert data["perCall"] == smallest["usd"] / smallest["credits"]
    for row in prices.values():
        assert f"{row['credits']:,}" in html
        assert f"${row['usd']}" in html


def test_checkout_forms_keep_the_worker_contract() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    html = _page(tiers)
    forms = re.findall(r'(<form method="post" action="([^"]+)">(.*?)</form>)', html)
    expected = {pid: row for pid, row in tiers["billing"]["prices"].items()
                if not row.get("placeholder")}
    assert len(forms) == len(expected)
    posted = {}
    for _, action, inner in forms:
        assert action == pricing.CHECKOUT_URL
        price_id = re.search(r'name="price_id" value="([^"]+)"', inner)
        button = re.search(r'<button type="submit">([^<]+)</button>', inner)
        assert price_id and button
        posted[price_id.group(1)] = button.group(1)
    assert posted == {pid: "Subscribe" if row["kind"] == "plan" else "Buy"
                      for pid, row in expected.items()}


def test_price_changes_need_no_page_code_change() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    price_id = next(pid for pid, row in tiers["billing"]["prices"].items()
                    if row["kind"] == "plan")
    tiers["billing"]["prices"][price_id] |= {"credits": 8, "usd": 3}
    html = _page(tiers)
    assert "8 credits" in html
    assert "$3/mo" in html
    assert {"credits": 8, "usd": 3, "name": tiers["billing"]["prices"][price_id]["name"]} in _payload(html)["plans"]


def test_honesty_contracts_match_cli_billing_and_legal_docs() -> None:
    html = _page()
    assert "offline CLI cost nothing" in html
    assert re.search(r"CLI.{0,30}(metered|costs? credits)", html, re.I) is None
    assert "An error, a refusal, or no model fits" in html
    assert "anything that is not a successful answer" in html
    assert "free</strong>" in html
    pledge = "No referral fees, no paid placement, no provider-paid visibility"
    assert pledge in html
    assert pledge in (REPO_ROOT / "docs/legal/neutrality.md").read_text()


def test_endpoints_contact_and_no_third_party_assets() -> None:
    html = _page()
    assert pricing.DECIDE_ENDPOINT in html
    assert pricing.MCP_ENDPOINT in html
    assert "sales@modelspec.dev" in html
    assert "fonts.googleapis" not in html
    assert "fonts.gstatic" not in html
    for match in re.finditer(r'<(?:script|img)\b[^>]*\bsrc=[\'\"](https?://[^\'\"]+)', html, re.I):
        raise AssertionError(f"third-party request: {match.group(1)}")


def test_landing_and_decide_link_pricing() -> None:
    landing = (REPO_ROOT / "pipeline/landing.py").read_text()
    decide = (REPO_ROOT / "web/src/decide/App.tsx").read_text()
    assert landing.count('href="/pricing/"') >= 2
    assert '<a href="/pricing/">Pricing</a>' in decide
