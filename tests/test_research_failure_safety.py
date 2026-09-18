"""MODEL-5: a deliberately broken source must fail the run, not damage data.

Exercises the seeder against a mocked HTTP layer only -- no real network
calls are made. Proves four properties:

1. When models.dev is unreachable, returns non-200, returns malformed JSON,
   or returns JSON missing the expected provider/model shape, the seeder
   exits non-zero with a clear message. It must never exit 0 having done
   nothing, which reads as "no new models today".
2. None of those failure modes modifies, deletes, or truncates an existing
   card. Verified against a temporary copy of real cards from models/.
3. A card that fails validation cannot reach a pull request -- the workflow
   YAML's validation step runs, and fails the job, before create-pull-request.
4. A write that dies partway through processing leaves no half-written card
   file behind; a card written before the crash stays complete.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "daily-research.yml"

from scripts import seed_models_dev as seeder  # noqa: E402


class _JudgesPageAsCreator:
    """Stub TypeSafe judge (MODEL-82): these fixtures are the page's own models.

    ``test-model-a`` names no organisation, so attribution asks for a judgment.
    Never calls the API; picks the first offered organisation with full
    confidence and says the page is not reselling.
    """

    model = "jev-test"

    def evaluate(self, state, questions):
        option = next(iter(questions["creator"]["criteria"]))
        return {
            "answers": {
                "creator": {"choice": option, "probabilities": {option: 1.0}, "confidence": 1.0},
                "reseller": {"noul": 0.0},
            },
            "usage": {"input_tokens": 0},
        }


# ─────────────────────────────────────────────────────────────────────────
# Fakes for the HTTP layer. No test in this file makes a real request.
# ─────────────────────────────────────────────────────────────────────────


class _FakeResponse:
    def __init__(
        self,
        status_code: int = 200,
        json_data: Any = None,
        json_error: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data
        self._json_error = json_error

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", seeder.MODELS_DEV_URL)
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"{self.status_code} error", request=request, response=response
            )

    def json(self) -> Any:
        if self._json_error is not None:
            raise self._json_error
        return self._json_data


def _get_raising(exc: Exception):
    def _get(*args: Any, **kwargs: Any) -> _FakeResponse:
        raise exc

    return _get


def _get_returning(response: _FakeResponse):
    def _get(*args: Any, **kwargs: Any) -> _FakeResponse:
        return response

    return _get


FAILURE_MODES = {
    "unreachable": _get_raising(
        httpx.ConnectError(
            "Connection refused", request=httpx.Request("GET", seeder.MODELS_DEV_URL)
        )
    ),
    "non_200": _get_returning(_FakeResponse(status_code=503)),
    "malformed_json": _get_returning(
        _FakeResponse(json_error=json.JSONDecodeError("Expecting value", "not json", 0))
    ),
    "not_an_object": _get_returning(_FakeResponse(json_data=["openai", "anthropic"])),
    "no_known_provider": _get_returning(_FakeResponse(json_data={"unexpected": "shape"})),
    "provider_missing_models_key": _get_returning(
        _FakeResponse(json_data={"openai": {"not_models": {}}})
    ),
}


def _run_main_expecting_exit(monkeypatch: pytest.MonkeyPatch, mode: str) -> pytest.ExceptionInfo:
    monkeypatch.setattr(seeder.httpx, "get", FAILURE_MODES[mode])
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only"])
    with pytest.raises(SystemExit) as exc_info:
        seeder.main()
    return exc_info


# ─────────────────────────────────────────────────────────────────────────
# Property 1: every broken-source shape exits non-zero with a clear message.
# ─────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("mode", sorted(FAILURE_MODES))
def test_broken_source_exits_nonzero_with_clear_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], mode: str
) -> None:
    exc_info = _run_main_expecting_exit(monkeypatch, mode)

    assert exc_info.value.code not in (0, None), (
        f"mode {mode!r} must not exit 0/None -- that reads as a quiet day "
        "with no new models"
    )

    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert captured.err.strip(), "must print a message explaining the failure"


def test_fetch_models_dev_raises_source_error_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit-level check that each shape is rejected by check_payload/fetch_models_dev."""
    for mode in FAILURE_MODES:
        monkeypatch.setattr(seeder.httpx, "get", FAILURE_MODES[mode])
        with pytest.raises(seeder.SourceError):
            seeder.fetch_models_dev()


# ─────────────────────────────────────────────────────────────────────────
# Property 2: none of those failure modes touches an existing card.
# ─────────────────────────────────────────────────────────────────────────


def _copy_sample_cards(dest_models_dir: Path) -> dict[Path, bytes]:
    """Copy a few real *.md cards into dest_models_dir; return the originals' bytes."""
    originals: dict[Path, bytes] = {}
    for provider_dir in sorted((REPO_ROOT / "models").iterdir()):
        if not provider_dir.is_dir():
            continue
        for card in sorted(provider_dir.glob("*.md"))[:1]:
            rel = card.relative_to(REPO_ROOT / "models")
            dest = dest_models_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = card.read_bytes()
            dest.write_bytes(data)
            originals[dest] = data
        if len(originals) >= 3:
            break
    assert len(originals) >= 3, "expected at least 3 real cards to copy as fixtures"
    return originals


@pytest.mark.parametrize("mode", sorted(FAILURE_MODES))
def test_broken_source_leaves_existing_cards_byte_for_byte_untouched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mode: str
) -> None:
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    originals = _copy_sample_cards(models_dir)

    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    _run_main_expecting_exit(monkeypatch, mode)

    for path, original_bytes in originals.items():
        assert path.is_file(), f"{path} was deleted"
        assert path.read_bytes() == original_bytes, f"{path} was modified or truncated"

    all_files = {p for p in models_dir.rglob("*") if p.is_file()}
    assert all_files == set(originals), (
        "no new, stray, or partial files should appear when the source is broken: "
        f"found {all_files - set(originals)}"
    )


# ─────────────────────────────────────────────────────────────────────────
# Property 3: a card that fails validation cannot reach a pull request.
# ─────────────────────────────────────────────────────────────────────────


def _workflow_steps() -> list[dict[str, Any]]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["research"]["steps"]
    assert isinstance(steps, list)
    return steps


def _index_of(steps: list[dict[str, Any]], predicate) -> int:
    for index, step in enumerate(steps):
        if predicate(step):
            return index
    raise AssertionError("no matching step found")


def test_validation_failure_stops_the_job_before_create_pull_request() -> None:
    steps = _workflow_steps()

    validate_index = _index_of(
        steps, lambda s: "validate everything" in (s.get("name") or "").lower()
    )
    pr_index = _index_of(
        steps,
        lambda s: (s.get("uses") or "").startswith("peter-evans/create-pull-request"),
    )

    assert validate_index < pr_index, (
        "the validation step must run, and be able to fail the job, before "
        "create-pull-request -- otherwise an invalid card can reach a PR"
    )

    validate_step = steps[validate_index]
    script = validate_step["run"]
    assert 'report["invalid"]' in script
    assert "sys.exit(1)" in script

    # No step may opt out of failing the job -- that would let the workflow
    # limp past validation with an invalid card still on disk.
    for step in steps:
        assert step.get("continue-on-error") in (None, False), (
            f"step {step.get('name')!r} sets continue-on-error, which would "
            "let the job proceed past a real failure"
        )

    # The PR step's own guard must not force it to run regardless of the
    # earlier steps' outcome.
    pr_if = steps[pr_index].get("if", "")
    assert "always()" not in pr_if


def test_validate_pr_all_is_what_gates_the_pull_request() -> None:
    """The validation step really does invoke the project's own validator."""
    steps = _workflow_steps()
    validate_step = steps[
        _index_of(steps, lambda s: "validate everything" in (s.get("name") or "").lower())
    ]
    assert "validate_pr.py" in validate_step["run"]
    assert "--all" in validate_step["run"]


def test_survey_step_surfaces_its_output_and_fails_when_the_seeder_does() -> None:
    """A broken source makes the seeder exit non-zero (see property 1 above).

    The survey step redirects the seeder's stdout/stderr into survey.txt, so
    a non-zero exit there must still (a) print survey.txt to the Actions log
    and (b) fail the step -- otherwise the ERROR message this whole file
    proves the seeder emits is captured in a file nobody looks at, and the
    step reports success regardless.
    """
    steps = _workflow_steps()
    survey_step = steps[
        _index_of(steps, lambda s: "what is missing" in (s.get("name") or "").lower())
    ]
    script = survey_step["run"]

    assert "cat survey.txt" in script, (
        "the survey step must print survey.txt when the seeder fails, or a "
        "broken-source error is captured but never seen"
    )
    assert "exit 1" in script, (
        "the survey step must fail the job when the seeder exits non-zero"
    )
    assert survey_step.get("continue-on-error") in (None, False)


# ─────────────────────────────────────────────────────────────────────────
# Property 4: a write that dies partway leaves no half-written card.
# ─────────────────────────────────────────────────────────────────────────


def test_atomic_write_failure_leaves_no_temp_or_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "card.md"

    def _boom(*args: Any, **kwargs: Any) -> None:
        raise OSError("disk exploded")

    monkeypatch.setattr(seeder.os, "fsync", _boom)

    with pytest.raises(OSError):
        seeder.write_card_atomically(target, "some content\n")

    assert not target.exists(), "a failed write must not create the destination"
    leftover = list(tmp_path.iterdir())
    assert leftover == [], f"stray temp files left behind: {leftover}"


def test_atomic_write_failure_does_not_touch_existing_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "card.md"
    target.write_text("existing good content\n", encoding="utf-8")

    def _boom(*args: Any, **kwargs: Any) -> None:
        raise OSError("disk exploded")

    monkeypatch.setattr(seeder.os, "replace", _boom)

    with pytest.raises(OSError):
        seeder.write_card_atomically(target, "new content that must not land\n")

    assert target.read_text(encoding="utf-8") == "existing good content\n"
    leftover = [p for p in tmp_path.iterdir() if p != target]
    assert leftover == [], f"stray temp files left behind: {leftover}"


def test_crash_partway_through_providers_leaves_no_half_written_card(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    models_dir = tmp_path / "models"
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "make_judge", lambda config: _JudgesPageAsCreator())

    api_data = {
        "openai": {
            "models": {"test-model-a": {"id": "test-model-a", "name": "Test Model A"}}
        },
        "anthropic": {
            "models": {"test-model-b": {"id": "test-model-b", "name": "Test Model B"}}
        },
    }
    monkeypatch.setattr(
        seeder.httpx, "get", _get_returning(_FakeResponse(json_data=api_data))
    )

    real_write = seeder.write_card_atomically
    calls = {"n": 0}

    def _flaky_write(file_path: Path, content: str) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("simulated crash mid-run")
        real_write(file_path, content)

    monkeypatch.setattr(seeder, "write_card_atomically", _flaky_write)
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py"])

    with pytest.raises(SystemExit) as exc_info:
        seeder.main()
    assert exc_info.value.code != 0

    all_files = sorted(p for p in models_dir.rglob("*") if p.is_file())
    assert len(all_files) == 1, f"expected only the card written before the crash, got {all_files}"

    # The surviving card is complete and parses -- not truncated by the crash
    # that hit the *next* model.
    seeder.ModelCard.from_yaml_file(all_files[0])


def test_card_that_fails_round_trip_validation_is_never_written(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Validate-before-write: a card that does not round-trip must not reach disk.

    The seeder validates by loading the serialized YAML back into a ModelCard
    before it ever calls write_card_atomically. If that ordering were reversed
    (write, then validate -- the original code), a card that fails validation
    would already be sitting on disk by the time the error is caught.
    """
    models_dir = tmp_path / "models"
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "make_judge", lambda config: _JudgesPageAsCreator())

    api_data = {
        "openai": {
            "models": {"test-model-bad": {"id": "test-model-bad", "name": "Test Model Bad"}}
        },
    }
    monkeypatch.setattr(seeder.httpx, "get", _get_returning(_FakeResponse(json_data=api_data)))
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py"])

    def _reject(content: str):
        raise ValueError("simulated: this card does not round-trip")

    monkeypatch.setattr(seeder.ModelCard, "from_yaml_string", staticmethod(_reject))

    with pytest.raises(SystemExit) as exc_info:
        seeder.main()
    assert exc_info.value.code != 0

    all_files = [p for p in models_dir.rglob("*") if p.is_file()]
    assert all_files == [], f"a card that failed validation must not be written: {all_files}"
