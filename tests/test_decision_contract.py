"""MODEL-135: the decision contract, v1.

The contract comes before the engine so the engine tickets (MODEL-141, 142,
145) can build against it in parallel. These tests hold what a caller relies
on: every type round-trips, the condition grammar reads the same in its YAML
and compact forms, an invalid spec names the condition, field and reason, the
spec hash is canonical, and the public document, the generated JSON Schema and
the types agree.

The facet registry (MODEL-133, ``decision.registry.facet``) was being built in
parallel, so these tests inject a small stub with the agreed interface
(``.id``, ``.value_type``, ``.tier``, ``.risk``; ``KeyError`` when unknown).
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from decision import contract as c  # noqa: E402
from decision import decide  # noqa: E402

DOC = REPO_ROOT / "docs" / "decision-contract.md"
SCHEMA = REPO_ROOT / "docs" / "decision-contract.schema.json"


# ── registry stub (MODEL-133's interface) ─────────────────────────────────


@dataclass(frozen=True)
class _Facet:
    id: str
    value_type: str
    tier: str
    risk: str


_STUB = {
    f.id: f
    for f in [
        _Facet("input_price", "number", "guaranteed", "capability"),
        _Facet("context_window", "integer", "guaranteed", "capability"),
        _Facet("swe_bench_pro", "number", "best_effort", "capability"),
        _Facet("coding", "number", "guaranteed", "capability"),
        _Facet("cost_per_task", "number", "best_effort", "capability"),
        _Facet("output_tps", "number", "best_effort", "capability"),
        _Facet("offered_on", "string", "guaranteed", "capability"),
        _Facet("deployment", "enum", "guaranteed", "capability"),
        _Facet("license", "enum", "guaranteed", "governance"),
        _Facet("origin.lab_country", "enum", "guaranteed", "governance"),
        _Facet("data.trains_on_customer_data", "bool", "guaranteed", "governance"),
        _Facet("license.commercial_use", "bool", "guaranteed", "governance"),
        _Facet("parameters.total", "integer", "best_effort", "capability"),
        _Facet("release_date", "date", "guaranteed", "capability"),
    ]
}


def stub_facet(facet_id: str) -> _Facet:
    return _STUB[facet_id]


# ── the DPF example, the one every section below leans on ────────────────

DPF_SPEC = """
spec_version: 1
snapshot: latest
profile: profile:acme-prod
task_type: refactor
capabilities:
  coding.rust: required
  formal_verification: preferred
where:
  - input_price in [0.50, 3.00]
  - swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01
  - any: [ offered_on = aws-bedrock:us-east-1, deployment = self_hosted ]
  - not: license = noncommercial
  - coding >= model(openai/gpt-6-sol)
  - context_window >= 200000 soft(0.2)
optimize:
  weights: { coding: 0.6, -cost_per_task: 0.3, output_tps: 0.1 }
unknowns: default
explain: summary
limit: 20
save_as: acme-rust-refactor
"""


def _spec(text: str = DPF_SPEC) -> c.Spec:
    return c.parse_spec(text, facets=stub_facet)


# ── the compact condition grammar ─────────────────────────────────────────


COMPACT = [
    "input_price in [0.5, 3.0]",
    "swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01",
    "offered_on = aws-bedrock:us-east-1",
    "license != noncommercial",
    "coding >= model(openai/gpt-6-sol)",
    "context_window >= 200000 soft(0.2)",
    "context_window >= 200000 soft(penalty: 0.2)",
    "origin.lab_country in {US}",
    "origin.lab_country not in {CN, RU}",
    "known(parameters.total)",
    "known(parameters.total) soft(0.1)",
    "swe_bench_pro > 40 @provider_self_report @max_effort",
    "swe_bench_pro > 40 @any @effort(high) @harness(claude-code@2.1) @direct",
    "data.trains_on_customer_data = false unknown(fail)",
    "data.trains_on_customer_data = false unknown: fail",
    "release_date >= 2026-01-01 unknown(pass)",
    'offered_on = "odd value, with a comma"',
    "any(offered_on = aws-bedrock:us-east-1; deployment = self_hosted)",
    "all(input_price <= 3; not(license = noncommercial)) soft(0.5)",
    "not(license = noncommercial) unknown(list)",
    "input_price < -1.5",
]


@pytest.mark.parametrize("text", COMPACT)
def test_compact_conditions_round_trip(text: str) -> None:
    cond = c.parse_condition(text)
    rendered = c.render_condition(cond)
    again = c.parse_condition(rendered)
    assert again == cond
    assert c.render_condition(again) == rendered


@pytest.mark.parametrize("text", COMPACT)
def test_compact_and_yaml_forms_are_the_same_condition(text: str) -> None:
    cond = c.parse_condition(text)
    as_yaml = cond.model_dump(mode="json", by_alias=True, exclude_none=True)
    assert c.parse_condition(as_yaml) == cond


def test_evidence_qualifiers_parse_into_named_fields() -> None:
    cond = c.parse_condition(
        "swe_bench_pro >= 55 @independent @default_effort @harness(codex-cli@1.4) "
        "@direct measured_after 2026-06-01"
    )
    assert isinstance(cond, c.Compare)
    q = cond.qualifiers
    assert q is not None
    assert q.measured_by == "independent"
    assert q.effort == "default"
    assert q.harness == "codex-cli@1.4"
    assert q.direct is True
    assert q.measured_after == date(2026, 6, 1)


def test_relative_condition_names_the_model() -> None:
    cond = c.parse_condition("coding >= model(openai/gpt-6-sol)")
    assert isinstance(cond, c.Compare)
    assert cond.value == c.ModelRef(model="openai/gpt-6-sol")


def test_set_values_are_canonically_ordered() -> None:
    assert c.parse_condition("x in {b, a}") == c.parse_condition("x in {a, b, a}")


def test_iso_dates_are_dates_in_both_forms() -> None:
    compact = c.parse_condition("release_date >= 2026-01-01")
    as_dict = c.parse_condition({"facet": "release_date", "op": ">=", "value": "2026-01-01"})
    assert compact == as_dict
    assert compact.value == date(2026, 1, 1)


# ── invalid conditions name the condition, the field and the reason ───────


BAD_CONDITIONS = [
    ("swe_bench_pro >= 55 @independnt", "swe_bench_pro", "@independnt"),
    ("swe_bench_pro >= 55 @independent @provider_self_report", "swe_bench_pro", "measured_by"),
    ("swe_bench_pro >=", "swe_bench_pro", "value"),
    ("input_price in [3, 1]", "input_price", "low"),
    ("known(parameters.total) unknown(list)", "parameters.total", "known()"),
    ("context_window >= 1 soft(0)", "context_window", "penalty"),
    ("swe_bench_pro > 1 @harness(claude-code)", "swe_bench_pro", "name@major.minor"),
    ("coding >= model(GPT 6)", "coding", "model"),
    ("coding == 3", "coding", "operator"),
    ("coding >= 3 unknown(maybe)", "coding", "unknown"),
    ("coding >= 3 measured_after yesterday", "coding", "date"),
    ("Coding >= 3", "Coding", "facet"),
    ("x in {}", "x", "empty"),
    ("any(a = 1)", None, "at least two"),
]


@pytest.mark.parametrize(("text", "field", "reason"), BAD_CONDITIONS)
def test_bad_conditions_name_condition_field_and_reason(text, field, reason) -> None:
    with pytest.raises(c.SpecError) as info:
        c.parse_spec({"spec_version": 1, "where": [text], "optimize": {"max": "coding"}},
                     facets=None)
    [issue] = info.value.issues
    assert issue.condition == text
    assert issue.field == field
    assert reason in issue.reason
    assert issue.path == "where[0]"
    # the message a person reads carries all three
    message = str(info.value)
    assert text in message and reason in message


def test_a_bad_nested_condition_points_at_its_own_path() -> None:
    raw = {
        "spec_version": 1,
        "where": ["coding >= 1", {"any": ["deployment = self_hosted", "coding >= @x"]}],
        "optimize": {"max": "coding"},
    }
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=None)
    [issue] = info.value.issues
    assert issue.path == "where[1].any[1]"
    assert issue.condition == "coding >= @x"
    assert issue.field == "coding"


def test_yaml_splitting_a_compact_condition_gets_a_useful_error() -> None:
    text = "spec_version: 1\noptimize: {max: coding}\nwhere:\n  - coding >= 1 soft(penalty: 0.2)\n"
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(text, facets=None)
    [issue] = info.value.issues
    assert "soft(0.2)" in issue.reason and "quote" in issue.reason
    assert issue.path == "where[0]"


def test_a_bad_yaml_form_condition_is_reported_too() -> None:
    raw = {"spec_version": 1, "optimize": {"max": "coding"},
           "where": [{"facet": "coding", "op": ">=", "value": 3, "soft": {"penalty": 2}}]}
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=None)
    [issue] = info.value.issues
    assert issue.field == "coding"
    assert "penalty" in issue.reason
    assert issue.path == "where[0]"


# ── the registry: unknown facet names fail loudly ─────────────────────────


def test_unknown_facet_fails_naming_it() -> None:
    text = DPF_SPEC.replace("input_price in", "input_prize in")
    with pytest.raises(c.SpecError) as info:
        _spec(text)
    [issue] = info.value.issues
    assert issue.field == "input_prize"
    # registry checks run on the parsed spec, so the condition is quoted canonically
    assert issue.condition == "input_prize in [0.5, 3.0]"
    assert "unknown facet" in issue.reason
    assert issue.path == "where[0]"


def test_every_facet_reference_is_checked() -> None:
    raw = {
        "spec_version": 1,
        "where": [{"not": "nope_a = 1"}],
        "optimize": {"weights": {"coding": 1, "-nope_b": 1}},
        "profile": {"profile_version": 1, "rules": ["nope_c = true"]},
    }
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=stub_facet)
    fields = {i.field for i in info.value.issues}
    assert fields == {"nope_a", "nope_b", "nope_c"}
    paths = {i.path for i in info.value.issues}
    assert paths == {"where[0].not", "optimize.weights", "profile.rules[0]"}


def test_ordering_an_unordered_facet_is_rejected() -> None:
    raw = {"spec_version": 1, "where": ["license.commercial_use >= true"],
           "optimize": {"max": "coding"}}
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=stub_facet)
    [issue] = info.value.issues
    assert issue.field == "license.commercial_use"
    assert "bool" in issue.reason


def test_optimising_an_unordered_facet_is_rejected() -> None:
    raw = {"spec_version": 1, "optimize": {"max": "license"}}
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=stub_facet)
    [issue] = info.value.issues
    assert issue.field == "license"
    assert issue.path == "optimize.max"


# ── the spec ──────────────────────────────────────────────────────────────


def test_the_dpf_example_parses() -> None:
    spec = _spec()
    assert spec.spec_version == 1
    assert spec.snapshot == "latest"
    assert spec.profile == "profile:acme-prod"
    assert spec.task_type == "refactor"
    assert spec.capabilities == {"coding.rust": "required", "formal_verification": "preferred"}
    assert len(spec.where) == 6
    assert isinstance(spec.where[2], c.AnyOf)
    assert isinstance(spec.where[3], c.NotOf)
    assert spec.optimize.weights == {"coding": 0.6, "-cost_per_task": 0.3, "output_tps": 0.1}
    assert spec.explain == "summary"
    assert spec.limit == 20
    assert spec.save_as == "acme-rust-refactor"


def test_free_text_task_is_parsed_but_rejected_in_slice_1() -> None:
    text = DPF_SPEC + 'task: "Refactor the Rust parser module"\n'
    with pytest.raises(c.SpecError) as info:
        _spec(text)
    [issue] = info.value.issues
    assert issue.field == "task"
    assert "not yet in slice 1" in issue.reason
    # the parser itself accepts it; the rejection is a slice-1 rule
    assert c.Spec.model_validate(yaml.safe_load(text)).task.startswith("Refactor")


@pytest.mark.parametrize(
    ("patch", "field", "reason"),
    [
        ({"spec_version": 2}, "spec_version", "1"),
        ({"snapshot": "yesterday"}, "snapshot", "snap_"),
        ({"profile": "acme"}, "profile", "profile:"),
        ({"explain": "verbose"}, "explain", "summary"),
        ({"limit": 0}, "limit", "1"),
        ({"save_as": "Has Spaces"}, "save_as", "pattern"),
        ({"task_type": "vibes"}, "task_type", "refactor"),
        ({"capabilities": {"coding": "nice"}}, "capabilities.coding", "required"),
        ({"unknowns": "pass"}, "unknowns", "default"),
        ({"wher": []}, "wher", "not a spec field"),
        ({"optimize": {}}, "optimize", "exactly one"),
        ({"optimize": {"max": "coding", "min": "input_price"}}, "optimize", "exactly one"),
        ({"optimize": {"weights": {"coding": 0}}}, "optimize.weights", "positive"),
        ({"optimize": {"weights": {"coding": 1, "-coding": 1}}}, "optimize.weights", "twice"),
        ({"optimize": {"pareto": ["coding"]}}, "optimize.pareto", "two"),
        ({"optimize": {"lexicographic": [{"max": "coding"}]}}, "optimize.lexicographic", "two"),
        ({"optimize": {"lexicographic": [{"max": "coding"}, {"min": "input_price within 5%"}]}},
         "optimize.lexicographic", "last"),
    ],
)
def test_invalid_spec_fields_name_field_and_reason(patch, field, reason) -> None:
    raw = {"spec_version": 1, "optimize": {"max": "coding"}} | patch
    with pytest.raises(c.SpecError) as info:
        c.parse_spec(raw, facets=None)
    issues = info.value.issues
    assert any(i.field == field and reason in i.reason for i in issues), issues


def test_optimize_is_required() -> None:
    with pytest.raises(c.SpecError) as info:
        c.parse_spec({"spec_version": 1}, facets=None)
    assert [i.field for i in info.value.issues] == ["optimize"]


def test_lexicographic_tolerances() -> None:
    spec = c.parse_spec(
        {"spec_version": 1, "optimize": {"lexicographic": [
            {"max": "output_tps within 5%"},
            {"min": "cost_per_task", "within": 0.25},
            {"max": "coding"},
        ]}},
        facets=stub_facet,
    )
    steps = spec.optimize.lexicographic
    assert steps[0].max == "output_tps" and steps[0].within == c.Tolerance(relative=0.05)
    assert steps[1].min == "cost_per_task" and steps[1].within == c.Tolerance(absolute=0.25)
    assert steps[2].within is None


def test_duplicate_yaml_keys_are_rejected() -> None:
    with pytest.raises(c.SpecError) as info:
        c.parse_spec("spec_version: 1\nlimit: 5\nlimit: 6\noptimize: {max: coding}\n",
                     facets=None)
    assert "limit" in str(info.value)


def test_inline_profile() -> None:
    spec = c.parse_spec(
        {
            "spec_version": 1,
            "optimize": {"max": "coding"},
            "profile": {
                "profile_version": 1,
                "id": "profile:acme-prod",
                "offerings": [{"model": "anthropic/claude-opus-5-5", "provider": "aws-bedrock",
                               "region": "us-east-1", "tier": "enterprise"}],
                "local": [{"model": "qwen/qwen3-8-27b", "runtime": "vllm",
                           "hardware": {"class": "nvidia-dgx-spark", "count": 2,
                                        "memory_gb": 256}}],
                "harnesses": ["claude-code@2.1", "dpf-native@1.0"],
                "rules": ["origin.lab_country in {US}", "license.commercial_use = true"],
                "budget": {"max_cost_per_task_usd": 2.0},
            },
        },
        facets=stub_facet,
    )
    assert isinstance(spec.profile, c.InventoryProfile)
    assert spec.profile.local[0].hardware.class_ == "nvidia-dgx-spark"
    assert len(spec.profile.rules) == 2


# ── the canonical spec hash ───────────────────────────────────────────────


def test_hash_has_the_published_shape() -> None:
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", c.spec_hash(_spec()))


def test_hash_is_stable_under_key_order_and_whitespace() -> None:
    reordered = """
optimize:
    weights:   {output_tps: 0.1,   -cost_per_task: 0.3, coding: 0.6}
save_as: acme-rust-refactor
limit: 20
explain:    summary
where:
  - "input_price   in [0.5,3]"
  - swe_bench_pro >= 55   @independent  @default_effort measured_after 2026-06-01
  - any: [ offered_on = aws-bedrock:us-east-1, deployment = self_hosted ]
  - not: license = noncommercial
  - coding >= model(openai/gpt-6-sol)
  - context_window >= 200000.0   soft(0.2)
capabilities: {formal_verification: preferred, coding.rust: required}
task_type: refactor
profile: profile:acme-prod
snapshot: latest
spec_version: 1
"""
    assert c.spec_hash(_spec(reordered)) == c.spec_hash(_spec())


def test_hash_is_the_same_for_compact_and_yaml_conditions() -> None:
    compact = {"spec_version": 1, "optimize": {"max": "coding"},
               "where": ["swe_bench_pro >= 55 @independent measured_after 2026-06-01"]}
    structured = {"spec_version": 1, "optimize": {"max": "coding"},
                  "where": [{"facet": "swe_bench_pro", "op": ">=", "value": 55,
                             "qualifiers": {"measured_by": "independent",
                                            "measured_after": "2026-06-01"}}]}
    assert c.spec_hash(c.parse_spec(compact, facets=stub_facet)) == \
        c.spec_hash(c.parse_spec(structured, facets=stub_facet))


def test_hash_treats_omitted_defaults_as_the_defaults() -> None:
    bare = {"spec_version": 1, "optimize": {"max": "coding"}}
    explicit = bare | {"snapshot": "latest", "explain": "summary", "limit": 20,
                       "unknowns": "default", "where": []}
    assert c.spec_hash(c.parse_spec(bare, facets=None)) == \
        c.spec_hash(c.parse_spec(explicit, facets=None))


def test_hash_changes_when_the_spec_does() -> None:
    assert c.spec_hash(_spec()) != c.spec_hash(_spec(DPF_SPEC.replace("0.6", "0.7")))
    # condition order is part of the spec: it orders the elimination funnel
    swapped = DPF_SPEC.replace(
        "  - input_price in [0.50, 3.00]\n  - swe_bench_pro",
        "  - swe_bench_pro",
    ).replace("  - any:", "  - input_price in [0.50, 3.00]\n  - any:")
    assert c.spec_hash(_spec(swapped)) != c.spec_hash(_spec())


def test_hash_is_pinned() -> None:
    """A change here changes every published spec_hash: that is a contract change."""
    spec = c.parse_spec({"spec_version": 1, "optimize": {"max": "coding"}}, facets=None)
    assert c.canonical_json(spec) == (
        '{"explain":"summary","limit":20,"optimize":{"max":"coding"},'
        '"snapshot":"latest","spec_version":1,"unknowns":"default","where":[]}'
    )


# ── the decision ──────────────────────────────────────────────────────────


EVIDENCE = {
    "benchmark": "multi_swe_bench", "version": "1.0", "sub_category": "rust",
    "value": 48.2, "unit": "percent", "measured_by": "independent", "effort": "default",
    "harness": "claude-code@2.1", "date": "2026-09-20", "date_type": "observed",
    "source": "https://example.org/leaderboard", "directness": "direct",
}

DECISION = {
    "contract_version": c.CONTRACT_VERSION,
    "decision_id": "dec_01J8ZK3Q7Y",
    "snapshot": "snap_2026-09-24T06:00Z",
    "spec_hash": "sha256:" + "0" * 64,
    "explain": "full",
    "status": "answered",
    "results": [{
        "rank": 1,
        "offering": {"model": "anthropic/claude-opus-5-5", "provider": "aws-bedrock",
                     "region": "us-east-1", "tier": "enterprise"},
        "harness": "claude-code@2.1",
        "effort": "high",
        "evidence": [{"domain": "coding.rust", "items": [EVIDENCE]}],
        "estimates": [{"domain": "coding.rust", "value": 0.81, "interval": [0.74, 0.87]}],
        "p_best": 0.62,
        "top3_stability": 0.94,
        "soft_penalty": 0.0,
        "contributions": [{"dimension": "coding.rust", "weight": 0.6, "value": 0.81,
                           "normalisation": "min-max over the feasible set",
                           "evidence": [EVIDENCE]}],
        "warnings": ["provisional_released_2_days_ago"],
    }],
    "may_qualify": [{"model": "google/gemini-3-8-pro",
                     "unknown": ["data.trains_on_customer_data"]}],
    "eliminated": {
        "funnel": [{"condition": "input_price in [0.5, 3.0]", "before": 212, "after": 64,
                    "may_qualify": 3}],
        "models": [{"model": "acme/slow-1", "condition": "swe_bench_pro >= 55 @independent",
                    "value": 41.0}],
    },
    "constraint_costs": [{"condition": "origin.lab_country in {US}", "admits": 12,
                          "gain": {"coding.rust": 0.06}}],
    "tipping_points": [{"description": "rank 1 holds unless the cost weight exceeds 0.35",
                        "dimension": "-cost_per_task", "threshold": 0.35,
                        "new_top": "openai/gpt-6-sol"}],
    "relax": [],
    "warnings": [],
}


def test_decision_round_trips() -> None:
    decision = c.Decision.model_validate(DECISION)
    dumped = decision.model_dump(mode="json", by_alias=True)
    assert c.Decision.model_validate(dumped) == decision
    assert dumped["results"][0]["evidence"][0]["items"][0]["date"] == "2026-09-20"


def test_no_feasible_names_what_to_relax() -> None:
    raw = DECISION | {"status": "no_feasible", "results": [], "relax": []}
    with pytest.raises(ValueError, match="relax"):
        c.Decision.model_validate(raw)
    ok = c.Decision.model_validate(raw | {"relax": ["input_price in [0.5, 3.0]"]})
    assert ok.relax == ["input_price in [0.5, 3.0]"]


def test_no_feasible_has_no_results_and_answered_has_no_relax() -> None:
    with pytest.raises(ValueError, match="no_feasible"):
        c.Decision.model_validate(DECISION | {"status": "no_feasible", "relax": ["x = 1"]})
    with pytest.raises(ValueError, match="relax"):
        c.Decision.model_validate(DECISION | {"relax": ["x = 1"]})


def test_a_decision_cites_a_concrete_snapshot() -> None:
    with pytest.raises(ValueError, match="snap_"):
        c.Decision.model_validate(DECISION | {"snapshot": "latest"})


def test_estimates_and_p_best_are_optional_in_slice_1() -> None:
    result = dict(DECISION["results"][0])
    for key in ("estimates", "p_best", "top3_stability"):
        result.pop(key)
    decision = c.Decision.model_validate(DECISION | {"results": [result]})
    assert decision.results[0].estimates is None
    assert decision.results[0].p_best is None


def test_ranks_are_one_to_n() -> None:
    second = dict(DECISION["results"][0]) | {"rank": 3}
    with pytest.raises(ValueError, match="rank"):
        c.Decision.model_validate(DECISION | {"results": [DECISION["results"][0], second]})


# ── round-trip every type ─────────────────────────────────────────────────


def _samples() -> list:
    spec = _spec()
    decision = c.Decision.model_validate(DECISION)
    result = decision.results[0]
    return [
        spec,
        spec.optimize,
        c.Objective(max="coding"),
        c.Objective(pareto=["coding", "-cost_per_task"]),
        c.Objective(lexicographic=[c.LexStep(max="output_tps", within=c.Tolerance(relative=0.05)),
                                   c.LexStep(min="cost_per_task")]),
        c.LexStep(min="cost_per_task", within=c.Tolerance(relative=0.1)),
        c.Tolerance(absolute=1.5),
        c.Hardware(class_="nvidia-dgx-spark", count=2, memory_gb=256),
        c.EvidenceQualifiers(measured_by="any", effort="max", harness="aider@0.9",
                             measured_after=date(2026, 1, 1), direct=True),
        c.Soft(penalty=0.2),
        c.ModelRef(model="openai/gpt-6-sol"),
        *[c.parse_condition(t) for t in COMPACT],
        c.InventoryProfile(profile_version=1, harnesses=["claude-code@2.1"]),
        c.ProfileOffering(model="openai/gpt-6-sol", provider="openai"),
        c.LocalModel(model="qwen/qwen3-8-27b", hardware=c.Hardware(class_="dgx", count=1)),
        c.Budget(max_cost_per_task_usd=2.0),
        decision,
        result,
        result.offering,
        result.evidence[0],
        result.evidence[0].items[0],
        result.estimates[0],
        result.contributions[0],
        decision.may_qualify[0],
        decision.eliminated,
        decision.eliminated.funnel[0],
        decision.eliminated.models[0],
        decision.constraint_costs[0],
        decision.tipping_points[0],
        c.NearMiss(offering=result.offering, condition="context >= 90", distance=10),
        c.ShownFact(facet="context", value=80, unit="tokens"),
        c.CandidateValues(offering=result.offering),
        c.NumberOrigin(path="/results/0/rank", basis="ordinal"),
    ]


def test_every_contract_type_has_a_round_trip_sample() -> None:
    covered = {type(s) for s in _samples()}
    missing = {t.__name__ for t in c.CONTRACT_TYPES} - {t.__name__ for t in covered}
    assert not missing


@pytest.mark.parametrize("sample", _samples(), ids=lambda s: type(s).__name__)
def test_every_type_round_trips_through_json(sample) -> None:
    kind = type(sample)
    as_json = json.dumps(sample.model_dump(mode="json", by_alias=True, exclude_none=True))
    again = kind.model_validate(json.loads(as_json))
    assert again == sample


# ── library entry point ───────────────────────────────────────────────────


def test_decide_requires_a_snapshot() -> None:
    with pytest.raises(ValueError, match="snapshot is required"):
        decide(_spec(), None)


# ── the public document, the JSON Schema and the types agree ─────────────


def test_schema_file_is_generated_from_the_types() -> None:
    expected = c.render_json_schema()
    assert SCHEMA.read_text() == expected, (
        "docs/decision-contract.schema.json is stale; regenerate with "
        "`python -m decision.schema`"
    )


def test_doc_names_the_contract_version() -> None:
    text = DOC.read_text()
    assert f"Contract version: **{c.CONTRACT_VERSION}**" in text
    assert json.loads(SCHEMA.read_text())["x-contract-version"] == c.CONTRACT_VERSION


def _all_fields(model: type) -> set[str]:
    return {f.alias or name for name, f in model.model_fields.items()}


def test_doc_names_every_field_of_every_type() -> None:
    text = DOC.read_text()
    missing = sorted(
        f"{t.__name__}.{name}"
        for t in c.CONTRACT_TYPES
        for name in _all_fields(t)
        if f"`{name}`" not in text
    )
    assert not missing, f"fields not documented in {DOC.name}: {missing}"


def test_doc_names_every_closed_value() -> None:
    text = DOC.read_text()
    missing = sorted(v for v in c.closed_values() if f"`{v}`" not in text)
    assert not missing, f"values not documented in {DOC.name}: {missing}"


def test_doc_examples_are_valid() -> None:
    text = DOC.read_text()
    specs = re.findall(r"```yaml spec\n(.*?)```", text, re.S)
    decisions = re.findall(r"```json decision\n(.*?)```", text, re.S)
    conditions = re.findall(r"```text conditions\n(.*?)```", text, re.S)
    assert specs and decisions and conditions
    for block in specs:
        c.parse_spec(block, facets=None)
    for block in decisions:
        c.Decision.model_validate_json(block)
    for block in conditions:
        for line in block.splitlines():
            if line.strip():
                c.parse_condition(line.strip())
