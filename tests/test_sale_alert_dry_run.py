"""The local sale-alert command previews safely and sends at most one notice."""

from __future__ import annotations

import asyncio
import json
import os
import runpy
import subprocess
import sys
from http import client as http_client
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sale_alert_dry_run.py"
TOKEN = "test-app-secret+&=unpublished"
USER = "test-user-secret+&=unpublished"
TX = "0x123456" + "ab" * 29
MESSAGES = {
    "stripe": "$5.00 · dry-run 250-credit pack · card",
    "x402": "$0.02 · dry-run paid result · x402 · tx 0x1234…",
}


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("PUSHOVER_APP_TOKEN", TOKEN)
    monkeypatch.setenv("PUSHOVER_USER_KEY", USER)
    monkeypatch.delenv("SALE_ALERT_TTL_SECONDS", raising=False)


@pytest.fixture(autouse=True)
def http(monkeypatch):
    log = SimpleNamespace(
        connections=[], calls=[], closed=0, status=200,
        body=b'{"status": 1, "request": "synthetic"}', error=None,
    )

    class Connection:
        def __init__(self, host, *, timeout):
            log.connections.append((host, timeout))

        def request(self, method, path, body, headers):
            log.calls.append((method, path, body, headers))
            if log.error is not None:
                raise log.error

        def getresponse(self):
            return SimpleNamespace(status=log.status, read=lambda: log.body)

        def close(self):
            log.closed += 1

    monkeypatch.setattr(http_client, "HTTPSConnection", Connection)
    return log


def invoke(monkeypatch, *args):
    assert SCRIPT.is_file(), "scripts/sale_alert_dry_run.py is missing"
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), *args])
    with pytest.raises(SystemExit) as stopped:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    return stopped.value.code


def preview(capsys):
    captured = capsys.readouterr()
    for secret in (TOKEN, USER):
        assert secret not in captured.out + captured.err
    return json.loads(captured.out), captured.err


def test_preview_both_sales_redacts_secrets_without_http(monkeypatch, http, capsys):
    assert invoke(monkeypatch) == 0
    payloads, err = preview(capsys)
    assert err == ""
    assert payloads == {
        channel: {
            "token": "[REDACTED]", "user": "[REDACTED]",
            "title": "ModelSpec sale", "message": message,
            "priority": "0", "ttl": "900",
        }
        for channel, message in MESSAGES.items()
    }
    assert http.connections == []
    assert http.calls == []


@pytest.mark.parametrize("send", [False, True])
@pytest.mark.parametrize("name", ["PUSHOVER_APP_TOKEN", "PUSHOVER_USER_KEY"])
@pytest.mark.parametrize("value", [None, "", " \t "])
def test_missing_credentials_refuse_before_http(monkeypatch, http, capsys, send, name, value):
    if value is None:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, value)
    assert invoke(monkeypatch, *(["--send"] if send else [])) == 2
    captured = capsys.readouterr()
    assert name in captured.err
    assert captured.out == ""
    assert TOKEN not in captured.err
    assert USER not in captured.err
    assert http.connections == []


@pytest.mark.parametrize("channel", ["stripe", "x402"])
def test_send_posts_one_selected_sale(monkeypatch, http, capsys, channel):
    args = ["--send"] if channel == "stripe" else ["--send", "--channel", channel]
    assert invoke(monkeypatch, *args) == 0
    payloads, err = preview(capsys)
    assert "accepted one" in err
    assert channel in err
    assert "900" in err
    assert http.connections == [("api.pushover.net", 5)]
    assert len(http.calls) == 1
    method, path, body, headers = http.calls[0]
    assert (method, path) == ("POST", "/1/messages.json")
    assert headers == {"Content-Type": "application/x-www-form-urlencoded"}
    fields = {key: values[0] for key, values in parse_qs(body.decode()).items()}
    assert fields == {**payloads[channel], "token": TOKEN, "user": USER}
    assert fields["message"] == MESSAGES[channel]
    assert http.closed == 1


@pytest.mark.parametrize("raw,expected", [
    ("", "900"), ("  ", "900"), ("30", "30"), ("0", "1"),
    ("-10", "1"), ("86400", "86400"), ("86401", "86400"),
])
def test_send_uses_configured_ttl_with_worker_bounds(monkeypatch, http, capsys, raw, expected):
    monkeypatch.setenv("SALE_ALERT_TTL_SECONDS", raw)
    assert invoke(monkeypatch, "--send") == 0
    payloads, _ = preview(capsys)
    assert {form["ttl"] for form in payloads.values()} == {expected}
    assert len(http.calls) == 1
    assert parse_qs(http.calls[0][2].decode())["ttl"] == [expected]


def test_invalid_ttl_refuses_without_echoing_value(monkeypatch, http, capsys):
    monkeypatch.setenv("SALE_ALERT_TTL_SECONDS", TOKEN)
    assert invoke(monkeypatch, "--send") == 2
    captured = capsys.readouterr()
    assert "SALE_ALERT_TTL_SECONDS" in captured.err
    assert TOKEN not in captured.out + captured.err
    assert USER not in captured.out + captured.err
    assert http.connections == []


@pytest.mark.parametrize("failure", ["transport", "http", "redirect", "rejected", "invalid_json"])
def test_failed_send_exits_without_retry_or_secret_leak(monkeypatch, http, capsys, failure):
    http.body = json.dumps({"status": 0, "errors": [TOKEN, USER]}).encode()
    if failure == "transport":
        http.error = OSError(f"request failed with {TOKEN} and {USER}")
    elif failure == "http":
        http.status = 500
    elif failure == "redirect":
        http.status = 302
    elif failure == "invalid_json":
        http.body = f"not JSON {TOKEN} {USER}".encode()
    assert invoke(monkeypatch, "--send") == 1
    _, err = preview(capsys)
    assert "failed" in err
    assert "accepted" not in err
    assert len(http.calls) == 1
    assert len(http.connections) == 1
    assert http.closed == 1


def test_preview_matches_actual_worker_requests(monkeypatch, capsys):
    monkeypatch.setenv("SALE_ALERT_TTL_SECONDS", "30")
    assert invoke(monkeypatch) == 0
    payloads, _ = preview(capsys)
    monkeypatch.syspath_prepend(str(ROOT / "api" / "worker" / "src"))
    import sale_alerts

    requests = []
    pending = []

    async def fetch(url, body):
        assert url == "https://api.pushover.net/1/messages.json"
        requests.append({key: values[0] for key, values in parse_qs(body).items()})
        return SimpleNamespace(status=200)

    monkeypatch.setattr(sale_alerts, "_fetch", fetch)
    monkeypatch.setattr(sale_alerts, "_seen", set())
    env = SimpleNamespace(
        SALE_ALERTS_ENABLED="1", PUSHOVER_APP_TOKEN=TOKEN,
        PUSHOVER_USER_KEY=USER, SALE_ALERT_TTL_SECONDS="30",
    )
    ctx = SimpleNamespace(waitUntil=pending.append)

    async def deliver():
        sale_alerts.notify_sale(env, ctx, channel="card", product="dry-run 250-credit pack",
                                amount_usd="5.00", ref="evt_dry_run_stripe")
        sale_alerts.notify_sale(env, ctx, channel="x402", product="dry-run paid result",
                                amount_usd="0.02", ref=TX)
        await asyncio.gather(*pending)

    asyncio.run(deliver())
    assert requests == [
        {**payloads[channel], "token": TOKEN, "user": USER}
        for channel in ("stripe", "x402")
    ]


def test_direct_command_works_without_pythonpath():
    assert SCRIPT.is_file(), "scripts/sale_alert_dry_run.py is missing"
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, env=env,
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert set(json.loads(result.stdout)) == {"stripe", "x402"}
    assert TOKEN not in result.stdout + result.stderr
    assert USER not in result.stdout + result.stderr
