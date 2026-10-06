"""The distributed CLI guides keyless callers and sends keyed calls only to the API."""

from __future__ import annotations

import copy
import json
import stat
import tomllib
from types import SimpleNamespace

import httpx
import pytest
from typer.testing import CliRunner

from cli.modelspec import auth, client, setup
from cli.modelspec.cli import app
from cli.modelspec.guidance import BUNDLE
from pipeline import agent_copy, entity, pricing

KEY = "live_model307_test_secret"
SPEC = {
    "spec_version": 1,
    "where": ["model.class = text-generator"],
    "optimize": {"min": "offering.cost_per_task"},
    "snapshot": "latest",
    "task_tokens": {"input": 1234, "output": 567},
    "fields": None,
    "explain": "none",
}
API_TEXT = (
    '{"status":"ok", "decision_id":"dec_12345678", '
    '"answer":{"kind":"tied","members":["lab/a","lab/b"]}}'
)


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("MODELSPEC_CACHE", str(tmp_path / "old-cache"))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    def forbidden(request):
        raise AssertionError("A guidance or local-validation command tried HTTP")

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(forbidden))


def run(args, *, keyed=False, input=None):
    return CliRunner().invoke(
        app, args, input=input, env={"MODELSPEC_API_KEY": KEY} if keyed else {}
    )


def assert_error(result, code=None):
    assert result.exit_code != 0, result.output
    payload = json.loads(result.stdout)
    assert payload["next"] and all(isinstance(line, str) and line for line in payload["next"])
    assert KEY not in result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr
    if code:
        assert payload["error"]["code"] == code
    return payload


@pytest.mark.parametrize("args", [[], ["help", "agent"], ["--json"], ["help", "agent", "--json"]])
def test_orientation_is_keyless_offline_and_identical(args):
    result = run(args)
    assert result.exit_code == 0, result.output
    assert entity.ONE_SENTENCE in result.stdout
    for path in agent_copy.INSTALL_PATHS:
        assert path in result.stdout
    assert "No data download" in result.stdout
    assert "pip install modelspec is an unrelated project" in result.stdout
    if "--json" in args:
        data = json.loads(result.stdout)
        assert data == json.loads(run(["--json"]).stdout)
        assert data["coverage"] == BUNDLE["coverage"]
        assert "https://modelspec.dev/api/coverage.json" in data["coverage_note"]
        assert data["coverage"]["decision"]["catalogue"]["models"] == data["coverage"]["models"]
        assert data["ways_in"] == {
            "cli": agent_copy.INSTALL_PATHS[0],
            "mcp": entity.MCP_ENDPOINT,
            "http": "https://api.modelspec.dev/v1/decide",
        }


@pytest.mark.parametrize("http_status, status", [(200, "no_feasible"), (200, "partial"), (400, None)])
def test_typed_coverage_is_passed_through_and_uses_coverage_recovery(monkeypatch, http_status, status):
    body = {"coverage": {"kind": "out_of_coverage", "message": "Speech is outside this snapshot.",
                         "classes": [{"id": "text-generator", "models": 2}],
                         "url": "https://modelspec.dev/api/coverage.json"}}
    if status:
        body["status"] = status
    else:
        body["error"] = {"code": "invalid_spec", "message": "Unknown speech domain."}
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(
        lambda request: httpx.Response(http_status, json=body)))
    result = run(["decide", "--spec", "-", "--json"], keyed=True, input=json.dumps(SPEC))
    assert result.exit_code == 2, result.output
    payload = json.loads(result.stdout)
    assert payload["coverage"] == body["coverage"]
    assert "https://modelspec.dev/api/coverage.json" in " ".join(payload["next"])


@pytest.mark.parametrize(
    "args",
    [
        ["--json"],
        ["help", "agent", "--json"],
        ["key", "--json"],
        *[["setup", "mcp", "--client", name, "--json"] for name in BUNDLE["clients"]],
    ],
)
def test_no_keyless_command_returns_model_data_or_vocabulary(args, tmp_path):
    # A populated old cache must never affect this CLI.
    cache = tmp_path / "old-cache"
    cache.mkdir()
    (cache / "snapshot.json").write_text('{"model_id":"private/model", "rank":1}')
    result = run(args)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    for forbidden in (
        "private/model",
        '"model_id"',
        '"rank_score"',
        '"facets"',
        '"results"',
        '"allowed_values"',
        '"spec_version"',
    ):
        assert forbidden not in result.stdout
    assert payload.get("coverage", {}).keys() <= {"models", "providers", "benchmarks", "as_of", "summary", "decision"}
    assert set(cache.iterdir()) == {cache / "snapshot.json"}


def test_key_prices_come_from_the_same_site_source():
    data = json.loads(run(["key", "--json"]).stdout)
    tiers = pricing.load_tiers(agent_copy.ROOT)
    assert data["pricing"] == pricing.procurement_data(tiers)
    low = pricing.format_usd(data["pricing"]["usd_per_answer"]["min"])
    assert f"From {low} per answer" in data["price"]
    assert f"Answers start at {low}" in data["tell_the_human"]
    assert "¢" not in data["price"]
    assert "¢" not in data["tell_the_human"]
    contract = (agent_copy.ROOT / "docs/cli-contract.md").read_text(encoding="utf-8")
    assert low in contract
    assert "¢" not in contract
    rates = [row["usd"] / row["credits"] for row in tiers["billing"]["prices"].values()]
    assert data["pricing"]["usd_per_answer"] == {"min": min(rates), "max": max(rates) * 2}
    changed = copy.deepcopy(tiers)
    next(iter(changed["billing"]["prices"].values()))["usd"] = 1
    assert pricing.procurement_data(changed) != data["pricing"]
    assert "free board" in data["tell_the_human"]
    assert not any(
        word in data["tell_the_human"].lower()
        for word in ("hurry", "urgent", "must buy", "limited time")
    )


@pytest.mark.parametrize(
    "args",
    [
        ["decide", "--spec", "does-not-exist"],
        ["decide", "--template", "anything"],
        ["vocab"],
        ["feedback", "--rating", "reliable"],
    ],
)
def test_all_remote_commands_require_a_key_before_reading_or_requesting(args):
    payload = assert_error(run([*args, "--json"]), "missing_api_key")
    assert any("modelspec key" in line for line in payload["next"])
    assert any("human" in line or "provide an existing key" in line for line in payload["next"])


@pytest.mark.parametrize("kind", ["json-file", "yaml-file", "stdin"])
def test_decide_sends_exactly_the_supplied_spec_and_passes_the_body_through(
    monkeypatch, tmp_path, kind
):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.url == "https://api.modelspec.dev/v1/decide"
        assert request.method == "POST"
        assert json.loads(request.content) == SPEC
        assert request.headers["authorization"] == f"Bearer {KEY}"
        assert request.headers["user-agent"] == "modelspec-cli/0.3.0"
        return httpx.Response(
            200, text=API_TEXT, headers={"x-modelspec-guide-version": BUNDLE["guide_version"]}
        )

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    path = tmp_path / "spec"
    text = json.dumps(SPEC)
    if kind == "yaml-file":
        import yaml

        text = yaml.safe_dump(SPEC)
    path.write_text(text)
    before = set(tmp_path.rglob("*"))
    result = run(
        ["decide", "--spec", "-" if kind == "stdin" else str(path), "--json"],
        keyed=True,
        input=text if kind == "stdin" else None,
    )
    assert result.exit_code == 0, result.output
    assert result.stdout == API_TEXT
    assert len(calls) == 1
    assert set(tmp_path.rglob("*")) == before


def test_template_is_looked_up_with_a_key_then_sent_unchanged(monkeypatch):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.headers["authorization"] == f"Bearer {KEY}"
        if request.method == "GET":
            assert dict(request.url.params) == {
                "section": "templates",
                "id": "example",
                "detail": "full",
            }
            return httpx.Response(200, json={"templates": [{"id": "example", "spec": SPEC}]})
        assert json.loads(request.content) == SPEC
        return httpx.Response(200, text=API_TEXT)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    result = run(["decide", "--template", "example", "--json"], keyed=True)
    assert result.exit_code == 0, result.output
    assert result.stdout == API_TEXT
    assert [request.url.path for request in calls] == ["/v1/vocabulary", "/v1/decide"]


def test_vocab_matches_mcp_lookup_arguments_and_has_no_public_fallback(monkeypatch):
    def handler(request):
        assert request.method == "GET"
        assert request.url.host == "api.modelspec.dev"
        assert request.url.path == "/v1/vocabulary"
        assert dict(request.url.params) == {
            "section": "facets",
            "search": "cost",
            "id": "one",
            "ids": "two,three,four",
            "detail": "full",
            "offset": "2",
            "limit": "5",
        }
        assert request.headers["authorization"] == f"Bearer {KEY}"
        return httpx.Response(200, text='{"facets":[{"id":"one"}],"next":"call decide"}')

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    result = run(
        [
            "vocab",
            "--section",
            "facets",
            "--search",
            "cost",
            "--id",
            "one",
            "--ids",
            "two,three",
            "--ids",
            "four",
            "--detail",
            "full",
            "--offset",
            "2",
            "--limit",
            "5",
            "--json",
        ],
        keyed=True,
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["facets"] == [{"id": "one"}]


def test_feedback_matches_mcp_fields_and_preserves_the_privacy_boundary(monkeypatch):
    def handler(request):
        assert request.url.path == "/v1/feedback"
        assert "authorization" not in request.headers
        assert json.loads(request.content) == {
            "client": "cli",
            "rating": "confusing",
            "decision_id": "dec_12345678",
            "note": "Missing evidence",
            "trying_to_decide": "a role",
            "template": "example",
        }
        return httpx.Response(200, json={"status": "not_recorded", "message": "Nothing kept"})

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    result = run(
        [
            "feedback",
            "dec_12345678",
            "--rating",
            "confusing",
            "--note",
            "Missing evidence",
            "--trying-to-decide",
            "a role",
            "--template",
            "example",
            "--json",
        ],
        keyed=True,
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"status": "not_recorded", "message": "Nothing kept"}


@pytest.mark.parametrize(
    "status,code,expected",
    [
        (400, "invalid_spec", "reported field"),
        (401, "missing_api_key", "modelspec key"),
        (401, "invalid_api_key", "modelspec key"),
        (403, "key_revoked", "modelspec key"),
        (402, "insufficient_credits", "pricing"),
        (429, "rate_limited", "pricing"),
        (422, "out_of_coverage", "coverage summary"),
        (422, "no_feasible", "coverage summary"),
        (426, "upgrade_required", "pipx upgrade modelspec-dev"),
        (502, "export_unavailable", "/v1/health"),
    ],
)
@pytest.mark.parametrize("command", ["vocab", "decide", "feedback"])
def test_every_hosted_error_has_next_steps(monkeypatch, status, code, expected, command):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(
            lambda request: httpx.Response(
                status,
                json={
                    "error": {"code": code, "message": "Server said " + KEY},
                    "reading": {"not_applied": ["field"]},
                },
                headers={"retry-after": "60"},
            )
        ),
    )
    args = {
        "vocab": ["vocab"],
        "decide": ["decide", "--spec", "-"],
        "feedback": ["feedback", "--rating", "reliable"],
    }[command]
    payload = assert_error(run([*args, "--json"], keyed=True, input=json.dumps(SPEC)), code)
    assert any(expected in line for line in payload["next"])
    assert payload["reading"] == {"not_applied": ["field"]}
    assert payload["retry_after"] == "60"


@pytest.mark.parametrize(
    "status,expected",
    [
        (200, "/v1/health"),
        (401, "modelspec key"),
        (402, "pricing"),
        (429, "pricing"),
        (503, "/v1/health"),
    ],
)
def test_non_json_responses_still_have_next(monkeypatch, status, expected):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(status, text="HTML error")),
    )
    payload = assert_error(run(["vocab", "--json"], keyed=True))
    assert any(expected in line for line in payload["next"])


@pytest.mark.parametrize(
    "args", [["vocab"], ["decide", "--spec", "-"], ["feedback", "--rating", "reliable"]]
)
def test_network_errors_have_health_url_and_alternatives(monkeypatch, args):
    def handler(request):
        raise httpx.ConnectError(KEY, request=request)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    payload = assert_error(
        run([*args, "--json"], keyed=True, input=json.dumps(SPEC)), "network_error"
    )
    assert any("/v1/health" in line for line in payload["next"])


def test_server_validates_semantics_and_requirements_are_never_removed(monkeypatch):
    spec = {"spec_version": 1, "optimize": {"max": "unsupported.facet"}, "task": "not supported"}

    def handler(request):
        assert json.loads(request.content) == spec
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": "invalid_spec",
                    "issues": [{"path": "task", "reason": "unsupported"}],
                },
                "reading": {"not_applied": ["task"]},
            },
        )

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    payload = assert_error(
        run(["decide", "--spec", "-", "--json"], keyed=True, input=json.dumps(spec)), "invalid_spec"
    )
    assert payload["reading"]["not_applied"] == ["task"]


@pytest.mark.parametrize("json_mode", [False, True])
def test_an_unregistered_value_reaches_the_agent_with_its_allowed_values(monkeypatch, json_mode):
    """MODEL-318: the Worker's value issue arrives whole, in JSON and on stderr."""
    issue = {
        "path": "where[0]", "condition": "model.weights_openness = proprietary",
        "field": "model.weights_openness",
        "reason": "'proprietary' is not a registered value of model.weights_openness",
        "value": "proprietary", "value_type": "enum",
        "allowed_values": ["closed_weights", "open_weights"],
        "next": "https://api.modelspec.dev/v1/vocabulary?section=facets&id=model.weights_openness",
    }
    monkeypatch.setattr(client, "_transport", httpx.MockTransport(lambda request: httpx.Response(
        400, json={"error": {"code": "invalid_spec", "issues": [issue]}})))
    result = run(["decide", "--spec", "-", *(["--json"] if json_mode else [])],
                 keyed=True, input=json.dumps(SPEC))
    if json_mode:
        assert assert_error(result, "invalid_spec")["error"]["issues"] == [issue]
    else:
        assert result.exit_code != 0
        assert json.dumps(issue, ensure_ascii=False) in result.stderr


@pytest.mark.parametrize("json_mode", [False, True])
def test_new_guide_version_suggests_upgrade_without_changing_the_api_body(monkeypatch, json_mode):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(
            lambda request: httpx.Response(
                200, text=API_TEXT, headers={"x-modelspec-guide-version": "new-guide"}
            )
        ),
    )
    result = run(
        ["decide", "--spec", "-", *(["--json"] if json_mode else [])],
        keyed=True,
        input=json.dumps(SPEC),
    )
    assert result.exit_code == 0, result.output
    if json_mode:
        assert result.stdout == API_TEXT
        assert json.loads(result.stderr)["next"]
    assert "pipx upgrade modelspec-dev" in result.stderr


@pytest.mark.parametrize(
    "args,input,code",
    [
        (["unrecognized"], None, "usage_error"),
        (["offline", "rank", "coding"], None, "usage_error"),
        (["snapshot", "fetch"], None, "usage_error"),
        (["feedback"], None, "usage_error"),
        (["vocab", "--unknown"], None, "usage_error"),
        (["auth"], None, "usage_error"),
        (["decide"], None, "spec_source"),
        (["decide", "--spec", "-", "--template", "a"], None, "spec_source"),
        (["decide", "--spec", "absent"], None, "spec_unreadable"),
        (["decide", "--spec", "-"], "[not: valid", "spec_unreadable"),
        (["decide", "--spec", "-"], '{"spec_version":1}', "invalid_spec"),
        (["decide", "--spec", "-"], "[]", "invalid_spec"),
        (["decide", "--spec", "-"], '{"optimize":{"min":NaN}}', "invalid_spec"),
        (["decide", "--spec", "-"], "x" * 65537, "spec_too_large"),
        (["vocab", "--limit", "21"], None, "invalid_vocabulary"),
        (["vocab", "--offset", "-1"], None, "invalid_vocabulary"),
        (["vocab", "--offset", "not-a-number"], None, "usage_error"),
        (["vocab", "facets", "--section", "domains"], None, "invalid_vocabulary"),
        (["vocab", "--detail", "wrong"], None, "invalid_vocabulary"),
        (["feedback", "--rating", "invented"], None, "invalid_feedback"),
        (["feedback", "--rating", "reliable", "--note", "x" * 1001], None, "invalid_feedback"),
        (["auth", "set", "--stdin"], "\n", "invalid_api_key"),
        (["setup", "mcp", "--client", "wrong"], None, "invalid_client"),
        (["setup", "mcp", "--client", "generic", "--write", "--yes"], None, "config_path_required"),
    ],
)
def test_local_and_usage_errors_always_carry_next(args, input, code):
    assert_error(run([*args, "--json"], keyed=True, input=input), code)


def test_human_errors_end_with_the_same_recovery_as_json():
    result = run(["vocab"])
    assert result.exit_code == 5
    payload = assert_error(run(["vocab", "--json"]))
    assert result.stderr.rstrip().endswith(payload["next"][-1])


def test_auth_stores_a_private_key_never_echoes_and_environment_wins(monkeypatch):
    result = run(["auth", "set", "--stdin", "--json"], input=KEY + "\n")
    assert result.exit_code == 0, result.output
    assert KEY not in result.stdout + result.stderr
    path = auth.key_path()
    assert path.read_text() == KEY + "\n"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert auth.require_key().secret == KEY
    monkeypatch.setenv("MODELSPEC_API_KEY", "live_environment_wins")
    assert auth.require_key().secret == "live_environment_wins"
    monkeypatch.setenv("MODELSPEC_API_KEY", "")
    assert_error(run(["vocab", "--json"]), "missing_api_key")
    assert KEY not in repr(auth.Credential(KEY))


def test_insecure_auth_file_and_symlink_are_refused(tmp_path):
    path = auth.key_path()
    path.parent.mkdir(parents=True)
    path.write_text(KEY)
    path.chmod(0o644)
    assert_error(run(["vocab", "--json"]), "auth_unreadable")
    path.unlink()
    target = tmp_path / "target"
    target.write_text("unchanged")
    path.symlink_to(target)
    assert_error(run(["auth", "set", "--stdin", "--json"], input=KEY), "auth_unwritable")
    assert target.read_text() == "unchanged"


@pytest.mark.parametrize("fchmod", ["missing", "unsupported"])
def test_windows_saved_key_uses_profile_acl_instead_of_posix_mode(monkeypatch, fchmod):
    def unsupported(*args):
        raise OSError("fchmod is unavailable on Windows")

    windows_os = SimpleNamespace(**{**vars(auth.os), "name": "nt"})
    if fchmod == "missing":
        del windows_os.fchmod
    else:
        windows_os.fchmod = unsupported
    monkeypatch.setattr(auth, "os", windows_os)
    result = run(["auth", "set", "--stdin", "--json"], input=KEY)
    assert result.exit_code == 0, result.output
    path = auth.key_path()
    path.chmod(0o666)
    assert auth.require_key().secret == KEY
    assert "Windows uses the user-profile directory ACL" in result.stdout
    assert KEY not in result.stdout + result.stderr


@pytest.mark.parametrize("name", list(BUNDLE["clients"]))
def test_each_mcp_client_prints_native_config_without_keys_or_writes(name, tmp_path):
    result = run(["setup", "mcp", "--client", name, "--json"], keyed=True)
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    config = (
        tomllib.loads(data["snippet"])
        if BUNDLE["clients"][name]["format"] == "toml"
        else json.loads(data["snippet"])
    )
    assert (
        config[BUNDLE["clients"][name]["table"]]["modelspec"] == BUNDLE["clients"][name]["server"]
    )
    assert KEY not in result.stdout + result.stderr
    assert not list(tmp_path.rglob("*"))


def test_desktop_snippet_has_an_explicit_env_placeholder():
    result = run(["setup", "mcp", "--client", "claude-desktop", "--json"], keyed=True)
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    server = json.loads(data["snippet"])["mcpServers"]["modelspec"]
    assert server["env"] == {"MODELSPEC_AUTH_HEADER": "Bearer <MODELSPEC_API_KEY>"}
    assert server["args"][-2:] == ["--header", "Authorization:${MODELSPEC_AUTH_HEADER}"]
    assert "macOS GUI apps do not inherit your shell environment" in data["next"][0]
    assert "This stores the key in that config" in data["next"][0]
    assert KEY not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "name", ["claude-code", "claude-desktop", "codex", "gemini", "grok", "cursor", "generic"]
)
def test_write_shows_diff_and_preserves_other_servers_and_settings(name, tmp_path):
    path = tmp_path / "mcp-config"
    is_toml = BUNDLE["clients"][name]["format"] == "toml"
    original = (
        '# My configuration\nmodel = "mine"\n[mcp_servers.other]\nurl = "https://other.example/mcp"\n'
        if is_toml
        else '{"setting":42,"mcpServers":{"other": {"command":"mine", "args": ["keep"]}}}\n'
    )
    path.write_text(original)
    args = ["setup", "mcp", "--client", name, "--config", str(path), "--write", "--json"]
    result = run(args)
    assert_error(result, "confirmation_required")
    assert path.read_text() == original
    assert "@@" in result.stderr
    result = run([*args, "--yes"])
    assert result.exit_code == 0, result.output
    assert "@@" in result.stderr
    data = json.loads(result.stdout)
    assert data["written"] is True
    backup = path.with_name(path.name + ".modelspec-bak")
    assert data["backup"] == str(backup)
    assert str(backup) in data["message"]
    assert backup.read_bytes() == original.encode()
    assert stat.S_IMODE(backup.stat().st_mode) == 0o600
    updated = path.read_text()
    if is_toml:
        assert '# My configuration\nmodel = "mine"' in updated
        assert '[mcp_servers.other]\nurl = "https://other.example/mcp"\n' in updated
    else:
        assert '"other": {"command":"mine", "args": ["keep"]}' in updated
    before = tomllib.loads(original) if is_toml else json.loads(original)
    after = tomllib.loads(updated) if is_toml else json.loads(updated)
    expected = copy.deepcopy(before)
    expected[BUNDLE["clients"][name]["table"]]["modelspec"] = BUNDLE["clients"][name]["server"]
    assert after == expected
    second = run([*args, "--yes"])
    assert second.exit_code == 0
    assert json.loads(second.stdout)["written"] is False
    assert path.read_text() == updated
    assert list(tmp_path.glob("*.modelspec-bak*")) == [backup]


@pytest.mark.parametrize("json_mode", [False, True])
def test_config_backup_preserves_exact_bytes_and_existing_backups(tmp_path, json_mode):
    path = tmp_path / "mcp.json"
    original = '{\r\n "name": "café", "mcpServers": {}\r\n}\r\n'.encode()
    path.write_bytes(original)
    first_backup = path.with_name(path.name + ".modelspec-bak")
    first_backup.write_bytes(b"earlier config")
    result = run([
        "setup", "mcp", "--client", "claude-desktop", "--config", str(path),
        "--write", "--yes", *(["--json"] if json_mode else []),
    ], keyed=True)
    assert result.exit_code == 0, result.output
    backups = sorted(tmp_path.glob("mcp.json.modelspec-bak.*"))
    assert len(backups) == 1
    backup = backups[0]
    assert first_backup.read_bytes() == b"earlier config"
    assert backup.read_bytes() == original
    assert stat.S_IMODE(backup.stat().st_mode) == 0o600
    assert str(backup) in result.stdout
    if json_mode:
        assert json.loads(result.stdout)["backup"] == str(backup)
    assert KEY not in path.read_text() + result.stdout + result.stderr


def test_backup_failure_leaves_config_unchanged(monkeypatch, tmp_path):
    path = tmp_path / "mcp.json"
    path.write_bytes(b"{}\r\n")

    def denied(*args):
        raise PermissionError("Cannot create backup")

    monkeypatch.setattr(setup, "_backup", denied)
    assert_error(run([
        "setup", "mcp", "--client", "cursor", "--config", str(path),
        "--write", "--yes", "--json",
    ]), "config_unwritable")
    assert path.read_bytes() == b"{}\r\n"
    assert list(tmp_path.iterdir()) == [path]


def test_toml_merge_preserves_a_distinct_server_with_a_dotted_name(tmp_path):
    path = tmp_path / "config.toml"
    other = '[mcp_servers."modelspec.extra"]\nurl = "https://other.example/mcp"\n'
    path.write_text(other + '[mcp_servers."modelspec"]\nurl = "https://old.example/mcp"\n')
    result = run(
        [
            "setup",
            "mcp",
            "--client",
            "codex",
            "--config",
            str(path),
            "--write",
            "--yes",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.output
    assert other in path.read_text()
    servers = tomllib.loads(path.read_text())["mcp_servers"]
    assert servers["modelspec.extra"] == {"url": "https://other.example/mcp"}
    assert servers["modelspec"] == BUNDLE["clients"]["codex"]["server"]


def test_setup_redacts_an_existing_secret_and_requires_confirmation(monkeypatch, tmp_path):
    path = tmp_path / "config"
    path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "modelspec": {"url": "old", "headers": {"Authorization": f"Bearer {KEY}"}}
                }
            }
        )
    )
    result = run(
        ["setup", "mcp", "--client", "cursor", "--config", str(path), "--write", "--yes", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert KEY not in result.stdout + result.stderr
    assert "[redacted]" in result.stderr


def test_setup_interactive_accept_decline_and_concurrent_edit(monkeypatch, tmp_path):
    path = tmp_path / "config"
    args = ["setup", "mcp", "--client", "cursor", "--config", str(path), "--write"]
    monkeypatch.setattr(
        setup,
        "sys",
        SimpleNamespace(platform=sys_platform(), stdin=SimpleNamespace(isatty=lambda: True)),
    )
    monkeypatch.setattr(setup.typer, "confirm", lambda *a, **k: False)
    result = run(args)
    assert result.exit_code == 0, result.output
    assert not path.exists()
    monkeypatch.setattr(setup.typer, "confirm", lambda *a, **k: True)
    created = run([*args, "--json", "--yes"])
    assert created.exit_code == 0, created.output
    assert json.loads(created.stdout)["backup"] is None
    assert not list(tmp_path.glob("*.modelspec-bak*"))
    path.write_text("{}")

    def changed(*a, **k):
        path.write_text('{"other": 1}')
        return True

    monkeypatch.setattr(setup.typer, "confirm", changed)
    result = run(args)
    assert result.exit_code == 1
    assert path.read_text() == '{"other": 1}'
    assert "changed after" in result.stderr


def sys_platform():
    import sys

    return sys.platform


def test_config_and_unknown_template_errors_have_next(monkeypatch, tmp_path):
    path = tmp_path / "config"
    path.write_text("not json")
    assert_error(
        run(
            [
                "setup",
                "mcp",
                "--client",
                "cursor",
                "--config",
                str(path),
                "--write",
                "--yes",
                "--json",
            ]
        ),
        "config_unreadable",
    )
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json={"templates": []})),
    )
    assert_error(run(["decide", "--template", "missing", "--json"], keyed=True), "unknown_template")


@pytest.mark.parametrize("body", [[], None, "unexpected", {"status": {"unexpected": True}}])
def test_malformed_hosted_bodies_have_recovery_in_json(monkeypatch, body):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, text=json.dumps(body))),
    )
    payload = assert_error(run(["vocab", "--json"], keyed=True), "unexpected_response")
    assert any("/v1/health" in step for step in payload["next"])


@pytest.mark.parametrize("templates", [None, 5, {"id": "test"}])
def test_malformed_template_response_has_recovery(monkeypatch, templates):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json={"templates": templates})),
    )
    assert_error(run(["decide", "--template", "test", "--json"], keyed=True), "unexpected_response")


@pytest.mark.parametrize("command", ["auth", "setup"])
def test_filesystem_write_failures_have_recovery(monkeypatch, tmp_path, command):
    def denied(*args, **kwargs):
        raise PermissionError("Cannot write")

    if command == "auth":
        monkeypatch.setattr(auth.tempfile, "mkstemp", denied)
        result = run(["auth", "set", "--stdin", "--json"], input=KEY)
        expected = "auth_unwritable"
    else:
        monkeypatch.setattr(setup.tempfile, "mkstemp", denied)
        result = run(
            [
                "setup",
                "mcp",
                "--client",
                "cursor",
                "--config",
                str(tmp_path / "settings.json"),
                "--write",
                "--yes",
                "--json",
            ]
        )
        expected = "config_unwritable"
    assert_error(result, expected)


def test_invalid_environment_key_is_never_sent_or_echoed(monkeypatch):
    monkeypatch.setenv("MODELSPEC_API_KEY", "bad\nheader")
    payload = assert_error(run(["vocab", "--json"]), "invalid_api_key")
    assert "bad" not in json.dumps(payload)


def test_key_prompt_cancellation_has_recovery():
    assert_error(run(["auth", "set", "--json"]), "interrupted")


@pytest.mark.parametrize("templates", [[], None, [{"id": "test", "spec": {"spec_version": 2}}]])
def test_template_errors_preserve_the_upgrade_hint(monkeypatch, templates):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"templates": templates},
                headers={"x-modelspec-guide-version": "new-guide"},
            )
        ),
    )
    payload = assert_error(run(["decide", "--template", "test", "--json"], keyed=True))
    assert any("pipx upgrade modelspec-dev" in step for step in payload["next"])


def test_second_request_network_error_preserves_the_upgrade_hint(monkeypatch):
    def handler(request):
        if request.method == "GET":
            return httpx.Response(
                200,
                json={"templates": [{"id": "test", "spec": SPEC}]},
                headers={"x-modelspec-guide-version": "new-guide"},
            )
        raise httpx.ConnectError("Network down")

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    payload = assert_error(run(["decide", "--template", "test", "--json"], keyed=True))
    assert any("pipx upgrade modelspec-dev" in step for step in payload["next"])


def test_json_escaped_credential_reflection_is_redacted(monkeypatch):
    secret = 'live_"test\\credential'
    monkeypatch.setenv("MODELSPEC_API_KEY", secret)
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(
            lambda request: httpx.Response(
                401,
                json={"error": {"code": "invalid_api_key", "message": secret}},
            )
        ),
    )
    result = run(["vocab", "--json"])
    payload = assert_error(result, "invalid_api_key")
    assert "[redacted]" in payload["error"]["message"]
    assert secret not in result.output
    assert json.dumps(secret)[1:-1] not in result.output
