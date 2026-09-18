"""MODEL-72: the API reference and the OpenAPI spec cannot drift from the Worker.

Documentation rots silently, so nothing here reads the prose for plausibility.
Every assertion is between a document and the implementation:

* `api/worker/openapi.yaml` must be exactly what `api/worker/openapi.py`
  generates from `rank_service`, `policy_service`, `entry.py` and the scorer —
  so a field added to a response, a new enum value or a new refusal fails the
  build until the spec is regenerated;
* the spec's operations must be exactly the endpoints `entry.py` routes;
* every `error.code` each endpoint can emit must appear in its reference
  (`docs/api.md` for rank, `docs/api-policy-check.md` for policy-check) with a
  stated fix, and every `HTTP_*` status with it;
* the requests in the spec must be ones the parsers accept and the endpoints
  answer with a 200, and the worked responses pasted in the references must
  validate against the spec — they are real captures, not illustrations;
* the policy verdicts are a tagged union in the spec: a check or row carrying a
  sibling variant's key is invalid, which is what stops a spec-driven client
  reading `undetermined` as a pass;
* the quotas in the reference must be the numbers in `tiers.json`, and what the
  references say about keys must match the deployed switch: the access gate is
  wired with `ACCESS_ENFORCED` off, so a key is optional and a presented one is
  checked. The tests fail the day the switch or the key store binding changes,
  which is the day the references have to change;
* the neutrality commitment (MODEL-70) is live as data and linked; the terms
  are drafts and are not presented as in force. Each of those flips a test the
  day it stops being true.

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
POLICY_REFERENCE = REPO_ROOT / "docs" / "api-policy-check.md"
SPEC_PATH = REPO_ROOT / "api" / "worker" / "openapi.yaml"
TIERS_PATH = REPO_ROOT / "api" / "worker" / "tiers.json"
ENTRY = REPO_ROOT / "api" / "worker" / "src" / "entry.py"

#: The reference's own budget, from the ticket. Fenced blocks are the worked
#: example and the OpenAPI document, which the ticket excludes. It applies per
#: reference: one endpoint's reference did not fit twice in 800 words, so
#: policy-check has its own page under the same budget rather than an
#: overrun one (MODEL-72, after MODEL-80 landed).
WORD_BUDGET = 800
REFERENCES = (REFERENCE, POLICY_REFERENCE)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = _load(REPO_ROOT / "api" / "worker" / "openapi.py", "modelspec_openapi_generator")
service = generator.service
policy = generator.policy


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reference() -> str:
    return REFERENCE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def policy_reference() -> str:
    return POLICY_REFERENCE.read_text(encoding="utf-8")


def _statuses(module: Any, floor: int = 0) -> set[int]:
    return {value for name, value in vars(module).items()
            if name.startswith("HTTP_") and isinstance(value, int) and value >= floor}


def _worked_response(text: str) -> dict[str, Any]:
    import json

    blocks = re.findall(r"```json\n(.*?)```", text, flags=re.S)
    assert blocks, "the reference has no worked response"
    return json.loads(blocks[0])


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


def test_the_spec_describes_exactly_the_endpoints_the_worker_routes(spec: dict[str, Any]) -> None:
    """Read from `entry.ACCEPTED_ENDPOINTS`, the list every 404 names back."""
    import ast

    tree = ast.parse(ENTRY.read_text(encoding="utf-8"))
    routed = next(
        {elt.value for elt in node.value.elts}
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ACCEPTED_ENDPOINTS")
    described = {f"{method.upper()} {path}"
                 for path, operations in spec["paths"].items() for method in operations}
    assert described == routed, (
        f"entry.py routes {sorted(routed)}; the spec describes {sorted(described)}")
    assert spec["openapi"].startswith("3.")
    assert spec["servers"][0]["url"] == "https://api.modelspec.dev"
    assert spec["info"]["version"] == service.SCHEMA_VERSION == policy.SCHEMA_VERSION


def test_the_request_vocabulary_is_the_engines(spec: dict[str, Any]) -> None:
    properties = spec["components"]["schemas"]["RankRequest"]["properties"]
    assert properties["use_case"]["enum"] == sorted(USE_CASE_PROFILES)
    environment = properties["environment"]["properties"]
    assert environment["hosting"]["enum"] == [*sorted(service.HOSTING_MODES), None]
    assert environment["runtime"]["enum"] == [
        *sorted(LOCAL_PLATFORMS | CLOUD_PLATFORMS | PROVIDER_PLATFORMS), None]
    assert properties["limit"]["maximum"] == service.MAX_LIMIT
    assert spec["info"]["x-max-request-bytes"] == {
        "/v1/rank": service.MAX_BODY_BYTES, "/v1/policy-check": policy.MAX_BODY_BYTES}


def test_the_policy_request_vocabulary_is_the_parsers(spec: dict[str, Any]) -> None:
    from pipeline.policy_export import platform_classes

    properties = spec["components"]["schemas"]["PolicyCheckRequest"]["properties"]
    assert properties["verdicts"]["items"]["enum"] == list(policy.VERDICTS)
    assert properties["platforms"]["items"]["enum"] == platform_classes()["all"]
    assert properties["limit"]["maximum"] == policy.MAX_LIMIT
    assert properties["limit"]["default"] == policy.DEFAULT_LIMIT
    assert properties["models"]["maxItems"] == policy.MAX_NAMED_MODELS
    accepted = generator._reject_unknown_sets()
    assert sorted(properties) == accepted["top-level"]
    assert sorted(properties["policy"]["properties"]) == accepted["policy"]


def test_every_status_the_worker_can_return_is_in_the_spec(spec: dict[str, Any]) -> None:
    rank = set(spec["paths"]["/v1/rank"]["post"]["responses"])
    rank |= set(spec["paths"]["/v1/health"]["get"]["responses"])
    missing = {str(s) for s in _statuses(service)} - rank
    assert missing == set(), f"the rank Worker has a status the spec does not describe: {missing}"

    checked = set(spec["paths"]["/v1/policy-check"]["post"]["responses"])
    missing = {str(s) for s in _statuses(policy)} - checked
    assert missing == set(), f"policy-check has a status the spec does not describe: {missing}"


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


def test_the_policy_example_is_a_request_the_endpoint_answers(spec: dict[str, Any]) -> None:
    content = spec["paths"]["/v1/policy-check"]["post"]["requestBody"]["content"][
        "application/json"]
    example = generator._example_from_schema(content, spec)
    assert example == content["example"]
    assert generator._validate(example, content["schema"], spec) == []

    status, body = generator._policy_answer(example)
    assert status == policy.HTTP_OK, body
    assert body["determinations"]["entitlement"] == policy.ENTITLEMENT_PUBLIC
    problems = generator._validate(
        body, spec["components"]["schemas"]["PolicyCheckResponse"], spec)
    assert problems == [], problems


def test_both_worked_responses_validate_against_the_spec(
        spec: dict[str, Any], reference: str, policy_reference: str) -> None:
    """The pasted responses are real captures, so they must be bodies the spec accepts."""
    schemas = spec["components"]["schemas"]
    rank = _worked_response(reference)
    assert rank["schema_version"] == service.SCHEMA_VERSION
    assert generator._validate(rank, schemas["RankResponse"], spec) == []

    checked = _worked_response(policy_reference)
    assert checked["endpoint"] == "policy-check"
    assert generator._validate(checked, schemas["PolicyCheckResponse"], spec) == []


def test_the_spec_will_not_let_undetermined_pass_for_a_pass(spec: dict[str, Any]) -> None:
    """The tagged union holds in the spec, not only in the prose."""
    import copy

    status, body = generator._policy_answer(generator._FULL_POLICY_REQUEST, paid=True)
    assert status == policy.HTTP_OK
    rows = {row["verdict"]: row for row in body["result"]}
    assert set(rows) == set(policy.VERDICTS), "the fixtures must produce every verdict"
    row_schema = {"$ref": "#/components/schemas/PolicyRow"}
    for row in rows.values():
        assert generator._validate(row, row_schema, spec) == []

    smuggled = copy.deepcopy(rows["undetermined"])
    check = next(c for c in smuggled["checks"] if c["state"] == "undetermined")
    check["satisfied"] = {}
    assert generator._validate(smuggled, row_schema, spec), (
        "an undetermined check carrying a `satisfied` key validated")

    relabelled = copy.deepcopy(rows["fail"])
    relabelled["passed"] = {"constraints": [], "conditions": []}
    assert generator._validate(relabelled, row_schema, spec), (
        "a failed row carrying a `passed` key validated")


# ── every error, with its fix ────────────────────────────────────────────────

def _codes_of(*modules: str) -> set[str]:
    import ast

    codes: set[str] = set()
    for name in modules:
        tree = ast.parse((ENTRY.parent / f"{name}.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "RequestError"
                    and node.args and isinstance(node.args[0], ast.Constant)):
                codes.add(node.args[0].value)
            if isinstance(node, ast.Dict):
                codes |= {v.value for k, v in zip(node.keys, node.values)
                          if isinstance(k, ast.Constant) and k.value == "code"
                          and isinstance(v, ast.Constant) and isinstance(v.value, str)}
    return codes


def test_every_error_code_the_worker_emits_has_a_documented_fix(
        reference: str, policy_reference: str) -> None:
    assert _codes_of("rank_service", "policy_service", "entry") == generator.source_error_codes()
    transport = set(generator.entry_error_codes())
    for text, name, modules in ((reference, "docs/api.md", ("rank_service",)),
                                (policy_reference, "docs/api-policy-check.md",
                                 ("policy_service",))):
        fixes = _error_table(text)
        missing = sorted((_codes_of(*modules) | transport) - set(fixes))
        assert missing == [], f"{name} does not tell a caller what to do about: {missing}"
        for code, fix in fixes.items():
            assert len(fix.split()) >= 3, f"{name}: {code} has no usable fix: {fix!r}"


def test_every_refusal_status_is_documented(reference: str, policy_reference: str) -> None:
    for text, module in ((reference, service), (policy_reference, policy)):
        statuses = {int(line.strip().strip("|").split("|")[0].strip())
                    for line in text.splitlines()
                    if line.strip().startswith("| 4") or line.strip().startswith("| 5")}
        emitted = _statuses(module, 400)
        assert emitted <= statuses, f"undocumented status(es): {sorted(emitted - statuses)}"


def test_the_policy_reference_states_the_parsers_limits(policy_reference: str) -> None:
    assert str(policy.MAX_BODY_BYTES) in policy_reference
    assert f"0–{policy.MAX_LIMIT}, default {policy.DEFAULT_LIMIT}" in policy_reference
    for why in policy.WHY:
        assert f"`{why}`" in policy_reference, f"undetermined.why={why} is not explained"


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

@pytest.mark.parametrize("path", REFERENCES, ids=lambda p: p.name)
def test_each_reference_is_under_the_word_budget(path: Path) -> None:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'`_./-]*", _prose(path.read_text(encoding="utf-8")))
    assert len(words) < WORD_BUDGET, (
        f"{path.name} is {len(words)} words of prose; the budget is {WORD_BUDGET}")


@pytest.mark.parametrize("path", REFERENCES, ids=lambda p: p.name)
def test_each_reference_starts_with_a_use_when_sentence(path: Path) -> None:
    head = path.read_text(encoding="utf-8").split("\n\n", 2)[1]
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


def test_the_access_gate_is_wired_and_the_reference_says_it_is_not_enforced(
        reference: str) -> None:
    """The day someone flips ACCESS_ENFORCED, this fails and the docs must change."""
    entry = ENTRY.read_text(encoding="utf-8")
    assert "access.gate(" in entry, "entry.py no longer calls the access gate"
    assert not generator.access_enforced(), (
        "ACCESS_ENFORCED is on in wrangler.jsonc. docs/api.md still says a key is "
        "optional — update it, and regenerate openapi.yaml.")
    prose = _prose(reference)
    assert "not live yet" not in prose.lower()
    assert "takes no key and meters nothing" not in prose
    assert "**A key is optional today.**" in prose
    assert "`ACCESS_ENFORCED`" in prose
    assert not generator.access_store_bound(), (
        "the ACCESS key store is bound now. docs/api.md still says a live key is refused "
        "access_store_not_configured — update it.")
    assert "access_store_not_configured" in prose


def test_every_access_refusal_is_documented_in_both_references(
        reference: str, policy_reference: str) -> None:
    """The gate stands in front of both endpoints, so both references name its refusals."""
    for text, name in ((reference, "docs/api.md"),
                       (policy_reference, "docs/api-policy-check.md")):
        fixes = _error_table(text)
        missing = sorted(set(generator.access.REFUSALS) - set(fixes))
        if name == "docs/api.md":
            # The sandbox answers /v1/rank, so rank never refuses a test_ key.
            missing = sorted(set(missing) - {"sandbox_not_available"})
        else:
            # Its reference points at api.md's table for the shared ones.
            missing = sorted(set(missing) - {"missing_api_key", "invalid_api_key",
                                             "key_revoked", "rate_limited",
                                             "tier_not_configured", "access_not_configured",
                                             "access_store_not_configured"})
        assert missing == [], f"{name} does not tell a caller what to do about: {missing}"
        for code, fix in fixes.items():
            assert len(fix.split()) >= 3, f"{name}: {code} has no usable fix: {fix!r}"
    for status in {str(s) for s in generator.access.REFUSALS.values()}:
        assert f"| {status} |" in reference, f"docs/api.md does not list status {status}"


def test_the_paid_policy_entitlement_follows_the_tier_and_the_reference_says_so(
        spec: dict[str, Any], policy_reference: str) -> None:
    """The day `_entitlement` grants the store any other way, this fails."""
    assert generator.entitlement_follows_tier(), (
        "entry.py::_entitlement no longer grants the determinations by a tier's paid flag. "
        "docs/api-policy-check.md and openapi.yaml say it does — update both.")
    assert "The paid tier is not live." not in policy_reference
    assert "a key whose tier is paid" in policy_reference
    block = spec["x-modelspec-access"]["policy_check_paid_entitlement"]
    assert "whose tier is paid" in block["status"]


NEUTRALITY_URL = "https://modelspec.dev/api/rank/profiles.json"


def test_the_live_neutrality_commitment_is_linked(reference: str) -> None:
    """MODEL-70 published the commitment as data; the reference links where it lives.

    This used to assert the opposite — that nothing was linked, because nothing
    existed. The commitment is now written into `profiles.json` by the build and
    into every `/v1/rank` answer, so the link must be there and must point at it.
    """
    from api.ranking.engine import neutrality_commitment
    from pipeline.ranking import RANKING_POLICY

    assert f"]({NEUTRALITY_URL})" in reference
    assert "`.ranking_policy.neutrality`" in reference
    # What the link serves is what the build writes, and what a rank answer carries.
    assert RANKING_POLICY["neutrality"] == neutrality_commitment()
    assert generator._answer(generator.EXAMPLE_REQUEST)["policy"]["neutrality"] == (
        neutrality_commitment())
    assert neutrality_commitment()["pledge"].split(",")[0] in reference


def test_the_draft_terms_are_not_presented_as_in_force(reference: str) -> None:
    """The legal pages are unadopted drafts. The day `pipeline.legal.DRAFT` flips,
    this fails, and the reference has to start linking them as terms."""
    from pipeline import legal

    assert legal.DRAFT is True, (
        "the MODEL-70 legal pages are adopted now. docs/api.md still says no terms are in "
        "force and deliberately does not link them — update it.")
    assert "No terms of use are in force." in reference
    for draft in ("modelspec.dev/legal/terms", "modelspec.dev/legal/privacy",
                  "modelspec.dev/legal/neutrality"):
        assert f"](https://{draft}" not in reference, (
            f"docs/api.md links {draft}, an unadopted draft, as if it were in force")


@pytest.mark.skipif(os.environ.get("MODELSPEC_LIVE_API") != "1",
                    reason="set MODELSPEC_LIVE_API=1 to fetch modelspec.dev")
def test_the_linked_neutrality_commitment_resolves() -> None:
    """The link in the reference answers, and answers with the commitment."""
    import json
    import urllib.request

    from api.ranking.engine import neutrality_commitment

    request = urllib.request.Request(NEUTRALITY_URL,
                                     headers={"user-agent": generator.USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        assert response.status == 200
        published = json.loads(response.read())
    assert published["ranking_policy"]["neutrality"] == neutrality_commitment()


def test_the_spec_records_the_access_layer_as_wired_and_not_enforced(
        spec: dict[str, Any]) -> None:
    import json

    block = spec["x-modelspec-access"]
    assert block["status"] == "wired; enforcement off"
    assert block["enforced"] is False and block["key_store_bound"] is False
    tiers = json.loads(TIERS_PATH.read_text(encoding="utf-8"))
    assert block["sandbox_prefix"] == tiers["sandbox_prefix"]
    assert block["tiers"]["sandbox"]["daily_limit"] is None
    assert block["refusals"] == dict(sorted(generator.access.REFUSALS.items()))
    # A key is optional: the anonymous requirement `{}` is listed beside the schemes.
    assert spec["security"][0] == {}
    assert {"bearer", "apiKey"} <= set(spec["components"]["securitySchemes"])
    for path in ("/v1/rank", "/v1/policy-check"):
        responses = spec["paths"][path]["post"]["responses"]
        for status in {str(s) for s in generator.access.REFUSALS.values()}:
            if path == "/v1/rank" and status == "400":
                continue  # sandbox_not_available is policy-check's only
            assert status in responses, f"{path} does not describe {status}"


def test_every_access_refusal_the_gate_produces_validates_against_the_spec(
        spec: dict[str, Any]) -> None:
    schema = spec["components"]["schemas"]["AccessRefused"]
    for code, (status, body) in generator._access_refusals().items():
        assert generator._validate(body, schema, spec) == [], code
        assert status == generator.access.REFUSALS[code]


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
    # #97: nothing in the smoke step may be able to abort it before the retry
    # loop has run. The probe comes after the loop and cannot exit on its own.
    loop = deploy.index('while [ "$SECONDS" -lt "$deadline" ]')
    probe_line = next(line for line in deploy.splitlines()
                      if "python3 api/worker/openapi.py --probe" in line)
    assert deploy.index(probe_line) > loop, "the spec probe must run after the retry loop"
    after = deploy[deploy.index(probe_line):].split("\n", 2)[1]
    assert "|| fail" in probe_line + after, "the spec probe must report through fail()"


# ── the live proof, opt-in ───────────────────────────────────────────────────

@pytest.mark.skipif(os.environ.get("MODELSPEC_LIVE_API") != "1",
                    reason="set MODELSPEC_LIVE_API=1 to call api.modelspec.dev")
def test_a_request_built_only_from_the_spec_succeeds_against_the_live_service() -> None:
    assert generator.probe("https://api.modelspec.dev") == 0
