"""The access reference follows the deployment and policy resolution paths."""
import json
import re
import sys
import types

import pytest
import yaml

from pipeline.worker_flags import production_vars
from tests.test_tier_policy_bundle import REPO_ROOT, _vendor, access_config


def test_access_reference_deploy_command_matches_workflow():
    doc = (REPO_ROOT / "docs/api-access.md").read_text()
    commands = [line.strip() for line in doc.splitlines()
                if "deploy --var" in line]
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/rank-api.yml").read_text())
    deploy = next(step["run"] for step in workflow["jobs"]["deploy"]["steps"]
                  if step.get("name") == "Deploy")
    # MODEL-487: the step runs the documented command inside the retry wrapper.
    wrapper = 'python3 "$GITHUB_WORKSPACE/scripts/deploy_retry.py" -- '
    assert [wrapper + command for command in commands] == [deploy.strip()]
    assert "TIER_POLICY:" not in commands[0]


def test_access_reference_explains_generated_policy_fallback(monkeypatch, tmp_path):
    _vendor().write_tier_policy(tmp_path)
    namespace = {}
    exec((tmp_path / "tier_policy.py").read_text(), namespace)
    monkeypatch.setitem(sys.modules, "tier_policy", types.SimpleNamespace(TEXT=namespace["TEXT"]))
    monkeypatch.setattr(access_config, "DEFAULT_POLICY_PATH", tmp_path / "absent.json")
    policy = access_config.load_policy(types.SimpleNamespace())
    expected = json.loads((REPO_ROOT / "api/worker/tiers.json").read_text())
    assert policy.version == access_config.policy_from_mapping(expected).version
    assert policy.tier("free").daily_limit == expected["tiers"]["free"]["daily_limit"]
    with pytest.raises(access_config.PolicyError):
        access_config.load_policy(path=tmp_path / "absent.json")
    doc = (REPO_ROOT / "docs/api-access.md").read_text()
    assert "tier_policy.TEXT" in doc
    assert "explicit path does not fall back" in " ".join(doc.split())
    assert "A Worker without the variable refuses" not in doc


def test_access_reference_shipped_settings_match_configuration():
    doc = (REPO_ROOT / "docs/api-access.md").read_text()
    actual = production_vars(REPO_ROOT)
    for flag in ("ACCESS_ENFORCED", "BILLING_ENABLED", "VISIT_GATE_ENABLED"):
        match = re.search(rf"`{flag}=(true|false)`", doc)
        assert match, f"missing current setting for {flag}"
        assert match[1] == actual[flag]
    policy = json.loads((REPO_ROOT / "api/worker/tiers.json").read_text())
    assert json.dumps(policy["billing"]["friends_promotion_code_prefix"]) in doc
    assert "Stripe issuance is inert" not in doc
    assert "no key has been issued" not in doc
    assert "shipping off" not in doc
