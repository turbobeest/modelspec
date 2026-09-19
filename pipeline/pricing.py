"""Pricing page generated from `api/worker/tiers.json` (MODEL-93).

The published `/pricing/` page cannot drift from the Worker configuration:
every dollar amount and credit figure is read from that file at build time.
Billing-not-live copy is decided by `BILLING_ENABLED` in
`api/worker/wrangler.jsonc` at the same moment. Enterprise is not a Price;
it is a contact line.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipeline import render as r
from pipeline.export import Build

TIERS_REL = Path("api/worker/tiers.json")
WRANGLER_REL = Path("api/worker/wrangler.jsonc")
PAGE_PATH = Path("pricing") / "index.html"


def _live_jsonc(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("//"))


def billing_enabled(root: Path) -> bool:
    raw = (Path(root) / WRANGLER_REL).read_text(encoding="utf-8")
    return '"BILLING_ENABLED": "true"' in _live_jsonc(raw)


def load_tiers(root: Path) -> dict[str, Any]:
    return json.loads((Path(root) / TIERS_REL).read_text(encoding="utf-8"))


def _usd(amount: int) -> str:
    return f"${int(amount)}"


def _credits(amount: int) -> str:
    return f"{int(amount):,}"


def page(tiers: dict[str, Any], *, live: bool, build: Build,
         base: str = "https://modelspec.dev") -> str:
    free = tiers["tiers"]["free"]
    credits = tiers["credits"]
    prices = tiers["billing"]["prices"]
    plans = [row | {"price_id": pid} for pid, row in prices.items()
             if row.get("kind") == "plan"]
    packs = [row | {"price_id": pid} for pid, row in prices.items()
             if row.get("kind") == "pack"]
    rank_w = credits["weights"]["rank"]
    policy_w = credits["weights"]["policy-check"]
    expiry = credits["pack_expiry_days"]
    burst = credits["burst_limit"]
    get_a_key = tiers["urls"]["get_a_key"]

    live_note = (
        '<p class="lede"><strong>Billing is not live.</strong> The figures '
        "below are the configured prices. Checkout is not enabled on this "
        "deployment; nothing here can be bought yet. What is served today is "
        "the free tier: live rankings, no determinations, no charge.</p>"
        if not live else
        '<p class="lede">Paid access is metered in credits. Only a successful '
        "result draws them.</p>"
    )

    plan_rows = (
        "<tr><th>Free</th>"
        "<td>—</td>"
        "<td>—</td>"
        f"<td>{free['daily_limit']} rankings / UTC day, "
        f"{free['burst_limit']}/min burst. No determinations.</td></tr>"
    )
    for row in plans:
        plan_rows += (
            f"<tr><th>{r.esc(row['name'])}</th>"
            f"<td>{_credits(row['credits'])} / month</td>"
            f"<td>{_usd(row['usd'])}/mo</td>"
            f"<td>Monthly allowance is set to { _credits(row['credits']) } on "
            "each paid invoice (reset, no rollover). Determinations included "
            "while the balance is above zero. No daily cap; "
            f"{burst}/min burst.</td></tr>"
        )
    plan_rows += (
        "<tr><th>Enterprise</th><td>—</td><td>—</td>"
        "<td>Contact <a href=\"mailto:sales@modelspec.dev\">"
        "sales@modelspec.dev</a>.</td></tr>"
    )

    pack_rows = ""
    for row in packs:
        pack_rows += (
            f"<tr><th>{r.esc(row['name'])}</th>"
            f"<td>{_credits(row['credits'])}</td>"
            f"<td>{_usd(row['usd'])}</td>"
            f"<td>Added to the pack balance. Expires {expiry} days after "
            "purchase. Oldest-expiring spent first.</td></tr>"
        )

    body = f"""
<h1>Pricing</h1>
{live_note}
<p>Paid access is metered in <strong>credits</strong>. One balance per API key.
A funded key (balance above zero) receives the paid answer, including cited
commercial-use and data-residency determinations. A key with no remaining
credits receives the free-tier answer, not an error, and a field that says
credits are exhausted and where to buy. Free callers without a key are
unchanged: {free['daily_limit']} rankings per UTC day, {free['burst_limit']}/min
burst, no determinations.</p>

<h2>Plans</h2>
<div class="scroll"><table><thead><tr><th>Plan</th><th>Credits</th><th>Price</th>
<th>What it includes</th></tr></thead><tbody>{plan_rows}</tbody></table></div>

<h2>Packs</h2>
<p>One-off purchases. They add to a separate pack balance and expire {expiry}
days after purchase. Cancellation of a plan zeros the monthly allowance at
once; pack credits are unaffected. x402 top-ups land in this same pack
balance, with the same expiry rule.</p>
<div class="scroll"><table><thead><tr><th>Pack</th><th>Credits</th><th>Price</th>
<th>Expiry</th></tr></thead><tbody>{pack_rows}</tbody></table></div>

<h2>What a credit buys</h2>
<ul>
<li>A successful ranking costs <strong>{rank_w} credit</strong>.</li>
<li>A successful compliance check costs <strong>{policy_w} credits</strong>.</li>
<li>Only a successful result costs credits. 4xx, 5xx, and a well-formed
request that matches no model cost nothing.</li>
<li>Draw order: monthly allowance first, then pack credits, oldest expiry
first.</li>
</ul>

<h2>The paid answer</h2>
<p>A funded key receives cited commercial-use and data-residency
determinations on <span class="mono">POST /v1/policy-check</span>. The free
answer does not include them; those checks come back undetermined and labelled
as a tier gap, never as a pass.</p>

<h2>Neutrality</h2>
<p>No referral fees, no paid placement, no provider-paid visibility. The
commitment is published as data at
<a href="/api/rank/profiles.json"><span class="mono">/api/rank/profiles.json</span></a>
under <span class="mono">ranking_policy.neutrality</span>, and as prose at
<a href="/legal/neutrality/">/legal/neutrality/</a>.</p>

<p>Terms (draft, not adopted): <a href="/legal/terms/">/legal/terms/</a>.
Keys, when issuance is on, are claimed at the Checkout success URL and shown
once. Buy URL: <span class="mono">{r.esc(get_a_key)}</span>.</p>
<p>There is no SLA and no uptime promise on this page.</p>
"""
    return r.shell(
        title="Pricing — ModelSpec",
        description=(
            "ModelSpec API pricing: Solo and Team monthly credits, one-off packs, "
            "and what a successful ranking or compliance check costs."
        ),
        canonical=base.rstrip("/") + "/pricing/",
        body=body,
        build=build,
        site="ModelSpec",
        nav_links=r.MS_NAV,
    )


def write(tree: Path, root: Path, build: Build,
          base: str = "https://modelspec.dev") -> dict[str, Any]:
    tiers = load_tiers(root)
    live = billing_enabled(root)
    html = page(tiers, live=live, build=build, base=base)
    out = Path(tree) / PAGE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return {
        "path": "/pricing/",
        "billing_enabled": live,
        "sitemap_paths": ["/pricing/"],
    }
