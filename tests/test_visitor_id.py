"""MODEL-241: the keyed, rotating visitor id, and what reaches the meter."""

from __future__ import annotations

import hashlib
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))

import visitor  # noqa: E402

KEY_A = "fixture-key-a-0123456789abcdef"
KEY_B = "fixture-key-b-0123456789abcdef"
IP = "203.0.113.7"
DAY = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def test_the_id_is_opaque_and_holds_neither_the_ip_nor_its_bare_hash():
    out = visitor.visitor_id(IP, KEY_A, DAY)
    assert out.startswith("visitor:")
    assert IP not in out
    assert hashlib.sha256(IP.encode()).hexdigest() not in out
    assert hashlib.sha256(f"{IP}|2026-09-30".encode()).hexdigest() not in out


def test_the_id_is_stable_within_a_day_and_changes_across_days_keys_and_addresses():
    base = visitor.visitor_id(IP, KEY_A, DAY)
    assert base == visitor.visitor_id(IP, KEY_A, DAY + timedelta(hours=5))
    assert base != visitor.visitor_id(IP, KEY_A, DAY + timedelta(days=1))
    assert base != visitor.visitor_id(IP, KEY_B, DAY)
    assert base != visitor.visitor_id("203.0.113.8", KEY_A, DAY)


def test_no_key_or_no_address_means_no_id_never_a_bare_hash():
    assert visitor.visitor_id(IP, None, DAY) is None
    assert visitor.visitor_id(IP, "", DAY) is None
    assert visitor.visitor_id(IP, "short", DAY) is None
    assert visitor.visitor_id(None, KEY_A, DAY) is None
    assert visitor.visitor_id("  ", KEY_A, DAY) is None


def test_the_request_helper_reads_the_secret_from_the_environment():
    request = SimpleNamespace(headers={"CF-Connecting-IP": IP})
    env = SimpleNamespace(VISITOR_HMAC_KEY=KEY_A)
    assert visitor.visitor_id_for(request, env, DAY) == visitor.visitor_id(IP, KEY_A, DAY)
    assert visitor.visitor_id_for(request, SimpleNamespace(), DAY) is None


def test_only_the_keyed_id_reaches_the_kv_meter():
    import asyncio

    import access_config
    import access_kv
    import access_limits

    kv = access_kv.MemoryKV()
    ident = visitor.visitor_id(IP, KEY_A, DAY)
    limits = access_config.TierLimits(name="anonymous", daily_limit=10, burst_limit=5,
                                     live_data=True, paid=False, description="fixture")
    asyncio.run(access_limits.consume(kv, ident, limits, DAY))
    written = [name for op, name in kv.calls if op == "put"]
    assert written
    forbidden = (IP, hashlib.sha256(IP.encode()).hexdigest(),
                 hashlib.sha256(f"visitor:{hashlib.sha256(IP.encode()).hexdigest()}".encode()).hexdigest())
    blob = " ".join(written) + " " + " ".join(kv.data.values())
    for bad in forbidden:
        assert bad not in blob
    assert any(ident.removeprefix("visitor:") in name or ident in name for name in written)
