"""MODEL-100: which *class* of model a problem needs, before ranking within one.

The design is `docs/design/class-selection.md`; these are the tests that hold
it. Written first, so this file is red on its own.

Four claims are under test, and the third is the one that matters most:

* the taxonomy is a **view** over `ModelType` — every value is placed, and a
  new enum member is a red test on the commit that adds it;
* a class is **derived** from the pair `(emits, decides)`, not hand-listed;
* **no number ever orders one class above another**, and cost-to-correct
  evidence (MODEL-99) never reaches `rank_score`;
* the **refusal paths exist from the first commit**. A class-fit answer that
  could only ever say yes is the failure mode this work exists to avoid.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from api import class_fit as cf
from api import classes as cls
from api.ranking.engine import USE_CASE_PROFILES, neutrality_commitment
from schema.enums import ModelType

REPO_ROOT = Path(__file__).resolve().parents[1]


# ── 1. the taxonomy is a view over ModelType ────────────────────────────────


def test_every_model_type_is_placed_exactly_once() -> None:
    """A new enum member fails here, which is where its class gets argued."""
    placed: dict[str, str] = {}
    for model_class in cls.CLASSES:
        for value in model_class.model_types:
            assert value not in placed, f"{value} placed twice"
            placed[value] = model_class.id
    for non_class, values in cls.NON_CLASSES.items():
        for value in values:
            assert value not in placed, f"{value} placed twice"
            placed[value] = non_class

    assert set(placed) == {t.value for t in ModelType}


def test_every_placed_value_is_a_real_model_type() -> None:
    """A typo is a test failure, not a silent no-op (schema/applicability.py)."""
    for value in cls.MODEL_TYPE_PLACEMENT:
        ModelType(value)


def test_the_decision_model_class_is_the_decider() -> None:
    """MODEL-98's value is the one this whole ticket was opened for."""
    assert cls.class_for_model_type("decision-model") == "decider"
    assert cls.class_for_model_type("router") == "decider"


def test_lineage_values_name_no_class_and_say_where_to_look() -> None:
    for value in ("adapter", "quantized-variant", "distilled", "merged"):
        assert cls.class_for_model_type(value) is None
        assert cls.non_class_for_model_type(value) == "derived"
    assert "lineage.base_model" in cls.NON_CLASS_RESOLUTION["derived"]


def test_miscellaneous_is_not_a_class() -> None:
    assert cls.class_for_model_type("miscellaneous") is None
    assert cls.non_class_for_model_type("miscellaneous") == "unclassified"


def test_domain_values_are_text_generators_not_classes_of_their_own() -> None:
    for value in ("medical", "legal", "financial"):
        assert cls.class_for_model_type(value) == "text-generator"


# ── 2. the class is derived from the facets, not hand-listed ────────────────


def test_the_emits_decides_pair_is_injective() -> None:
    """`class = CLASS_BY_PAIR[(emits, decides)]` has to be a function."""
    pairs = [(c.emits, c.decides) for c in cls.CLASSES]
    assert len(set(pairs)) == len(pairs)
    for model_class in cls.CLASSES:
        assert cls.CLASS_BY_PAIR[(model_class.emits, model_class.decides)] == model_class.id


def test_every_facet_value_is_in_the_published_vocabulary() -> None:
    for model_class in cls.CLASSES:
        assert model_class.emits in cls.EMITS
        assert model_class.decides in cls.DECIDES
        assert model_class.consumes
        for kind in model_class.consumes:
            assert kind in cls.CONSUMES


def test_the_two_decision_shapes_that_distinguish_a_decider_are_both_used() -> None:
    """`schema/enums.py` says a classifier's taxonomy is fixed and a decision
    model's is per request. That sentence is the axis, so both values exist."""
    shapes = {c.decides for c in cls.CLASSES}
    assert "which_of_a_fixed_set" in shapes
    assert "which_of_a_caller_defined_set" in shapes


# ── 3. no cross-class scores ────────────────────────────────────────────────


def _numbers(node: object, path: str = "") -> list[str]:
    """Every path under `node` holding an int or a float."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            found += _numbers(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += _numbers(value, f"{path}[{index}]")
    elif isinstance(node, bool):
        pass
    elif isinstance(node, (int, float)):
        found.append(path)
    return found


#: The one number a class may carry: an inventory count, not a score.
ALLOWED_NUMERIC_SUFFIXES = (".catalogue.card_count",)


def test_no_candidate_class_carries_a_number_that_is_not_an_inventory_count() -> None:
    answer = cf.class_fit(task="write a summary a person will read")
    offenders = [
        path for path in _numbers(answer["candidates"], "candidates")
        if not path.endswith(ALLOWED_NUMERIC_SUFFIXES)
    ]
    assert offenders == [], f"a number appeared beside a class: {offenders}"


def test_candidates_are_returned_in_sorted_order_so_no_ranking_hides_in_it() -> None:
    answer = cf.class_fit(emits="choice", consumes=["structured_state"])
    ids = [c["class"] for c in answer["candidates"]]
    assert ids == sorted(ids)
    assert len(ids) > 1


def test_the_answer_never_claims_to_order_classes() -> None:
    answer = cf.class_fit(emits="choice", consumes=["structured_state"])
    assert answer["policy"]["orders_classes"] is False
    assert answer["policy"]["cross_class_scores"] == "never"
    for candidate in answer["candidates"]:
        assert "score" not in candidate
        assert "rank" not in candidate


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def test_the_scorer_does_not_import_class_fit_in_either_direction() -> None:
    """The boundary is visible in a `git diff`, not left to good intentions.

    Cost-to-correct is fitness evidence for a *task*; `rank_score` is a
    within-class composite. If the scorer could see this package, a measurement
    of one task could lift a model in a ranking of another, invisibly.
    """
    for relative in ("api/ranking/engine.py", "pipeline/ranking.py"):
        imported = _imports(REPO_ROOT / relative)
        assert not {"api.classes", "api.class_fit"} & imported, relative


def test_the_rule_imports_only_the_taxonomy_and_the_standard_library() -> None:
    imported = _imports(REPO_ROOT / "api" / "class_fit.py")
    repo_imports = {n for n in imported if n.split(".")[0] in {"api", "pipeline", "schema", "cli"}}
    assert repo_imports == {"api.classes"}


def test_the_taxonomy_imports_nothing_from_this_repository() -> None:
    """Stdlib only, so the Worker bundle can vendor it unchanged."""
    imported = _imports(REPO_ROOT / "api" / "classes.py")
    assert not {n for n in imported if n.split(".")[0] in {"api", "pipeline", "schema", "cli"}}


def test_no_cost_to_correct_number_is_served() -> None:
    """MODEL-99's figures stay in docs/research/. A number beside a class name
    is a score whatever the key is called."""
    answer = cf.class_fit(emits="choice", consumes=["structured_state"])
    blob = json.dumps(answer)
    for figure in ("90.1", "97.9", "0.036", "1.447", "180", "5253"):
        assert figure not in blob


# ── 4. the refusals, which ship with the first answer path ──────────────────


def test_an_empty_request_is_refused_and_says_what_would_have_worked() -> None:
    answer = cf.class_fit()
    assert answer["fit_status"] == "refused"
    assert answer["refusal"]["code"] == "empty_request"
    assert answer["refusal"]["vocabulary"]["emits"] == list(cls.EMITS)


def test_prose_that_matches_no_published_term_is_refused_not_guessed_at() -> None:
    answer = cf.class_fit(task="zzzz qqqq wwww")
    assert answer["fit_status"] == "refused"
    assert answer["refusal"]["code"] == "no_term_matched"
    assert answer["candidates"] == []
    # The caller is handed the whole class list rather than a guess.
    assert len(answer["refusal"]["classes"]) == len(cls.CLASSES)


def test_a_facet_value_outside_the_vocabulary_is_refused_by_name() -> None:
    answer = cf.class_fit(emits="vibes")
    assert answer["fit_status"] == "refused"
    assert answer["refusal"]["code"] == "unknown_facet_value"
    assert answer["refusal"]["field"] == "emits"
    assert answer["refusal"]["value"] == "vibes"


def test_the_request_text_is_never_echoed_back() -> None:
    """Prose is a term source only. `neutrality_commitment()` publishes
    `stores_customer_prompts: false` as architecture, not a promise."""
    secret = "classify the internal codename thunderbird"
    answer = cf.class_fit(task=secret)
    blob = json.dumps(answer)
    assert "thunderbird" not in blob
    assert "classify" in blob  # the matched term, and only the matched term


def test_a_task_nothing_emits_is_unavailable_not_empty() -> None:
    answer = cf.class_fit(emits="series", decides="what_to_do_next")
    assert answer["fit_status"] == "unavailable"
    assert answer["candidates"] == []
    assert answer["vocabulary"]["emits"] == list(cls.EMITS)


def test_an_exclusion_always_carries_a_reason_from_the_closed_set() -> None:
    answer = cf.class_fit(emits="vector")
    assert answer["fit_status"] == "resolved"
    assert [c["class"] for c in answer["candidates"]] == ["vectoriser"]
    assert answer["excluded"]
    for row in answer["excluded"]:
        assert row["excluded_reason"] in cf.EXCLUDED_REASONS


def test_lineage_and_miscellaneous_are_excluded_as_not_a_class() -> None:
    answer = cf.class_fit(emits="open_text")
    excluded = {row["class"]: row["excluded_reason"] for row in answer["excluded"]}
    assert excluded["derived"] == "not_a_class"
    assert excluded["unclassified"] == "not_a_class"


# ── evidence: absent is not zero (the MODEL-97 lesson, reapplied) ───────────


def test_a_class_with_no_evidence_supplied_reports_unknown_not_zero() -> None:
    answer = cf.class_fit(emits="choice", consumes=["structured_state"])
    for candidate in answer["candidates"]:
        assert candidate["catalogue"]["evidence_state"] == "unknown"
        assert "card_count" not in candidate["catalogue"]


def test_a_class_the_catalogue_holds_none_of_reports_empty() -> None:
    evidence = cf.CatalogueEvidence(card_counts={"decider": 0, "text-generator": 412})
    answer = cf.class_fit(emits="choice", consumes=["structured_state"], evidence=evidence)
    states = {c["class"]: c["catalogue"] for c in answer["candidates"]}
    assert states["decider"]["evidence_state"] == "empty"
    assert states["decider"]["card_count"] == 0
    assert states["text-generator"]["evidence_state"] == "populated"


def test_examples_are_capped_and_sorted_so_no_order_reads_as_a_ranking() -> None:
    evidence = cf.CatalogueEvidence(
        card_counts={"vectoriser": 4},
        examples={"vectoriser": ["z/one", "a/two", "m/three", "b/four"]},
    )
    answer = cf.class_fit(emits="vector", evidence=evidence)
    ids = answer["candidates"][0]["catalogue"]["example_model_ids"]
    assert ids == ["a/two", "b/four", "m/three"]


# ── the worked example: MODEL-99's attribution task ─────────────────────────
#
# The answer has to be "both, in this order", and it has to admit the catalogue
# holds no decision model at all. Getting either half wrong makes the endpoint
# a yes-machine.

ATTRIBUTION_EVIDENCE = cf.CatalogueEvidence(
    card_counts={"decider": 0, "text-generator": 412},
    examples={"text-generator": ["openai/gpt-5", "anthropic/claude-x"]},
    rank_profiles={"text-generator": ["general", "reasoning"], "decider": []},
)


def _attribution_answer() -> dict:
    return cf.class_fit(
        task="decide which organisation trained this model, or that it cannot be established",
        emits="choice",
        consumes=["structured_state"],
        evidence=ATTRIBUTION_EVIDENCE,
    )


def test_the_attribution_task_does_not_resolve_to_one_class() -> None:
    answer = _attribution_answer()
    assert answer["fit_status"] == "partial"
    assert [c["class"] for c in answer["candidates"]] == ["decider", "text-generator"]


def test_the_attribution_answer_is_both_in_this_order() -> None:
    answer = _attribution_answer()
    assert answer["composition"], "a cascade is the honest answer here"
    chain = answer["composition"][0]
    assert chain["sequence"] == ["decider", "text-generator"]
    assert chain["evidence"] == "one measured task"
    assert "cost-to-correct-attribution" in chain["see"]


def test_the_composition_is_not_an_ordering() -> None:
    """A chain says the classes compose. It does not say either is better."""
    answer = _attribution_answer()
    chain = answer["composition"][0]
    assert _numbers(chain, "composition") == []
    assert answer["policy"]["orders_classes"] is False


def test_the_attribution_answer_admits_the_catalogue_has_no_decider() -> None:
    answer = _attribution_answer()
    decider = next(c for c in answer["candidates"] if c["class"] == "decider")
    assert decider["catalogue"]["evidence_state"] == "empty"
    assert decider["rank_profiles"] == []
    assert "no model" in decider["next"].lower() or "cannot name" in decider["next"].lower()


def test_the_partial_answer_carries_the_question_the_caller_must_settle() -> None:
    answer = _attribution_answer()
    assert answer["distinguishing_questions"]
    question = answer["distinguishing_questions"][0]
    assert set(question["between"]) == {"choice", "open_text"}
    assert question["ask"]


def test_a_text_generator_is_a_candidate_only_through_a_published_adaptation() -> None:
    """It emits prose; the caller parses a choice out of it. MODEL-99 did
    exactly that, and scored a malformed answer as a wrong one."""
    answer = _attribution_answer()
    generator = next(c for c in answer["candidates"] if c["class"] == "text-generator")
    assert generator["emits_adapted"] is not None
    assert generator["emits_adapted"]["from"] == "open_text"
    assert generator["emits_adapted"]["to"] == "choice"


def test_decides_is_the_strict_facet_and_admits_no_adaptation() -> None:
    """Adapting `decides` means the caller writes the decision themselves,
    which is a different architecture, so it is an exact filter."""
    answer = cf.class_fit(
        emits="choice", decides="which_of_a_caller_defined_set",
        evidence=ATTRIBUTION_EVIDENCE,
    )
    assert [c["class"] for c in answer["candidates"]] == ["decider"]
    assert answer["fit_status"] == "resolved"
    excluded = {row["class"]: row["excluded_reason"] for row in answer["excluded"]}
    assert excluded["text-generator"] == "decision_shape_mismatch"


# ── the published rule ──────────────────────────────────────────────────────


def test_the_policy_publishes_what_the_matcher_cannot_do() -> None:
    policy = cls.class_fit_policy()
    assert policy["version"] == "class-fit-v1"
    assert policy["basis"] == "model_type"
    assert policy["axis"] == ["consumes", "emits", "decides"]
    for limit in ("paraphrase", "negation"):
        assert any(limit in cannot for cannot in policy["cannot"])


def test_the_policy_names_every_refusal_the_rule_can_produce() -> None:
    published = {row["code"] for row in cls.class_fit_policy()["refuses_when"]}
    assert published == set(cf.REFUSAL_CODES)


def test_the_policy_carries_the_neutrality_commitment_by_calling_it() -> None:
    """Called, never transcribed: `tests/test_legal.py` stays the single check
    that the prose and the JSON agree."""
    assert cls.class_fit_policy()["neutrality"] == neutrality_commitment()


def test_the_published_file_carries_every_class_and_its_terms() -> None:
    from pipeline import class_export

    payload = class_export.class_fit_export(
        {"commit": "abc", "export_schema_version": "3.0"},
        model_type_counts={"decision-model": 0, "llm-chat": 3},
        examples_by_model_type={"llm-chat": ["a/one", "b/two"]},
    )
    ids = [row["id"] for row in payload["classes"]]
    assert ids == sorted(ids)
    assert len(ids) == len(cls.CLASSES) + len(cls.NON_CLASSES)
    decider = next(row for row in payload["classes"] if row["id"] == "decider")
    assert decider["catalogue"]["card_count"] == 0
    assert decider["catalogue"]["evidence_state"] == "empty"
    assert decider["terms"]
    assert payload["policy"]["orders_classes"] is False


def test_the_published_rank_profiles_are_derived_from_preferred_types() -> None:
    """Not a hand list. For `decider` it is empty today, which is the true and
    useful statement that ranking stops at that class boundary."""
    from pipeline import class_export

    payload = class_export.class_fit_export(
        {"commit": "abc", "export_schema_version": "3.0"}, model_type_counts={})
    by_id = {row["id"]: row for row in payload["classes"]}
    assert by_id["decider"]["rank_profiles"] == []
    assert "coding" in by_id["text-generator"]["rank_profiles"]
    for key in by_id["text-generator"]["rank_profiles"]:
        assert key in USE_CASE_PROFILES


def test_the_export_holds_no_score_anywhere() -> None:
    from pipeline import class_export

    payload = class_export.class_fit_export(
        {"commit": "abc", "export_schema_version": "3.0"},
        model_type_counts={"llm-chat": 7})
    offenders = [
        path for path in _numbers(payload["classes"], "classes")
        if not path.endswith(ALLOWED_NUMERIC_SUFFIXES)
    ]
    assert offenders == []


def test_the_design_document_is_where_the_reasoning_lives() -> None:
    text = (REPO_ROOT / "docs" / "design" / "class-selection.md").read_text(encoding="utf-8")
    for anchor in ("consumes", "emits", "decides", "MODEL-99", "partial"):
        assert anchor in text


@pytest.mark.parametrize("model_class", cls.CLASSES, ids=lambda c: c.id)
def test_every_class_states_why_its_pair_is_its_own_class(model_class) -> None:
    """The reason a rule survives review, in the file the reviewer reads."""
    assert model_class.because
    assert model_class.terms
