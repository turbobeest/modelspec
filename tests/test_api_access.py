"""API keys, rate limits and the sandbox (MODEL-69).

These tests are the acceptance criteria, and several of them are written to
fail rather than to pass: the sandbox is handed a key store and a data path
that raise if they are touched, the exempt tier is checked for by parsing the
package's own syntax tree, and the secret this file issues is searched for in
every log line, header, response body and stored value the gateway produced.

The modules under test are the Worker's, imported from `api/worker/src`. They
import nothing from the Workers runtime, which is what makes them testable
here — the same arrangement MODEL-68 made for the scorer.
"""

from __future__ import annotations

import ast
import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access  # noqa: E402
import access_config  # noqa: E402
import access_keys as keys  # noqa: E402
import access_limits as limits  # noqa: E402
import access_sandbox as sandbox  # noqa: E402
from access_kv import MemoryKV  # noqa: E402

from pipeline.ranking import Candidate, rank_report  # noqa: E402

ACCESS_MODULES = sorted(WORKER_SRC.glob("access*.py"))

#: A fixed clock. Mid-afternoon UTC, so "the day resets at midnight" is a
#: visible move rather than an accident of the test's start time.
T0 = datetime(2026, 9, 17, 14, 30, 0, tzinfo=UTC)

ENVELOPE = {"schema_version": "1.0", "endpoint": "rank", "service_commit": "testsha",
            "export_origin": "https://modelspec.dev",
            "build": {"commit": None, "built_at": None, "export_schema_version": None}}


def run(coro: Any) -> Any:
    """The repository has no asyncio plugin configured; it does not need one."""
    return asyncio.run(coro)


@pytest.fixture
def policy() -> access_config.AccessPolicy:
    return access_config.load_policy()


class Recorder:
    """Collects everything the gateway said, for the no-secrets sweep."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def __call__(self, event: str, fields: dict[str, Any]) -> None:
        self.events.append((event, dict(fields)))

    def text(self) -> str:
        return json.dumps(self.events, default=str)


class ExplodingKV:
    """A key store that fails the test if it is read or written at all."""

    async def get(self, name: str) -> str | None:
        raise AssertionError(f"the sandbox read the key store: {name}")

    async def put(self, name: str, value: str, *, expiration_ttl: int | None = None) -> None:
        raise AssertionError(f"the sandbox wrote to the key store: {name}")

    async def delete(self, name: str) -> None:
        raise AssertionError(f"the sandbox deleted from the key store: {name}")


async def _never_live(record: Any) -> tuple[int, dict[str, Any]]:
    raise AssertionError("the live data path was reached")


def _sandbox_answer() -> tuple[int, dict[str, Any]]:
    return sandbox.rank_response(sandbox.request_from_payload({"use_case": "general"}),
                                 envelope=dict(ENVELOPE))


def _live_answer(rows: int = 1):
    async def live(record: Any) -> tuple[int, dict[str, Any]]:
        return 200, {**ENVELOPE, "tier_served": record.tier, "result": [{"rank": 1}] * rows}
    return live


async def _serve(key: str | None, kv: Any, policy: access_config.AccessPolicy, *,
                 now: datetime = T0, log: Any = None,
                 live: Any = None, sandbox_fn: Any = None) -> access.Outcome:
    return await access.serve(
        api_key=key, kv=kv, policy=policy, now=now, envelope=dict(ENVELOPE),
        live=live or _live_answer(), sandbox=sandbox_fn or _sandbox_answer, log=log,
    )


async def _issue(kv: Any, tier: str, policy: access_config.AccessPolicy,
                 secret: str) -> Any:
    _, record = await keys.issue(kv, tier=tier, owner="tests@modelspec.dev",
                                 now=T0, policy=policy, secret=secret)
    return record


# ── the tier table is configuration ──────────────────────────────────────────

def test_the_shipped_tier_table_carries_the_decided_limits(policy):
    assert policy.timezone == "UTC"
    free = policy.tier("free")
    assert (free.daily_limit, free.burst_limit) == (10, 5)
    assert policy.tier(policy.sandbox_tier).unlimited
    assert policy.tier(policy.sandbox_tier).live_data is False
    assert policy.sandbox_prefix == "test_"


def test_a_limit_changes_with_no_code_change(policy):
    """The acceptance criterion MODEL-73 depends on.

    The only thing edited between the two halves of this test is a JSON
    document. No module is patched, reloaded or monkeypatched.
    """
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["tiers"]["free"]["daily_limit"] = 2
    tightened = access_config.policy_from_json(json.dumps(table))

    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_config"))
    served = [run(_serve("live_config", kv, tightened,
                         now=T0 + timedelta(seconds=61 * i))).status for i in range(3)]
    assert served == [200, 200, 429]


def test_no_access_module_hard_codes_a_limit():
    """Grep is not the proof; the syntax tree is.

    Any numeric literal bound to a name that reads like a limit would be a
    second place a tier's numbers live, and the next change would edit one of
    them.
    """
    suspicious = ("limit", "quota", "per_day", "per_minute", "max_requests")
    offenders: list[str] = []
    for module in ACCESS_MODULES:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id.lower() for t in targets if isinstance(t, ast.Name)
                     # HTTP status codes are named by the protocol, not by us.
                     and not t.id.startswith("HTTP_")]
            if not any(word in name for name in names for word in suspicious):
                continue
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                offenders.append(f"{module.name}:{node.lineno} {names}")
    assert offenders == [], f"tier limits must live in tiers.json: {offenders}"


def test_a_tier_table_in_another_timezone_is_refused():
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["timezone"] = "Europe/London"
    with pytest.raises(access_config.PolicyError, match="reset boundary"):
        access_config.policy_from_json(json.dumps(table))


def test_a_tier_table_without_a_signup_url_is_refused():
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["urls"] = {}
    with pytest.raises(access_config.PolicyError, match="get_a_key"):
        access_config.policy_from_json(json.dumps(table))


def test_the_policy_is_read_from_the_environment_first(policy):
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["tiers"]["free"]["daily_limit"] = 4

    class Env:
        TIER_POLICY = json.dumps(table)

    assert access_config.load_policy(Env()).tier("free").daily_limit == 4
    assert policy.tier("free").daily_limit == 10


def test_a_missing_policy_is_an_error_not_a_default(tmp_path):
    with pytest.raises(access_config.PolicyError, match="no tier table"):
        access_config.load_policy(None, path=tmp_path / "absent.json")


# ── an unkeyed request ───────────────────────────────────────────────────────

def test_an_unkeyed_request_is_refused_and_told_where_to_get_a_key(policy):
    outcome = run(_serve(None, ExplodingKV(), policy, live=_never_live))
    assert outcome.status == access.HTTP_UNAUTHORIZED == 401
    error = outcome.body["error"]
    assert error["code"] == "missing_api_key"
    assert "https://modelspec.dev/pricing" in error["message"]
    assert error["how_to_get_a_key"] == "https://modelspec.dev/pricing"
    assert "test_" in error["sandbox"]
    assert outcome.headers["www-authenticate"].startswith("Bearer")


def test_an_unknown_key_is_refused(policy):
    outcome = run(_serve("live_nobody", MemoryKV(), policy, live=_never_live))
    assert outcome.status == 401
    assert outcome.body["error"]["code"] == "invalid_api_key"


def test_a_revoked_key_is_refused_and_told_why(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_gone"))
    assert run(keys.revoke(kv, "live_gone")) is True
    outcome = run(_serve("live_gone", kv, policy, live=_never_live))
    assert outcome.status == 403
    assert outcome.body["error"]["code"] == "key_revoked"


def test_a_key_naming_an_unconfigured_tier_is_our_fault_not_the_callers(policy):
    kv = MemoryKV()
    record = keys.KeyRecord(key_id=keys.key_id("live_ghost"), tier="platinum",
                            owner="x", created_at="2026-01-01T00:00:00Z")
    run(kv.put(keys.storage_name("live_ghost"), json.dumps(record.to_json())))
    outcome = run(_serve("live_ghost", kv, policy, live=_never_live))
    assert outcome.status == 500
    assert outcome.body["error"]["code"] == "tier_not_configured"


def test_a_key_is_read_from_either_header_and_never_from_the_url():
    headers = {"authorization": "Bearer live_abc"}
    assert keys.extract(lambda name: headers.get(name)) == "live_abc"
    headers = {"x-api-key": "live_def"}
    assert keys.extract(lambda name: headers.get(name)) == "live_def"
    assert keys.extract(lambda name: None) is None
    # A Basic credential is not an API key, and must not be read as one.
    headers = {"authorization": "Basic bGl2ZV9hYmM="}
    assert keys.extract(lambda name: headers.get(name)) is None


# ── the free tier's day ──────────────────────────────────────────────────────

def test_a_free_key_is_served_on_call_ten_and_refused_on_call_eleven(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_free"))
    # Spaced a minute apart so this measures the day, not the burst window.
    statuses = [run(_serve("live_free", kv, policy,
                           now=T0 + timedelta(seconds=61 * i))).status
                for i in range(11)]
    assert statuses[:10] == [200] * 10
    assert statuses[10] == 429


def test_the_daily_window_resets_at_the_next_utc_midnight(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_day"))
    for i in range(10):
        run(_serve("live_day", kv, policy, now=T0 + timedelta(seconds=61 * i)))

    before_midnight = datetime(2026, 9, 17, 23, 59, 59, tzinfo=UTC)
    assert run(_serve("live_day", kv, policy, now=before_midnight)).status == 429

    midnight = datetime(2026, 9, 18, 0, 0, 0, tzinfo=UTC)
    served = run(_serve("live_day", kv, policy, now=midnight))
    assert served.status == 200
    assert served.meter.window(limits.DAY).used == 1


def test_the_refusal_names_the_exact_reset_moment(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_reset"))
    for i in range(10):
        run(_serve("live_reset", kv, policy, now=T0 + timedelta(seconds=61 * i)))
    outcome = run(_serve("live_reset", kv, policy, now=T0 + timedelta(seconds=61 * 11)))
    error = outcome.body["error"]
    assert error["code"] == "rate_limited"
    assert error["scope"] == "daily"
    assert error["limit"] == 10
    assert error["used"] == 10
    assert error["remaining"] == 0
    assert error["window_seconds"] == 86_400
    assert error["window"] == "1 day, fixed, resetting at 00:00:00 UTC"
    assert error["resets_at"] == "2026-09-18T00:00:00Z"
    assert error["retry_after_seconds"] > 0
    assert [w["scope"] for w in error["windows"]] == ["daily", "burst"]
    assert outcome.headers["retry-after"] == str(error["retry_after_seconds"])
    assert outcome.headers["ratelimit-limit"] == "10"


def test_a_refused_call_does_not_spend_quota(policy):
    """Being told no must not cost a request, or a looping client never recovers."""
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_norefund"))
    for i in range(6):
        run(_serve("live_norefund", kv, policy, now=T0 + timedelta(seconds=i)))
    counter = limits.counter_name(keys.key_id("live_norefund"), limits.DAY, "2026-09-17")
    assert kv.data[counter] == "5"


# ── the burst window ─────────────────────────────────────────────────────────

def test_the_sixth_call_inside_a_minute_is_refused(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_burst"))
    statuses = [run(_serve("live_burst", kv, policy,
                           now=T0 + timedelta(seconds=i))).status for i in range(6)]
    assert statuses == [200] * 5 + [429]

    outcome = run(_serve("live_burst", kv, policy, now=T0 + timedelta(seconds=5)))
    error = outcome.body["error"]
    assert error["scope"] == "burst"
    assert error["limit"] == 5
    assert error["window_seconds"] == 60
    assert error["resets_at"] == "2026-09-17T14:31:00Z"

    # The next wall-clock minute is a new window.
    assert run(_serve("live_burst", kv, policy, now=T0 + timedelta(seconds=61))).status == 200


def test_the_windows_are_named_by_the_utc_clock():
    bucket, reset = limits.day_window(T0)
    assert (bucket, reset) == ("2026-09-17", datetime(2026, 9, 18, tzinfo=UTC))
    bucket, reset = limits.minute_window(T0)
    assert (bucket, reset) == ("2026-09-17T14:30", datetime(2026, 9, 17, 14, 31, tzinfo=UTC))
    with pytest.raises(ValueError, match="timezone-aware"):
        limits.day_window(datetime(2026, 9, 17, 14, 30))


# ── the sandbox ──────────────────────────────────────────────────────────────

def test_a_sandbox_key_answers_without_touching_the_key_store_or_the_data_path(policy):
    """The test that fails if the data path is touched.

    `ExplodingKV` raises on every operation and `_never_live` raises when
    called, so a sandbox answer that consulted either could not return at all.
    """
    outcome = run(_serve("test_anything", ExplodingKV(), policy, live=_never_live))
    assert outcome.status == 200
    assert outcome.body["sandbox"] is True
    assert outcome.trace == ("key.sandbox",)
    assert outcome.tier == "sandbox"
    assert outcome.body["result"], "the sandbox must answer with rows"
    assert all(row["provider"] == "ModelSpec Sandbox" for row in outcome.body["result"])
    assert all(row["model_id"].startswith("sandbox/") for row in outcome.body["result"])


def test_the_sandbox_is_unlimited(policy):
    """Fifty calls in the same second, which the free tier refuses after five."""
    statuses = {run(_serve("test_loop", ExplodingKV(), policy, now=T0,
                           live=_never_live)).status for _ in range(50)}
    assert statuses == {200}


def test_sandbox_rows_carry_exactly_the_fields_the_scorer_produces():
    """Not a hand-written fixture: the same function produces both row sets.

    A field added to `pipeline.ranking.score` appears on both sides of this
    assertion at once, which is the property that keeps the sandbox a usable
    integration target.
    """
    real = rank_report(
        [Candidate(model_id="acme/real", display_name="Real", provider="Acme",
                   model_type="llm-chat",
                   benchmark_scores={"mmlu_pro": 70.0, "gpqa_diamond": 50.0,
                                     "arena_elo_overall": 1300.0, "ifeval": 80.0,
                                     "math_500": 70.0, "humaneval": 80.0,
                                     "mt_bench": 8.0, "swe_bench_verified": 50.0,
                                     "gdpval_aa": 40.0},
                   context_window=128_000, cost_input=1.0)],
        "general", limit=5)
    _, body = sandbox.rank_response(sandbox.request_from_payload({"use_case": "general"}),
                                    envelope=dict(ENVELOPE))
    assert real["ranked"], "the control candidate must itself be rankable"
    assert {k for k in body["result"][0]} == {k for k in real["ranked"][0]}


def test_the_sandbox_answers_every_profile_the_live_endpoint_offers():
    from api.ranking.engine import USE_CASE_PROFILES
    for use_case in USE_CASE_PROFILES:
        status, body = sandbox.rank_response(
            sandbox.request_from_payload({"use_case": use_case}), envelope=dict(ENVELOPE))
        assert status == 200
        assert body["profile"] == use_case
        assert body["ranked_count"] + body["unranked_count"] == body["candidates_considered"]


def test_the_sandbox_is_deterministic():
    first = sandbox.rank_response(sandbox.request_from_payload({}), envelope=dict(ENVELOPE))
    second = sandbox.rank_response(sandbox.request_from_payload({}), envelope=dict(ENVELOPE))
    assert json.dumps(first, default=str) == json.dumps(second, default=str)


def test_the_sandbox_body_has_the_live_body_shape():
    """Checked against the live handler itself, once MODEL-68 has landed."""
    service_path = WORKER_SRC / "rank_service.py"
    if not service_path.exists():
        pytest.skip("the live rank service (MODEL-68) is not on this branch yet")

    import importlib.util
    spec = importlib.util.spec_from_file_location("rank_service_for_shape", service_path)
    assert spec and spec.loader
    service = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("rank_service_for_shape", service)
    spec.loader.exec_module(service)

    export = {"build": {"commit": "abc", "built_at": "2026-09-17", "export_schema_version": "2.0"},
              "candidates": []}
    live_status, live_body = service.rank({"use_case": "general"}, export, None,
                                          "testsha", "https://modelspec.dev")
    _, sandbox_body = sandbox.rank_response(
        sandbox.request_from_payload({"use_case": "general"}),
        envelope=service._envelope({}, "testsha", "https://modelspec.dev"))
    assert set(sandbox_body) - {"sandbox"} == set(live_body) - {"error"}
    assert live_status in (200, service.HTTP_NO_MATCH)


# ── the exempt key is not a branch ───────────────────────────────────────────

def test_an_exempt_key_takes_the_same_steps_as_a_paying_key(policy):
    kv = MemoryKV()
    run(_issue(kv, "paid", policy, "live_paid"))
    run(_issue(kv, "dpf", policy, "live_exempt"))

    paid = run(_serve("live_paid", kv, policy))
    exempt = run(_serve("live_exempt", kv, policy))

    assert paid.trace == exempt.trace == ("key.lookup", "limits.consume", "serve.live")
    assert paid.status == exempt.status == 200
    # Both are metered. Exemption is a null limit, not a skipped meter: usage
    # of an exempt key is still worth knowing.
    assert paid.meter.window(limits.DAY).used == 1
    assert exempt.meter.window(limits.DAY).used == 1
    assert exempt.meter.window(limits.DAY).limit is None
    assert exempt.meter.window(limits.DAY).remaining is None


def test_an_exempt_key_is_served_past_every_limit_a_paid_key_has(policy):
    kv = MemoryKV()
    run(_issue(kv, "dpf", policy, "live_exempt2"))
    paid_burst = policy.tier("paid").burst_limit or 0
    statuses = {run(_serve("live_exempt2", kv, policy, now=T0)).status
                for _ in range(paid_burst + 5)}
    assert statuses == {200}


def test_no_module_branches_on_the_exempt_tier_by_name():
    """The tier is data. If its name appears in code, a branch has grown.

    Docstrings and comments are stripped first: this package is allowed to
    explain itself, it is not allowed to test for a tier.
    """
    offenders: list[str] = []
    for module in ACCESS_MODULES:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    docstrings.add(id(body[0].value))
        for node in ast.walk(tree):
            text = None
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if id(node) in docstrings:
                    continue
                text = node.value
            elif isinstance(node, ast.Name):
                text = node.id
            elif isinstance(node, ast.Attribute):
                text = node.attr
            if text and "dpf" in text.lower():
                offenders.append(f"{module.name}:{node.lineno} {text!r}")
    assert offenders == [], f"the exempt tier must stay data: {offenders}"


# ── keys are never written down ──────────────────────────────────────────────

def test_no_key_value_is_ever_logged_returned_or_stored(policy, caplog, capsys):
    secret = "live_S3CRET-do-not-log-me"
    kv = MemoryKV()
    run(_issue(kv, "free", policy, secret))
    recorder = Recorder()

    outcomes = [
        run(_serve(secret, kv, policy, now=T0, log=recorder)),
        run(_serve(None, kv, policy, now=T0, log=recorder, live=_never_live)),
        run(_serve("live_unknown-" + secret, kv, policy, now=T0, log=recorder,
                   live=_never_live)),
        run(_serve("test_" + secret, ExplodingKV(), policy, now=T0, log=recorder,
                   live=_never_live)),
    ]
    # And the refusal path, which formats the most text of any of them.
    for i in range(1, 12):
        outcomes.append(run(_serve(secret, kv, policy, now=T0 + timedelta(seconds=61 * i),
                                   log=recorder)))

    haystack = "\n".join([
        recorder.text(),
        caplog.text,
        capsys.readouterr().out,
        json.dumps([o.body for o in outcomes], default=str),
        json.dumps([o.headers for o in outcomes], default=str),
        json.dumps([repr(o) for o in outcomes]),
        json.dumps(kv.data, default=str),
        json.dumps(list(kv.data), default=str),
        json.dumps([name for _, name in kv.calls]),
    ])
    assert secret not in haystack
    assert "S3CRET" not in haystack
    # What is emitted instead identifies the key without being one.
    assert keys.key_id(secret) in recorder.text()
    assert len(keys.key_id(secret)) == 12


def test_a_stored_record_holds_a_fingerprint_and_not_a_key(policy):
    kv = MemoryKV()
    secret, record = run(keys.issue(kv, tier="free", owner="a@b.c", now=T0, policy=policy))
    assert secret.startswith("live_")
    assert secret not in json.dumps(kv.data)
    assert secret not in "".join(kv.data)
    assert record.key_id == keys.key_id(secret)
    assert secret not in repr(record)
    assert not any(secret in str(value) for value in record.to_json().values())
    assert run(keys.lookup(kv, secret)) == record
    assert run(keys.lookup(kv, "live_other")) is None


def test_issuing_a_key_for_an_unconfigured_tier_fails_at_issue_time(policy):
    with pytest.raises(access_config.PolicyError):
        run(keys.issue(MemoryKV(), tier="platinum", owner="a@b.c", now=T0, policy=policy))


def test_two_keys_meter_separately(policy):
    kv = MemoryKV()
    run(_issue(kv, "free", policy, "live_one"))
    run(_issue(kv, "free", policy, "live_two"))
    for i in range(5):
        assert run(_serve("live_one", kv, policy, now=T0 + timedelta(seconds=i))).status == 200
    assert run(_serve("live_one", kv, policy, now=T0 + timedelta(seconds=5))).status == 429
    assert run(_serve("live_two", kv, policy, now=T0 + timedelta(seconds=5))).status == 200
