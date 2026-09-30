"""The responsive /pricing/ page is generated from the billing contract."""

from __future__ import annotations

import json
import re
from datetime import date
from html import unescape
from pathlib import Path

from pipeline import pricing, worker_flags
from pipeline.export import Build

REPO_ROOT = Path(__file__).resolve().parent.parent
TIERS_PATH = REPO_ROOT / "api/worker/tiers.json"


def _build() -> Build:
    return Build(commit="0" * 40, built_at="2026-09-17T00:00:00Z",
                 as_of=date(2026, 9, 17))


def _page(tiers: dict | None = None, **flags: bool | str) -> str:
    return pricing.page(tiers or json.loads(TIERS_PATH.read_text()), build=_build(), **flags)


def _payload(page: str) -> dict:
    match = re.search(r'<script id="pricing-data" type="application/json">(.*?)</script>', page)
    assert match
    return json.loads(match.group(1))


def _rendered_text(page: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", page))


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
    assert pricing.FREE_TIER_TITLE in html
    assert '<a href="/method/">Method</a>' in html
    assert 'property="og:image" content="https://modelspec.dev/og-card-pricing.png"' in html
    assert 'name="twitter:image" content="https://modelspec.dev/og-card-pricing.png"' in html


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
    assert data["payPerCall"] is True
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


def test_billing_on_keeps_the_purchase_copy_and_columns() -> None:
    html = _page(billing_live=True)
    assert "Buy credits for your agents" in html
    assert "Pay by card. You get one API key and one balance" in html
    assert html.count('role="columnheader">Purchase</th>') == 2
    assert "Checkout is hosted by Stripe; card details never reach ModelSpec." in html
    assert "Cancel any time." in html
    assert "What will your agents spend?" in html
    assert "Cheapest way to pay" in html


def test_billing_off_presents_a_price_list_without_purchase_language() -> None:
    html = _page(billing_live=False, access_enforced=False, x402_live=False)
    assert "Plans and packs" in html
    assert "What credits cost for paid access." in html
    assert "Purchase" not in html
    assert "What would your agents spend at these prices?" in html
    assert "Cheapest published option" in html
    assert ("The hosted API answers on a free tier today; these are the "
            "credit prices for paid access.") in html
    assert "Hosted API and MCP answers use prepaid credits" not in html
    assert re.search(r"\b(buy|checkout|card|cancel(?:ling)?)\b", _rendered_text(html), re.I) is None


def test_price_changes_need_no_page_code_change() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    price_id = next(pid for pid, row in tiers["billing"]["prices"].items()
                    if row["kind"] == "plan")
    tiers["billing"]["prices"][price_id] |= {"credits": 8, "usd": 3}
    html = _page(tiers)
    assert "8 credits" in html
    assert "$3/mo" in html
    assert {"credits": 8, "usd": 3, "name": tiers["billing"]["prices"][price_id]["name"]} in _payload(html)["plans"]


def test_hero_names_the_cheapest_product_kind_and_matches_the_shown_rates() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    prices = list(tiers["billing"]["prices"].values())
    rates = [row["usd"] / row["credits"] for row in prices]
    cheapest = min(prices, key=lambda row: row["usd"] / row["credits"])
    html = _page(tiers, x402_live=False)
    assert "the Team plan's rate" in html
    assert f"{pricing._rate(min(rates))}–{pricing._rate(max(rates))}" in html
    assert cheapest["kind"] == "plan"

    pack = next(row for row in prices if row["kind"] == "pack")
    pack["usd"] = 1
    pack["credits"] = 100_000
    html = _page(tiers, x402_live=False)
    assert f"the {pack['name']}'s rate" in html
    assert "pack plan's rate" not in html


def test_honesty_contracts_match_cli_billing_and_legal_docs() -> None:
    html = _page()
    assert "The board on this site costs nothing." in html
    assert "offline CLI" not in html
    assert re.search(r"CLI.{0,30}(metered|costs? credits)", html, re.I) is None
    assert "No answer, no charge" not in html
    assert "Only a successful answer draws credits." in html
    assert "An error, a refusal, or no model fits" in html
    assert "anything that is not a successful answer" in html
    assert 'class="free">free</td>' in html
    x402_rule = "Per-call settlement cannot be un-settled if `produce` then returns 5xx."
    assert x402_rule in (REPO_ROOT / "docs/x402.md").read_text()
    assert ("A per-call payment is settled before the answer is produced; if the service "
            "then fails, that payment isn't refunded automatically.") in html
    pledge = "No referral fees, no paid placement, no provider-paid visibility"
    assert pledge in html
    assert pledge in (REPO_ROOT / "docs/legal/neutrality.md").read_text()


def test_price_lists_and_answer_costs_have_table_semantics() -> None:
    html = _page()
    tables = re.findall(r'<table\b[^>]*>(.*?)</table>', html)
    assert len(tables) == 3
    assert [re.search(r'<caption>(.*?)</caption>', table).group(1) for table in tables] == [
        "Monthly plans · allowance resets each invoice",
        "Packs · one-off, last 365 days",
        "Credits drawn from a prepaid balance",
    ]
    for table in tables:
        assert re.search(r'<th scope="col"(?: role="columnheader")?>', table)
        assert re.search(r'<th scope="row"(?: role="rowheader")?>', table)
    for table in tables[:2]:
        assert 'role="rowgroup"' in table
        assert 'role="row"' in table
        assert 'role="cell"' in table
    tiers = json.loads(TIERS_PATH.read_text())
    prices = tiers["billing"]["prices"].values()
    assert len(re.findall(r'<tr class="price-row plan" role="row">', tables[0])) == sum(
        row["kind"] == "plan" for row in prices)
    assert len(re.findall(r'<tr class="price-row pack" role="row">', tables[1])) == sum(
        row["kind"] == "pack" for row in prices)
    assert len(re.findall(r'<tr class="cost-row">', tables[2])) == 5


def test_endpoints_contact_and_no_third_party_assets() -> None:
    html = _page()
    assert pricing.DECIDE_ENDPOINT in html
    assert pricing.MCP_ENDPOINT in html
    assert "sales@modelspec.dev" in html
    assert "fonts.googleapis" not in html
    assert "fonts.gstatic" not in html
    for match in re.finditer(r'<(?:script|img)\b[^>]*\bsrc=[\'\"](https?://[^\'\"]+)', html, re.I):
        raise AssertionError(f"third-party request: {match.group(1)}")


def test_production_switches_generate_what_ships_today(tmp_path: Path) -> None:
    variables = worker_flags.production_vars(REPO_ROOT)
    assert worker_flags.enabled(variables, "BILLING_ENABLED") is False
    assert worker_flags.enabled(variables, "X402_ENABLED") is False
    assert worker_flags.enabled(variables, "X402_MAINNET") is False
    assert worker_flags.enabled(variables, "ACCESS_ENFORCED") is False
    pricing.write(tmp_path, REPO_ROOT, _build())
    html = (tmp_path / "pricing" / "index.html").read_text()
    assert "<form" not in html
    assert "x402" not in html.lower()
    assert "Or let your agents pay as they go" not in html
    assert "Plans and packs" in html
    assert "Purchase" not in html
    assert "answers on a free tier today" in html
    assert re.search(r"\b(buy|checkout|card|cancel(?:ling)?)\b", _rendered_text(html), re.I) is None
    assert _payload(html)["payPerCall"] is False
    assert "perCall" not in _payload(html)
    assert "coming soon" not in html.lower()
    assert "opening soon" not in html.lower()
    assert "People decide free. Agents start free." in html
    assert "People decide free. Agents pay per answer." not in html


def test_billing_and_x402_render_independently() -> None:
    tiers = json.loads(TIERS_PATH.read_text())
    form_count = sum(not row.get("placeholder")
                     for row in tiers["billing"]["prices"].values())
    for billing_live in (False, True):
        for x402_live in (False, True):
            html = _page(tiers, billing_live=billing_live, x402_live=x402_live,
                         x402_network="eip155:8453")
            assert len(re.findall(r"<form\b", html)) == (form_count if billing_live else 0)
            assert ("Or let your agents pay as they go" in html) is x402_live
            assert ("Pay per call" in html) is False
            assert _payload(html)["payPerCall"] is x402_live
            assert ("to $0.004" in html) is x402_live
            assert ("settled on Base mainnet" in html) is x402_live
            if not x402_live:
                assert "x402" not in html.lower()
                assert "per-call payment" not in html
                assert "plans and packs below" in html


def test_x402_requires_mainnet_before_the_page_presents_it() -> None:
    for enabled, mainnet in ((False, False), (False, True), (True, False), (True, True)):
        live = pricing.x402_is_live(enabled, mainnet)
        html = _page(x402_live=live, x402_network="eip155:8453")
        assert live is (enabled and mainnet)
        assert ("Or let your agents pay as they go" in html) is live
    assert worker_flags.production_vars(REPO_ROOT)["X402_NETWORK"] == "eip155:84532"


def test_worker_flags_read_only_top_level_production_vars(tmp_path: Path) -> None:
    path = tmp_path / worker_flags.WRANGLER_REL
    path.parent.mkdir(parents=True)
    path.write_text('''{
      "env": {"staging": {"vars": {"X402_ENABLED": "true"}}},
      /* production follows staging on purpose */
      "vars": {"X402_ENABLED": "false", "BILLING_ENABLED": "true",},
    }''')
    variables = worker_flags.production_vars(tmp_path)
    assert worker_flags.enabled(variables, "X402_ENABLED") is False
    assert worker_flags.enabled(variables, "BILLING_ENABLED") is True
    assert worker_flags.enabled(variables, "X402_MAINNET") is False


def test_worker_flag_off_spellings_match_the_worker() -> None:
    for value in ("0", "no", "off", "", "false", " FALSE "):
        assert worker_flags.enabled({"FLAG": value}, "FLAG") is False
    assert worker_flags.enabled({}, "FLAG") is False
    assert worker_flags.enabled({"FLAG": "yes"}, "FLAG") is True


def test_x402_copy_names_the_configured_network() -> None:
    html = _page(x402_live=True, x402_network="eip155:84532")
    assert "settled on Base Sepolia" in html
    assert "settled on Base mainnet" not in html


def test_landing_and_decide_link_pricing() -> None:
    landing = (REPO_ROOT / "pipeline/landing.py").read_text()
    decide = (REPO_ROOT / "web/src/decide/App.tsx").read_text()
    assert landing.count('href="/pricing/"') >= 2
    assert '<a href="/pricing/">Pricing</a>' in decide


def test_pricing_descriptions_and_hero_state_mcp_decision_key_requirement() -> None:
    requirement = "MCP decision tools (rank, policy_check, decide) require an API key."
    for enforced in (False, True):
        page = _page(access_enforced=enforced)
        description = pricing.DESCRIPTION if enforced else pricing.FREE_TIER_DESCRIPTION
        assert requirement in description
        assert requirement in _rendered_text(page)
        assert "offline CLI" not in page
        if not enforced:
            assert "API and MCP server answer on a free tier" not in page
