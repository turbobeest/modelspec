"""MODEL-333: exercise the buy CLI with no network or real credentials."""

from __future__ import annotations

import base64
import copy
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import httpx
import pytest

from tests.test_x402 import _eip55

ROOT = Path(__file__).resolve().parents[1]
FLAG = "--i-understand-this-spends-real-usdc"
PAYER_KEY = "0x" + "11" * 32  # Public test vector, used only with mocks.
API_KEY = "live_test_only"
RECEIVER = "0x69429dbEEEE7218084AB5B896788f5fCE452419C"
ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
TX = "0x" + "ab" * 32


def offer():
    accepts = [
        {"scheme": "exact", "network": "eip155:8453", "asset": ASSET.lower(),
         "payTo": RECEIVER.lower(), "amount": str(amount), "maxTimeoutSeconds": 60,
         "extra": {"name": "USDC", "version": "2", "credits": credits}}
        for amount, credits in [(5_000_000, 250), (25_000_000, 1300),
                                (50_000_000, 2750), (100_000_000, 6000)]
    ]
    return {"x402Version": 2, "accepts": accepts,
            "error": {"packs": [
                {"credits": row["extra"]["credits"],
                 "price": {"amount": row["amount"], "atomic": int(row["amount"])}}
                for row in accepts]}}


def encoded(value):
    return base64.b64encode(json.dumps(value).encode()).decode()


@pytest.fixture
def run_buy(monkeypatch, capsys):
    monkeypatch.setenv("MODELSPEC_API_KEY", API_KEY)
    monkeypatch.setenv("X402_PAYER_PRIVATE_KEY", PAYER_KEY)
    requests = []
    signed = []
    typed = []
    from_keys = []
    real_client = httpx.Client

    def from_key(key):
        from_keys.append(key)
        return SimpleNamespace(address="0x" + "22" * 20)

    def sign(message, private_key):
        signed.append((message, private_key))
        return SimpleNamespace(signature=bytes.fromhex("cd" * 65))

    def encode(*, full_message):
        typed.append(full_message)
        return "test-typed-message"

    account = ModuleType("eth_account")
    account.Account = SimpleNamespace(from_key=from_key, sign_message=sign)
    messages = ModuleType("eth_account.messages")
    messages.encode_typed_data = encode
    utils = ModuleType("eth_utils")
    utils.to_checksum_address = _eip55
    utils.is_checksum_address = lambda address: (
        re.fullmatch(r"0x[0-9a-fA-F]{40}", address) is not None and _eip55(address) == address)
    monkeypatch.setitem(sys.modules, "eth_account", account)
    monkeypatch.setitem(sys.modules, "eth_account.messages", messages)
    monkeypatch.setitem(sys.modules, "eth_utils", utils)

    def run(args=(), *, body=None, before=0, after=250, discovery_status=402,
            settlement=None, payment_status=400, payment_error=None,
            before_status=200, after_status=200, required_header=None):
        path = ROOT / "scripts" / "x402_mainnet_buy.py"
        assert path.is_file(), "MODEL-333 buy CLI has not been implemented"
        spec = importlib.util.spec_from_file_location("x402_mainnet_buy", path)
        assert spec is not None and spec.loader is not None
        buy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(buy)
        body = copy.deepcopy(offer() if body is None else body)
        settle = {"success": True, "network": "eip155:8453", "transaction": TX}
        if settlement is not None:
            settle = settlement
        balance_calls = 0

        def handle(request):
            nonlocal balance_calls
            requests.append(request)
            assert request.url.host == "api.modelspec.dev"
            assert request.headers["authorization"] == f"Bearer {API_KEY}"
            if request.url.path == "/v1/credits":
                balance_calls += 1
                value, status = ((before, before_status) if balance_calls == 1
                                 else (after, after_status))
                return httpx.Response(status, json={"available": value})
            assert request.url.path == "/v1/decide" and request.method == "POST"
            assert json.loads(request.content) == {"spec_version": 1}
            if "PAYMENT-SIGNATURE" not in request.headers:
                header = required_header or encoded({
                    "x402Version": body.get("x402Version"),
                    "accepts": body.get("accepts")})
                return httpx.Response(discovery_status, json=body,
                                      headers={"PAYMENT-REQUIRED": header})
            if payment_error:
                raise payment_error(request)
            headers = {} if settle == {} else {"PAYMENT-RESPONSE": encoded(settle)}
            return httpx.Response(payment_status,
                                  json={"error": {"code": "invalid_spec",
                                                  "message": PAYER_KEY}}, headers=headers)

        def client(**kwargs):
            assert kwargs.get("follow_redirects", False) is False
            assert kwargs.get("trust_env") is False
            return real_client(transport=httpx.MockTransport(handle), **kwargs)

        monkeypatch.setattr(buy.httpx, "Client", client)
        code = buy.main(list(args))
        output = capsys.readouterr()
        assert PAYER_KEY not in output.out + output.err
        assert API_KEY not in output.out + output.err
        return SimpleNamespace(code=code, out=output.out + output.err,
                               requests=requests, signed=signed, typed=typed,
                               from_keys=from_keys)

    return run


def test_dry_run_prints_exact_live_offer_without_signing(run_buy, monkeypatch):
    monkeypatch.delenv("X402_PAYER_PRIVATE_KEY")
    result = run_buy()
    assert result.code == 0
    assert result.signed == result.from_keys == []
    assert "dry_run" in result.out
    shown = json.loads(result.out.strip().splitlines()[-1])
    assert shown["offer"] == offer()["accepts"][0]
    assert shown["pack_credits"] == 250
    assert all("PAYMENT-SIGNATURE" not in r.headers for r in result.requests)


@pytest.mark.parametrize("field,value,message", [
    ("network", "eip155:84532", "network"),
    ("network", "eip155:1", "network"),
    ("asset", "0x" + "33" * 20, "asset"),
    ("payTo", "0x" + "44" * 20, "payTo"),
    ("payTo", "0x69429DbEEEE7218084AB5B896788f5fCE452419C", "checksum"),
    ("payTo", None, "payTo"),
    ("amount", "5000001", "5000000"),
    ("amount", "25000000", "5000000"),
    ("amount", "4999999", "5000000"),
    ("amount", "-5000000", "5000000"),
    ("amount", "5e6", "5000000"),
    ("amount", None, "5000000"),
    ("scheme", "upto", "scheme"),
])
def test_refuses_unsafe_offer_before_signing(run_buy, field, value, message):
    body = offer()
    body["accepts"] = [body["accepts"][0]]
    body["accepts"][0][field] = value
    result = run_buy([FLAG], body=body)
    assert result.code != 0
    assert message in result.out
    assert result.signed == result.from_keys == []


@pytest.mark.parametrize("credits", [249, 251, 1300, "250", None, True])
def test_refuses_offer_with_wrong_credits(run_buy, credits):
    body = offer()
    body["accepts"][0]["extra"]["credits"] = credits
    result = run_buy([FLAG], body=body)
    assert result.code != 0
    assert "250" in result.out
    assert result.signed == []


@pytest.mark.parametrize("change", ["credits", "amount", "atomic", "missing", "duplicate"])
def test_refuses_inconsistent_pack_listing(run_buy, change):
    body = offer()
    pack = body["error"]["packs"][0]
    if change == "credits":
        pack["credits"] = 6000
    elif change in {"amount", "atomic"}:
        pack["price"][change] = 25_000_000 if change == "atomic" else "25000000"
    elif change == "missing":
        body["error"]["packs"] = []
    else:
        body["error"]["packs"].append(copy.deepcopy(pack))
    result = run_buy([FLAG], body=body)
    assert result.code != 0
    assert result.signed == []


@pytest.mark.parametrize("change", ["version", "accepts", "header"])
def test_refuses_inconsistent_402_protocol(run_buy, change):
    body = offer()
    header = None
    if change == "version":
        body["x402Version"] = 1
    elif change == "accepts":
        body["accepts"] = []
    else:
        header = encoded({"x402Version": 2, "accepts": []})
    result = run_buy([FLAG], body=body, required_header=header)
    assert result.code != 0
    assert result.signed == []


@pytest.mark.parametrize("receiver", [RECEIVER, RECEIVER.lower(), "0x" + RECEIVER[2:].upper()])
def test_buys_one_pack_and_checks_exact_balance_increase(run_buy, receiver):
    body = offer()
    body["accepts"][0]["payTo"] = receiver
    result = run_buy([FLAG], body=body, before=0, after=250)
    assert result.code == 0
    assert len(result.signed) == len(result.from_keys) == 1
    assert result.from_keys == [PAYER_KEY]
    paid = [r for r in result.requests if "PAYMENT-SIGNATURE" in r.headers]
    assert len(paid) == 1
    payload = json.loads(base64.b64decode(paid[0].headers["PAYMENT-SIGNATURE"]))
    assert payload["x402Version"] == 2
    assert payload["accepted"] == body["accepts"][0]
    assert payload["payload"]["authorization"]["value"] == "5000000"
    assert payload["payload"]["authorization"]["to"] == receiver
    assert result.typed[0]["domain"] == {
        "name": "USDC", "version": "2", "chainId": 8453,
        "verifyingContract": ASSET.lower()}
    assert result.typed[0]["primaryType"] == "TransferWithAuthorization"
    assert [r.url.path for r in result.requests] == [
        "/v1/credits", "/v1/decide", "/v1/decide", "/v1/credits"]
    assert '"before": 0' in result.out
    assert TX in result.out and '"after": 250' in result.out


@pytest.mark.parametrize("after", [0, 249, 251, 6000])
def test_credit_delta_mismatch_fails_without_retry(run_buy, after):
    result = run_buy([FLAG], after=after)
    assert result.code != 0
    assert '"before": 0' in result.out and f'"after": {after}' in result.out
    assert TX in result.out and "250" in result.out
    assert len(result.signed) == 1
    assert sum("PAYMENT-SIGNATURE" in r.headers for r in result.requests) == 1


@pytest.mark.parametrize("settlement", [
    {}, {"success": False, "transaction": TX, "network": "eip155:8453"},
    {"success": True, "transaction": TX, "network": "eip155:84532"},
    {"success": True, "network": "eip155:8453"},
    {"success": True, "transaction": "malformed-transaction", "network": "eip155:8453"},
])
def test_uncertain_settlement_reports_balance_and_never_retries(run_buy, settlement):
    result = run_buy([FLAG], settlement=settlement)
    assert result.code != 0
    assert '"after": 250' in result.out
    assert "without retry" in result.out
    assert len(result.signed) == 1
    assert sum("PAYMENT-SIGNATURE" in r.headers for r in result.requests) == 1


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.ConnectError])
def test_payment_transport_error_reports_known_balance_without_retry(run_buy, error):
    result = run_buy([FLAG], payment_error=lambda request: error(PAYER_KEY, request=request))
    assert result.code != 0
    assert '"before": 0' in result.out and '"after": 250' in result.out
    assert "without retry" in result.out
    assert len(result.signed) == 1
    assert sum("PAYMENT-SIGNATURE" in r.headers for r in result.requests) == 1


def test_payment_http_failure_is_not_retried(run_buy):
    result = run_buy([FLAG], payment_status=503)
    assert result.code != 0
    assert TX in result.out and '"after": 250' in result.out
    assert len(result.signed) == 1


@pytest.mark.parametrize("before,status", [(None, 200), (-1, 200), (True, 200),
                                         ("0", 200), (0, 503), (250, 200)])
def test_bad_or_funded_initial_balance_never_signs(run_buy, before, status):
    result = run_buy([FLAG], before=before, before_status=status)
    assert result.code != 0
    assert result.signed == []


def test_after_balance_unavailable_preserves_transaction_and_fails(run_buy):
    result = run_buy([FLAG], after_status=503)
    assert result.code != 0
    assert TX in result.out
    assert '"after": null' in result.out
    assert len(result.signed) == 1


@pytest.mark.parametrize("name", ["MODELSPEC_API_KEY", "X402_PAYER_PRIVATE_KEY"])
def test_missing_environment_credential_never_signs(run_buy, monkeypatch, name):
    monkeypatch.delenv(name)
    result = run_buy([FLAG])
    assert result.code != 0
    assert name in result.out
    assert result.signed == []


@pytest.mark.parametrize("argument", ["--private-key", "--api-key", "--key-file", "--stdin"])
def test_credentials_cannot_be_supplied_through_arguments(run_buy, argument):
    result = run_buy([argument, PAYER_KEY])
    assert result.code != 0
    assert result.signed == []


def test_signing_exception_never_exposes_private_key(run_buy, monkeypatch):
    def broken(_key):
        raise ValueError(PAYER_KEY)

    monkeypatch.setattr(sys.modules["eth_account"].Account, "from_key", broken)
    result = run_buy([FLAG])
    assert result.code != 0
    assert "sign" in result.out
    assert all("PAYMENT-SIGNATURE" not in r.headers for r in result.requests)


def test_discovery_http_failure_never_signs(run_buy):
    result = run_buy([FLAG], discovery_status=400)
    assert result.code != 0
    assert "402" in result.out
    assert result.signed == []


def test_remote_offer_and_receipt_cannot_echo_credentials(run_buy):
    body = offer()
    body["accepts"][0]["description"] = PAYER_KEY + API_KEY
    result = run_buy([FLAG], body=body, settlement={
        "success": True, "transaction": PAYER_KEY, "network": "eip155:8453"})
    assert result.code == 0
    assert "[REDACTED]" in result.out


@pytest.mark.parametrize("secret", ['fake"key', "fake\\key", "fake\nkey"])
def test_malformed_environment_secret_is_redacted_before_json_output(run_buy, monkeypatch, secret):
    monkeypatch.setenv("X402_PAYER_PRIVATE_KEY", secret)
    body = offer()
    body["accepts"][0]["description"] = secret
    result = run_buy(body=body)
    assert result.code == 0
    shown = json.loads(result.out.strip().splitlines()[-1])
    assert shown["offer"]["description"] == "[REDACTED]"
