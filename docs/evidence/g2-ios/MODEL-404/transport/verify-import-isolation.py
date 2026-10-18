"""Exercise real decisions and schema generation after the offline replay helper."""

import asyncio
import sys

from api.worker import openapi
from tests.replay_billing_launch import replay

runtime = {name: sys.modules.get(name) for name in ("js", "workers", "bundled_data")}
response, = asyncio.run(replay({"calls": [{
    "path": "/v1/decide", "method": "POST",
    "headers": {"origin": "https://modelspec.dev"}, "body": "{}",
}]}))
assert response["status"] == 401
assert all(sys.modules.get(name) is previous for name, previous in runtime.items())
print("Runtime module stubs restored; keyless request refused with 401.")

from decision.contract import parse_spec
from decision.engine import decide
from tests.test_hardware_fit import assess, fixture_snapshot

answer = decide(parse_spec({
    "spec_version": 1, "optimize": {"max": "model.context_window"},
}, facets=None), fixture_snapshot())
assert answer.answer is not None
assert answer.answer.members == ["lab/hardware-model"]
print("Real decision after replay:", answer.status, answer.answer.members)

status, hardware = assess()
assert status == 200
assert (hardware["hardware_fit_version"], hardware["estimated_fit"], hardware["margin_bytes"]) == (
    "2.0", "likely", 18_795_200_000,
)
print("Real hardware assessment after replay:", status, hardware["hardware_fit_version"],
      hardware["estimated_fit"], hardware["margin_bytes"])

spec = openapi.build_spec()
assert spec["components"]["schemas"]["HardwareFitRefused"]["properties"]["hardware_fit_version"]["enum"] == ["2.0"]
print("Real OpenAPI generation after replay: hardware-fit 2.0.")
