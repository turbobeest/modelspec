"""`modelspec decide --emit-router-config` (MODEL-208).

The Coding agent on a budget template, run through the CLI against a cached,
signed snapshot, emits each format; each passes the tool's own published schema
(vendored under tests/fixtures/router_schemas, see its README) and lists exactly
the decision's qualifying models.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import jsonschema
import pytest
import yaml
from typer.testing import CliRunner

from cli.modelspec import legacy as cli_mod
from decision import contract, router_config
from decision import snapshot as decision_snapshot
from decision.registry import default as default_registry
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from decision.vocabulary import build_vocabulary
from tests.snapshot_records import SOURCES, evidence, fact, model, offering
from tests.test_decision_cli import _test_ed25519_key

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = REPO_ROOT / "tests" / "fixtures" / "router_schemas"

# model, repo_work, patch_work, preference proxy, input price, providers
LINEUP = [
    ("lab/frontier", 74.0, 70.0, None, 1.2, ("anthropic", "aws-bedrock")),
    ("lab/solid", 72.0, 69.0, None, 0.8, ("openai", "azure-ai-foundry")),
    ("lab/budget", 55.0, 50.0, None, 0.1, ("deepseek",)),
    ("lab/older", 40.0, 38.0, 35.0, 0.3, ("xai",)),
    ("lab/mystery", None, None, 85.0, 0.05, ("zai",)),
]
TAGS = {"repo_work": [("software_engineering", "direct")],
        "patch_work": [("software_engineering", "direct")],
        "preference_proxy": [("software_engineering", "proxy")]}


BUDGET_CODING_SPEC = {
    "spec_version": 1,
    "where": [
        "model.class = text-generator",
        "model.lifecycle = active",
        "model.context_window >= 200000",
        "offering.cost_per_task <= 0.25",
    ],
    "optimize": {"weights": {"software_engineering": 0.6, "-offering.cost_per_task": 0.4}},
}


def _schema(path: Path) -> jsonschema.Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


@pytest.fixture
def budget_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    models, offerings, rows = [], [], []
    for mid, repo, patch, proxy, price, providers in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.lifecycle", "active"),
            fact("model", mid, "model.context_window", 200_000),
        ]))
        for step, provider in enumerate(providers):
            oid = f"{provider}/{mid}/global/standard"
            dearer = price * (1 + step / 10)
            offerings.append(offering(mid, provider, facts=[
                fact("offering", oid, "offering.price.input", dearer, source="src-pricing"),
                fact("offering", oid, "offering.price.output", 4 * dearer, source="src-pricing"),
            ]))
        for benchmark, score in (("repo_work", repo), ("patch_work", patch),
                                 ("preference_proxy", proxy)):
            if score is not None:
                rows.append(evidence(mid, benchmark, score, day="2026-09-01"))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains=TAGS,
                       benchmark_metadata={name: {"direction": "higher_is_better"}
                                           for name in TAGS}),
        registry=default_registry(), as_of=date(2026, 9, 27))
    cache = tmp_path / "cache"
    generation = cache / "decision" / built.snapshot_id
    generation.mkdir(parents=True)
    signer, public_keys = _test_ed25519_key("test-router-config")
    snapshot_bytes = built.to_bytes(key=None, ed25519_signer=signer)
    (generation / "snapshot.json.gz").write_bytes(snapshot_bytes)
    index = load_snapshot_bytes(snapshot_bytes, key=None, public_keys=public_keys)
    vocabulary = build_vocabulary(index)
    # The lineup's prices and bands are drawn for this spec. Pin it, so tuning the
    # registry template's thresholds (MODEL-204 moved the cap to $0.05) cannot
    # move a test about router output.
    template = next(row for row in vocabulary["templates"] if row["id"] == "budget-coding")
    template["spec"] = BUDGET_CODING_SPEC
    (generation / "vocabulary.json").write_text(
        json.dumps(vocabulary, ensure_ascii=False), encoding="utf-8")
    (cache / "decision" / "current").write_text(built.snapshot_id + "\n", encoding="utf-8")
    monkeypatch.setenv("MODELSPEC_CACHE", str(cache))
    monkeypatch.setattr(decision_snapshot, "load_public_keys", lambda: public_keys)
    return cache


def _run(*args: str):
    return CliRunner().invoke(cli_mod.app, ["decide", "--template", "budget-coding", *args])


@pytest.fixture
def decision(budget_cache) -> dict:
    result = _run("--json")
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def _band(decision: dict, name: str) -> list[str]:
    return [entry["model"] for entry in decision["bands"][name]]


def _audit_header(text: str, decision: dict) -> None:
    for key in ("decision_id", "spec_hash", "snapshot"):
        assert decision[key] in text


def test_the_lineup_has_every_band(decision) -> None:
    assert _band(decision, "best") == ["lab/solid", "lab/frontier", "lab/budget"]
    assert _band(decision, "rest") == ["lab/older"]
    assert _band(decision, "thin") == ["lab/mystery"]


def test_litellm_passes_its_schema_and_lists_exactly_the_best_band(decision) -> None:
    result = _run("--emit-router-config", "litellm")

    assert result.exit_code == 0, result.output
    text = result.stdout
    config = yaml.safe_load(text)
    _schema(SCHEMAS / "litellm-config-yaml.schema.json").validate(config)
    names = list(dict.fromkeys(row["model_name"] for row in config["model_list"]))
    assert names == _band(decision, "best")
    header = [line for line in text.splitlines() if line.startswith("#")]
    _audit_header("\n".join(header), decision)
    assert "# regenerate: modelspec decide --template budget-coding --emit-router-config litellm" \
        in header
    # Each qualifying offering is a deployment of its model, the band's own first.
    frontier = [row for row in config["model_list"] if row["model_name"] == "lab/frontier"]
    assert [row["litellm_params"]["model"] for row in frontier] == [
        "anthropic/<anthropic model id for lab/frontier>",
        "bedrock/<aws-bedrock model id for lab/frontier>",
    ]
    assert [row["model_info"]["id"] for row in frontier] == [
        "modelspec:anthropic/lab/frontier/global/standard",
        "modelspec:aws-bedrock/lab/frontier/global/standard",
    ]


def test_openrouter_passes_its_schema_and_lists_exactly_the_best_band(decision) -> None:
    result = _run("--emit-router-config", "openrouter")

    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    _schema(SCHEMAS / "openrouter-create-guardrail-request.schema.json").validate(body)
    assert body["allowed_models"] == [
        f"<openrouter model id for {model_id}>" for model_id in _band(decision, "best")]
    assert body["allowed_providers"] == [
        "openai", "azure", "anthropic", "amazon-bedrock", "deepseek"]
    _audit_header(body["description"], decision)
    assert body["name"] == f"modelspec {decision['decision_id']}"


def test_generic_json_passes_its_schema_and_carries_routes_and_reasons(decision) -> None:
    result = _run("--emit-router-config", "json")

    assert result.exit_code == 0, result.output
    body = json.loads(result.stdout)
    _schema(REPO_ROOT / "schemas" / "router-config-v1.schema.json").validate(body)
    assert [row["model"] for row in body["models"]] == _band(decision, "best")
    assert {key: body["audit"][key] for key in ("decision_id", "spec_hash", "snapshot")} == {
        key: decision[key] for key in ("decision_id", "spec_hash", "snapshot")}
    solid = body["models"][0]
    assert solid["band"] == "best" and solid["thin"] is False
    assert [route["offering_id"] for route in solid["routes"]] == [
        "openai/lab/solid/global/standard", "azure-ai-foundry/lab/solid/global/standard"]
    assert all(route["provider_model_id"] is None for route in solid["routes"])
    assert solid["reasons"][0] == "passed every Must"


def test_include_rest_adds_the_rest_band_after_the_best(decision) -> None:
    body = json.loads(_run("--emit-router-config", "json", "--include-rest").stdout)

    assert [(row["model"], row["band"]) for row in body["models"]] == [
        ("lab/solid", "best"), ("lab/frontier", "best"), ("lab/budget", "best"),
        ("lab/older", "rest"),
    ]
    assert body["bands"]["included"] == ["best", "rest"]


def test_thin_models_are_listed_only_when_asked_and_are_labelled(decision) -> None:
    for fmt in router_config.FORMATS:
        for extra in ((), ("--include-rest",)):
            assert "lab/mystery" not in _run("--emit-router-config", fmt, *extra).stdout

    litellm = _run("--emit-router-config", "litellm", "--include-thin").stdout
    assert "# thin: lab/mystery [thin: not enough evidence yet]" in litellm
    body = json.loads(_run("--emit-router-config", "json", "--include-thin").stdout)
    assert (body["models"][-1]["model"], body["models"][-1]["band"],
            body["models"][-1]["thin"]) == ("lab/mystery", "thin", True)
    openrouter = json.loads(_run("--emit-router-config", "openrouter", "--include-thin").stdout)
    assert openrouter["allowed_models"][-1] == "<openrouter model id for lab/mystery>"
    assert "Thin, not enough evidence yet: lab/mystery" in openrouter["description"]
    _schema(SCHEMAS / "openrouter-create-guardrail-request.schema.json").validate(openrouter)


def test_json_output_is_unchanged_when_the_config_goes_to_a_file(
    decision, budget_cache, tmp_path: Path,
) -> None:
    plain = _run("--json")
    out = tmp_path / "litellm.yaml"
    with_config = _run("--json", "--emit-router-config", "litellm", "--out", str(out))

    assert with_config.exit_code == 0, with_config.output
    assert with_config.stdout == plain.stdout
    config = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert {row["model_name"] for row in config["model_list"]} == set(_band(decision, "best"))


def test_config_to_a_file_leaves_the_readable_summary_on_stdout(
    decision, tmp_path: Path,
) -> None:
    plain = _run()
    out = tmp_path / "guardrail.json"
    with_config = _run("--emit-router-config", "openrouter", "--out", str(out))

    assert with_config.exit_code == 0, with_config.output
    assert with_config.stdout == plain.stdout
    assert json.loads(out.read_text(encoding="utf-8"))["allowed_models"][0] == (
        "<openrouter model id for lab/solid>")
    assert f"wrote openrouter router config: 3 models, 5 routes to {out}" in with_config.stderr


def _row(model_id: str, provider: str | None) -> router_config.Listed:
    ref = contract.OfferingRef(model=model_id, provider=provider)
    entry = contract.BandEntry(model=model_id, offering=ref, score=0.5, score_interval=(0.4, 0.6))
    return router_config.Listed(band="best", entry=entry,
                                routes=(router_config.Route(ref, None, 1),))


def test_a_model_with_no_provider_keeps_the_provider_restriction_for_the_rest() -> None:
    audit = {"decision_id": "dec_x", "spec_hash": "sha256:" + "0" * 64, "snapshot": "snap_x",
             "contract_version": contract.CONTRACT_VERSION}

    mixed = json.loads(router_config._openrouter(
        [_row("lab/hosted", "anthropic"), _row("lab/own", None)], audit, ["best"]))
    assert mixed["allowed_providers"] == ["anthropic"]
    assert "No provider named for lab/own" in mixed["description"]
    _schema(SCHEMAS / "openrouter-create-guardrail-request.schema.json").validate(mixed)

    unnamed = json.loads(router_config._openrouter([_row("lab/own", None)], audit, ["best"]))
    assert "allowed_providers" not in unnamed
    assert unnamed["allowed_models"] == ["<openrouter model id for lab/own>"]


def test_no_credential_and_no_referral_parameter_is_ever_written(decision) -> None:
    for fmt in router_config.FORMATS:
        output = _run("--emit-router-config", fmt, "--include-rest", "--include-thin").stdout
        # The LiteLLM header comment says how to add a key; the config itself holds none.
        text = "\n".join(line for line in output.splitlines() if not line.startswith("#"))
        assert not re.search(r"api_key|secret|token|sk-|password", text, re.IGNORECASE)
        assert not re.search(r"ref=|referr|affiliate|utm_|\?", text, re.IGNORECASE)


@pytest.mark.parametrize(("args", "message"), [
    (("--emit-router-config", "helicone"), "unknown router config format 'helicone'"),
    (("--emit-router-config", "litellm", "--json"), "needs --out PATH"),
    (("--include-rest",), "need --emit-router-config"),
    (("--out", "x.yaml"), "need --emit-router-config"),
    (("--emit-router-config", "json", "--why-not", "lab/older"), "cannot be combined"),
])
def test_usage_errors_exit_1(budget_cache, args, message) -> None:
    result = _run(*args)

    assert result.exit_code == 1
    assert message in result.stderr


def test_a_decision_without_a_leader_lists_nothing_unless_thin_is_asked_for(
    budget_cache, tmp_path: Path,
) -> None:
    only_thin = tmp_path / "thin.yaml"
    only_thin.write_text("where: [offering.provider = zai]\n", encoding="utf-8")
    runner = CliRunner()

    refused = runner.invoke(cli_mod.app, [
        "decide", str(only_thin), "--template", "budget-coding",
        "--emit-router-config", "json", "--json", "--out", str(tmp_path / "x.json")])
    assert refused.exit_code == 1
    error = json.loads(refused.stderr)["error"]
    assert error["code"] == "empty_allow_list"
    assert "--include-thin adds 1" in error["message"]
    assert not (tmp_path / "x.json").exists()

    asked = runner.invoke(cli_mod.app, [
        "decide", str(only_thin), "--template", "budget-coding",
        "--emit-router-config", "json", "--include-thin"])
    assert asked.exit_code == 0, asked.output
    assert [(row["model"], row["band"]) for row in json.loads(asked.stdout)["models"]] == [
        ("lab/mystery", "thin")]


def test_a_decision_with_no_feasible_model_lists_nothing(budget_cache, tmp_path: Path) -> None:
    none = tmp_path / "none.yaml"
    none.write_text("where: [model.context_window >= 900000]\n", encoding="utf-8")

    result = CliRunner().invoke(cli_mod.app, [
        "decide", str(none), "--template", "budget-coding", "--emit-router-config", "litellm"])

    assert result.exit_code == 1
    assert "no model passed every Must" in result.stderr


def test_every_litellm_prefix_is_a_litellm_provider() -> None:
    litellm = pytest.importorskip("litellm")
    known = {provider.value for provider in litellm.provider_list}
    assert set(router_config.LITELLM_PROVIDERS.values()) <= known


def test_the_litellm_proxy_loads_the_config(decision, tmp_path: Path) -> None:
    pytest.importorskip("litellm.proxy.proxy_server")
    import asyncio

    from litellm.proxy.proxy_server import ProxyConfig

    path = tmp_path / "config.yaml"
    path.write_text(_run("--emit-router-config", "litellm").stdout, encoding="utf-8")
    _router, model_list, _settings = asyncio.run(
        ProxyConfig().load_config(router=None, config_file_path=str(path)))
    assert [row["model_name"] for row in model_list] == [
        "lab/solid", "lab/solid", "lab/frontier", "lab/frontier", "lab/budget"]
