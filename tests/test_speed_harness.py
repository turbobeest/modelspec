"""The MODEL-212 speed harness, tested without spending (docs/method/speed-measurement.md).

The instrument is checked against a stream whose timing is known, on a local
socket; the statistics against an independent implementation; the spend cap,
the key handling and the router ban directly. No test sends a paid request.
"""

from __future__ import annotations

import dataclasses
import json
import random
import socket
import statistics
import threading
import time
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from scripts.speed import verify as verify_module
from scripts.speed.__main__ import dry_run
from scripts.speed.aggregate import AggregateError, aggregate
from scripts.speed.method import (
    MIN_SAMPLES,
    REPETITIONS_PER_SLOT,
    SLOT_HOURS_UTC,
    WARMUPS_PER_SLOT,
    WORKLOADS,
    median_interval,
    summarise,
    throughput,
    workload,
)
from scripts.speed.plan import Call, call_bound_usd, calls, load_plan, slot_cost
from scripts.speed.providers import APIS, FIRST_PARTY_HOSTS, Request
from scripts.speed.run import SpendRefusedError, run_slot
from scripts.speed.transport import (
    FIXTURES,
    Exchange,
    FixtureTransport,
    LiveTransport,
    Profile,
)

FASTEST = "google-gemini-api/google/gemini-3-8-flash/global/standard"


def _baseline():
    return dataclasses.replace(load_plan(), name="baseline", repetitions=REPETITIONS_PER_SLOT,
                               warmups=WARMUPS_PER_SLOT)


def _fixture_transport() -> FixtureTransport:
    return FixtureTransport({e.offering: Profile(800, 100) for e in load_plan().entries})


@pytest.fixture(scope="module")
def dry(tmp_path_factory):
    return dry_run(_baseline(), 12, tmp_path_factory.mktemp("speed-dry-run"))


# ── the published method cannot drift silently ─────────────────────────────


def test_the_prompts_are_speed_v1s():
    """A changed prompt is a new method version, never an edit to speed-v1."""
    assert {w.id: w.prompt_sha256() for w in WORKLOADS} == {
        "short_chat": "sha256:743138fce1cf3513d388ff1564135988ab210c3ef8f64b51e7e21645d187fb78",
        "coding": "sha256:a99104a18b3cf95c989881d285156ae8e2b90bacef9ad6df46a3bc17cbf1e341",
        "long_context":
            "sha256:865894fffe22f95cb285098e0cc300b052ad50f27790cbabdc2070a09e210f7e",
    }


def test_every_target_is_a_first_party_provider_host():
    assert {api.host for api in APIS.values()} <= FIRST_PARTY_HOSTS
    assert not any("router" in h or "openrouter" in h for h in FIRST_PARTY_HOSTS)
    assert {e.api for e in load_plan().entries} <= set(APIS)


# ── the instrument against a stream of known timing ────────────────────────

#: The truth, set by the server: first content after FIRST_TOKEN_S, then one
#: event of TOKENS_PER_EVENT tokens every GAP_S, so TOKENS_PER_EVENT / GAP_S
#: tokens a second. It is defined here, not by the code under test.
FIRST_TOKEN_S, EVENTS, TOKENS_PER_EVENT, GAP_S = 0.30, 24, 32, 0.05


def _events(api: str) -> list[dict]:
    total = EVENTS * TOKENS_PER_EVENT
    text = "word " * TOKENS_PER_EVENT
    if api == "anthropic":
        return ([{"type": "message_start", "message": {"usage": {"input_tokens": 12}}}]
                + [{"type": "content_block_delta", "delta": {"type": "text_delta", "text": text}}]
                * EVENTS
                + [{"type": "message_delta", "usage": {"output_tokens": total}}])
    if api == "gemini":
        return ([{"candidates": [{"content": {"parts": [{"text": text}]}}]}] * (EVENTS - 1)
                + [{"candidates": [{"content": {"parts": [{"text": text}]}}],
                    "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": total}}])
    return ([{"choices": [{"delta": {"content": text}}]}] * EVENTS
            + [{"choices": [], "usage": {"prompt_tokens": 12, "completion_tokens": total}}])


class _KnownStream(BaseHTTPRequestHandler):
    """Streams over HTTP/1.1 chunked transfer, as the providers do."""

    protocol_version = "HTTP/1.1"

    def _chunk(self, data: bytes) -> None:
        self.wfile.write(f"{len(data):x}\r\n".encode() + data + b"\r\n")
        self.wfile.flush()

    def do_POST(self):
        self.rfile.read(int(self.headers["content-length"]))
        api = self.path.strip("/")
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("transfer-encoding", "chunked")
        self.send_header("connection", "close")
        self.end_headers()
        start = time.perf_counter()
        # Absolute deadlines, so sleep overshoot never accumulates.
        for i, event in enumerate(_events(api)):
            content = i > 0 or api != "anthropic"
            index = i if api != "anthropic" else i - 1
            if content and index < EVENTS:
                time.sleep(max(0.0, start + FIRST_TOKEN_S + index * GAP_S - time.perf_counter()))
            self._chunk(f"data: {json.dumps(event)}\n\n".encode())
        self._chunk(b"data: [DONE]\n\n")
        self._chunk(b"")

    def log_message(self, *args):
        pass


@pytest.mark.parametrize("api", ["anthropic", "openai", "gemini"])
def test_the_live_transport_measures_a_stream_of_known_timing(api):
    """The answer to the cancelled 2026-09 programme: the timing path itself,
    real sockets, chunked transfer and each real parser, against a known truth."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _KnownStream)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        request = Request(api, "127.0.0.1", f"/{api}", {}, {"stream": True})
        exchange = LiveTransport(tls=False, port=server.server_port).send(request)
        result = APIS[api].parse(exchange.events)
    finally:
        server.shutdown()
    measured = throughput(result.visible_tokens, result.content_events,
                          result.first_content_s, result.last_content_s)
    assert result.content_events == EVENTS
    assert FIRST_TOKEN_S <= result.first_content_s <= FIRST_TOKEN_S + 0.05
    assert measured == pytest.approx(TOKENS_PER_EVENT / GAP_S, rel=0.05)


# ── parsing each provider's wire format ────────────────────────────────────


@pytest.mark.parametrize("api,wire,input_tokens", [
    ("anthropic", "anthropic", 152), ("openai", "chat", 150), ("gemini", "gemini", 149),
])
def test_each_fixture_stream_parses_to_its_usage(api, wire, input_tokens):
    payloads = [json.loads(line)["data"] for line in
                (FIXTURES / f"{wire}.jsonl").read_text().splitlines()]
    result = APIS[api].parse((i * 0.01, p) for i, p in enumerate(payloads))
    assert (result.input_tokens, result.billed_output_tokens, result.visible_tokens,
            result.content_events, result.error) == (input_tokens, 256, 256, 32, None)


def test_reasoning_tokens_are_billed_but_not_counted_as_visible_output():
    events = [(0.5, '{"choices":[{"delta":{"content":"hi"}}]}'),
              (0.6, '{"choices":[],"usage":{"prompt_tokens":10,"completion_tokens":300,'
                    '"completion_tokens_details":{"reasoning_tokens":200}}}')]
    result = APIS["openai"].parse(events)
    assert (result.billed_output_tokens, result.reasoning_tokens, result.visible_tokens) == (
        300, 200, 100)


# ── statistics, two independent implementations ─────────────────────────────


def test_the_median_interval_of_twenty_is_the_sixth_and_fifteenth():
    assert median_interval([float(x) for x in range(1, 21)]) == (6.0, 15.0)
    assert median_interval([3.0, 1.0, 2.0]) == (1.0, 3.0)


@pytest.mark.parametrize("seed", range(30))
def test_the_verifier_recomputes_the_same_statistics_independently(seed):
    rng = random.Random(seed)
    xs = sorted(rng.lognormvariate(0, 0.5) for _ in range(rng.randint(1, 60)))
    summary = summarise(xs)
    assert verify_module._interval(xs) == summary.interval
    assert verify_module._quantile(xs, 0.25) == pytest.approx(summary.iqr[0])
    assert verify_module._quantile(xs, 0.75) == pytest.approx(summary.iqr[1])
    assert (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 == pytest.approx(
        statistics.median(xs))


# ── spend ──────────────────────────────────────────────────────────────────


def test_a_run_whose_worst_case_exceeds_the_cap_sends_nothing():
    plan = load_plan()
    transport = _fixture_transport()
    with pytest.raises(SpendRefusedError, match="nothing was sent"):
        run_slot(plan, transport, cap_usd=slot_cost(plan).bound_usd - 0.01,
                 keys={api: "k" for api in APIS}, vantage="test")
    assert transport.calls == 0


def test_a_run_missing_a_key_sends_nothing():
    plan = load_plan()
    transport = _fixture_transport()
    keys = {api: "k" for api in APIS if api != "gemini"}
    with pytest.raises(SpendRefusedError, match="GEMINI_API_KEY"):
        run_slot(plan, transport, cap_usd=1000, keys=keys, vantage="test")
    assert transport.calls == 0


class _Overbilling:
    """A provider that bills far more than the request allowed."""

    provenance = "fixture"

    def __init__(self):
        self.calls = 0

    def send(self, request):
        self.calls += 1
        usage = {"choices": [], "usage": {"prompt_tokens": 10**6, "completion_tokens": 10**6}}
        return Exchange(200, 0.0, iter([(0.1, '{"choices":[{"delta":{"content":"x"}}]}'),
                                        (0.2, json.dumps(usage))]))


def test_the_cap_holds_even_when_a_provider_overbills():
    """No request is sent unless the spend so far plus its worst case fits the cap,
    whatever order the slot's shuffle puts the providers in."""
    plan = load_plan()
    cap = slot_cost(plan).bound_usd
    entries = {e.offering: e for e in plan.entries}
    for hour in SLOT_HOURS_UTC:
        clock = datetime(2026, 9, 1, hour, tzinfo=UTC)
        run = run_slot(plan, _Overbilling(), cap_usd=cap, keys={api: "k" for api in APIS},
                       vantage="test", now=lambda clock=clock: clock)
        assert run["stopped"] == "cap"
        spent = 0.0
        for sample in run["samples"]:
            call = Call(entries[sample["offering"]], workload(sample["workload"]),
                        sample["sample"], sample["warmup"])
            assert spent + call_bound_usd(call) <= cap + 1e-9
            spent += sample["cost_usd"]


def test_keys_never_reach_a_run_record():
    secret = "sk-model212-must-not-leak"
    run = run_slot(load_plan(), _fixture_transport(), cap_usd=1000,
                   keys={api: secret for api in APIS}, vantage="test")
    assert secret not in json.dumps(run)
    assert secret not in repr(APIS["openai"].request(secret, "m", "p", 1))


# ── the dry run, end to end on fixtures ────────────────────────────────────


def test_the_dry_run_opens_no_socket(monkeypatch, tmp_path):
    def refuse(*args, **kwargs):
        raise AssertionError("a dry run opened a socket")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    result = dry_run(_baseline(), 12, tmp_path)
    assert result["fixture_calls"] == 12 * len(calls(_baseline(), "x"))


def test_the_dry_run_publishes_every_headline_result_and_verifies_it(dry):
    measurement = dry["measurement"]
    headline = [r for r in measurement["results"] if r["workload"] == "short_chat"]
    assert len(headline) == 10 and all(r["publishable"] for r in headline)
    assert {r["n"] for r in headline} == {24}
    assert len(measurement["facts"]) == 20
    fact = next(f for f in measurement["facts"]
                if f["id"] == "google-gemini-api/google/gemini-3-8-flash/global/standard"
                              "#offering.speed.throughput")
    block = fact["measurement"]
    assert (block["measured_by"], block["method"], block["workload"], block["provenance"],
            block["n"], block["time_slots"]) == (
        "ModelSpec", "speed-v1", "short_chat", "fixture", 24, 12)
    assert block["interval"][0] <= fact["value"] == block["median"] <= block["interval"][1]
    assert [v["outcome"] for v in dry["verifications"]] == ["verified"] * 20


def test_a_single_pilot_slot_publishes_nothing():
    """The pilot tests plumbing; its one slot cannot pass the gates."""
    run = run_slot(load_plan(), _fixture_transport(), cap_usd=1000,
                   keys={api: "k" for api in APIS}, vantage="test")
    measurement = aggregate([run])
    assert measurement["facts"] == []
    reasons = {reason for r in measurement["results"] for reason in r["reasons"]}
    assert any(r.startswith("1 time slots") for r in reasons)
    # Five repetitions ran; only speed-v1's two a slot count.
    assert any(r.startswith(f"2 good samples; the gate is {MIN_SAMPLES}") for r in reasons)


def _pilot_slots(slots: int) -> list[dict]:
    plan = load_plan()
    runs = []
    for i in range(slots):
        clock = datetime(2026, 9, 1, tzinfo=UTC) + timedelta(hours=6 * i)
        runs.append(run_slot(plan, _fixture_transport(), cap_usd=1000,
                             keys={api: "k" for api in APIS}, vantage="test",
                             now=lambda clock=clock: clock))
    return runs


def test_clustered_pilot_slots_do_not_publish():
    """Four five-repetition slots over two days reached n=20 before the per-slot
    cap; samples in one slot share provider load, so they are not independent."""
    measurement = aggregate(_pilot_slots(4))
    assert measurement["facts"] == []
    assert {r["n"] for r in measurement["results"]} == {8}


def test_a_run_passed_twice_is_refused(dry):
    with pytest.raises(AggregateError, match="appears twice"):
        aggregate(dry["runs"] + dry["runs"][:1])


def test_the_verifier_refuses_a_run_set_that_is_not_the_measurements(dry):
    records = verify_module.verify(dry["measurement"], dry["runs"][1:])
    assert {r["outcome"] for r in records} == {"mismatch"}
    assert "not exactly the runs" in records[0]["diff"]


def test_the_verifier_re_times_samples_instead_of_trusting_them(dry):
    """A collector that wrote a wrong per-sample number is caught from the raw events."""
    runs = json.loads(json.dumps(dry["runs"]))
    for run in runs:
        for sample in run["samples"]:
            if sample["offering"] == FASTEST and sample["throughput_tps"]:
                sample["throughput_tps"] *= 2
    measurement = aggregate(runs)
    records = {r["target"]["id"]: r for r in verify_module.verify(measurement, runs)}
    tampered = records[f"{FASTEST}#offering.speed.throughput"]
    assert tampered["outcome"] == "mismatch" and "median" in tampered["diff"]


def test_hidden_reasoning_holds_an_offering_that_claims_none(dry):
    runs = json.loads(json.dumps(dry["runs"]))
    for run in runs:
        for sample in run["samples"]:
            if sample["offering"] == FASTEST:
                sample["reasoning_tokens"] = 40
    row = next(r for r in aggregate(runs)["results"]
               if (r["offering"], r["workload"]) == (FASTEST, "short_chat"))
    assert not row["publishable"]
    assert any("claims no reasoning" in reason for reason in row["reasons"])


def test_a_cached_or_failed_sample_is_counted_but_never_aggregated(dry):
    runs = json.loads(json.dumps(dry["runs"]))
    target = next(s for s in runs[0]["samples"] if not s["warmup"])
    target["status"] = "cache_hit"
    measurement = aggregate(runs)
    row = next(r for r in measurement["results"]
               if (r["offering"], r["workload"]) == (target["offering"], target["workload"]))
    assert (row["n"], row["attempted"], row["failures"]) == (23, 24, {"cache_hit": 1})


def test_a_tampered_median_fails_verification(dry):
    measurement = json.loads(json.dumps(dry["measurement"]))
    fact = measurement["facts"][0]
    fact["value"] = fact["measurement"]["median"] = fact["value"] + 1
    records = verify_module.verify(measurement, dry["runs"])
    assert records[0]["outcome"] == "mismatch" and "median" in records[0]["diff"]
    assert {r["outcome"] for r in records[1:]} == {"verified"}


def test_runs_from_another_vantage_are_dropped(dry):
    runs = json.loads(json.dumps(dry["runs"]))
    runs[0]["vantage"] = "elsewhere"
    measurement = aggregate(runs)
    assert measurement["dropped_runs"] == [runs[0]["run_id"]]
    assert measurement["vantage"] == "fixture"


def test_an_effort_change_between_runs_is_refused(dry):
    """A window measures one configuration; half at another effort is two."""
    runs = json.loads(json.dumps(dry["runs"]))
    for run in runs[: len(runs) // 2]:
        for entry in run["offerings"]:
            if entry["api"] == "openai":
                entry["params"] = {"reasoning_effort": "high"}
    with pytest.raises(AggregateError, match="settings changed between runs"):
        aggregate(runs)
    records = verify_module.verify(dry["measurement"], runs)
    assert all("changed between runs" in r["diff"] for r in records)


def test_one_thinking_request_holds_an_offering_that_claims_none(dry):
    """Anthropic reports thinking only as events inside output_tokens, and a
    minority of reasoning requests would slip past a median: any one holds."""
    events = [(0.1, '{"type":"content_block_delta","delta":{"type":"thinking_delta",'
                    '"thinking":"hmm"}}')]
    assert APIS["anthropic"].parse(events).reasoning_events == 1
    runs = json.loads(json.dumps(dry["runs"]))
    offering = "anthropic/anthropic/claude-sonnet-5-5/global/standard"
    sample = next(s for s in runs[0]["samples"] if s["offering"] == offering
                  and s["workload"] == "short_chat" and not s["warmup"])
    sample["reasoning_events"] = 1
    row = next(r for r in aggregate(runs)["results"]
               if (r["offering"], r["workload"]) == (offering, "short_chat"))
    assert not row["publishable"]
    assert "1 counted requests reasoned" in " ".join(row["reasons"])
