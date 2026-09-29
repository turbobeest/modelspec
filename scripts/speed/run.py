"""Run one slot of the speed method against a transport.

A slot is every call in the plan once. Before the first call the run refuses
if any key is missing or if the plan's worst-case cost exceeds the cap. Before
every call it refuses to continue if the spend so far plus that call's worst
case would exceed the cap. Warm-ups are recorded and never aggregated. Every
sample keeps its raw stream events, so the verifier can re-time it.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import secrets
from collections.abc import Callable, Mapping
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from scripts.speed.method import (
    METHOD_ID,
    MIN_CONTENT_EVENTS,
    MIN_VISIBLE_TOKENS,
    SLOT_HOURS_UTC,
    WORKLOADS,
    nonce_line,
    throughput,
)
from scripts.speed.plan import Call, Plan, call_bound_usd, calls, slot_cost, usage_usd
from scripts.speed.providers import APIS, StreamResult
from scripts.speed.transport import Transport

RUN_FORMAT = "modelspec.speed-run"


class SpendRefusedError(RuntimeError):
    """The run would, or could, spend more than its cap. Nothing was sent."""


def slot_label(now: datetime) -> str:
    """The scheduled slot a run belongs to: the latest slot hour at or before ``now``."""
    hour = max(h for h in SLOT_HOURS_UTC if h <= now.hour)
    return now.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()


def keys_from_env(env: Mapping[str, str] = os.environ) -> dict[str, str]:
    """Each API's key from its environment variable. ``run_slot`` refuses a gap."""
    return {api.id: env[api.env] for api in APIS.values() if env.get(api.env)}


def probe_vantage() -> str:
    """Where the probe sits: the Cloudflare location its traffic enters at. Free."""
    connection = http.client.HTTPSConnection("www.cloudflare.com", timeout=20)
    try:
        connection.request("GET", "/cdn-cgi/trace")
        fields = dict(line.split("=", 1) for line in
                      connection.getresponse().read().decode().splitlines() if "=" in line)
    finally:
        connection.close()
    return f"cloudflare-colo:{fields.get('colo', 'unknown')}/{fields.get('loc', 'unknown')}"


def _status(http_status: int, result: StreamResult) -> str:
    if http_status != 200:
        return "http_error"
    if result.error:
        return "stream_error"
    if result.first_content_s is None or result.billed_output_tokens is None:
        return "no_content"
    if result.cached_input_tokens:
        return "cache_hit"
    if (result.visible_tokens or 0) < MIN_VISIBLE_TOKENS:
        return "short_output"
    if (result.content_events < MIN_CONTENT_EVENTS
            or result.last_content_s <= result.first_content_s):
        return "not_streamed"
    return "ok"


def _sample(call: Call, started_at: datetime, nonce: str, http_status: int,
            connect_s: float | None, result: StreamResult, cost: float,
            error: str | None, events: list[tuple[float, str]]) -> dict[str, Any]:
    status = "transport_error" if error else _status(http_status, result)
    ttft = tps = None
    if status == "ok":
        ttft = round(result.first_content_s * 1000, 1)
        tps = round(throughput(result.visible_tokens, result.content_events,
                               result.first_content_s, result.last_content_s), 2)
    return {
        "offering": call.entry.offering,
        "workload": call.workload.id,
        "sample": call.sample,
        "warmup": call.warmup,
        "started_at": started_at.isoformat(),
        "nonce": nonce,
        "status": status,
        "http_status": http_status,
        "error": error,
        "connect_ms": None if connect_s is None else round(connect_s * 1000, 1),
        "ttft_ms": ttft,
        "throughput_tps": tps,
        "input_tokens": result.input_tokens,
        "cached_input_tokens": result.cached_input_tokens,
        "billed_output_tokens": result.billed_output_tokens,
        "reasoning_tokens": result.reasoning_tokens,
        "reasoning_events": result.reasoning_events,
        "visible_tokens": result.visible_tokens,
        "content_events": result.content_events,
        "cost_usd": round(cost, 6),
        "events": [[round(t, 6), payload] for t, payload in events],
    }


def run_slot(plan: Plan, transport: Transport, *, cap_usd: float, keys: Mapping[str, str],
             vantage: str, now: Callable[[], datetime] = lambda: datetime.now(UTC),
             nonce: Callable[[Call], str] = lambda call: secrets.token_hex(8),
             ) -> dict[str, Any]:
    """Run every call in ``plan`` once and return the run record."""
    worst = slot_cost(plan).bound_usd
    if worst > cap_usd:
        raise SpendRefusedError(
            f"the plan can cost up to ${worst:.2f}, over the ${cap_usd:.2f} cap; nothing was sent")
    missing = sorted({APIS[e.api].env for e in plan.entries if e.api not in keys})
    if missing:
        raise SpendRefusedError(f"missing provider keys: {', '.join(missing)}")
    started = now()
    slot = slot_label(started)
    spent = 0.0
    stopped = None
    samples = []
    for call in calls(plan, seed=slot):
        bound = call_bound_usd(call)
        if spent + bound > cap_usd:
            stopped = "cap"
            break
        api = APIS[call.entry.api]
        token = nonce(call)
        request = api.request(
            keys[call.entry.api], call.entry.api_model,
            nonce_line(token) + call.workload.prompt(), call.workload.max_output_tokens,
            call.entry.params, offering=call.entry.offering, workload=call.workload.id,
            tag=token)
        started_at = now()
        http_status, connect_s, result, error = 0, None, StreamResult(), None
        events: list[tuple[float, str]] = []
        try:
            exchange = transport.send(request)
            http_status, connect_s = exchange.status, exchange.connect_s
            if exchange.status == 200:
                result = api.parse(_tap(exchange.events, events))
            else:
                result.error = (exchange.error_body or "")[:300]
        except Exception as exc:  # noqa: BLE001 - one bad reply must not lose a paid run
            error = f"{type(exc).__name__}: {exc}"[:300]
        if result.input_tokens is not None and result.billed_output_tokens is not None:
            cost = usage_usd(call.entry, result.input_tokens, result.billed_output_tokens)
        elif http_status == 200 or error:
            cost = bound
        else:
            cost = 0.0
        spent += cost
        samples.append(_sample(call, started_at, token, http_status, connect_s, result,
                               cost, error, events))
    finished = now()
    run = {
        "format": RUN_FORMAT,
        "method": METHOD_ID,
        "provenance": transport.provenance,
        "plan": plan.name,
        "slot": slot,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "vantage": vantage,
        "workloads": {w.id: {"prompt_sha256": w.prompt_sha256(),
                             "max_output_tokens": w.max_output_tokens} for w in WORKLOADS},
        "offerings": [asdict(e) for e in plan.entries],
        "cap_usd": cap_usd,
        "bound_usd": round(worst, 4),
        "spent_usd": round(spent, 4),
        "stopped": stopped,
        "samples": samples,
    }
    run["run_id"] = f"{METHOD_ID}-{slot[:13]}-{_digest(run)[:12]}"
    return run


def _tap(events, into: list[tuple[float, str]]):
    for item in events:
        into.append(item)
        yield item


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()
