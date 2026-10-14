"""MODEL-381: the distributed keyed CLI emits Worker-rendered router configs."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import jsonschema
import pytest
import yaml
from typer.testing import CliRunner

from cli.modelspec import cli as cli_module
from cli.modelspec import client
from cli.modelspec.cli import app

ROOT = Path(__file__).resolve().parents[1]
KEY = "live_model381_test_only"
SPEC = {"spec_version": 1, "optimize": {"max": "model.context_window"}}
LITELLM_CONFIG = """# decision_id: dec_router381
# snapshot: snap_router381
model_list:
  - model_name: lab/verified
    litellm_params:
      model: openai/verified-provider-id
    model_info:
      id: modelspec:openai/lab/verified/global/standard
      mode: null
      base_model: null
"""


@pytest.fixture
def worker(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("MODELSPEC_API_KEY", KEY)
    seen = []
    body = {
        "representation": "bounded",
        "bounded_version": "1.4",
        "projects_contract": "2.17",
        "decision_id": "dec_router381",
        "snapshot": "snap_router381",
        "status": "answered",
        "router_config": LITELLM_CONFIG,
    }

    def respond(request):
        seen.append(request)
        if request.url.path == "/v1/vocabulary":
            return httpx.Response(200, json={"templates": [{"id": "coding", "spec": SPEC}]})
        return httpx.Response(200, json=body)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(respond))
    return seen, body


def run(*args, global_json=False):
    return CliRunner().invoke(
        app,
        [*(["--json"] if global_json else []), "decide", "--spec", "-", *args],
        input=json.dumps(SPEC),
    )


def test_keyed_litellm_config_has_verified_ids_and_passes_schema(worker):
    seen, body = worker
    result = run("--emit-router-config", "litellm")
    assert result.exit_code == 0, result.output
    assert result.stdout == LITELLM_CONFIG
    config = yaml.safe_load(result.stdout)
    schema = json.loads(
        (ROOT / "tests/fixtures/router_schemas/litellm-config-yaml.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(config)
    assert config["model_list"][0]["litellm_params"]["model"] == "openai/verified-provider-id"
    assert len(seen) == 1
    assert seen[0].url.path == "/v1/decide"
    assert seen[0].headers["Authorization"] == f"Bearer {KEY}"
    assert json.loads(seen[0].content) == {
        **SPEC,
        "fields": [
            "model_rank",
            "cost_per_task",
            "estimates",
            "p_best",
            "contributions",
            "evidence",
        ],
        "router_config": {"format": "litellm", "include_rest": False, "include_thin": False},
    }
    assert KEY not in result.output


def test_keyed_config_loads_in_litellm_router(worker, monkeypatch):
    result = run("--emit-router-config", "litellm")
    assert result.exit_code == 0, result.output
    config = yaml.safe_load(result.stdout)
    monkeypatch.setenv("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    litellm = pytest.importorskip("litellm")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-no-provider-calls")
    router = litellm.Router(model_list=config["model_list"])
    assert router.model_names == ["lab/verified"]


@pytest.mark.parametrize(
    "fmt,text",
    [
        (
            "litellm",
            "# no verified offering.api_model_id in this snapshot\n"
            "model_list:\n  - model_name: lab/unknown\n    litellm_params:\n"
            "      model: openai/<openai model id for lab/unknown>\n",
        ),
        (
            "openrouter",
            '{"allowed_models":["<openrouter model id for lab/unknown>"],'
            '"description":"no verified offering.router_slug in this snapshot"}\n',
        ),
        (
            "json",
            '{"provider_model_id":null,"provider_model_id_placeholder":'
            '"<openai model id for lab/unknown>","provider_model_id_reason":'
            '"no verified offering.api_model_id in this snapshot"}\n',
        ),
    ],
    ids=["litellm", "openrouter", "json"],
)
def test_null_identifiers_keep_worker_placeholder_and_reason(worker, fmt, text):
    worker[1]["router_config"] = text
    result = run("--emit-router-config", fmt)
    assert result.exit_code == 0, result.output
    assert result.stdout == text
    assert "<" in result.stdout and "no verified offering." in result.stdout


@pytest.mark.parametrize("global_json", [False, True])
def test_config_file_keeps_one_json_worker_body(worker, tmp_path, global_json):
    out = tmp_path / "router.yaml"
    result = run(
        "--emit-router-config",
        "litellm",
        "--out",
        str(out),
        *([] if global_json else ["--json"]),
        global_json=global_json,
    )
    assert result.exit_code == 0, result.output
    assert out.read_text() == LITELLM_CONFIG
    assert json.loads(result.stdout) == worker[1]
    assert str(out) in result.stderr


def test_template_and_band_options_reach_worker(worker):
    result = CliRunner().invoke(
        app,
        [
            "decide",
            "--template",
            "coding",
            "--emit-router-config",
            "json",
            "--include-rest",
            "--include-thin",
        ],
    )
    assert result.exit_code == 0, result.output
    seen, _ = worker
    assert [request.url.path for request in seen] == ["/v1/vocabulary", "/v1/decide"]
    assert json.loads(seen[-1].content)["router_config"] == {
        "format": "json",
        "include_rest": True,
        "include_thin": True,
    }


@pytest.mark.parametrize(
    "args,message",
    [
        (["--out", "unused.yaml"], "need --emit-router-config"),
        (["--include-rest"], "need --emit-router-config"),
        (["--include-thin"], "need --emit-router-config"),
        (["--emit-router-config", "invalid"], "unknown router config format"),
        (["--emit-router-config", "litellm", "--json"], "needs --out PATH"),
    ],
)
def test_router_flag_errors_have_legacy_code_and_exit_one(worker, args, message):
    result = run(*args, global_json=True)
    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "router_config_usage"
    assert message in payload["error"]["message"]
    assert payload["next"]
    assert not worker[0]


def test_config_requires_key_before_spec_read_or_http(worker, monkeypatch):
    monkeypatch.setenv("MODELSPEC_API_KEY", "")

    def forbidden_read(source):
        pytest.fail("A keyless router config command read the spec")

    monkeypatch.setattr(cli_module, "load_spec", forbidden_read)
    result = run("--emit-router-config", "litellm", "--out", "unused.yaml", global_json=True)
    assert result.exit_code == 5, result.output
    assert json.loads(result.stdout)["error"]["code"] == "missing_api_key"
    assert not worker[0]


def test_missing_rendered_config_fails_without_writing(worker, tmp_path):
    worker[1].pop("router_config")
    out = tmp_path / "router.yaml"
    result = run("--emit-router-config", "litellm", "--out", str(out), global_json=True)
    assert result.exit_code == 1, result.output
    assert json.loads(result.stdout)["error"]["code"] == "unexpected_response"
    assert not out.exists()


def test_unwritable_config_is_a_structured_error(worker, tmp_path):
    out = tmp_path / "missing" / "router.yaml"
    result = run("--emit-router-config", "litellm", "--out", str(out), global_json=True)
    assert result.exit_code == 1, result.output
    assert json.loads(result.stdout)["error"]["code"] == "unwritable"
    assert not out.exists()
