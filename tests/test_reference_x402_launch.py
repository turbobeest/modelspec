"""The launch runbook separates the completed rollout from staging work."""
import re

from pipeline.worker_flags import production_vars, parse_jsonc
from tests.test_tier_policy_bundle import REPO_ROOT as ROOT


def test_x402_launch_reference_matches_completed_configuration():
    doc = (ROOT / "docs/x402-go-live.md").read_text()
    config = production_vars(ROOT)
    opening = doc.split("## Mainnet blocker", 1)[0]
    for flag in ("X402_ENABLED", "X402_MAINNET"):
        match = re.search(rf"`{flag}=(true|false)`", opening)
        assert match, f"missing current setting for {flag}"
        assert match[1] == config[flag]
    assert bool(config["X402_PAY_TO"]) == ("nonempty `X402_PAY_TO`" in opening)
    assert "completed" in opening
    stage2 = doc.split("## Stage 2:", 1)[1].split("## Switch staging", 1)[0]
    assert "completed" in stage2
    assert "e8eaa9ce" in stage2 and "faed1e6a" in stage2
    assert "remains off pending" not in stage2
    staging = parse_jsonc((ROOT / "api/worker/wrangler.jsonc").read_text())["env"]["staging"]["vars"]
    assert f'`X402_MAINNET={staging["X402_MAINNET"]}`' in stage2
    assert f'`{staging["X402_NETWORK"]}`' in stage2
