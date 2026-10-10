"""MODEL-348: the keyed CLI compares a Spec through the hosted endpoint."""

from __future__ import annotations

import json

import httpx
import pytest
import yaml
from typer.testing import CliRunner

from cli.modelspec import cli, client

KEY = "live_model348_test_secret"
SPEC = {
    "spec_version": 1,
    "where": ["model.context_window >= 150"],
    "optimize": {"min": "offering.cost_per_task"},
    "snapshot": "snap_pinned",
    "task_tokens": {"input": 1234, "output": 567},
    "fields": None,
    "explain": "none",
}
API_TEXT = (
    '{ "contract_version":"2.14", "endpoint":"compare",'
    ' "snapshot":"snap_new", "compare_to":"snap_old",\n'
    ' "result":{"changed":false,'
    '"snapshot":{"old":{"id":"snap_old","as_of":null},'
    '"new":{"id":"snap_new","as_of":null}},'
    '"status":{"old":"answered","new":"answered"},'
    '"counts":{"entered":0,"left":0,"rank_changed":0,'
    '"may_qualify_changed":0,"models_changed":0},'
    '"models":[],"spec_snapshot_ignored":true} }\n'
)
COMPARISON = {
    "contract_version": "2.14",
    "endpoint": "compare",
    "snapshot": "snap_new",
    "compare_to": "snap_old",
    "result": {
        "changed": True,
        "snapshot": {
            "old": {"id": "snap_old", "as_of": "2026-09-26"},
            "new": {"id": "snap_new", "as_of": "2026-09-27"},
        },
        "status": {"old": "answered", "new": "partial"},
        "counts": {
            "entered": 1, "left": 1, "rank_changed": 1,
            "may_qualify_changed": 1, "models_changed": 3,
        },
        "models": [
            {
                "model": "lab/entered", "entered": True, "left": None,
                "rank_changed": None, "may_qualify": None,
                "values": [{
                    "kind": "facet", "facet": "model.context_window",
                    "offering": {
                        "model": "lab/entered", "provider": None,
                        "region": None, "tier": None,
                    },
                    "old": {"value": 100, "unit": "tokens", "records": ["entered#old"]},
                    "new": {"value": 200, "unit": "tokens", "records": ["entered#new"]},
                }],
            },
            {
                "model": "lab/departed", "entered": False,
                "left": {"reason": "model.context_window >= 150"},
                "rank_changed": None, "may_qualify": None,
                "values": [{
                    "kind": "facet", "facet": "model.context_window",
                    "offering": {
                        "model": "lab/departed", "provider": "p1",
                        "region": "global", "tier": "standard",
                    },
                    "old": {"value": 200, "unit": "tokens", "records": ["departed#old"]},
                    "new": {"value": 100, "unit": "tokens", "records": ["departed#new"]},
                }],
            },
            {
                "model": "lab/changed", "entered": False, "left": None,
                "rank_changed": {"old": 3, "new": 1},
                "may_qualify": {"old": ["model.context_window"], "new": None},
                "values": [
                    {
                        "kind": "cost_per_task",
                        "offering": {
                            "old": {
                                "model": "lab/changed", "provider": "p1",
                                "region": "global", "tier": "standard",
                            },
                            "new": {
                                "model": "lab/changed", "provider": "p2",
                                "region": "global", "tier": "standard",
                            },
                        },
                        "old": {
                            "value": 0.044, "unit": "usd_per_task",
                            "records": ["p1#input", "p1#output"],
                        },
                        "new": {
                            "value": 0.088, "unit": "usd_per_task",
                            "records": ["p2#input", "p2#output"],
                        },
                    },
                    {
                        "kind": "capability", "domain": "software_engineering",
                        "offering": {
                            "model": "lab/changed", "provider": None,
                            "region": None, "tier": None,
                        },
                        "old": {
                            "value": 0.61, "interval": [0.52, 0.70],
                            "records": ["changed#benchmark#old"],
                        },
                        "new": {
                            "value": 0.68, "interval": [0.60, 0.76],
                            "records": ["changed#benchmark#new"],
                        },
                    },
                ],
            },
        ],
        "spec_snapshot_ignored": True,
    },
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)

    def forbidden(request):
        raise AssertionError("Local refusal tried HTTP")

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(forbidden))


def run(args, *, keyed=True, input=None):
    return CliRunner().invoke(
        cli.app, args, input=input, env={"MODELSPEC_API_KEY": KEY} if keyed else {}
    )


@pytest.mark.parametrize(
    "source", [["--spec", "missing"], ["--spec", "-"], ["--template", "example"]]
)
def test_keyless_compare_refuses_before_spec_loading_or_http(monkeypatch, source):
    def forbidden(source):
        raise AssertionError("Keyless compare read a Spec")

    monkeypatch.setattr(cli, "load_spec", forbidden)
    result = run(["compare", *source, "--to", "snap_old", "--json"], keyed=False)
    assert result.exit_code == 5, result.output
    payload = json.loads(result.stdout)
    assert payload["error"] == {
        "code": "missing_api_key", "message": "This command needs a ModelSpec API key.",
    }
    assert payload["command"] == "modelspec compare"
    assert payload["schema_version"] == "2.0"
    assert payload["next"][0] == (
        "Run modelspec key, then modelspec auth set or set MODELSPEC_API_KEY."
    )
    assert "You can provide an existing key" in payload["next"][1]


@pytest.mark.parametrize("kind", ["json-file", "yaml-file", "stdin"])
@pytest.mark.parametrize("json_args", [["--json", "compare"], ["compare"]])
def test_compare_sends_exact_spec_and_preserves_response_bytes(
    monkeypatch, tmp_path, kind, json_args
):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.method == "POST"
        assert request.url == "https://api.modelspec.dev/v1/compare"
        assert request.headers["authorization"] == "Bearer live_model348_test_secret"
        assert json.loads(request.content) == {"compare_to": "snap_old", "spec": SPEC}
        return httpx.Response(200, text=API_TEXT)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    text = yaml.safe_dump(SPEC) if kind == "yaml-file" else json.dumps(SPEC)
    path = tmp_path / "spec"
    path.write_text(text)
    args = [*json_args, "--spec", "-" if kind == "stdin" else str(path), "--to", "snap_old"]
    if json_args == ["compare"]:
        args.append("--json")
    result = run(args, input=text if kind == "stdin" else None)
    assert result.exit_code == 0, result.output
    assert result.stdout_bytes == API_TEXT.encode("utf-8")
    assert result.stderr == ""
    assert len(calls) == 1


def test_template_lookup_is_keyed_and_then_compared_unchanged(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.headers["authorization"] == "Bearer live_model348_test_secret"
        if request.method == "GET":
            assert request.url.path == "/v1/vocabulary"
            assert dict(request.url.params) == {
                "section": "templates", "id": "example", "detail": "full",
            }
            return httpx.Response(200, json={"templates": [{"id": "example", "spec": SPEC}]})
        assert request.method == "POST"
        assert request.url == "https://api.modelspec.dev/v1/compare"
        assert json.loads(request.content) == {"compare_to": "snap_old", "spec": SPEC}
        return httpx.Response(200, text=API_TEXT)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    result = run(["compare", "--template", "example", "--to", "snap_old", "--json"])
    assert result.exit_code == 0, result.output
    assert result.stdout_bytes == API_TEXT.encode("utf-8")
    assert [request.url.path for request in calls] == ["/v1/vocabulary", "/v1/compare"]


@pytest.mark.parametrize("source", [[], ["--spec", "missing", "--template", "example"]])
def test_exactly_one_spec_source_is_required(source):
    result = run(["compare", *source, "--to", "snap_old", "--json"])
    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["error"] == {
        "code": "spec_source", "message": "Choose exactly one of --spec FILE|- and --template ID.",
    }
    assert payload["next"][0] == (
        "Check the reported field paths against the published schema and OpenAPI."
    )


@pytest.mark.parametrize("source", [["--spec", "missing"], ["--template", "example"]])
@pytest.mark.parametrize(
    "to", ["", "latest", "previous", "snap_", "snap_a/b", "snap_a b", "snap_a\n", "snap_é"]
)
def test_bad_snapshot_id_is_refused_before_spec_loading_or_http(monkeypatch, source, to):
    def forbidden(source):
        raise AssertionError("Invalid --to read a Spec")

    monkeypatch.setattr(cli, "load_spec", forbidden)
    result = run(["compare", *source, "--to", to, "--json"])
    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["error"] == {
        "code": "invalid_compare_to",
        "message": "The --to value must be a snapshot ID matching ^snap_[A-Za-z0-9:._-]+$.",
    }
    assert payload["next"] == [
        "Run modelspec help agent or modelspec --help for the supported commands.",
        "Read https://modelspec.dev/agents.md for the next call.",
        "Use --to with a snapshot ID from a prior modelspec decide response, "
        "such as snap_0123456789abcdef.",
    ]


def test_to_is_required():
    result = run(["compare", "--spec", "missing", "--json"])
    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "usage_error"
    assert payload["next"][-1] == "Run modelspec compare --help for this command's options."


def test_snapshot_id_accepts_all_published_characters(monkeypatch):
    def handler(request):
        assert json.loads(request.content) == {"compare_to": "snap_Az09:._-", "spec": SPEC}
        return httpx.Response(200, text=API_TEXT)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    result = run(
        ["compare", "--spec", "-", "--to", "snap_Az09:._-", "--json"], input=json.dumps(SPEC)
    )
    assert result.exit_code == 0, result.output


def test_human_output_lists_model_changes_values_and_records(monkeypatch):
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(200, json=COMPARISON)))
    result = run(["compare", "--spec", "-", "--to", "snap_old"], input=json.dumps(SPEC))
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "Comparison: snap_old -> snap_new (status: answered -> partial)",
        "Counts: entered=1, departed=1, rank_changed=1, may_qualify_changed=1, models_changed=3",
        "",
        "lab/entered: entered",
        "  model.context_window: 100 tokens [records: entered#old] "
        "-> 200 tokens [records: entered#new]",
        "  offering: lab/entered",
        "",
        "lab/departed: departed",
        "  reason: model.context_window >= 150",
        "  model.context_window: 200 tokens [records: departed#old] "
        "-> 100 tokens [records: departed#new]",
        "  offering: lab/departed (provider=p1, region=global, tier=standard)",
        "",
        "lab/changed: changed",
        "  rank: 3 -> 1",
        "  may_qualify: model.context_window -> none",
        "  cost_per_task: 0.044 usd_per_task [records: p1#input, p1#output] "
        "-> 0.088 usd_per_task [records: p2#input, p2#output]",
        "  offering: lab/changed (provider=p1, region=global, tier=standard) "
        "-> lab/changed (provider=p2, region=global, tier=standard)",
        "  capability software_engineering: 0.61 [interval: [0.52, 0.7]] "
        "[records: changed#benchmark#old] -> 0.68 [interval: [0.6, 0.76]] "
        "[records: changed#benchmark#new]",
        "  offering: lab/changed",
    ]
    assert result.stderr == ""


def test_human_output_handles_unknown_values_and_missing_optional_details(monkeypatch):
    body = json.loads(API_TEXT)
    body["result"]["changed"] = True
    body["result"]["counts"]["models_changed"] = 1
    body["result"]["models"] = [{
        "model": "lab/unknown", "entered": False,
        "values": [
            {"kind": "facet", "facet": "model.context_window", "old": {"value": None},
             "new": {"value": 200}},
            {"kind": "future_metric", "old": {"value": False}, "new": {"value": True}},
        ],
        "future_details": {"unexpected": "ignored"},
    }]
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(200, json=body)))
    result = run(["compare", "--spec", "-", "--to", "snap_old"], input=json.dumps(SPEC))
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "Comparison: snap_old -> snap_new (status: answered -> answered)",
        "Counts: entered=0, departed=0, rank_changed=0, may_qualify_changed=0, models_changed=1",
        "",
        "lab/unknown: changed",
        "  model.context_window: unknown -> 200",
        "  future_metric: false -> true",
    ]


def test_unchanged_human_comparison_exits_zero(monkeypatch):
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(200, text=API_TEXT)))
    result = run(["compare", "--spec", "-", "--to", "snap_old"], input=json.dumps(SPEC))
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "Comparison: snap_old -> snap_new (status: answered -> answered)",
        "Counts: entered=0, departed=0, rank_changed=0, may_qualify_changed=0, models_changed=0",
        "No changes.",
    ]


@pytest.mark.parametrize("as_json", [False, True])
def test_unhosted_snapshot_guidance_is_added_to_server_refusal(monkeypatch, as_json):
    body = {
        "contract_version": "2.14", "endpoint": "compare", "snapshot": "snap_new",
        "error": {
            "code": "comparison_snapshot_unavailable",
            "message": "the origin does not publish retained decision snapshot snap_old",
        },
    }
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(409, json=body)))
    result = run(
        ["compare", "--spec", "-", "--to", "snap_old", *(["--json"] if as_json else [])],
        input=json.dumps(SPEC),
    )
    assert result.exit_code == 1, result.output
    if as_json:
        assert json.loads(result.stdout) == {
            "contract_version": "2.14", "endpoint": "compare", "snapshot": "snap_new",
            "error": {
                "code": "comparison_snapshot_unavailable",
                "message": "the origin does not publish retained decision snapshot snap_old",
            },
            "schema_version": "2.0", "command": "modelspec compare",
            "next": [
                "Retained snapshots are not hosted yet.",
                "Run modelspec decide --spec FILE or modelspec decide --template ID "
                "for the current answer.",
            ],
        }
        assert result.stderr == ""
    else:
        assert result.stdout == ""
        assert result.stderr.splitlines() == [
            "the origin does not publish retained decision snapshot snap_old",
            "Next steps:",
            "Retained snapshots are not hosted yet.",
            "Run modelspec decide --spec FILE or modelspec decide --template ID "
            "for the current answer.",
        ]


@pytest.mark.parametrize("as_json", [False, True])
def test_401_exits_five_with_key_recovery(monkeypatch, as_json):
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(401, json={
            "error": {"code": "invalid_api_key", "message": "The ModelSpec key was refused."},
        })))
    result = run(
        ["compare", "--spec", "-", "--to", "snap_old", *(["--json"] if as_json else [])],
        input=json.dumps(SPEC),
    )
    assert result.exit_code == 5, result.output
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["error"] == {
            "code": "invalid_api_key", "message": "The ModelSpec key was refused.",
        }
        assert payload["next"][0] == (
            "Run modelspec key, then modelspec auth set or set MODELSPEC_API_KEY."
        )
        assert "You can provide an existing key" in payload["next"][1]
    else:
        assert result.stdout == ""
        assert result.stderr.splitlines()[:3] == [
            "The ModelSpec key was refused.",
            "Next steps:",
            "Run modelspec key, then modelspec auth set or set MODELSPEC_API_KEY.",
        ]
    assert KEY not in result.output


def test_compare_help_explains_the_endpoint_and_snapshot_option():
    result = run(["compare", "--help"], keyed=False)
    assert result.exit_code == 0, result.output
    assert "POST /v1/compare" in result.stdout
    assert "--to" in result.stdout
    assert "^snap_[A-Za-z0-9:._-]+$" in result.stdout
