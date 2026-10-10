"""The decide sales copy follows the pricing page and adopted commitment."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.ranking.engine import neutrality_commitment
from pipeline import decide_handoff, pricing, worker_flags

ROOT = Path(__file__).resolve().parents[1]


def _write_tiers(tmp_path: Path, tiers: dict) -> None:
    (tmp_path / pricing.TIERS_REL).parent.mkdir(parents=True)
    (tmp_path / pricing.TIERS_REL).write_text(json.dumps(tiers))
    (tmp_path / worker_flags.WRANGLER_REL).write_text('{"vars": {"BILLING_ENABLED": "false"}}')


def test_price_anchor_uses_the_team_rate() -> None:
    tiers = pricing.load_tiers(ROOT)
    team = pricing.team_usd_per_credit(tiers)
    data = decide_handoff.data(ROOT)
    price = pricing.format_usd(team * tiers["credits"]["weights"]["decide.summary"])
    assert data["price_line"] == f"Your agent gets this answer from {price}"
    assert data["price_line"] == "Your agent gets this answer from $0.008"
    assert "¢" not in data["price_line"]
    assert data["full_credits"] == tiers["credits"]["weights"]["decide.full"]


def test_changed_credit_weight_scales_the_team_rate(tmp_path: Path) -> None:
    tiers = pricing.load_tiers(ROOT)
    # A cheaper pack must not replace the Team plan on the decide anchor.
    tiers["billing"]["prices"]["price_changed"] = {
        "kind": "pack", "name": "Changed pack", "usd": 1, "credits": 2000,
        "interval": "once", "placeholder": False,
    }
    tiers["credits"]["weights"].update({"decide.summary": 3, "decide.full": 7})
    _write_tiers(tmp_path, tiers)
    data = decide_handoff.data(tmp_path)
    assert data["price_line"] == "Your agent gets this answer from $0.0239"
    assert data["full_credits"] == 7


def test_rendered_price_follows_a_changed_team_rate(tmp_path: Path) -> None:
    tiers = pricing.load_tiers(ROOT)
    team = next(row for row in tiers["billing"]["prices"].values()
                if row["name"] == "Team" and not row.get("legacy"))
    team["usd"] = 250
    _write_tiers(tmp_path, tiers)
    assert decide_handoff.data(tmp_path)["price_line"] == "Your agent gets this answer from $0.01"


@pytest.mark.parametrize("flag,href,label,note", [
    ("false", "/pricing/", "See pricing", "API keys open soon."),
    ("true", "/pricing/#pricing", "Get an API key", "Choose a plan or pack."),
    ("off", "/pricing/", "See pricing", "API keys open soon."),
])
def test_key_link_uses_the_same_production_flag_as_pricing(
    tmp_path: Path, flag: str, href: str, label: str, note: str,
) -> None:
    tiers = pricing.load_tiers(ROOT)
    (tmp_path / pricing.TIERS_REL).parent.mkdir(parents=True)
    (tmp_path / pricing.TIERS_REL).write_text(json.dumps(tiers))
    (tmp_path / worker_flags.WRANGLER_REL).write_text(json.dumps({
        "vars": {"BILLING_ENABLED": flag},
        "env": {"preview": {"vars": {"BILLING_ENABLED": "true"}}},
    }))
    assert decide_handoff.data(tmp_path)["key_link"] == {"href": href, "label": label, "note": note}
    page = pricing.page(tiers, billing_live=worker_flags.enabled(
        worker_flags.production_vars(tmp_path), "BILLING_ENABLED"))
    assert 'id="pricing"' in page
    sellable = any(not row.get("placeholder") and not row.get("legacy")
                   for row in tiers["billing"]["prices"].values())
    assert (f'action="{pricing.CHECKOUT_URL}"' in page) == (flag == "true" and sellable)


def test_badge_quotes_the_neutrality_commitment_exactly() -> None:
    badge = decide_handoff.data(ROOT)["neutrality"]
    commitment = neutrality_commitment()
    assert badge["text"] in commitment["pledge"]
    assert badge["href"] == commitment["neutrality_url"]


def test_mcp_clients_are_the_ones_the_cli_setup_accepts() -> None:
    bundle = json.loads((ROOT / "cli/modelspec/agent-bundle.json").read_text())
    assert decide_handoff.data(ROOT)["mcp_clients"] == list(bundle["clients"])
