"""A policy determination can be recorded at all (MODEL-77).

Three defects, one shape:

* `commercial_use` was a `bool | None` and could not hold `restricted`, which
  is the correct answer for every llama-community, gemma and deepseek card —
  165 of them, measured on this corpus.
* there was nowhere to cite the licence the answer was read from, so standing
  rule 1 made an honest determination impossible to write down;
* and a public `null` would start lying the moment determinations were made and
  withheld, asserting "not yet researched" on ~1,300 cards at once.

These tests pin the shape, the migration of the eight values that existed
before it, and the one mapping between the public card and the private
enrichment record.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import Licensing, ModelCard, PolicySource, PrimaryProvider  # noqa: E402
from schema.enrichment import EnrichmentRecord  # noqa: E402
from schema.enums import DisclosureState, UsePermission  # noqa: E402

#: The eight cards that carried `commercial_use: true` before MODEL-77,
#: captured from `origin/main` at 73f121e on 2026-09-16. They are the whole of
#: what the old boolean ever recorded: 8 filled, 1,331 null, across 1,339 cards.
#: `true` migrated to `allowed` — the one bool value that maps to exactly one
#: permission — and kept the fact that nobody cited anything.
MIGRATED_FROM_TRUE = {
    "deepcogito/cogito-671b-v2-1",
    "essentialai/rnj-1-instruct",
    "meta/muse-glimmer-30b",
    "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b",
    "nvidia/nvidia-nemotron-3-ultra-550b-a55b",
    "prism-ml/ternary-bonsai-27b",
    "thinkingmachines/inkling",
    "zhipu/glm-5-3-flash",
}

#: A real source, for tests that need one that is not the point of the test.
CITED = PolicySource(
    kind="license",
    url="https://www.apache.org/licenses/LICENSE-2.0",
    read_on="2026-09-16",
)


def _cards() -> list[tuple[str, dict]]:
    """Every card's frontmatter, parsed once. Raw YAML, not `ModelCard`: these
    tests are about what is *published*, and the export writes the frontmatter
    through verbatim."""
    out = []
    for path in sorted((REPO_ROOT / "models").glob("**/*.md")):
        if path.name == "LICENSE.md":
            continue
        head = path.read_text(encoding="utf-8").split("---", 2)[1]
        front = yaml.safe_load(head)
        out.append((front["model_id"], front))
    return out


CARDS = _cards()


# ── the migration ────────────────────────────────────────────────────────────

def test_no_card_still_carries_the_boolean() -> None:
    """The type change reached the data, not just the model."""
    offenders = [
        model_id for model_id, front in CARDS
        if isinstance((front.get("licensing") or {}).get("commercial_use"), bool)
        or (front.get("licensing") or {}).get("commercial_use") is None
    ]
    assert offenders == []


def test_the_eight_true_values_survived_as_allowed() -> None:
    """No loss: every card that said `true` says `allowed`, and only those."""
    allowed = {
        model_id for model_id, front in CARDS
        if (front.get("licensing") or {}).get("commercial_use") == "allowed"
    }
    assert allowed == MIGRATED_FROM_TRUE


def test_nothing_else_gained_a_determination() -> None:
    """Shape only. Every other card is `unspecified` — the honest empty state,
    not `withheld`, which would claim a determination nobody has made."""
    values = {}
    for _, front in CARDS:
        value = (front.get("licensing") or {}).get("commercial_use")
        values[value] = values.get(value, 0) + 1
    assert values == {"unspecified": len(CARDS) - 8, "allowed": 8}


def test_legacy_import_is_frozen_to_the_migrated_eight() -> None:
    """`legacy-import` is an amnesty for eight inherited values, not a loophole.

    It is the one source kind that carries no URL and no date, so a ninth card
    using it would be a new uncited determination — exactly what standing rule 1
    forbids. New work cites a document or does not record a value.
    """
    uncited = {
        model_id for model_id, front in CARDS
        if ((front.get("licensing") or {}).get("commercial_use_source") or {}).get("kind")
        == "legacy-import"
    }
    assert uncited == MIGRATED_FROM_TRUE


def test_every_card_still_validates_against_the_new_schema() -> None:
    for path in sorted((REPO_ROOT / "models").glob("**/*.md")):
        if path.name == "LICENSE.md":
            continue
        ModelCard.from_yaml_file(path)


def test_the_restricted_population_is_the_reason_this_changed() -> None:
    """165 cards whose licence grants commercial use up to a threshold. None
    gains a value here — but `restricted` now exists for them to gain."""
    restricted_licences = [
        model_id for model_id, front in CARDS
        if (front.get("licensing") or {}).get("license_type")
        in {"llama-community", "gemma", "deepseek"}
    ]
    assert len(restricted_licences) == 165


# ── a determination needs a source ───────────────────────────────────────────

@pytest.mark.parametrize("value", [
    UsePermission.ALLOWED, UsePermission.RESTRICTED, UsePermission.PROHIBITED,
])
def test_a_determination_without_a_source_fails_validation(value: UsePermission) -> None:
    with pytest.raises(ValidationError, match="commercial_use_source"):
        Licensing(commercial_use=value, commercial_use_conditions="x" if value is UsePermission.RESTRICTED else "")


def test_an_undated_source_is_not_a_source() -> None:
    """Licences are rewritten without notice, so the day it was read is not
    decoration."""
    with pytest.raises(ValidationError, match="read_on"):
        PolicySource(kind="license", url="https://example.test/licence", read_on="")


def test_a_source_without_a_url_is_not_a_source() -> None:
    with pytest.raises(ValidationError, match="url"):
        PolicySource(kind="terms_of_service", url="", read_on="2026-09-16")


def test_legacy_import_may_not_dress_itself_up() -> None:
    with pytest.raises(ValidationError, match="legacy-import"):
        PolicySource(kind="legacy-import", url="https://example.test/licence")


# ── conditional permission is expressible ────────────────────────────────────

def test_restricted_carries_its_condition() -> None:
    licensing = Licensing(
        commercial_use=UsePermission.RESTRICTED,
        commercial_use_source=PolicySource(
            kind="license",
            url="https://example.test/llama-community",
            read_on="2026-09-16",
            quote="…if monthly active users exceed 700 million…",
        ),
        commercial_use_conditions="allowed below 700M monthly active users; above it, a separate licence is required",
    )
    assert licensing.commercial_use is UsePermission.RESTRICTED
    assert "700M" in licensing.commercial_use_conditions


def test_restricted_without_the_restriction_is_refused() -> None:
    with pytest.raises(ValidationError, match="commercial_use_conditions"):
        Licensing(commercial_use=UsePermission.RESTRICTED, commercial_use_source=CITED)


def test_conditions_cannot_contradict_the_value() -> None:
    with pytest.raises(ValidationError, match="commercial_use_conditions"):
        Licensing(
            commercial_use=UsePermission.ALLOWED,
            commercial_use_source=CITED,
            commercial_use_conditions="only below 700M MAU",
        )


# ── the withheld state ───────────────────────────────────────────────────────

def test_withheld_is_not_unspecified() -> None:
    """The whole point: a consumer can tell "we decided and are not telling you"
    from "nobody has looked"."""
    withheld = Licensing(commercial_use=UsePermission.WITHHELD)
    unresearched = Licensing()
    assert withheld.commercial_use is UsePermission.WITHHELD
    assert unresearched.commercial_use is UsePermission.UNSPECIFIED
    assert withheld.commercial_use != unresearched.commercial_use
    assert withheld.model_dump()["commercial_use"] != unresearched.model_dump()["commercial_use"]


def test_the_old_shape_cannot_express_the_withheld_state() -> None:
    """`null` is why this ticket exists: it is the same token for both states."""
    with pytest.raises(ValidationError, match="no longer nullable"):
        Licensing(commercial_use=None)
    with pytest.raises(ValidationError, match="not a bool"):
        Licensing(commercial_use=True)


def test_a_withheld_card_publishes_nothing_about_the_determination() -> None:
    """Not even the citation: the source is part of what was withheld."""
    with pytest.raises(ValidationError, match="commercial_use_source"):
        Licensing(commercial_use=UsePermission.WITHHELD, commercial_use_source=CITED)
    with pytest.raises(ValidationError, match="commercial_use_conditions"):
        Licensing(commercial_use=UsePermission.WITHHELD, commercial_use_conditions="below 700M MAU")


# ── data_residency: [] stopped meaning two things ────────────────────────────

def test_unresearched_residency_is_null_not_an_empty_list() -> None:
    provider = PrimaryProvider()
    assert provider.data_residency is None
    assert provider.data_residency_disclosure is DisclosureState.UNRESEARCHED
    with pytest.raises(ValidationError, match="data_residency"):
        PrimaryProvider(data_residency=[])


def test_an_empty_published_residency_is_an_answer() -> None:
    """"The provider commits to no region" is a determination a buyer can act
    on. It is only legible because unresearched is now `null`."""
    provider = PrimaryProvider(
        data_residency=[],
        data_residency_disclosure=DisclosureState.PUBLISHED,
        data_residency_source=CITED,
    )
    assert provider.data_residency == []


def test_published_residency_needs_a_source() -> None:
    with pytest.raises(ValidationError, match="data_residency_source"):
        PrimaryProvider(data_residency=["eu-west-1"],
                        data_residency_disclosure=DisclosureState.PUBLISHED)


def test_withheld_residency_is_distinguishable_from_unresearched() -> None:
    withheld = PrimaryProvider(data_residency_disclosure=DisclosureState.WITHHELD)
    assert withheld.data_residency is None
    assert withheld.data_residency_disclosure is not DisclosureState.UNRESEARCHED


def test_every_card_starts_unresearched_not_empty() -> None:
    """The corpus-wide ambiguity MODEL-79 depends on being gone."""
    states = set()
    for _, front in CARDS:
        provider = ((front.get("availability") or {}).get("primary_provider") or {})
        states.add((
            provider.get("data_residency"),
            provider.get("data_residency_disclosure"),
        ))
    assert states == {(None, "unresearched")}


# ── public marker and private record are one decision ────────────────────────

def _record(**kwargs) -> EnrichmentRecord:
    base = dict(
        model_id="meta/llama-3-70b-instruct",
        field="commercial_use",
        commercial_use=UsePermission.RESTRICTED,
        conditions="allowed below 700M monthly active users",
        source=PolicySource(kind="license", url="https://example.test/licence",
                            read_on="2026-09-16"),
        determined_by="jamie",
        determined_on="2026-09-16",
    )
    base.update(kwargs)
    return EnrichmentRecord(**base)


def test_a_withheld_record_projects_onto_a_legal_public_card() -> None:
    """`public_fields()` is the only mapping between the two halves, and the
    card's own validators are what judge it — so the public marker cannot drift
    away from the private record without this failing."""
    licensing = Licensing(**_record().public_fields())
    assert licensing.commercial_use is UsePermission.WITHHELD
    assert licensing.commercial_use_source is None
    assert licensing.commercial_use_conditions == ""


def test_a_published_record_projects_the_whole_determination() -> None:
    licensing = Licensing(**_record(published=True).public_fields())
    assert licensing.commercial_use is UsePermission.RESTRICTED
    assert licensing.commercial_use_source is not None
    assert licensing.commercial_use_source.url == "https://example.test/licence"
    assert "700M" in licensing.commercial_use_conditions


def test_a_residency_record_projects_onto_a_legal_provider() -> None:
    record = _record(field="data_residency", commercial_use=None,
                     data_residency=["eu-central-1"], conditions="")
    withheld = PrimaryProvider(**record.public_fields())
    assert withheld.data_residency is None
    assert withheld.data_residency_disclosure is DisclosureState.WITHHELD

    record = _record(field="data_residency", commercial_use=None,
                     data_residency=["eu-central-1"], conditions="", published=True)
    published = PrimaryProvider(**record.public_fields())
    assert published.data_residency == ["eu-central-1"]
    assert published.data_residency_disclosure is DisclosureState.PUBLISHED


def test_a_record_carries_value_source_read_date_determiner_and_conditions() -> None:
    record = _record()
    assert record.commercial_use is UsePermission.RESTRICTED
    assert record.source.url and record.source.read_on
    assert record.determined_by and record.determined_on
    assert record.conditions


@pytest.mark.parametrize("bad,match", [
    ({"determined_by": " "}, "determined_by"),
    ({"determined_on": "2026-09"}, "determined_on"),
    ({"conditions": ""}, "restriction"),
    ({"commercial_use": UsePermission.WITHHELD}, "not a determination"),
    ({"commercial_use": UsePermission.UNSPECIFIED}, "not a determination"),
    ({"source": PolicySource(kind="legacy-import")}, "legacy-import"),
    ({"data_residency": ["eu-west-1"]}, "one record"),
])
def test_an_undefendable_record_is_refused(bad: dict, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        _record(**bad)
