"""`POST /v1/policy-check` (MODEL-80): the compliance answer, and its third state.

What these tests hold, in the order the ticket puts them:

* a policy document produces a verdict per model **and per platform**, and a
  model that passes on one platform and fails on another comes back that way;
* a `fail` names the constraint that eliminated it and cites a document with the
  day it was read;
* a `restricted` grant returns its condition text, never a bare pass;
* `undetermined` is **structurally** distinct from `pass` — the test asserts on
  the presence and absence of keys, not on a string, because a consumer reading
  the shape is the one this protects;
* a caller can demand no undetermined rows and get a documented hard failure;
* the free tier reaches the endpoint and not the determinations, and the
  difference is visible on the response rather than inferred from it;
* no verdict is ever inferred: a blank country, an unnamed licence, an uncited
  value and a local runtime all yield `undetermined`.

The service is imported from its path for the same reason `test_rank_worker.py`
imports its own: it sits beside the Worker entry point so Wrangler bundles it,
and it is written to import nothing from the Workers runtime precisely so this
suite can run it.
"""

from __future__ import annotations

import functools
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline import policy_export  # noqa: E402
from scripts.residency.platforms import LOCAL_RUNTIMES, platform_slugs  # noqa: E402

WORKER_ROOT = REPO_ROOT / "api" / "worker"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = _load("modelspec_policy_service", WORKER_ROOT / "src" / "policy_service.py")
loader = _load("modelspec_load_determinations", WORKER_ROOT / "load_determinations.py")

SERVICE_COMMIT = "0123456789abcdef0123456789abcdef01234567"
ORIGIN = "https://modelspec.test"
BUILD = {"commit": "deadbeef", "built_at": "2026-09-17T00:00:00Z",
         "eligibility_as_of": "2026-09-01", "export_schema_version": "2.0"}


# ── fixtures: a small catalogue with one of each interesting shape ───────────

def _model(model_id: str, *, licence: str | None = "apache-2.0", country: str = "US",
           commercial: str = "unspecified", conditions: str = "",
           source: dict[str, Any] | None = None,
           platforms: list[str] | None = None) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "display_name": model_id.upper(),
        "provider": model_id.split("/")[0],
        "licence": {"license_type": licence, "license_url": "https://example.test/l",
                    "tos_url": "", "open_weights": True},
        "commercial_use": {"value": commercial, "conditions": conditions,
                           "source": source},
        "origin": {"country": country, "org_type": "private"},
        "primary_provider": {"name": "", "data_residency": None,
                             "data_residency_disclosure": "unresearched",
                             "data_residency_source": None},
        "platforms": [{"platform": p, "model_id_on_platform": "", "url": "",
                       "gated": False, "listed_regions": []}
                      for p in (["aws_bedrock"] if platforms is None else platforms)],
    }


CITED = {"kind": "license", "url": "https://example.test/LICENSE",
         "read_on": "2026-09-16", "quote": "You may use it commercially."}
UNCITED = {"kind": "legacy-import", "url": "", "read_on": "", "quote": ""}


def catalogue(models: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "build": BUILD,
        "platform_classes": {"all": sorted(platform_slugs()),
                             "unbounded": sorted(LOCAL_RUNTIMES)},
        "count": len(models),
        "models": models,
    }


def store(commercial_use: dict[str, Any] | None = None,
          residency: dict[str, Any] | None = None,
          generated_on: str = "2026-09-17") -> dict[str, Any]:
    return {"bundle_version": "1", "generated_on": generated_on,
            "commercial_use": commercial_use or {}, "residency": residency or {}}


def determination(value: str, conditions: str = "",
                  read_on: str = "2026-09-16") -> dict[str, Any]:
    return {"value": value, "conditions": conditions, "determined_on": "2026-09-16",
            "source": {"kind": "license", "url": "https://example.test/LICENSE",
                       "read_on": read_on, "quote": "the operative clause"}}


def residency_record(regions: list[str] | None, scope: str = "determined",
                     read_on: str = "2026-09-16") -> dict[str, Any]:
    record = {"scope": scope, "regions": regions, "reason": "", "checked": [],
              "determined_on": "2026-09-16", "notes": "", "source": None}
    if scope == "determined":
        record["source"] = {"kind": "provider_documentation",
                            "url": "https://example.test/regions",
                            "read_on": read_on, "quote": ""}
    return record


def check(payload: dict[str, Any], models: list[dict[str, Any]],
          st: dict[str, Any] | None = None,
          entitlement: str = service.ENTITLEMENT_PUBLIC):
    return service.check(payload, catalogue(models), st, entitlement,
                         SERVICE_COMMIT, ORIGIN)


def rows_by_platform(body: dict[str, Any]) -> dict[str | None, dict[str, Any]]:
    return {row["platform"]: row for row in body["result"]}


# ── the third state is structural, not a string ──────────────────────────────

def test_undetermined_carries_no_pass_shaped_key():
    """A consumer that reads `satisfied` finds nothing on an undetermined check.

    This is the whole safety property. If `undetermined` were a flag on a check
    that still carried `satisfied`, every naive consumer would read it as a
    pass, and the thing that gets deployed is a model nobody checked.
    """
    status, body = check(
        {"policy": {"origin": {"permitted_countries": ["US"]}}},
        [_model("acme/no-country", country="")])
    assert status == service.HTTP_OK
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    assert "passed" not in row and "failed" not in row
    assert "undetermined" in row
    check_row = row["checks"][0]
    assert check_row["state"] == "undetermined"
    assert "satisfied" not in check_row and "violated" not in check_row
    assert check_row["undetermined"]["why"] == "not_on_card"
    assert check_row["undetermined"]["meaning"]


def test_pass_carries_no_undetermined_shaped_key():
    status, body = check({"policy": {"origin": {"permitted_countries": ["US"]}}},
                         [_model("acme/us")])
    row = body["result"][0]
    assert row["verdict"] == "pass"
    assert "undetermined" not in row and "failed" not in row
    assert row["passed"]["constraints"] == ["origin"]
    assert "undetermined" not in row["checks"][0]


def test_an_unnamed_licence_is_undetermined_and_never_a_default():
    status, body = check({"policy": {"licence": {"allowed": ["apache-2.0"]}}},
                         [_model("acme/nolicence", licence=None)])
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    assert row["checks"][0]["undetermined"]["why"] == "not_on_card"


def test_an_uncited_commercial_use_is_undetermined_not_a_pass():
    """The eight `legacy-import` cards are the case this protects.

    They carry `commercial_use: allowed` and, by the card schema's own
    admission, no document and no read date. A compliance answer that cannot be
    rechecked on the day it is questioned is not an answer, so it is the third
    state — not a pass with a quiet caveat.
    """
    status, body = check(
        {"policy": {"commercial_use": {"required": True}}},
        [_model("acme/legacy", commercial="allowed", source=UNCITED)])
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    assert row["checks"][0]["undetermined"]["why"] == "uncited"
    assert row["checks"][0]["undetermined"]["public_state"] == "allowed"


# ── fail names the constraint and cites a source with a read date ────────────

def test_fail_names_the_eliminating_constraint_and_cites_it():
    status, body = check(
        {"policy": {"licence": {"allowed": ["apache-2.0"]},
                    "commercial_use": {"required": True}}},
        [_model("acme/nc", licence="cc-by-nc-4.0", commercial="prohibited",
                source=CITED)])
    row = body["result"][0]
    assert row["verdict"] == "fail"
    assert row["failed"]["constraint"] == "licence"
    eliminated = row["failed"]["eliminated_by"]
    assert "cc-by-nc-4.0" in eliminated["violated"]["because"]
    # The commercial-use violation is not lost just because the licence went first.
    assert row["failed"]["also_violated"] == ["commercial_use"]
    commercial = [c for c in row["checks"] if c["constraint"] == "commercial_use"][0]
    assert commercial["violated"]["source"]["url"] == CITED["url"]
    assert commercial["violated"]["read_on"] == "2026-09-16"


def test_every_violated_check_carries_a_read_date():
    status, body = check(
        {"policy": {"commercial_use": {"required": True}}},
        [_model("acme/no", commercial="prohibited", source=CITED)])
    for row in body["result"]:
        for c in row["checks"]:
            if c["state"] == "violated" and c["violated"].get("source"):
                assert c["violated"]["read_on"]


# ── restricted returns the condition text, never a bare pass ─────────────────

RESTRICTION = "free below 700M monthly active users; a licence is required above it"


def test_restricted_is_not_a_pass_by_default_and_states_its_condition():
    status, body = check(
        {"policy": {"commercial_use": {"required": True}}},
        [_model("meta/llama", commercial="restricted", conditions=RESTRICTION,
                source=CITED)])
    row = body["result"][0]
    assert row["verdict"] == "fail"
    violated = row["failed"]["eliminated_by"]["violated"]
    assert RESTRICTION in violated["because"]
    assert violated["conditions"] == RESTRICTION
    assert violated["commercial_use"] == "restricted"


def test_an_accepted_restriction_still_returns_the_condition_text():
    status, body = check(
        {"policy": {"commercial_use": {"required": True, "accept_restricted": True}}},
        [_model("meta/llama", commercial="restricted", conditions=RESTRICTION,
                source=CITED)])
    row = body["result"][0]
    assert row["verdict"] == "pass"
    satisfied = row["checks"][0]["satisfied"]
    assert satisfied["conditional"] is True
    assert satisfied["conditions"] == RESTRICTION
    # And again on the verdict block, so a caller reading only the verdict sees it.
    assert row["passed"]["conditions"][0]["text"] == RESTRICTION
    assert row["passed"]["conditions"][0]["source"]["read_on"] == "2026-09-16"


def test_commercial_use_required_false_is_refused_rather_than_ignored():
    with pytest.raises(service.RequestError) as exc:
        check({"policy": {"commercial_use": {"required": False}}}, [_model("a/b")])
    assert exc.value.code == "invalid_request"


# ── per model AND per platform ───────────────────────────────────────────────

def test_a_model_passes_on_one_platform_and_fails_on_another():
    """The acceptance criterion MODEL-79 exists to make possible.

    Residency is a property of the place a model is served from. The same
    licence, the same origin, the same model — and two verdicts, because
    `aws_bedrock` publishes `eu-west-1` and `groq` does not.
    """
    st = store(residency={
        "aws_bedrock": residency_record(["us-east-1", "eu-west-1"]),
        "groq": residency_record(["us-east-1"]),
    })
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/dual", platforms=["aws_bedrock", "groq"])],
        st, service.ENTITLEMENT_DETERMINATIONS)
    assert status == service.HTTP_OK
    rows = rows_by_platform(body)
    assert rows["aws_bedrock"]["verdict"] == "pass"
    assert rows["groq"]["verdict"] == "fail"
    failed = rows["groq"]["failed"]["eliminated_by"]["violated"]
    assert failed["published_regions"] == ["us-east-1"]
    assert failed["read_on"] == "2026-09-16"
    assert body["summary"]["rows"] == 2
    assert body["summary"]["models_checked"] == 1
    # One model, two verdicts: the summary keeps "passes somewhere" apart from
    # a row count, because a governance buyer needs both.
    assert body["summary"]["models_with_a_passing_platform"] == 1
    assert body["summary"]["verdicts"] == {"pass": 1, "fail": 1, "undetermined": 0}


def test_a_determined_empty_region_list_is_a_fail_not_an_unknown():
    """`[]` means the platform published its terms and commits to no region."""
    st = store(residency={"groq": residency_record([])})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["groq"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "fail"
    assert "commits to no processing region" in row["failed"]["eliminated_by"]["violated"]["because"]


def test_a_researched_unknown_is_undetermined_and_says_what_was_checked():
    st = store(residency={"ai21_labs": {
        "scope": "undetermined", "regions": None, "source": None,
        "reason": "the trust centre lists subprocessors, not selectable regions",
        "checked": ["https://trust.ai21.com/"], "determined_on": "2026-09-16",
        "notes": ""}})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["ai21_labs"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    body_of = row["checks"][0]["undetermined"]
    assert body_of["why"] == "not_determined"
    assert body_of["checked"] == ["https://trust.ai21.com/"]
    assert body_of["reason"]


def test_a_no_commitment_finding_is_a_fail_that_cites_the_documents():
    """A withheld card with no region list still has a paid answer: the finding."""
    st = store(residency={"ai21_labs": {
        "scope": "undetermined", "regions": None, "source": None,
        "non_disclosure": "no-commitment",
        "reason": "the trust centre lists subprocessors, not selectable regions",
        "checked": ["https://trust.ai21.com/"],
        "documents": [{"url": "https://trust.ai21.com/", "read_on": "2026-09-16"}],
        "determined_on": "2026-09-16", "notes": ""}})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["ai21_labs"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "fail"
    violated = row["failed"]["eliminated_by"]["violated"]
    assert violated["finding"] == "no_commitment"
    assert "commit to no processing region" in violated["because"]
    assert violated["documents"] == [
        {"url": "https://trust.ai21.com/", "read_on": "2026-09-16"}]
    assert violated["reason"]
    assert violated["read_on"] == "2026-09-16"
    assert "satisfied" not in row["checks"][0]
    assert body["provenance"]["determination_read_dates"]["residency"] == ["2026-09-16"]


def test_no_commitment_resolves_from_checked_urls_when_documents_is_absent():
    """Older KV blobs have `checked` strings; the endpoint still has to answer."""
    st = store(residency={"poe": {
        "scope": "undetermined", "regions": None, "source": None,
        "non_disclosure": "no-commitment",
        "reason": "privacy policy names no processing location",
        "checked": ["https://example.com/privacy"],
        "determined_on": "2026-09-16", "notes": ""}})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["poe"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    violated = body["result"][0]["failed"]["eliminated_by"]["violated"]
    assert violated["finding"] == "no_commitment"
    assert violated["documents"] == [
        {"url": "https://example.com/privacy", "read_on": "2026-09-16"}]


def test_a_no_commitment_finding_without_documents_is_not_a_silent_fail():
    """A withheld claim the store cannot defend is not_determined, never an empty fail."""
    st = store(residency={"ai21_labs": {
        "scope": "undetermined", "regions": None, "source": None,
        "non_disclosure": "no-commitment", "reason": "", "checked": [],
        "documents": [], "determined_on": "2026-09-16", "notes": ""}})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["ai21_labs"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    assert row["checks"][0]["undetermined"]["why"] == "not_determined"


@pytest.mark.parametrize("slug", sorted(LOCAL_RUNTIMES))
def test_a_local_runtime_is_unbounded_and_is_not_for_sale(slug):
    """No region list can be true of a local runtime, at any tier, for any money."""
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=[slug])], store(),
        service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "undetermined"
    undetermined = row["checks"][0]["undetermined"]
    assert undetermined["why"] == "unbounded"
    assert undetermined["available_in_tier"] is None


@pytest.mark.parametrize("slug", ["samsung_gauss", "tii_falcon", "zero_one_ai"])
def test_weights_only_publishers_stay_unbounded_even_if_kv_still_has_a_finding(slug):
    """The export class wins. A leftover no-commitment row must not become a fail."""
    st = store(residency={slug: {
        "scope": "undetermined", "regions": None, "source": None,
        "non_disclosure": "no-commitment",
        "reason": "stale finding from before they were classified unbounded",
        "checked": ["https://example.test/privacy"],
        "determined_on": "2026-09-16", "notes": ""}})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=[slug])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    assert status == service.HTTP_OK
    undetermined = body["result"][0]["checks"][0]["undetermined"]
    assert undetermined["why"] == "unbounded"
    assert undetermined["available_in_tier"] is None


def test_a_card_with_no_platform_gets_a_row_not_a_silence():
    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/nowhere", platforms=[])], store(),
        service.ENTITLEMENT_DETERMINATIONS)
    assert len(body["result"]) == 1
    row = body["result"][0]
    assert row["platform"] is None
    assert row["checks"][0]["undetermined"]["why"] == "no_platform"


def test_regions_are_matched_literally_and_never_normalised():
    """"Germany" is not `eu-central-1`, and this endpoint will not pretend."""
    st = store(residency={"aws_bedrock": residency_record(["eu-central-1"])})
    status, body = check(
        {"policy": {"residency": {"required_regions": ["Germany"]}}},
        [_model("acme/x")], st, service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "fail"
    violated = row["failed"]["eliminated_by"]["violated"]
    assert violated["matching"] == "literal"
    assert violated["published_regions"] == ["eu-central-1"]


def test_match_all_requires_every_region():
    st = store(residency={"aws_bedrock": residency_record(["eu-west-1"])})
    payload = {"policy": {"residency": {"required_regions": ["eu-west-1", "eu-west-2"],
                                        "match": "all"}}}
    status, body = check(payload, [_model("acme/x")], st,
                         service.ENTITLEMENT_DETERMINATIONS)
    row = body["result"][0]
    assert row["verdict"] == "fail"
    assert row["failed"]["eliminated_by"]["violated"]["missing"] == ["eu-west-2"]


# ── require_no_undetermined is a documented hard failure ─────────────────────

def test_require_no_undetermined_is_a_hard_failure_with_the_offenders():
    status, body = check(
        {"policy": {"origin": {"permitted_countries": ["US"]}},
         "require_no_undetermined": True},
        [_model("acme/ok"), _model("acme/blank", country="")])
    assert status == service.HTTP_UNDETERMINED_PRESENT
    assert body["error"]["code"] == "undetermined_present"
    assert body["error"]["undetermined_rows"] == 1
    assert body["error"]["undetermined_by_constraint"] == {"origin": 1}
    assert body["error"]["examples"][0]["model_id"] == "acme/blank"
    assert body["result"] == []
    # The summary still describes the whole catalogue, so the caller knows what
    # they are up against rather than only that something failed.
    assert body["summary"]["verdicts"]["pass"] == 1


def test_require_no_undetermined_passes_when_nothing_is_unknown():
    status, body = check(
        {"policy": {"origin": {"permitted_countries": ["US"]}},
         "require_no_undetermined": True},
        [_model("acme/ok")])
    assert status == service.HTTP_OK
    assert body["result"][0]["verdict"] == "pass"


# ── the free/paid split is legible, never a silent degradation ───────────────

FREE_PAID_POLICY = {"policy": {"commercial_use": {"required": True}}}


def test_the_free_tier_says_what_it_could_not_see():
    status, body = check(FREE_PAID_POLICY, [_model("acme/x", commercial="withheld")])
    assert status == service.HTTP_OK
    assert body["determinations"]["included"] is False
    assert body["determinations"]["entitlement"] == service.ENTITLEMENT_PUBLIC
    assert body["determinations"]["undetermined_for_lack_of_entitlement"] == 1
    assert body["determinations"]["why"]
    undetermined = body["result"][0]["checks"][0]["undetermined"]
    assert undetermined["why"] == "tier"
    assert undetermined["available_in_tier"] == "paid"
    assert undetermined["public_state"] == "withheld"


def test_the_paid_tier_answers_the_same_request_from_the_determinations():
    st = store(commercial_use={"acme/x": determination("restricted", RESTRICTION)})
    status, body = check(FREE_PAID_POLICY, [_model("acme/x", commercial="withheld")],
                         st, service.ENTITLEMENT_DETERMINATIONS)
    assert body["determinations"]["included"] is True
    assert body["determinations"]["store"]["generated_on"] == "2026-09-17"
    assert body["determinations"]["undetermined_for_lack_of_entitlement"] == 0
    row = body["result"][0]
    assert row["verdict"] == "fail"
    violated = row["failed"]["eliminated_by"]["violated"]
    assert violated["answered_from"] == "determinations"
    assert violated["conditions"] == RESTRICTION
    # The free tier said "undetermined" for the same model and the same policy.
    # That is the difference being sold, and it is visible on both responses.
    _, free = check(FREE_PAID_POLICY, [_model("acme/x", commercial="withheld")])
    assert free["result"][0]["verdict"] == "undetermined"


def test_an_entitled_request_with_no_store_fails_rather_than_degrading():
    """The failure mode this product exists to prevent, in one assertion."""
    with pytest.raises(service.RequestError) as exc:
        check(FREE_PAID_POLICY, [_model("acme/x", commercial="withheld")],
              None, service.ENTITLEMENT_DETERMINATIONS)
    assert exc.value.code == "determinations_unavailable"
    assert exc.value.status == service.HTTP_DETERMINATIONS_UNAVAILABLE


def test_a_paid_tier_with_no_record_says_not_determined_not_tier():
    """On the paid tier the store *is* the answer, so its silence is authoritative."""
    status, body = check(FREE_PAID_POLICY, [_model("acme/x", commercial="withheld")],
                         store(), service.ENTITLEMENT_DETERMINATIONS)
    undetermined = body["result"][0]["checks"][0]["undetermined"]
    assert undetermined["why"] == "not_determined"
    assert undetermined["available_in_tier"] is None


def test_the_free_tier_still_answers_the_public_constraints():
    """A crippled taste sells nothing: licence and origin are public and answered."""
    status, body = check(
        {"policy": {"licence": {"prohibited": ["cc-by-nc-4.0"]},
                    "origin": {"permitted_countries": ["US"]}}},
        [_model("acme/us"), _model("acme/nc", licence="cc-by-nc-4.0"),
         _model("acme/cn", country="CN")])
    verdicts = [r["verdict"] for r in body["result"]]
    assert verdicts.count("pass") == 1
    assert verdicts.count("fail") == 2


# ── audit: the answer carries what it was computed from ──────────────────────

def test_the_response_carries_build_commit_and_the_read_dates():
    st = store(commercial_use={"acme/x": determination("allowed", read_on="2026-09-16")},
               residency={"aws_bedrock": residency_record(["eu-west-1"],
                                                          read_on="2026-09-15")})
    status, body = check(
        {"policy": {"commercial_use": {"required": True},
                    "residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", commercial="withheld")], st,
        service.ENTITLEMENT_DETERMINATIONS)
    assert body["build"]["commit"] == "deadbeef"
    assert body["build"]["export_schema_version"] == "2.0"
    assert body["service_commit"] == SERVICE_COMMIT
    assert body["provenance"]["determination_read_dates"] == {
        "commercial_use": ["2026-09-16"], "residency": ["2026-09-15"]}
    assert body["provenance"]["determinations_generated_on"] == "2026-09-17"


def test_paging_never_truncates_the_summary():
    models = [_model(f"acme/m{n:03d}") for n in range(20)]
    status, body = check(
        {"policy": {"origin": {"permitted_countries": ["US"]}}, "limit": 5},
        models)
    assert body["summary"]["rows"] == 20
    assert body["page"]["returned"] == 5
    assert body["page"]["truncated"] is True
    assert body["page"]["matching_rows"] == 20


def test_verdict_filter_narrows_rows_but_not_counts():
    status, body = check(
        {"policy": {"origin": {"permitted_countries": ["US"]}}, "verdicts": ["fail"]},
        [_model("acme/us"), _model("acme/cn", country="CN")])
    assert body["summary"]["verdicts"] == {"pass": 1, "fail": 1, "undetermined": 0}
    assert [r["model_id"] for r in body["result"]] == ["acme/cn"]


# ── the request is validated, never guessed at ───────────────────────────────

def test_an_empty_policy_is_refused_rather_than_passing_everything():
    with pytest.raises(service.RequestError) as exc:
        check({"policy": {}}, [_model("a/b")])
    assert exc.value.code == "invalid_request"
    assert "every model would pass" in exc.value.message


@pytest.mark.parametrize("payload", [
    {"policy": {"orgin": {"permitted_countries": ["US"]}}},
    {"policy": {"origin": {"countries": ["US"]}}},
    {"policy": {"origin": {"permitted_countries": ["US"]}}, "platforms": ["aws_bedroc"]},
    {"policy": {"origin": {"permitted_countries": ["US"]}}, "verdicts": ["maybe"]},
    {"policy": {"residency": {"required_regions": []}}},
    {"policy": {"licence": {"allowed": ["mit"], "prohibited": ["mit"]}}},
])
def test_a_malformed_request_is_refused(payload):
    with pytest.raises(service.RequestError):
        check(payload, [_model("a/b")])


def test_an_unknown_model_is_refused_rather_than_silently_dropped():
    with pytest.raises(service.RequestError) as exc:
        check({"policy": {"origin": {"permitted_countries": ["US"]}},
               "models": ["acme/nope"]}, [_model("acme/us")])
    assert exc.value.code == "unknown_model"


# ── the public export the free tier reads ────────────────────────────────────

@functools.lru_cache(maxsize=1)
def real_catalogue() -> dict[str, Any]:
    from pipeline.load import load_models
    from schema.card import ModelCard
    cards = [ModelCard.from_yaml_file(str(m.path)) for m in load_models(REPO_ROOT)]
    return policy_export.build_catalogue(cards, BUILD)


def test_platform_classes_are_derived_not_copied():
    classes = policy_export.platform_classes()
    assert classes["all"] == sorted(platform_slugs())
    assert classes["unbounded"] == sorted(LOCAL_RUNTIMES)
    assert len(classes["unbounded"]) == 9
    assert {"samsung_gauss", "tii_falcon", "zero_one_ai"} <= set(classes["unbounded"])
    # The Worker reads the classification from the export rather than holding a
    # second list, so a new local runtime cannot go unnoticed in the endpoint.
    assert "LOCAL_RUNTIMES" not in (WORKER_ROOT / "src" / "policy_service.py").read_text()


def test_the_export_never_carries_a_determination():
    """The public half publishes empty states faithfully and adds nothing.

    If this ever fails, a determination has been written into a public artifact
    and the product has been given away (decision-record §2.2).
    """
    catalogue_json = real_catalogue()
    for row in catalogue_json["models"]:
        commercial = row["commercial_use"]
        if commercial["value"] in ("allowed", "restricted", "prohibited"):
            # The only determined values on public cards today are the eight
            # uncited `legacy-import` ones MODEL-77 inherited.
            assert (commercial["source"] or {}).get("kind") == "legacy-import"
        residency = row["primary_provider"]
        if residency["data_residency_disclosure"] != "published":
            assert residency["data_residency"] is None


def test_the_catalogue_answers_a_policy_per_model_and_per_platform():
    """The acceptance criterion, against the real 1,339 cards."""
    status, body = service.check(
        {"policy": {"licence": {"prohibited": ["cc-by-nc-4.0", "cc-by-nc-sa-4.0"]},
                    "origin": {"permitted_countries": ["US", "GB", "DE", "FR"]},
                    "commercial_use": {"required": True}},
         "limit": 0},
        real_catalogue(), None, service.ENTITLEMENT_PUBLIC, SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_OK
    summary = body["summary"]
    assert summary["models_checked"] == real_catalogue()["count"]
    assert summary["rows"] >= summary["models_checked"]
    assert sum(summary["verdicts"].values()) == summary["rows"]
    # Every commercial-use check is undetermined on the free tier today, which
    # is §9.4's gate on turning paid tiers on, stated as a number.
    assert summary["by_constraint"]["commercial_use"]["undetermined"] == summary["rows"]
    assert body["determinations"]["included"] is False


# ── the loader, which is the only thing that writes the private store ────────

def test_the_loader_refuses_a_path_inside_this_repository(tmp_path):
    """Prose has never stopped a determination being committed. This does."""
    with pytest.raises(loader.LoadError) as exc:
        loader._refuse_repo_paths(REPO_ROOT / "enrichment" / "commercial_use.jsonl",
                                  "--commercial-use")
    assert "never live here" in str(exc.value)
    # And an output directory inside the repo is refused for the same reason.
    with pytest.raises(loader.LoadError):
        loader._refuse_repo_paths(REPO_ROOT / "dist", "--out")
    loader._refuse_repo_paths(tmp_path, "--out")


def _write(tmp_path: Path, name: str, records: list[dict[str, Any]]) -> Path:
    path = tmp_path / name
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return path


def test_the_loader_builds_a_manifest_that_verifies_the_blobs(tmp_path):
    commercial = _write(tmp_path, "cu.jsonl", [{
        "model_id": "acme/x", "field": "commercial_use", "commercial_use": "restricted",
        "conditions": RESTRICTION, "determined_by": "agent", "determined_on": "2026-09-16",
        "published": False,
        "source": {"kind": "license", "url": "https://example.test/L",
                   "read_on": "2026-09-16", "quote": "q"}}])
    residency = _write(tmp_path, "res.jsonl", [
        {"platform": "aws_bedrock", "scope": "determined", "regions": ["eu-west-1"],
         "determined_on": "2026-09-16", "checked": [], "reason": "", "notes": "",
         "source": {"kind": "provider_documentation", "url": "https://example.test/r",
                    "read_on": "2026-09-16", "quote": ""}},
        {"platform": "ai21_labs", "scope": "undetermined", "regions": None,
         "source": None, "non_disclosure": "no-commitment",
         "checked": ["https://trust.ai21.com/"],
         "reason": "no region list", "notes": "", "determined_on": "2026-09-16"}])

    blobs = loader.build(commercial, residency, generated_on="2026-09-17")
    # The manifest is written last, which is what makes a half-finished load
    # invisible to the endpoint rather than half-served.
    assert list(blobs)[-1] == loader.KEY_MANIFEST

    import hashlib
    manifest = json.loads(blobs[loader.KEY_MANIFEST])
    for key in (loader.KEY_COMMERCIAL_USE, loader.KEY_RESIDENCY):
        digest = hashlib.sha256(blobs[key].encode("utf-8")).hexdigest()
        assert manifest["blobs"][key]["sha256"] == digest

    cu = json.loads(blobs[loader.KEY_COMMERCIAL_USE])["commercial_use"]
    assert cu["acme/x"]["conditions"] == RESTRICTION
    res = json.loads(blobs[loader.KEY_RESIDENCY])["residency"]
    assert res["aws_bedrock"]["regions"] == ["eu-west-1"]
    # A no-commitment finding is carried with the documents, not dropped.
    assert res["ai21_labs"]["scope"] == "undetermined"
    assert res["ai21_labs"]["non_disclosure"] == "no-commitment"
    assert res["ai21_labs"]["checked"] == ["https://trust.ai21.com/"]
    assert res["ai21_labs"]["documents"] == [
        {"url": "https://trust.ai21.com/", "read_on": "2026-09-16"}]

    # And the blobs feed the service unchanged.
    st = {"bundle_version": manifest["bundle_version"],
          "generated_on": manifest["generated_on"],
          "commercial_use": cu, "residency": res}
    status, body = check({"policy": {"commercial_use": {"required": True,
                                                        "accept_restricted": True}}},
                         [_model("acme/x", commercial="withheld")], st,
                         service.ENTITLEMENT_DETERMINATIONS)
    assert body["result"][0]["verdict"] == "pass"
    assert body["result"][0]["passed"]["conditions"][0]["text"] == RESTRICTION

    status, body = check(
        {"policy": {"residency": {"required_regions": ["eu-west-1"]}}},
        [_model("acme/x", platforms=["ai21_labs"])], st,
        service.ENTITLEMENT_DETERMINATIONS)
    violated = body["result"][0]["failed"]["eliminated_by"]["violated"]
    assert violated["finding"] == "no_commitment"
    assert violated["documents"][0]["url"] == "https://trust.ai21.com/"
    assert violated["documents"][0]["read_on"] == "2026-09-16"


@pytest.mark.parametrize("record,fragment", [
    ({"platform": "ollama", "scope": "unbounded", "regions": None},
     "no region list can be true of it"),
    ({"platform": "samsung_gauss", "scope": "undetermined",
      "non_disclosure": "no-commitment",
      "checked": ["https://example.test/privacy"],
      "reason": "weights only", "determined_on": "2026-09-16"},
     "no region list can be true of it"),
    ({"platform": "aws_bedrock", "scope": "determined", "regions": None},
     "null is not an answer"),
    ({"platform": "poe", "scope": "undetermined", "non_disclosure": "no-commitment",
      "checked": [], "reason": "", "determined_on": "2026-09-16"},
     "name the documents"),
])
def test_the_loader_refuses_an_indefensible_residency_record(tmp_path, record, fragment):
    with pytest.raises(loader.LoadError) as exc:
        loader.residency_blob([record])
    assert fragment in str(exc.value)


@pytest.mark.parametrize("record,fragment", [
    ({"model_id": "a/b", "field": "commercial_use", "commercial_use": "restricted",
      "conditions": "", "source": {"kind": "license", "url": "https://x.test",
                                   "read_on": "2026-09-16"}},
     "700M monthly active users"),
    ({"model_id": "a/b", "field": "commercial_use", "commercial_use": "withheld",
      "source": {"kind": "license", "url": "https://x.test", "read_on": "2026-09-16"}},
     "something was decided"),
    ({"model_id": "a/b", "field": "data_residency", "commercial_use": "allowed",
      "source": {"kind": "license", "url": "https://x.test", "read_on": "2026-09-16"}},
     "not per model"),
    ({"model_id": "a/b", "field": "commercial_use", "commercial_use": "allowed",
      "source": {"kind": "legacy-import", "url": "", "read_on": ""}},
     "nothing was read"),
    ({"model_id": "a/b", "field": "commercial_use", "commercial_use": "allowed",
      "source": {"kind": "license", "url": "https://x.test", "read_on": ""}},
     "cannot be rechecked"),
])
def test_the_loader_refuses_an_indefensible_determination(record, fragment):
    with pytest.raises(loader.LoadError) as exc:
        loader.commercial_use_blob([record])
    assert fragment in str(exc.value)


def test_the_loader_prints_its_wrangler_commands_without_touching_cloudflare(tmp_path):
    commercial = _write(tmp_path, "cu.jsonl", [])
    residency = _write(tmp_path, "res.jsonl", [])
    out = tmp_path / "staged"
    result = subprocess.run(
        [sys.executable, str(WORKER_ROOT / "load_determinations.py"),
         "--commercial-use", str(commercial), "--residency", str(residency),
         "--out", str(out)],
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "wrangler kv key put determinations/manifest" in result.stdout
    # The manifest command is printed last for the same reason it is written last.
    lines = [l for l in result.stdout.splitlines() if "kv key put" in l]
    assert loader.KEY_MANIFEST in lines[-1]


# ── the Worker wires it up ───────────────────────────────────────────────────

def test_the_worker_routes_policy_check_and_holds_no_determinations():
    entry = (WORKER_ROOT / "src" / "entry.py").read_text()
    assert "/v1/policy-check" in entry
    assert "policy_service.check(" in entry
    # The entitlement decision is one function, and it is the only place a
    # request is granted the private store, by the tier MODEL-69's gate resolved.
    assert "def _entitlement(" in entry
    # The Worker verifies the KV bundle against its manifest rather than
    # trusting whatever is in the namespace.
    assert "does not match the manifest" in entry


def test_the_service_imports_nothing_from_the_workers_runtime():
    source = (WORKER_ROOT / "src" / "policy_service.py").read_text()
    for forbidden in ("from js import", "from workers import", "import pipeline",
                      "import schema"):
        assert forbidden not in source


# ── the deploy smoke test's checker, fed real responses ──────────────────────

checker = _load("modelspec_check_policy_response",
                REPO_ROOT / ".github" / "scripts" / "check_policy_response.py")


def test_the_smoke_checker_accepts_a_real_response_and_rejects_a_merged_one():
    """The one regression that would matter: `undetermined` shaped like `pass`.

    The checker is what stands between a deploy and a response where the two
    are indistinguishable, so it is exercised against real output here rather
    than only against a hand-written fixture in CI.
    """
    _, body = check({"policy": {"origin": {"permitted_countries": ["US"]}}},
                    [_model("acme/us"), _model("acme/cn", country="CN"),
                     _model("acme/blank", country="")])
    assert checker.check_verdicts(body) == []

    # A row that claims a verdict and carries another verdict's block.
    merged = json.loads(json.dumps(body))
    undetermined_row = next(r for r in merged["result"] if r["verdict"] == "undetermined")
    undetermined_row["passed"] = {"constraints": ["origin"], "conditions": []}
    assert checker.check_verdicts(merged), "an undetermined row carrying `passed` passed"

    # A check that claims undetermined and carries `satisfied`.
    merged = json.loads(json.dumps(body))
    row = next(r for r in merged["result"] if r["verdict"] == "undetermined")
    row["checks"][0]["satisfied"] = {"origin_country": "US"}
    assert checker.check_verdicts(merged), "an undetermined check carrying `satisfied` passed"

    # A violated check with no citation date cannot be defended later.
    merged = json.loads(json.dumps(body))
    failed = next(r for r in merged["result"] if r["verdict"] == "fail")
    failed["checks"][0]["violated"]["source"] = {"kind": "license", "url": "u",
                                                 "read_on": None}
    assert checker.check_verdicts(merged), "a violated check with no read date passed"


def test_the_smoke_checker_holds_the_hard_failure_to_being_hard():
    _, body = check({"policy": {"origin": {"permitted_countries": ["US"]}},
                     "require_no_undetermined": True},
                    [_model("acme/blank", country="")])
    assert checker.check_undetermined(body) == []
    soft = json.loads(json.dumps(body))
    soft["result"] = [{"model_id": "acme/blank"}]
    assert checker.check_undetermined(soft), "a 422 that still returned rows passed"


def test_the_workflow_runs_the_policy_suite_and_smoke_checks_it():
    workflow = (REPO_ROOT / ".github" / "workflows" / "rank-api.yml").read_text()
    assert "tests/test_policy_check.py" in workflow
    assert "check_policy_response.py verdicts" in workflow
    assert "check_policy_response.py undetermined" in workflow
    # The workflow must never gain a path to the determinations.
    assert "commercial_use.jsonl" not in workflow
    assert "modelspec-business" not in workflow


def test_the_site_build_publishes_the_policy_export():
    workflow = (REPO_ROOT / ".github" / "workflows" / "deploy-sites.yml").read_text()
    assert "dist/modelspec/api/policy/catalogue.json" in workflow
    build = (REPO_ROOT / "pipeline" / "build.py").read_text()
    assert "policy_export.write_export(" in build
