"""The complete policy contract example runs against the frozen catalogue."""

import json
import re

from tests.test_policy_check import REPO_ROOT, real_catalogue, service


def test_policy_contract_complete_request_returns_a_nonempty_answer():
    text = (REPO_ROOT / "docs/policy-check-api.md").read_text(encoding="utf-8")
    block = next(block for block in re.findall(r"```jsonc\n(.*?)```", text, re.S)
                 if block.startswith("POST /v1/policy-check"))
    request = json.loads(re.sub(r"//[^\n]*", "", block[block.index("{"):]))
    status, body = service.check(
        request, real_catalogue(), None, service.ENTITLEMENT_PUBLIC,
        "documentation-test", "https://modelspec.test",
    )
    assert status == 200, body
    assert body["result"]
