"""MODEL-333. The post-flip probe passes on the expected 402 and fails on a wrong receiver."""

from __future__ import annotations

import base64
import importlib.util
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
PAY_TO = "0x" + "ab" * 20


def _probe():
    spec = importlib.util.spec_from_file_location(
        "x402_mainnet_probe", ROOT / "scripts" / "x402_mainnet_probe.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _transport(pay_to: str, swap: bool = False):
    packs = [(250, 5), (1300, 25), (2750, 50), (6000, 100)]
    if swap:
        packs[0], packs[-1] = (packs[-1][0], packs[0][1]), (packs[0][0], packs[-1][1])
    accepts = [{"scheme": "exact", "network": "eip155:8453",
                "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
                "payTo": pay_to, "amount": str(usd * 1_000_000),
                "extra": {"name": "USDC", "version": "2", "credits": credits}}
               for credits, usd in packs]
    body = {"x402Version": 2,
            "error": {"code": "payment_required",
                      "packs": [{"credits": credits,
                                 "price": {"amount": str(usd * 1_000_000)}}
                                for credits, usd in packs]},
            "accepts": accepts}
    header = base64.b64encode(json.dumps(
        {"x402Version": 2, "accepts": accepts}).encode()).decode()

    def handle(request: httpx.Request) -> httpx.Response:
        keyed = "authorization" in request.headers
        if request.url.path == "/v1/health":
            return httpx.Response(200, json={"service_commit": "abc123"})
        if request.url.path == "/v1/credits":
            return httpx.Response(200, json={"available": 0})
        if not keyed:
            return httpx.Response(401, json={"error": {"code": "missing_api_key"}})
        return httpx.Response(402, json=body, headers={"PAYMENT-REQUIRED": header})

    return httpx.MockTransport(handle)


def _run(monkeypatch, pay_to: str, swap: bool = False) -> None:
    probe = _probe()
    real = httpx.Client
    monkeypatch.setattr(probe.httpx, "Client",
                        lambda **kw: real(transport=_transport(pay_to, swap), **kw))
    monkeypatch.setenv("MODELSPEC_API_KEY", "live_probe")
    monkeypatch.setattr(sys, "argv", ["probe", "--expect-commit", "abc123",
                                      "--expect-pay-to", PAY_TO])
    probe.main()


def test_probe_passes_on_the_expected_mainnet_offer(monkeypatch, capsys) -> None:
    _run(monkeypatch, PAY_TO)
    out = capsys.readouterr().out
    assert "FAIL" not in out
    assert out.strip().endswith("x402 mainnet probe passed")


def test_probe_fails_on_another_receiver(monkeypatch, capsys) -> None:
    with pytest.raises(SystemExit) as stop:
        _run(monkeypatch, "0x" + "11" * 20)
    assert stop.value.code == 1
    assert "FAIL payTo 0x1111111111111111111111111111111111111111" in capsys.readouterr().out


def test_probe_fails_when_a_price_buys_the_wrong_pack(monkeypatch, capsys) -> None:
    with pytest.raises(SystemExit) as stop:
        _run(monkeypatch, PAY_TO, swap=True)
    assert stop.value.code == 1
    assert "FAIL accepts amount->credits" in capsys.readouterr().out
