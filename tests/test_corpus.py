"""The decision spec corpus across the CLI and the Worker (MODEL-203).

Every case in ``tests/corpus`` answers as its ``expect`` says, and
``modelspec decide --json`` prints the Worker's body byte for byte. The Worker
under its own pydantic (pylock.toml), run from the vendored bundle, is held to
these bytes in rank-api.yml (``python -m tests.corpus compare``): the version
gap behind the 2026-09-29 outage.
"""

from __future__ import annotations

import json

import pytest

from tests.corpus.corpus import (
    ACCESS_ANSWERS,
    BUILDERS,
    EXPLAIN_LEVELS,
    board_facets,
    cli_matches_worker,
    env_path,
    load,
    load_cases,
    problems,
    run_cli,
    run_worker,
    snapshot_bytes,
    worker_service,
)

CASES = load_cases()
BY_ID = {case.id: case for case in CASES}


@pytest.fixture(scope="module")
def snapshots(tmp_path_factory):
    cache = env_path("MODELSPEC_CORPUS_CACHE") or tmp_path_factory.mktemp("corpus-snapshots")
    # snapshot_bytes writes <name>.json.gz into the cache; the CLI reads that file.
    return {name: (load(snapshot_bytes(name, cache)), cache / f"{name}.json.gz")
            for name in BUILDERS}


@pytest.fixture(scope="module")
def service():
    return worker_service()


@pytest.fixture(scope="module")
def answers(snapshots, service):
    """The Worker's status and body bytes for every case, computed once."""
    return {case.id: run_worker(case, snapshots[case.snapshot][0], service) for case in CASES}


def test_every_case_is_well_formed():
    assert len(BY_ID) == len(CASES), "case ids must be unique"
    for case in CASES:
        assert case.intent.strip() and "\n" not in case.intent, case.id
        assert case.snapshot in BUILDERS, case.id
        assert case.same_as is None or case.same_as in BY_ID, case.id
        assert case.divergence is None or case.expect.http != 200, (
            f"{case.id}: a divergence is only allowed on a refusal")


def test_the_corpus_covers_the_checklist():
    """MODEL-203's list, so a case cannot be dropped without this failing."""
    from decision.registry import default
    from decision.templates import load_templates

    covered = {item for case in CASES for item in case.covers}
    required = {
        *(f"template:{t['id']}:{level}" for t in load_templates() for level in EXPLAIN_LEVELS),
        *(f"{side}:{facet.id}" for facet in board_facets() for side in ("must", "prefer")),
        *(f"{side}:{domain.id}" for domain in default().domains() for side in ("must", "prefer")),
        *(f"access:{answer or 'none'}" for answer in ACCESS_ANSWERS),
        "access:none-byte-identical",
        "refinement:live", "refinement:thin", "refinement:not_measured", "refinement:unregistered",
        "estate:plan-verified", "estate:plan-unverified", "estate:devices", "estate:exhausted",
        "estate:providers",
        "exclude_benchmarks",
        "answer:no_feasible", "answer:partial", "answer:tied", "answer:separated",
        "limit:1", "limit:max",
        "error:invalid_spec", "error:snapshot_not_loaded", "error:snapshot_changed",
    }
    assert required - covered == set()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_the_worker_answers_as_the_case_expects(case, answers):
    status, body = answers[case.id]
    assert problems(case, status, json.loads(body)) == [], case.intent


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_modelspec_decide_prints_the_workers_bytes(case, answers, snapshots, tmp_path):
    cli = run_cli(case, snapshots[case.snapshot][1], tmp_path)
    found = cli_matches_worker(case, answers[case.id], cli)
    if case.divergence is None:
        assert found == [], case.intent
    else:
        # The divergence left is the CLI answering from its own snapshot.
        assert cli[0] == 0, f"{case.id}: the CLI refused ({cli[2][:200]!r}); read its divergence"
        assert found, f"{case.id} no longer diverges; drop its `divergence`"


@pytest.mark.parametrize("case", [c for c in CASES if c.same_as], ids=lambda case: case.id)
def test_equivalent_specs_answer_byte_for_byte_alike(case, answers):
    assert answers[case.id] == answers[case.same_as], case.intent


def test_the_fixed_identity_preference_explains_without_a_record(answers):
    """A Prefer on an offering's provider made the live Worker throw (Cloudflare 1101)."""
    status, body = answers["facet-prefer-offering.provider"]
    assert status == 200
    contribution = json.loads(body)["results"][0]["contributions"][0]
    assert contribution["dimension"] == "offering.provider"
    assert contribution["records"] == []
    assert contribution["formula"] == "the offering's identity, which carries no source"



def test_every_category_has_tiers_and_best_and_budget_answer_differently(answers):
    """MODEL-204: the tiers of one use case are different trade-offs. Best and
    Budget do not share a leader unless no model has enough evidence to lead,
    which the page states with the thin band (MODEL-206)."""
    from decision.templates import load_catalogue

    catalogue = load_catalogue()
    all_tiers = {tier["id"] for tier in catalogue["tiers"]}
    for category in catalogue["categories"]:
        tiers = {row["tier"]: row for row in catalogue["templates"]
                 if row["category"] == category["id"]}
        assert len(tiers) >= 3, category["id"]
        if category["kind"] == "use":
            assert set(tiers) == all_tiers, category["id"]
        pair = [tiers.get("best"), tiers.get("budget")]
        if None in pair:
            continue
        bodies = [json.loads(answers[f"template-{row['id']}-summary"][1]) for row in pair]
        if not all(body["results"] for body in bodies):
            continue  # an unavailable tier shows its reason on the grid instead
        leaders = [body["results"][0]["model"] for body in bodies]
        best_band = [entry["model"] for entry in (bodies[0].get("bands") or {}).get("best", [])]
        assert leaders[0] != leaders[1] or not best_band, (category["id"], leaders)
