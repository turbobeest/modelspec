"""MODEL-441: deploy jobs point the Wrangler configs at their environment's account."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from pipeline.worker_flags import parse_jsonc

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "cloudflare_target", ROOT / ".github/scripts/cloudflare_target.py")
cloudflare_target = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cloudflare_target)

RANK = (ROOT / "api/worker/wrangler.jsonc").read_text(encoding="utf-8")
MCP = (ROOT / "mcp/wrangler.jsonc").read_text(encoding="utf-8")
NEW_ACCOUNT = "0123456789abcdef0123456789abcdef"
NEW_ACCESS = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
NEW_DETERMINATIONS = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
NEW_ENV = {"CF_ENVIRONMENT": "cloudflare-modelspec", "CLOUDFLARE_ACCOUNT_ID": NEW_ACCOUNT,
           "CF_TARGET_ACCOUNT_ID": NEW_ACCOUNT}


def test_no_environment_leaves_the_committed_config_byte_for_byte():
    assert cloudflare_target.retarget(RANK, {}) == (RANK, [])
    assert cloudflare_target.retarget(MCP, {"CF_WORKERS_DEV": ""}) == (MCP, [])


def test_the_rank_worker_moves_account_namespaces_and_workers_dev_together():
    text, changes = cloudflare_target.retarget(RANK, {
        **NEW_ENV,
        "CF_KV_ACCESS": NEW_ACCESS,
        "CF_KV_DETERMINATIONS": NEW_DETERMINATIONS,
        "CF_WORKERS_DEV": "true",
    })
    config = parse_jsonc(text)

    assert changes == ["account_id", "DETERMINATIONS namespace", "ACCESS namespace",
                       "workers_dev=true"]
    assert config["account_id"] == NEW_ACCOUNT
    assert config["kv_namespaces"] == [
        {"binding": "DETERMINATIONS", "id": NEW_DETERMINATIONS},
        {"binding": "ACCESS", "id": NEW_ACCESS},
    ]
    assert config["workers_dev"] is True
    assert config["env"] == parse_jsonc(RANK)["env"]
    assert config["routes"] == parse_jsonc(RANK)["routes"]


def test_the_mcp_worker_takes_the_account_and_keeps_its_service_binding():
    text, changes = cloudflare_target.retarget(MCP, {"CLOUDFLARE_ACCOUNT_ID": NEW_ACCOUNT})

    assert changes == ["account_id"]
    assert parse_jsonc(text)["account_id"] == NEW_ACCOUNT
    assert parse_jsonc(text)["services"] == [{"binding": "RANK", "service": "modelspec-rank"}]


@pytest.mark.parametrize("environ, message", [
    ({"CLOUDFLARE_ACCOUNT_ID": "not-an-account"}, "CLOUDFLARE_ACCOUNT_ID is not a 32-hex account id"),
    ({"CF_KV_ACCESS": "ACCESS"}, "CF_KV_ACCESS is not a 32-hex namespace id"),
    ({"CF_WORKERS_DEV": "yes", **NEW_ENV}, "CF_WORKERS_DEV must be true or false"),
    ({"CF_ROUTES": "on", **NEW_ENV}, "CF_ROUTES must be off or unset"),
    ({"CF_LEDGER_STANDBY": "yes", **NEW_ENV}, "CF_LEDGER_STANDBY must be true or unset"),
    ({"CF_ROUTES": "off"}, "CF_ROUTES is set for the production environment"),
    ({"CF_LEDGER_STANDBY": "true", "CF_ENVIRONMENT": "production"},
     "CF_LEDGER_STANDBY is set for the production environment"),
])
def test_malformed_values_stop_the_deploy_without_echoing_them(environ, message):
    with pytest.raises(ValueError) as caught:
        cloudflare_target.retarget(RANK, environ)
    assert str(caught.value) == message


def test_the_main_entry_rewrites_the_file_in_place(tmp_path, monkeypatch, capsys):
    path = tmp_path / "wrangler.jsonc"
    path.write_text(RANK, encoding="utf-8")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", NEW_ACCOUNT)

    assert cloudflare_target.main(["cloudflare_target.py", str(path)]) == 0
    assert parse_jsonc(path.read_text(encoding="utf-8"))["account_id"] == NEW_ACCOUNT
    assert NEW_ACCOUNT not in capsys.readouterr().out


def test_routes_off_leaves_both_workers_without_routes_and_everything_else_alone():
    for committed in (RANK, MCP):
        text, changes = cloudflare_target.retarget(committed, {"CF_ROUTES": "off", **NEW_ENV})
        config = parse_jsonc(text)
        before = parse_jsonc(committed)

        assert changes == ["account_id", "routes=off"]
        assert config["routes"] == []
        assert {k: v for k, v in config.items() if k not in ("routes", "account_id")} == \
            {k: v for k, v in before.items() if k not in ("routes", "account_id")}


def test_ledger_standby_adds_one_top_level_var_and_leaves_staging_alone():
    text, changes = cloudflare_target.retarget(RANK, {"CF_LEDGER_STANDBY": "true", **NEW_ENV})
    config, before = parse_jsonc(text), parse_jsonc(RANK)

    assert changes == ["account_id", "LEDGER_STANDBY"]
    assert config["vars"] == {"LEDGER_STANDBY": "true", **before["vars"]}
    assert config["env"] == before["env"]


@pytest.mark.parametrize("committed", [RANK, MCP])
@pytest.mark.parametrize("environ, message", [
    ({"CF_ENVIRONMENT": "cloudflare-modelspec", "CF_ROUTES": "off"},
     "CF_ROUTES needs a CLOUDFLARE_ACCOUNT_ID other than the serving account"),
    ({"CF_ENVIRONMENT": "cloudflare-modelspec", "CF_ROUTES": "off",
      "CLOUDFLARE_ACCOUNT_ID": parse_jsonc(RANK)["account_id"],
      "CF_TARGET_ACCOUNT_ID": parse_jsonc(RANK)["account_id"]},
     "CF_ROUTES needs a CLOUDFLARE_ACCOUNT_ID other than the serving account"),
    ({"CF_ENVIRONMENT": "cloudflare-modelspec", "CF_WORKERS_DEV": "true",
      "CLOUDFLARE_ACCOUNT_ID": NEW_ACCOUNT},
     "CF_WORKERS_DEV needs CF_TARGET_ACCOUNT_ID to name the same account"),
])
def test_transition_settings_never_reach_the_serving_account(committed, environ, message):
    with pytest.raises(ValueError) as caught:
        cloudflare_target.retarget(committed, environ)
    assert str(caught.value) == message
