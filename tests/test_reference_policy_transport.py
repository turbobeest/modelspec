"""Executable policy-check reference examples and pagination guarantees."""

import asyncio
import json
import re
from datetime import UTC, datetime

import pytest

from tests.test_api_docs import POLICY_REFERENCE, policy
from tests.test_policy_check import real_catalogue
from tests.test_x402 import _Req, _entry_env, entry


def test_policy_reference_worked_command_reaches_success(entry, monkeypatch):
    import access_config
    import access_keys

    text = POLICY_REFERENCE.read_text(encoding="utf-8")
    block = re.search(r"```bash\n(.*?)```", text, re.S).group(1)
    payload = json.loads(re.search(r"-d '(.*?)'", block, re.S).group(1))
    headers = {}
    key = "live_documentation_fixture"
    for header in re.findall(r"-H '(.*?)'", block):
        name, value = header.split(":", 1)
        headers[name] = value.strip().replace("<key>", key)

    async def catalogue(_origin):
        return real_catalogue()

    monkeypatch.setattr(entry, "_load_policy_catalogue", catalogue)
    worker = entry.Default()
    worker.env = _entry_env(ACCESS_ENFORCED="true", X402_ENABLED="false")
    asyncio.run(access_keys.issue(
        worker.env.ACCESS.store, tier="free", owner="docs@example.test",
        now=datetime.now(UTC), policy=access_config.load_policy(worker.env), secret=key,
    ))
    response = asyncio.run(worker.fetch(_Req("/v1/policy-check", payload, headers=headers)))
    assert response.status == 200, response.json()
    assert response.json()["result"]


@pytest.mark.parametrize("field", ["limit", "offset"])
def test_policy_reference_pagination_defaults_match_parser(field):
    text = POLICY_REFERENCE.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines()
               if line.startswith("| ") and f"`{field}`" in line.split("|")[1])
    documented_default = int(re.search(r"default (\d+)", row).group(1))
    request = {"policy": {"licence": {"allowed": ["mit"]}}}
    assert documented_default == policy.parse_request(request, set())[field]
    if field == "limit":
        documented_max = int(re.search(r"0–(\d+)", row).group(1))
        assert policy.parse_request({**request, field: documented_max}, set())[field] == documented_max
        with pytest.raises(policy.RequestError):
            policy.parse_request({**request, field: documented_max + 1}, set())
    else:
        assert "nonnegative integer" in row
        assert policy.parse_request({**request, field: 501}, set())[field] == 501
    with pytest.raises(policy.RequestError):
        policy.parse_request({**request, field: -1}, set())


def test_policy_reference_sandbox_recovery_requires_a_live_key():
    text = POLICY_REFERENCE.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if "| `sandbox_not_available` |" in line)
    recovery = row.split("|")[-2]
    assert "without a key" not in recovery
    assert "live key" in recovery
