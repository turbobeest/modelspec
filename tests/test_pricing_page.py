"""MODEL-93: /pricing/ is generated from tiers.json and cannot drift."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from pipeline.export import Build
from pipeline import pricing

REPO_ROOT = Path(__file__).resolve().parent.parent
TIERS_PATH = REPO_ROOT / "api" / "worker" / "tiers.json"


def _build() -> Build:
    return Build(commit="0" * 40, built_at="2026-09-17T00:00:00Z", as_of=date(2026, 9, 17))


def test_pricing_page_is_built_and_both_urls_are_wired(tmp_path: Path) -> None:
    result = pricing.write(tmp_path, REPO_ROOT, _build())
    page = tmp_path / "pricing" / "index.html"
    assert page.is_file()
    assert result["path"] == "/pricing/"
    assert result["sitemap_paths"] == ["/pricing/"]
    html = page.read_text(encoding="utf-8")
    assert 'rel="canonical" href="https://modelspec.dev/pricing/"' in html
    redirects = (REPO_ROOT / "site" / "holding" / "_redirects").read_text(encoding="utf-8")
    assert "/pricing /pricing/" in redirects


def test_every_price_and_credit_number_comes_from_tiers_json(tmp_path: Path) -> None:
    tiers = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
    result = pricing.write(tmp_path, REPO_ROOT, _build())
    html = (tmp_path / "pricing" / "index.html").read_text(encoding="utf-8")
    assert result["billing_enabled"] is False
    assert "Billing is not live" in html
    for _pid, row in tiers["billing"]["prices"].items():
        assert f"{row['credits']:,}" in html
        assert f"${row['usd']}" in html
        assert row["name"] in html
    credits = tiers["credits"]
    assert str(credits["weights"]["rank"]) in html
    assert str(credits["weights"]["policy-check"]) in html
    assert str(credits["pack_expiry_days"]) in html
    assert str(credits["burst_limit"]) in html
    free = tiers["tiers"]["free"]
    assert str(free["daily_limit"]) in html
    assert str(free["burst_limit"]) in html
    assert "sales@modelspec.dev" in html
    assert "Only a successful result" in html or "only a successful result" in html.lower()
    assert "/api/rank/profiles.json" in html
    assert "/legal/neutrality/" in html
    assert "/legal/terms/" in html
    assert "99.9" not in html
    assert "guaranteed uptime" not in html.lower()


def test_no_token_wording_and_no_third_party_requests(tmp_path: Path) -> None:
    pricing.write(tmp_path, REPO_ROOT, _build())
    html = (tmp_path / "pricing" / "index.html").read_text(encoding="utf-8")
    assert re.search(r"\btokens?\b", html, flags=re.I) is None
    assert "fonts.googleapis" not in html
    assert "fonts.gstatic" not in html
    assert "cdn." not in html
    for match in re.finditer(r"<(script|img)\b[^>]*\bsrc=['\"](https?://[^'\"]+)", html, flags=re.I):
        raise AssertionError(f"third-party {match.group(1)}: {match.group(2)}")
    for match in re.finditer(r"<link\b[^>]*\bhref=['\"](https?://[^'\"]+)", html, flags=re.I):
        href = match.group(1)
        assert href.startswith("https://modelspec.dev"), href


def test_a_credit_figure_change_needs_no_code_change() -> None:
    tiers = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
    tiers["billing"]["prices"]["price_1UHRwmBPydVRHUBjqhKcx8xV"]["credits"] = 8
    html = pricing.page(tiers, live=False, build=_build())
    assert "8 / month" in html
    assert "4,000 / month" not in html
