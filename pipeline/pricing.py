"""Build the data-driven ModelSpec pricing page (MODEL-186 follow-up)."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from pipeline import brand
from pipeline.export import Build

TIERS_REL = Path("api/worker/tiers.json")
PAGE_PATH = Path("pricing") / "index.html"
ASSET_DIR = "pricing-assets"
DATA_ID = "pricing-data"
CHECKOUT_URL = "https://api.modelspec.dev/v1/billing/checkout"
DECIDE_ENDPOINT = "https://api.modelspec.dev/v1/decide"
MCP_ENDPOINT = "https://api.modelspec.dev/mcp"
TITLE = "ModelSpec pricing — people decide free, agents pay per answer"
DESCRIPTION = ("The ModelSpec board and offline CLI are free. Hosted API and MCP "
               "answers use credits, with plans and packs.")
NETWORK_NAMES = {"eip155:8453": "Base mainnet", "eip155:84532": "Base Sepolia"}


def load_tiers(root: Path) -> dict[str, Any]:
    return json.loads((Path(root) / TIERS_REL).read_text(encoding="utf-8"))


def _money(value: int | float, suffix: str = "") -> str:
    return f"${value:,.0f}{suffix}"


def _rate(value: float) -> str:
    digits = 5 if value < .001 else 4
    return "$" + f"{value:.{digits}f}".rstrip("0").rstrip(".")


def _logo() -> str:
    return ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" '
            'height="40" rx="3" fill="#0B1426" stroke="#2a3b5c"/><line x1="6.5" y1="3" '
            'x2="6.5" y2="37.5" stroke="#F2C94C" stroke-width=".9"/><line x1="3" y1="34" '
            'x2="37" y2="34" stroke="#3FB68B" stroke-width="2.2"/><path d="M11 29 16 11 '
            '21 23 26 11 31 29" fill="none" stroke="#fff" stroke-width="1.5" '
            'stroke-linecap="round"/><g fill="#5AA9EC"><circle cx="11" cy="29" r="1.9"/>'
            '<circle cx="16" cy="11" r="1.9"/><circle cx="21" cy="23" r="1.9"/>'
            '<circle cx="26" cy="11" r="1.9"/><circle cx="31" cy="29" r="1.9"/></g></svg>')


def _buy_form(price_id: str, kind: str) -> str:
    label = "Subscribe" if kind == "plan" else "Buy"
    return (f'<form method="post" action="{CHECKOUT_URL}">'
            f'<input type="hidden" name="price_id" value="{html.escape(price_id)}">'
            f'<button type="submit">{label}</button></form>')


def x402_is_live(enabled: bool, mainnet: bool) -> bool:
    """Return whether the pricing page may present production x402 payments."""
    return enabled and mainnet


def calculator_data(tiers: dict[str, Any], *, x402_live: bool = True) -> dict[str, Any]:
    """Return the calculator contract generated from the billing tiers."""
    prices = tiers["billing"]["prices"]
    plans = [row for row in prices.values() if row["kind"] == "plan"]
    packs = [row for row in prices.values() if row["kind"] == "pack"]
    weights = tiers["credits"]["weights"]
    smallest_pack = min(packs, key=lambda row: row["credits"])
    data = {
        "plans": [{"name": row["name"], "credits": row["credits"], "usd": row["usd"]}
                  for row in plans],
        "packs": [{"credits": row["credits"], "usd": row["usd"]} for row in packs],
        "weights": {"decide": weights["decide.summary"],
                    "decideFull": weights["decide.full"], "rank": weights["rank"],
                    "check": weights["policy-check"]},
        "payPerCall": x402_live,
    }
    if x402_live:
        data["perCall"] = smallest_pack["usd"] / smallest_pack["credits"]
    return data


def page(tiers: dict[str, Any], *, build: Build | None = None,
         base: str = "https://modelspec.dev", live: bool | None = None,
         billing_live: bool = True, x402_live: bool = True,
         x402_network: str = "eip155:8453") -> str:
    """Render the responsive page. ``live`` remains accepted for old callers."""
    del build, live
    prices = tiers["billing"]["prices"]
    plans = [(pid, row) for pid, row in prices.items() if row["kind"] == "plan"]
    packs = [(pid, row) for pid, row in prices.items() if row["kind"] == "pack"]
    weights = tiers["credits"]["weights"]
    expiry = tiers["credits"]["pack_expiry_days"]
    smallest_pack = min((row for _, row in packs), key=lambda row: row["credits"])
    per_call = smallest_pack["usd"] / smallest_pack["credits"]
    cheapest = min(prices.values(), key=lambda row: row["usd"] / row["credits"])
    best_rate = cheapest["usd"] / cheapest["credits"]
    highest_rate = max(row["usd"] / row["credits"] for row in prices.values())
    cheapest_name = html.escape(cheapest["name"])
    network_name = html.escape(NETWORK_NAMES.get(x402_network, x402_network))
    form = _buy_form if billing_live else lambda _price_id, _kind: ""

    plan_rows = "".join(
        f'<tr class="price-row plan" role="row"><th scope="row" role="rowheader">{html.escape(row["name"])}</th>'
        f'<td role="cell">{row["credits"]:,} credits<span>{_rate(row["usd"] / row["credits"])}/credit</span></td>'
        f'<td role="cell"><strong>{_money(row["usd"], "/mo")}</strong></td>'
        f'<td role="cell">{"" if row.get("placeholder") else form(pid, row["kind"])}</td></tr>'
        for pid, row in plans
    )
    pack_rows = "".join(
        f'<tr class="price-row pack" role="row"><th scope="row" role="rowheader">{row["credits"]:,} credits</th>'
        f'<td role="cell">{_rate(row["usd"] / row["credits"])}/credit</td>'
        f'<td role="cell"><strong>{_money(row["usd"])}</strong></td>'
        f'<td role="cell">{"" if row.get("placeholder") else form(pid, row["kind"])}</td></tr>'
        for pid, row in packs
    )
    payload = json.dumps(calculator_data(tiers, x402_live=x402_live),
                         separators=(",", ":")).replace("<", "\\u003c")
    decision_buttons = "".join(
        f'<button type="button" data-value="{value}" aria-pressed="{str(value == 1000).lower()}">{value:,}</button>'
        for value in (100, 1000, 10000, 50000, 100000))
    check_buttons = "".join(
        f'<button type="button" data-value="{value}" aria-pressed="{str(value == 0).lower()}">{"None" if value == 0 else f"{value:,}"}</button>'
        for value in (0, 100, 1000, 10000))
    hero_payment = "prepaid credits or a per-call x402 payment" if x402_live else "prepaid credits"
    hero_rate = (f'<div><strong>{_rate(best_rate)}</strong><b>to {_rate(per_call)}</b></div>'
                 if x402_live else
                 f'<div><strong>{_rate(best_rate)}–{_rate(highest_rate)}</strong></div>')
    hero_detail = (f"One credit. The low end is the {cheapest_name} plan's rate; the high end "
                   "is paying per call with no account. A full explanation costs two credits."
                   if x402_live else
                   f"One credit. The low end is the {cheapest_name} plan's rate; the range "
                   "covers the plans and packs below. A full explanation costs two credits.")
    agents_panel = f'''<div class="card agents-card" id="agents"><h2>Or let your agents pay as they go</h2><p>No account, no key, no human in the loop. The API answers an unpaid request with HTTP 402 and a price; the agent pays in USDC over x402 and gets its answer in the same exchange.</p><div class="exchange"><div><i>→</i> POST api.modelspec.dev/v1/decide</div><div><em>←</em> 402 Payment Required <span>· 1 credit · {_rate(per_call)} USDC</span></div><div><i>→</i> retry with PAYMENT-SIGNATURE <span>· settled on {network_name}</span></div><div><mark>←</mark> 200 OK <span>· the ranked answer, and a receipt</span></div></div><ul><li>A keyless call costs {_rate(per_call)} a credit, times the answer's weight.</li><li>A keyed agent whose balance runs out is offered the same {len(packs)} packs, paid in USDC. They land in the key's pack balance.</li><li>A per-call payment is settled before the answer is produced; if the service then fails, that payment isn't refunded automatically.</li></ul><div class="endpoints"><span>Point your agent at either endpoint:</span><code>POST {DECIDE_ENDPOINT}\nMCP  {MCP_ENDPOINT}</code></div></div>''' if x402_live else ""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE}</title><meta name="description" content="{DESCRIPTION}">
<link rel="canonical" href="{base.rstrip('/')}/pricing/">{brand.head_links()}{brand.social_meta(TITLE)}
<link rel="stylesheet" href="/{ASSET_DIR}/pricing.css"></head><body><div class="axis" aria-hidden="true"></div>
<header>{_logo()}<a class="wordmark" href="/"><b>Model</b>Spec</a><nav><a href="/#agents">For agents</a><a class="current" href="/pricing/" aria-current="page">Pricing</a><a class="button" href="/decide/">Open the board</a></nav><a class="button mobile-board" href="/decide/">Open the board</a></header>
<main><section class="hero" id="pricing"><div><h1>People decide free. Agents pay per answer.</h1><p>The board on this site and the offline CLI cost nothing. Hosted API and MCP answers use {hero_payment}.</p></div><div class="rate-card"><span>One decision for an agent</span>{hero_rate}<p>{hero_detail}</p></div></section>
<section class="buy-grid"><div class="card buy-card"><h2>Buy credits for your agents</h2><p>Pay by card. You get one API key and one balance; every agent that carries the key draws from it.</p><table class="price-table" role="table"><caption>Monthly plans · allowance resets each invoice</caption><thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Plan</th><th scope="col" role="columnheader">Allowance</th><th scope="col" role="columnheader">Price</th><th scope="col" role="columnheader">Purchase</th></tr></thead><tbody role="rowgroup">{plan_rows}</tbody></table><table class="price-table" role="table"><caption>Packs · one-off, last {expiry} days</caption><thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Pack</th><th scope="col" role="columnheader">Rate</th><th scope="col" role="columnheader">Price</th><th scope="col" role="columnheader">Purchase</th></tr></thead><tbody role="rowgroup">{pack_rows}</tbody></table><p class="small">Checkout is hosted by Stripe; card details never reach ModelSpec. The plan allowance is spent first, then packs, oldest first. Cancel any time. For volume or invoicing, write to <a href="mailto:sales@modelspec.dev">sales@modelspec.dev</a>.</p></div>
{agents_panel}</section>
<section class="calculator"><div class="controls"><h2>What will your agents spend?</h2><fieldset data-control="decisions"><legend>Decisions a day</legend><div>{decision_buttons}</div></fieldset><fieldset data-control="full"><legend>Explanation with each decision</legend><div><button type="button" data-value="false" aria-pressed="true">Summary · {weights['decide.summary']} credit</button><button type="button" data-value="true" aria-pressed="false">Full · {weights['decide.full']} credits</button></div></fieldset><fieldset data-control="checks"><legend>Licence and data-residency checks a day</legend><div>{check_buttons}</div></fieldset></div><div class="estimate" aria-live="polite"><span data-credits></span><div><b>Cheapest way to pay</b><strong><span data-best-name></span> · <span data-best-cost></span><small> a month</small></strong></div><div data-options></div><p>A month is 30 days. Prices from the published plan and pack list; the arithmetic runs in your browser. On an exact tie, the calculator prefers an option without a subscription.</p></div></section>
<section class="costs"><div><h2>What an answer costs</h2><table class="cost-table"><caption>Credits drawn from a prepaid balance</caption><thead><tr><th scope="col">Answer</th><th scope="col">Cost</th></tr></thead><tbody><tr class="cost-row"><th scope="row">A decision<span>ranked answer with ties, no explanation or a summary</span></th><td>{weights['decide.summary']} credit</td></tr><tr class="cost-row"><th scope="row">A decision, fully explained<span>every fact, source and trade-off behind the order</span></th><td>{weights['decide.full']} credits</td></tr><tr class="cost-row"><th scope="row">A ranking<span>the ranked list for one capability</span></th><td>{weights['rank']} credit</td></tr><tr class="cost-row"><th scope="row">A licence and data-residency check<span>cited commercial-use and residency determinations</span></th><td>{weights['policy-check']} credits</td></tr><tr class="cost-row"><th scope="row">An error, a refusal, or no model fits<span>anything that is not a successful answer</span></th><td class="free">free</td></tr></tbody></table></div><div><h2>What stays free</h2><ul class="free-list"><li><b>The board, for people.</b> Every facet, every tie, every source, on this site. No account.</li><li><b>The CLI, offline.</b> Fetch the public snapshot once and decide locally, as often as you like.</li><li><b>The data.</b> The static export under /api is public, versioned JSON.</li><li><b>The sandbox.</b> Unlimited synthetic answers to build and test against. No signup.</li></ul></div></section>
<section class="trust"><div><h3>Paying never moves a model.</h3><p>Credits buy answers and determinations. No referral fees, no paid placement, no provider-paid visibility. A published commitment you can check.</p></div><div><h3>Only a successful answer draws credits.</h3><p>Errors, refusals and "no model fits" release the credit reservation. Your balance is one call away.</p></div><div><h3>The same facts, the same answer.</h3><p>A spec and a snapshot always give the same result, so an agent's choice can be audited later.</p></div></section></main>
<footer><span>© Sparks and Sawdust LLC</span><a href="/pricing/">Pricing</a><a href="/legal/terms/">Terms</a><a href="/legal/privacy/">Privacy</a><a href="/legal/neutrality/">Neutrality commitment</a><span>Prices in US dollars. Sales tax may apply at checkout.</span></footer>
<script id="{DATA_ID}" type="application/json">{payload}</script><script type="module" src="/{ASSET_DIR}/pricing.js"></script></body></html>\n'''


def write(tree: Path, root: Path, build: Build,
          base: str = "https://modelspec.dev") -> dict[str, Any]:
    from api.worker import openapi

    out = Path(tree) / PAGE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    x402_live = x402_is_live(openapi.x402_enabled(), openapi.x402_mainnet_enabled())
    out.write_text(page(load_tiers(root), build=build, base=base,
                        billing_live=openapi.billing_enabled(), x402_live=x402_live,
                        x402_network=openapi.x402_network()), encoding="utf-8")
    assets = Path(tree) / ASSET_DIR
    assets.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent / "pricing_assets"
    for name in ("pricing.css", "pricing.js"):
        (assets / name).write_bytes((source / name).read_bytes())
    return {"path": "/pricing/", "sitemap_paths": ["/pricing/"]}
