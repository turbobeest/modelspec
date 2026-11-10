"""The x402 guide describes admission and each checked-in environment."""
import asyncio
import re

from pipeline.worker_flags import parse_jsonc
from tests.test_x402 import entry, _entry_env, _decision_worker, _decision_request

from tests.test_tier_policy_bundle import REPO_ROOT as ROOT


def test_x402_reference_origin_admission_matches_shipped_flags(entry):
    doc = (ROOT / "docs/x402.md").read_text()
    config = parse_jsonc((ROOT / "api/worker/wrangler.jsonc").read_text())["vars"]
    env = _entry_env(**{name: config[name] for name in (
        "ACCESS_ENFORCED", "VISIT_GATE_ENABLED", "HUMAN_GATE_ENABLED", "X402_ENABLED",
    )})
    response = asyncio.run(_decision_worker(entry, env).fetch(_decision_request("https://modelspec.dev")))
    match = re.search(r"receives HTTP (\d+) `([a-z_]+)`", doc)
    assert match, "the guide must state the result of an Origin without credentials"
    assert (int(match[1]), match[2]) == (response.status, response.json()["error"]["code"])
    assert "admits only `/v1/decide` and `/v1/vocabulary`" in " ".join(doc.split())
    assert "ACCESS_ENFORCED=false" in doc
    assert "but doing so grants only" not in doc
    assert "admits keyless requests from `CORS_ORIGINS`" not in doc


def test_x402_reference_settings_match_production_and_staging():
    doc = (ROOT / "docs/x402.md").read_text()
    rows = {name: (prod.strip("`"), staging.strip("`"))
            for name, prod, staging in re.findall(
                r"^\| `(X402_\w+)` \| ([^|]+?) \| ([^|]+?) \|$", doc, re.M)}
    cfg = parse_jsonc((ROOT / "api/worker/wrangler.jsonc").read_text())
    for name in ("X402_ENABLED", "X402_MAINNET", "X402_NETWORK", "X402_ASSET", "X402_FACILITATOR_URL"):
        assert rows.get(name) == (cfg["vars"][name], cfg["env"]["staging"]["vars"][name])
    assert rows["X402_PAY_TO"] == tuple(
        "configured" if values["X402_PAY_TO"] else "empty"
        for values in (cfg["vars"], cfg["env"]["staging"]["vars"])
    )
