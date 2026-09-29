"""Outcome records are opt-in, local, and hold exactly the schema (MODEL-211, REV-9)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import cli as cli_mod  # noqa: E402
from cli.modelspec import outcome  # noqa: E402
from decision import snapshot as decision_snapshot  # noqa: E402
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes  # noqa: E402
from decision.vocabulary import build_vocabulary  # noqa: E402
from tests.snapshot_records import SOURCES, evidence, fact, model, offering  # noqa: E402
from tests.test_decision_cli import _test_ed25519_key  # noqa: E402

#: The whole schema. Adding a field must be a deliberate edit here, in the
#: consent text and in docs/cli-contract.md.
FIELDS = {
    "record_version", "decision_id", "spec_hash", "snapshot", "contract_version",
    "adopted_model", "adopted_offering", "was_leader", "in_best_band", "result",
    "task_kind", "latency_ms", "cost_usd", "recorded_at", "cli_version",
}

PROMPT = "Fix the login bug in acme-corp/billing; customer jane@acme.com says it 500s"
KEY = "sk-ant-api03-AbCdEf0123456789AbCdEf0123456789"
CUSTOMER = "acme-corp"

VALID = {
    "record_version": 1,
    "decision_id": "dec_0123456789abcdef01234567",
    "spec_hash": "sha256:" + "0" * 64,
    "snapshot": "snap_0123456789abcdef",
    "contract_version": "2.7",
    "adopted_model": "lab/coder",
    "adopted_offering": "provider",
    "was_leader": True,
    "in_best_band": True,
    "result": "success",
    "task_kind": "bug_fix",
    "latency_ms": 1200,
    "cost_usd": 0.04,
    "recorded_at": "2026-09-29T16:43Z",
    "cli_version": "0.1.1",
}


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "home"
    monkeypatch.setenv("MODELSPEC_HOME", str(path))
    monkeypatch.setenv("MODELSPEC_CACHE", str(tmp_path / "empty-cache"))
    return path


@pytest.fixture
def spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A cached snapshot where lab/coder leads and lab/other is in the rest band."""
    models, offerings, scores = [], [], []
    for mid, score in (("lab/coder", 70), ("lab/other", 40)):
        models.append(model(mid, facts=[fact("model", mid, "model.class", "text-generator")]))
        oid = f"openai/{mid}/global/standard"
        offerings.append(offering(mid, "openai", facts=[
            fact("offering", oid, "offering.price.input", 1.0, source="src-pricing"),
            fact("offering", oid, "offering.price.output", 2.0, source="src-pricing"),
        ]))
        scores.append(evidence(mid, "swe_bench_pro", score))
    built = build_snapshot(SnapshotInputs(
        models=models, offerings=offerings, evidence=scores, sources=SOURCES,
        benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
    ), gate=False)
    cache = tmp_path / "cache"
    generation = cache / "decision" / built.snapshot_id
    generation.mkdir(parents=True)
    signer, public_keys = _test_ed25519_key("test-outcome-fixture")
    snapshot_bytes = built.to_bytes(key=None, ed25519_signer=signer)
    (generation / "snapshot.json.gz").write_bytes(snapshot_bytes)
    index = load_snapshot_bytes(snapshot_bytes, key=None, public_keys=public_keys)
    (generation / "vocabulary.json").write_text(json.dumps(build_vocabulary(index)))
    (cache / "decision" / "current").write_text(built.snapshot_id + "\n")
    monkeypatch.setenv("MODELSPEC_CACHE", str(cache))
    monkeypatch.setattr(decision_snapshot, "load_public_keys", lambda: public_keys)
    path = tmp_path / "spec.yaml"
    path.write_text("spec_version: 1\noptimize:\n  max: swe_bench_pro\n")
    return path


def _decide(spec: Path):
    return CliRunner().invoke(cli_mod.app, ["decide", str(spec), "--json"])


def _invoke(*args: str):
    return CliRunner().invoke(cli_mod.app, ["outcome", *args])


def _files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*")) if root.exists() else []


# ── the schema ────────────────────────────────────────────────────────────


def test_the_schema_is_exactly_these_fields() -> None:
    assert set(outcome.OutcomeRecord.model_fields) == FIELDS
    assert outcome.OutcomeRecord.model_validate(VALID).model_dump() == VALID


@pytest.mark.parametrize("extra", ["prompt", "task", "api_key", "customer_id", "user",
                                   "repository", "hostname", "notes"])
def test_an_unknown_field_is_refused(extra: str) -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        outcome.OutcomeRecord.model_validate(VALID | {extra: PROMPT})


@pytest.mark.parametrize("field", sorted(
    name for name, value in VALID.items() if isinstance(value, str)))
@pytest.mark.parametrize("smuggled", [PROMPT, KEY, CUSTOMER, "lab/" + "x" * 200])
def test_no_string_field_accepts_prompt_key_or_identifier_text(field: str, smuggled: str) -> None:
    """Every string field is a closed literal or a bounded identifier pattern."""
    if field == "adopted_offering" and smuggled == CUSTOMER:
        pytest.skip("a provider slug is catalogue-checked by the command; see below")
    with pytest.raises(ValidationError):
        outcome.OutcomeRecord.model_validate(VALID | {field: smuggled})


@pytest.mark.parametrize(("field", "value"), [
    # Pattern-shaped payloads: no spaces, no capitals where the pattern allows none.
    ("decision_id", "dec_AcmeCorpJaneSmithSaysLoginBug500s"),
    ("decision_id", "dec_" + "a" * 25),
    ("snapshot", "snap_acme-corp.customer:jane"),
    ("cli_version", "1.4.0+acmecorp"),
    ("cli_version", "0.1.dev123+g1a2b3c4.d20260929"),
    ("latency_ms", 48213), ("cost_usd", 1234.56789012345),
    ("latency_ms", "1200"), ("latency_ms", -1), ("latency_ms", 1.5),
    ("cost_usd", "0.04"), ("cost_usd", float("nan")), ("cost_usd", -0.01),
    ("was_leader", "yes"), ("in_best_band", 1), ("record_version", 2),
    ("result", "succeeded"), ("task_kind", "write the payroll report"),
])
def test_numbers_and_flags_are_not_coerced(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        outcome.OutcomeRecord.model_validate(VALID | {field: value})


def test_the_consent_text_names_every_field() -> None:
    text = outcome.consent_text()
    for field in FIELDS:
        assert f"\n  {field} " in text, field


# ── consent ───────────────────────────────────────────────────────────────


def test_record_is_a_no_op_until_enabled(home: Path) -> None:
    result = _invoke("record", "dec_0123456789abcdef01234567", "--adopted", "lab/coder",
                     "--result", "success", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "command": "outcome record", "recorded": False, "reason": "disabled"}
    assert _files(home) == []


def test_enable_refuses_without_a_terminal_or_yes(home: Path) -> None:
    result = _invoke("enable")
    assert result.exit_code == 1
    assert "adopted_model" in result.stdout  # the text is shown before the refusal
    assert _files(home) == []


def test_enable_with_yes_prints_the_consent_and_turns_it_on(home: Path) -> None:
    result = _invoke("enable", "--yes")
    assert result.exit_code == 0, result.output
    assert outcome.consent_text() in result.stdout
    assert outcome.enabled()
    assert (home / "outcomes-consent.json").stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("consent", ['{"consent_version": 0}', '{"consent_version": true}',
                                     '{"consent_version": 1.0}', '[1]',
                                     '{"consent_version": 1, "all": true}'])
def test_a_consent_for_another_version_does_not_count(home: Path, consent: str) -> None:
    home.mkdir()
    (home / "outcomes-consent.json").write_text(consent)
    assert not outcome.enabled()


def test_the_cli_version_drops_a_local_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(outcome.metadata, "version", lambda _: "0.1.1.dev3+g1a2b3c4.laptop")
    assert outcome.cli_version() == "0.1.1.dev3"


def test_latency_and_cost_are_coarsened_to_three_figures(home: Path) -> None:
    _invoke("enable", "--yes")
    result = _invoke("record", VALID["decision_id"], "--adopted", "other", "--result", "success",
                     "--latency-ms", "48213", "--cost-usd", "1234.56789012345", "--json")
    assert result.exit_code == 0, result.output
    record = json.loads(result.stdout)["record"]
    assert (record["latency_ms"], record["cost_usd"]) == (48200, 1230.0)


def test_loose_permissions_are_tightened_and_symlinks_refused(tmp_path: Path, home: Path) -> None:
    home.mkdir(mode=0o755)
    (home / "outcomes.jsonl").write_text("")
    (home / "outcomes.jsonl").chmod(0o644)
    _invoke("enable", "--yes")
    assert _invoke("record", VALID["decision_id"], "--adopted", "other",
                   "--result", "success").exit_code == 0
    assert home.stat().st_mode & 0o777 == 0o700
    assert (home / "outcomes.jsonl").stat().st_mode & 0o777 == 0o600

    elsewhere = tmp_path / "elsewhere.jsonl"
    (home / "outcomes.jsonl").unlink()
    (home / "outcomes.jsonl").symlink_to(elsewhere)
    refused = _invoke("record", VALID["decision_id"], "--adopted", "other", "--result", "success")
    assert refused.exit_code == 1
    assert not elsewhere.exists()


def test_disable_is_one_command_and_delete_removes_the_records(home: Path) -> None:
    _invoke("enable", "--yes")
    _invoke("record", "dec_0123456789abcdef01234567", "--adopted", "other", "--result", "failure")
    assert (home / "outcomes.jsonl").is_file()

    kept = _invoke("disable")
    assert kept.exit_code == 0
    assert not outcome.enabled()
    assert "1 record stay in" in kept.stdout
    assert (home / "outcomes.jsonl").is_file()

    deleted = _invoke("disable", "--delete")
    assert deleted.exit_code == 0
    assert _files(home) == []


# ── recording ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(("args", "field"), [
    ((PROMPT, "--task-kind", "bug_fix"), "decision_id"),
    ((VALID["decision_id"], "--task-kind", KEY), "task_kind"),
])
def test_rejected_text_is_never_echoed(args: tuple[str, str, str], field: str) -> None:
    _invoke("enable", "--yes")
    decision_id, *rest = args
    result = _invoke("record", decision_id, "--adopted", "other", "--result", "success", *rest)
    assert result.exit_code == 1
    assert PROMPT not in result.output
    assert KEY not in result.output
    assert f"{field}:" in result.output


def test_an_uncatalogued_model_is_refused_and_other_names_nothing(home: Path) -> None:
    _invoke("enable", "--yes")
    refused = _invoke("record", "dec_0123456789abcdef01234567", "--adopted", f"{CUSTOMER}/private-ft",
                      "--result", "success")
    assert refused.exit_code == 1
    assert "--adopted other" in refused.output

    recorded = _invoke("record", "dec_0123456789abcdef01234567", "--adopted", "other",
                       "--result", "success", "--json")
    assert recorded.exit_code == 0, recorded.output
    line = (home / "outcomes.jsonl").read_text()
    assert CUSTOMER not in line
    assert json.loads(line)["adopted_model"] == "other"


def test_an_uncatalogued_provider_is_refused(spec: Path, home: Path) -> None:
    _invoke("enable", "--yes")
    result = _invoke("record", "dec_0123456789abcdef01234567", "--adopted", f"lab/coder/{CUSTOMER}",
                     "--result", "success")
    assert result.exit_code == 1
    assert "provider" in result.output
    assert not (home / "outcomes.jsonl").exists()


def test_decide_keeps_a_stub_only_when_enabled_and_record_resolves_it(
    spec: Path, home: Path,
) -> None:
    off = _decide(spec)
    assert off.exit_code == 0, off.output
    assert "outcome" not in off.stderr
    assert _files(home) == []

    _invoke("enable", "--yes")
    on = _decide(spec)
    assert on.exit_code == 0, on.output
    assert on.stdout == off.stdout  # stdout is still the decision, byte for byte
    decision = json.loads(on.stdout)
    assert f"outcome record {decision['decision_id']}" in on.stderr
    assert not (home / "outcomes.jsonl").exists()  # decide records no outcome

    stub = json.loads((home / "decision-stubs" / f"{decision['decision_id']}.json").read_text())
    assert set(stub) == {"decision_id", "spec_hash", "snapshot", "contract_version",
                         "leader", "best"}

    result = _invoke("record", decision["decision_id"], "--adopted", "lab/coder/openai",
                     "--result", "partial", "--latency-ms", "900", "--json")
    assert result.exit_code == 0, result.output
    record = json.loads(result.stdout)["record"]
    assert record | {"recorded_at": None, "cli_version": None} == {
        "record_version": 1,
        "decision_id": decision["decision_id"],
        "spec_hash": decision["spec_hash"],
        "snapshot": decision["snapshot"],
        "contract_version": decision["contract_version"],
        "adopted_model": "lab/coder",
        "adopted_offering": "openai",
        "was_leader": True,
        "in_best_band": True,
        "result": "partial",
        "task_kind": None,
        "latency_ms": 900,
        "cost_usd": None,
        "recorded_at": None,
        "cli_version": None,
    }

    for adopted in ("lab/other", "other"):
        rest = _invoke("record", decision["decision_id"], "--adopted", adopted,
                       "--result", "failure", "--json")
        assert rest.exit_code == 0, rest.output
        assert json.loads(rest.stdout)["record"]["was_leader"] is False
        assert json.loads(rest.stdout)["record"]["in_best_band"] is False

    _invoke("disable")
    assert not (home / "decision-stubs").exists()


def test_record_resolves_from_a_decision_file_and_keeps_none_of_it(
    tmp_path: Path, spec: Path, home: Path,
) -> None:
    decision = json.loads(_decide(spec).stdout)
    decision_file = tmp_path / "decision.json"
    decision_file.write_text(json.dumps(decision | {"prompt": PROMPT}))
    _invoke("enable", "--yes")

    wrong = _invoke("record", "dec_000000000000000000000000", "--adopted", "lab/coder",
                    "--result", "success", "--decision", str(decision_file))
    assert wrong.exit_code == 1
    assert "dec_000000000000000000000000" not in wrong.output

    result = _invoke("record", decision["decision_id"], "--adopted", "lab/coder",
                     "--result", "success", "--decision", str(decision_file), "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["record"]["was_leader"] is True
    assert PROMPT not in (home / "outcomes.jsonl").read_text()
    assert not (home / "decision-stubs").exists()


def test_show_and_export_emit_only_schema_valid_records(home: Path) -> None:
    _invoke("enable", "--yes")
    _invoke("record", "dec_0123456789abcdef01234567", "--adopted", "other", "--result", "success")
    with (home / "outcomes.jsonl").open("a") as handle:
        handle.write(json.dumps(VALID | {"prompt": PROMPT}) + "\n")
        handle.write("not json\n")

    exported = _invoke("export")
    assert exported.exit_code == 0
    lines = exported.stdout.splitlines()
    assert len(lines) == 1
    assert set(json.loads(lines[0])) == FIELDS
    assert PROMPT not in exported.stdout
    assert "2 lines did not match" in exported.stderr

    shown = _invoke("show", "--json")
    payload = json.loads(shown.stdout)
    assert (payload["enabled"], payload["count"], payload["refused_lines"]) == (True, 1, 2)
    assert PROMPT not in shown.stdout


def test_a_decision_file_cannot_vouch_for_an_uncatalogued_model(
    tmp_path: Path, spec: Path, home: Path,
) -> None:
    decision = json.loads(_decide(spec).stdout)
    private = f"{CUSTOMER}/jane-private-finetune"
    crafted = decision | {"bands": decision["bands"] | {
        "leader": private, "best": [{"model": private}]}}
    decision_file = tmp_path / "crafted.json"
    decision_file.write_text(json.dumps(crafted))
    _invoke("enable", "--yes")
    result = _invoke("record", decision["decision_id"], "--adopted", private,
                     "--result", "success", "--decision", str(decision_file))
    assert result.exit_code == 1
    assert "--adopted other" in result.output
    assert not (home / "outcomes.jsonl").exists()


@pytest.mark.parametrize("change", [
    {"snapshot": "snap_0123456789abcdef"},       # the ID no longer hashes these fields
    {"spec_hash": "sha256:" + "1" * 64},
    {"bands": "leader"},                          # malformed shapes fail cleanly
    {"answer": "lab/coder"},
    {"bands": {"best": ["lab/coder"]}},
])
def test_a_crafted_or_malformed_decision_file_is_refused(
    tmp_path: Path, spec: Path, home: Path, change: dict,
) -> None:
    decision = json.loads(_decide(spec).stdout)
    decision_file = tmp_path / "crafted.json"
    decision_file.write_text(json.dumps(decision | change))
    _invoke("enable", "--yes")
    result = _invoke("record", decision["decision_id"], "--adopted", "lab/coder",
                     "--result", "success", "--decision", str(decision_file))
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)  # an error message, not a traceback
    assert "invalid_decision" in _invoke(
        "record", decision["decision_id"], "--adopted", "lab/coder", "--result", "success",
        "--decision", str(decision_file), "--json").stderr
    assert not (home / "outcomes.jsonl").exists()
