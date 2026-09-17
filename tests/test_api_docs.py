"""MODEL-72: the API reference and the OpenAPI spec cannot drift from the Worker.

Documentation rots silently, so nothing here reads the prose for plausibility.
Every assertion is between a document and the implementation:

* `api/worker/openapi.yaml` must be exactly what `api/worker/openapi.py`
  generates from `rank_service`, `entry.py` and the scorer — so a field added to
  a response, a new enum value or a new refusal fails the build until the spec
  is regenerated;
* every `error.code` the two Worker modules can emit must appear in
  `docs/api.md` with a stated fix, and every `HTTP_*` status with it;
* the request in the spec must be one the parser accepts and the endpoint
  answers with a 200, so the documented example cannot become a request that
  fails;
* the quotas in the reference must be the numbers in `tiers.json`, and the claim
  that the access gate is **not live** must remain true — the test fails the day
  the gate is wired, which is the day the reference has to change.

The live endpoint is exercised by `api/worker/openapi.py --probe`, which CI runs
after a deploy. It is opt-in here (`MODELSPEC_LIVE_API=1`) so the suite needs no
network.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.ranking.engine import (  # noqa: E402
    CLOUD_PLATFORMS,
    LOCAL_PLATFORMS,
    PROVIDER_PLATFORMS,
    USE_CASE_PROFILES,
)

REFERENCE = REPO_ROOT / "docs" / "api.md"
SPEC_PATH = REPO_ROOT / "api" / "worker" / "openapi.yaml"
TIERS_PATH = REPO_ROOT / "api" / "worker" / "tiers.json"
ENTRY = REPO_ROOT / "api" / "worker" / "src" / "entry.py"

#: The reference's own budget, from the ticket. Fenced blocks are the worked
#: example and the OpenAPI document, which the ticket excludes.
WORD_BUDGET = 800


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load(REPO_ROOT / "api" / "worker" / "openapi.py", "modelspec_openapi_generator")
service = generator.service


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reference() -> str:
    return REFERENCE.read_text(encoding="utf-8")


def _prose(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def _error_table(text: str) -> dict[str, str]:
    """`error.code -> the stated fix`, read out of the reference's own table."""
    fixes: dict[str, str] = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or not cells[0].isdigit():
            continue
        code = cells[1].strip("`*")
        fixes[code] = cells[3]
    return fixes


# ── the spec is generated, not maintained ────────────────────────────────────

def test_the_committed_spec_is_what_the_implementation_generates() -> None:
    """The one assertion that makes every other document trustworthy."""
    assert SPEC_PATH.read_text(encoding="utf-8") == generator.render(), (
        "api/worker/openapi.yaml no longer matches the implementation. Run "
        "`python api/worker/openapi.py` and commit the result.")


def test_the_spec_names_this_service_and_its_paths(spec: dict[str, Any]) -> None:
    assert spec["openapi"].startswith("3.")
    assert spec["servers"][0]["url"] == "https://api.modelspec.dev"
    assert set(spec["paths"]) == {"/v1/rank", "/v1/health"}
    assert spec["info"]["version"] == service.SCHEMA_VERSION


def test_the_request_vocabulary_is_the_engines(spec: dict[str, Any]) -> None:
    properties = spec["components"]["schemas"]["RankRequest"]["properties"]
    assert properties["use_case"]["enum"] == sorted(USE_CASE_PROFILES)
    environment = properties["environment"]["properties"]
    assert environment["hosting"]["enum"] == [*sorted(service.HOSTING_MODES), None]
    assert environment["runtime"]["enum"] == [
        *sorted(LOCAL_PLATFORMS | CLOUD_PLATFORMS | PROVIDER_PLATFORMS), None]
    assert properties["limit"]["maximum"] == service.MAX_LIMIT
    assert spec["info"]["x-max-request-bytes"] == service.MAX_BODY_BYTES


def test_every_status_the_worker_can_return_is_in_the_spec(spec: dict[str, Any]) -> None:
    documented = set(spec["paths"]["/v1/rank"]["post"]["responses"])
    documented |= set(spec["paths"]["/v1/health"]["get"]["responses"])
    emitted = {str(value) for name, value in vars(service).items()
               if name.startswith("HTTP_") and isinstance(value, int)}
    assert emitted - documented == set(), (
        "the Worker has a status the spec does not describe: "
        f"{sorted(emitted - documented)}")


# ── the documented request works ─────────────────────────────────────────────

def test_the_spec_example_is_a_request_the_endpoint_answers(spec: dict[str, Any]) -> None:
    """Built from the spec alone, and answered by the real code with a 200."""
    content = spec["paths"]["/v1/rank"]["post"]["requestBody"]["content"]["application/json"]
    example = generator._example_from_schema(content, spec)
    assert example == content["example"], "the spec's example is not what the spec describes"

    status, body = service.rank(example, generator._export(), generator._HARDWARE,
                                "0" * 40, "https://modelspec.dev")
    assert status == service.HTTP_OK, body
    assert body["result"], "the documented example returned an empty shortlist"

    problems = generator._validate(body, spec["components"]["schemas"]["RankResponse"], spec)
    assert problems == [], problems


def test_the_worked_example_in_the_reference_is_the_documented_shape(reference: str) -> None:
    """The pasted response must still be a body this spec would accept."""
    import json

    blocks = re.findall(r"```json\n(.*?)```", reference, flags=re.S)
    assert blocks, "the reference has no worked response"
    body = json.loads(blocks[0])
    assert body["schema_version"] == service.SCHEMA_VERSION
    assert set(body) >= {"build", "service_commit", "applied", "policy", "result"}
    row = body["result"][0]
    assert row["evidence_basis"] in generator.VOCABULARIES["evidence_basis"]()
    assert body["ranking_status"] in generator.VOCABULARIES["ranking_status"]()


# ── every error, with its fix ────────────────────────────────────────────────

def test_every_error_code_the_worker_emits_has_a_documented_fix(reference: str) -> None:
    fixes = _error_table(reference)
    missing = sorted(generator.source_error_codes() - set(fixes))
    assert missing == [], (
        f"docs/api.md does not tell a caller what to do about: {missing}")
    for code, fix in fixes.items():
        assert len(fix.split()) >= 3, f"{code} has no usable fix: {fix!r}"


def test_every_refusal_status_is_documented(reference: str) -> None:
    statuses = {int(line.strip().strip("|").split("|")[0].strip())
                for line in reference.splitlines()
                if line.strip().startswith("| 4") or line.strip().startswith("| 5")}
    emitted = {value for name, value in vars(service).items()
               if name.startswith("HTTP_") and isinstance(value, int) and value >= 400}
    assert emitted <= statuses, f"undocumented status(es): {sorted(emitted - statuses)}"


def test_a_no_match_names_the_constraint_to_relax(reference: str) -> None:
    """The 422 the reference promises is the 422 the endpoint produces."""
    status, body = service.rank(
        {"use_case": "coding", "constraints": {"max_cost_per_million_input_tokens": 0.0}},
        generator._export(), generator._HARDWARE, "0" * 40, "https://modelspec.dev")
    assert status == service.HTTP_NO_MATCH
    error = body["error"]
    assert error["code"] == "no_match"
    assert error["relax"] == "constraints.max_cost_per_million_input_tokens"
    assert error["eliminated_by"]["survivors_after"] == 0
    assert "error.relax" in reference


# ── the reference's own budget, and its honesty ──────────────────────────────

def test_the_reference_is_under_the_word_budget(reference: str) -> None:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'`_./-]*", _prose(reference))
    assert len(words) < WORD_BUDGET, (
        f"docs/api.md is {len(words)} words of prose; the budget is {WORD_BUDGET}")


def test_the_reference_starts_with_a_use_when_sentence(reference: str) -> None:
    head = reference.split("\n\n", 2)[1]
    assert head.startswith("**Use when**"), head


def test_the_quotas_in_the_reference_are_the_numbers_in_tiers_json(reference: str) -> None:
    import json

    policy = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
    free = policy["tiers"]["free"]
    assert re.search(rf"\|\s*free\s*\|\s*{free['daily_limit']}\s*\|"
                     rf"\s*{free['burst_limit']}/min\s*\|", reference), (
        "the free tier's quota in docs/api.md is not the one in tiers.json")
    for unlimited in ("sandbox", "dpf"):
        assert policy["tiers"][unlimited]["daily_limit"] is None, (
            f"docs/api.md calls the {unlimited} tier unlimited; tiers.json now sets a limit")
    assert f"`{policy['sandbox_prefix']}`" in reference, (
        "the reference must name the sandbox key prefix tiers.json actually uses")


def test_the_access_gate_is_still_unwired_so_the_not_live_warning_is_true() -> None:
    """The day someone wires MODEL-69 in, this fails and the docs must change."""
    entry = ENTRY.read_text(encoding="utf-8")
    assert "import access" not in entry and "access.serve" not in entry, (
        "entry.py now uses the access layer. docs/api.md and openapi.yaml still say keys, "
        "quotas and the sandbox are not live — update both.")
    reference = REFERENCE.read_text(encoding="utf-8")
    assert "not live yet" in reference.lower()
    assert "takes no key and meters nothing" in reference


def test_nothing_links_a_page_that_does_not_exist(reference: str) -> None:
    """MODEL-70 has not published terms or the neutrality commitment."""
    for absent in ("modelspec.dev/terms", "modelspec.dev/pricing",
                   "modelspec.dev/docs/api", "neutrality.json"):
        assert f"](https://{absent}" not in reference, (
            f"docs/api.md links {absent}, which returns 404 until MODEL-70 ships")
    assert "MODEL-70" in reference, "the missing terms and neutrality commitment must be stated"


def test_the_spec_records_the_unwired_access_layer(spec: dict[str, Any]) -> None:
    import json

    block = spec["x-modelspec-not-yet-live"]
    assert "NOT wired" in block["status"]
    tiers = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
    assert block["when_wired"]["sandbox_prefix"] == tiers["sandbox_prefix"]
    assert block["when_wired"]["tiers"]["sandbox"]["daily_limit"] is None
    assert "401" in block["effect_today"]
    assert "security" not in spec, "the live endpoint requires no credential"


# ── the gate stays in CI ─────────────────────────────────────────────────────

def test_ci_checks_the_spec_and_probes_it_after_a_deploy() -> None:
    """Docs that are only checked locally drift the moment nobody looks."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "rank-api.yml").read_text(encoding="utf-8")
    assert "python api/worker/openapi.py --check" in workflow
    assert "python -m pytest -q tests/test_api_docs.py" in workflow
    assert "openapi.py --probe" in workflow
    bundle, deploy = workflow.split("\n  deploy:", 1)
    assert "--check" in bundle, "the drift check must run on pull requests, not only on main"
    assert "--probe" in deploy, "the live proof belongs after the deploy"


# ── the live proof, opt-in ───────────────────────────────────────────────────

@pytest.mark.skipif(os.environ.get("MODELSPEC_LIVE_API") != "1",
                    reason="set MODELSPEC_LIVE_API=1 to call api.modelspec.dev")
def test_a_request_built_only_from_the_spec_succeeds_against_the_live_service() -> None:
    assert generator.probe("https://api.modelspec.dev") == 0
