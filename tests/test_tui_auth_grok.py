"""Grok ACP status examples captured from the pinned 1.0.46 image."""

import copy
import json
import subprocess

import pytest

from qa import tui_auth as auth


# The login volume and an anonymous HOME returned this same native status.
# Grok's model catalog is public even when this sign-in method is unselected.
GROK_SIGN_IN_REQUIRED = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": 1,
        "authMethods": [
            {"id": "grok.com", "name": "Grok", "description": "Sign in with Grok"}
        ],
        "_meta": {"agentVersion": "1.0.46", "defaultAuthMethodId": None},
    },
}


@pytest.fixture
def config():
    return {
        "clis": {"grok": {"executable": "grok"}},
        "timeout_seconds": 10,
        "mcp_token_env": "MODELSPEC_API_KEY",
    }


def test_grok_native_sign_in_required_is_not_an_unknown_format(config, tmp_path, monkeypatch):
    monkeypatch.setattr(auth, "_rpc", lambda *args: [copy.deepcopy(GROK_SIGN_IN_REQUIRED)])
    monkeypatch.setattr(
        auth,
        "run_cli",
        lambda *args: subprocess.CompletedProcess([], 0, "grok-4.5\ngrok-4.6\n", ""),
    )
    result = auth.authentication_status("grok", config, tmp_path, {})
    assert result == {
        "logged_in": False,
        "auth_method": "none",
        "verified": True,
        "checks": [{"command": "Grok ACP initialize (auth method)", "exit_code": 0}],
        "reason": None,
    }


@pytest.mark.parametrize("method", ["cached_token", "grok.com"])
def test_grok_explicit_subscription_method_still_requires_model_check(
    method, config, tmp_path, monkeypatch
):
    reply = copy.deepcopy(GROK_SIGN_IN_REQUIRED)
    reply["result"]["_meta"]["defaultAuthMethodId"] = method
    monkeypatch.setattr(auth, "_rpc", lambda *args: [reply])
    monkeypatch.setattr(
        auth,
        "run_cli",
        lambda *args: subprocess.CompletedProcess([], 0, "grok-4.5\ngrok-4.6\n", ""),
    )
    result = auth.authentication_status("grok", config, tmp_path, {})
    assert result["logged_in"] is True
    assert result["auth_method"] == method
    assert result["verified"] is True
    assert result["checks"][-1] == {"command": "models", "exit_code": 0}


@pytest.mark.parametrize("malformation", ["missing_default", "unknown_method", "api_method", "ambiguous_methods"])
def test_grok_unrecognized_or_api_status_never_certifies_subscription(
    malformation, config, tmp_path, monkeypatch
):
    reply = copy.deepcopy(GROK_SIGN_IN_REQUIRED)
    metadata = reply["result"]["_meta"]
    if malformation == "missing_default":
        del metadata["defaultAuthMethodId"]
    elif malformation == "unknown_method":
        metadata["defaultAuthMethodId"] = "unknown"
    elif malformation == "api_method":
        metadata["defaultAuthMethodId"] = "api_key"
    else:
        reply["result"]["authMethods"].append({"id": "api_key"})
    metadata["accountId"] = "redacted-account"
    monkeypatch.setattr(auth, "_rpc", lambda *args: [reply])
    monkeypatch.setattr(
        auth,
        "run_cli",
        lambda *args: subprocess.CompletedProcess([], 0, "grok-4.5\n", ""),
    )
    result = auth.authentication_status("grok", config, tmp_path, {})
    assert result["verified"] is False
    assert result["logged_in"] is not True
    assert "redacted-account" not in json.dumps(result)
