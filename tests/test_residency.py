"""Residency is determined per platform, and the three states stay apart (MODEL-79).

The ticket's whole claim is that residency is a property of the platform, not of
the model: 50 determinations rather than 1,339. These tests pin the three
consequences of taking that seriously.

* The namespace is **derived**, so adding a platform to `Availability` makes it
  visibly undetermined instead of silently unconsidered.
* A local runtime **cannot** hold a region list. That is the one failure mode
  worth building a wall against: `["US"]` against Ollama looks completely
  plausible and is simply false, because the answer depends on where the
  operator put the machine.
* `determined []`, `undetermined` and `unbounded` are three different answers
  and no consumer has to guess which one an empty collection meant. MODEL-77
  removed that ambiguity from the card; this keeps it out of the table.

Jamie's decision of 2026-09-17 adds a fourth, and it is the one with teeth: a
platform whose documents were **read** and commit to no region publishes
`withheld`, because that is a researched answer, and a platform nobody could
**reach** publishes `unresearched`, because nobody looked. Those two records
are otherwise identical — both are `undetermined`, both have null regions, both
name URLs in `checked` — so the tests under "the two non-disclosures" exist to
fail the moment they start converging.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import Availability, PlatformEntry, PolicySource, PrimaryProvider  # noqa: E402
from schema.enums import DisclosureState  # noqa: E402
from scripts.residency import report  # noqa: E402
from scripts.residency.determination import (  # noqa: E402
    CARD_DISCLOSURE,
    PlatformResidency,
    classify,
    counts,
    disclosure_counts,
    disclosures,
    dump_store,
    load_store,
    unreached,
    unresolved_withheld,
    unrecorded,
    withheld,
)
from scripts.residency.platforms import (  # noqa: E402
    LOCAL_RUNTIMES,
    NonDisclosure,
    ResidencyScope,
    is_local_runtime,
    platform_slugs,
    requires_determination,
    unknown_slugs,
)

SOURCE = PolicySource(
    kind="provider_documentation",
    url="https://cloud.example/docs/locations",
    read_on="2026-09-16",
    quote="Available in the following regions.",
)


def determined(platform: str, regions: list[str]) -> PlatformResidency:
    return PlatformResidency(
        platform=platform,
        scope=ResidencyScope.DETERMINED,
        regions=regions,
        source=SOURCE,
        determined_by="tests",
        determined_on="2026-09-16",
    )


def undetermined(
    platform: str,
    non_disclosure: NonDisclosure = NonDisclosure.NO_COMMITMENT,
) -> PlatformResidency:
    return PlatformResidency(
        platform=platform,
        scope=ResidencyScope.UNDETERMINED,
        non_disclosure=non_disclosure,
        checked=["https://example.com/privacy"],
        reason="privacy policy names no processing location",
        determined_by="tests",
        determined_on="2026-09-16",
    )


def unreachable(platform: str) -> PlatformResidency:
    """A platform nobody got to. The documents below were attempted, not read.

    The slug passed to these helpers is an arbitrary member of the namespace
    and asserts nothing about the platform it names. The determinations are
    not in this repository and these fixtures are not a copy of them.
    """
    return PlatformResidency(
        platform=platform,
        scope=ResidencyScope.UNDETERMINED,
        non_disclosure=NonDisclosure.UNREACHED,
        checked=["https://example.cn/privacy"],
        reason="every connection timed out or was refused from this network",
        notes="unreached, not established as absent",
        determined_by="tests",
        determined_on="2026-09-17",
    )


# ── the namespace ───────────────────────────────────────────────────────────


def test_the_namespace_is_read_off_the_schema_not_copied():
    """A hand-copied list goes stale silently; a derived one cannot."""
    declared = [
        name
        for name, field in Availability.model_fields.items()
        if field.annotation is PlatformEntry
    ]
    assert list(platform_slugs()) == declared
    assert len(declared) == 50, (
        "the platform count changed. That is allowed — but a new platform is a "
        "new determination, so update the published counts rather than this number."
    )


def test_every_platform_lands_in_exactly_one_class():
    """The acceptance criterion, as an assertion: none left ambiguous."""
    scopes = classify([determined("aws_bedrock", ["us-east-1"])])
    assert set(scopes) == set(platform_slugs())
    assert all(isinstance(s, ResidencyScope) for s in scopes.values())
    assert scopes["aws_bedrock"] is ResidencyScope.DETERMINED
    assert scopes["ollama"] is ResidencyScope.UNBOUNDED
    assert scopes["kaggle_models"] is ResidencyScope.UNDETERMINED


def test_local_runtimes_are_a_subset_of_the_namespace():
    assert LOCAL_RUNTIMES <= set(platform_slugs())
    assert set(requires_determination()) == set(platform_slugs()) - LOCAL_RUNTIMES
    assert all(is_local_runtime(s) for s in LOCAL_RUNTIMES)


def test_unknown_slugs_names_what_is_not_a_platform():
    assert unknown_slugs(["ollama", "not_a_platform", "aws_bedrock"]) == ("not_a_platform",)


# ── the sentinel ────────────────────────────────────────────────────────────


@pytest.mark.parametrize("slug", sorted(LOCAL_RUNTIMES))
def test_a_local_runtime_cannot_be_given_a_region_list(slug):
    """The wall. `["US"]` against Ollama is plausible, false, and unwritable."""
    with pytest.raises(ValidationError, match="unbounded by construction"):
        determined(slug, ["US"])


@pytest.mark.parametrize("slug", sorted(LOCAL_RUNTIMES))
def test_a_local_runtime_cannot_be_recorded_at_all(slug):
    """Not even as undetermined: it is not a question a document answers."""
    with pytest.raises(ValidationError, match="unbounded by construction"):
        undetermined(slug)


def test_unbounded_needs_no_store_entry_and_is_never_missing_work():
    """Unbounded is a property of the software, so it is never outstanding work."""
    assert counts([])[ResidencyScope.UNBOUNDED] == len(LOCAL_RUNTIMES)
    assert not set(unrecorded([])) & LOCAL_RUNTIMES


def test_the_three_states_are_distinguishable_without_reading_the_list():
    """A consumer tells them apart by `scope`, never by the emptiness of a list."""
    commits_to_none = determined("groq", [])
    nobody_published = undetermined("poe")
    scopes = classify([commits_to_none, nobody_published])

    assert commits_to_none.regions == [] and commits_to_none.scope is ResidencyScope.DETERMINED
    assert nobody_published.regions is None
    assert scopes["ollama"] is ResidencyScope.UNBOUNDED
    assert len({scopes["groq"], scopes["poe"], scopes["ollama"]}) == 3


# ── what a record has to defend ─────────────────────────────────────────────


def test_a_determined_list_must_cite_the_document_it_was_read_from():
    with pytest.raises(ValidationError, match="must cite the document"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=["us-east-1"],
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_a_determined_list_may_not_claim_the_legacy_import_excuse():
    with pytest.raises(ValidationError, match="legacy-import"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=["us-east-1"],
            source=PolicySource(kind="legacy-import"),
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_determined_rejects_a_null_list_because_null_is_not_a_determination():
    with pytest.raises(ValidationError, match="not a determination at all"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=None,
            source=SOURCE,
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_an_undetermined_platform_names_what_was_checked_and_what_it_said():
    with pytest.raises(ValidationError, match="documents that were checked"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
            non_disclosure=NonDisclosure.NO_COMMITMENT,
            reason="nothing published",
            determined_by="tests",
            determined_on="2026-09-16",
        )
    with pytest.raises(ValidationError, match="states what the checked"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
            non_disclosure=NonDisclosure.NO_COMMITMENT,
            checked=["https://poe.com/tos"],
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_an_undetermined_platform_cannot_smuggle_a_value_or_a_source():
    with pytest.raises(ValidationError, match="regions carries a value"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
            non_disclosure=NonDisclosure.NO_COMMITMENT,
            regions=["US"],
            checked=["https://poe.com/tos"],
            reason="x",
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_a_record_for_a_platform_that_does_not_exist_is_refused():
    with pytest.raises(ValidationError, match="not a platform on Availability"):
        determined("aws_bedrok", ["us-east-1"])


def test_a_determination_has_an_author_and_an_exact_date():
    with pytest.raises(ValidationError, match="determination has an author"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=[],
            source=SOURCE,
            determined_by="  ",
            determined_on="2026-09-16",
        )
    with pytest.raises(ValidationError, match="exact ISO date"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=[],
            source=SOURCE,
            determined_by="tests",
            determined_on="September 2026",
        )


# ── the two non-disclosures ─────────────────────────────────────────────────


def test_an_undetermined_platform_must_say_which_non_disclosure_it_is():
    """No default. A default is how an unreached platform acquires an answer."""
    with pytest.raises(ValidationError, match="which non-disclosure"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
            checked=["https://poe.com/tos"],
            reason="names no processing location",
            determined_by="tests",
            determined_on="2026-09-17",
        )


def test_a_determined_platform_cannot_carry_a_non_disclosure():
    with pytest.raises(ValidationError, match="carries a non_disclosure"):
        PlatformResidency(
            platform="groq",
            scope=ResidencyScope.DETERMINED,
            regions=["us-east-1"],
            source=SOURCE,
            non_disclosure=NonDisclosure.NO_COMMITMENT,
            determined_by="tests",
            determined_on="2026-09-17",
        )


def test_every_non_disclosure_maps_to_exactly_one_card_state():
    """Adding a member to `NonDisclosure` must force a decision, not inherit one."""
    assert set(CARD_DISCLOSURE) == set(NonDisclosure)
    assert CARD_DISCLOSURE[NonDisclosure.NO_COMMITMENT] is DisclosureState.WITHHELD
    assert CARD_DISCLOSURE[NonDisclosure.UNREACHED] is DisclosureState.UNRESEARCHED


def test_reading_the_documents_and_finding_nothing_is_an_answer():
    """Jamie, 2026-09-17: 'no commitment exists' IS the researched answer.

    `unresearched` here would say nobody had looked at platforms whose records
    name up to five documents that were read.
    """
    record = undetermined("kaggle_models")
    assert record.card_disclosure() is DisclosureState.WITHHELD
    assert record.regions is None
    assert PrimaryProvider(**record.card_fields()).data_residency_disclosure is (
        DisclosureState.WITHHELD
    )


def test_an_unreached_platform_is_never_withheld():
    """The wall this decision needs, and the reason the field has no default.

    `withheld` claims a determination exists. For a platform whose every
    connection was refused, no determination exists and claiming one would be
    the same lie the decision was made to avoid, pointed the other way.
    """
    blocked = unreachable("poe")
    assert blocked.card_disclosure() is DisclosureState.UNRESEARCHED
    assert PrimaryProvider(**blocked.card_fields()).data_residency_disclosure is (
        DisclosureState.UNRESEARCHED
    )

    store = [
        determined("aws_bedrock", ["us-east-1"]),
        undetermined("kaggle_models"),
        blocked,
    ]
    assert "poe" not in withheld(store)
    assert unreached(store) == ("poe",)
    assert disclosures(store)["poe"] is DisclosureState.UNRESEARCHED
    assert not set(unreached(store)) & set(withheld(store))


def test_no_unreached_platform_is_withheld_in_any_arrangement_of_the_store():
    """Exhaustive over the record shapes, so the guarantee is not one example."""
    store = [unreachable(slug) for slug in requires_determination()[:5]]
    store += [undetermined(slug) for slug in requires_determination()[5:10]]
    store += [determined(slug, []) for slug in requires_determination()[10:15]]
    states = disclosures(store)
    for record in store:
        if record.non_disclosure is NonDisclosure.UNREACHED:
            assert states[record.platform] is DisclosureState.UNRESEARCHED
        else:
            assert states[record.platform] is DisclosureState.WITHHELD


def test_the_two_records_are_indistinguishable_except_where_it_counts():
    """Same scope, same null regions, same shape of `checked` — one field apart."""
    read = undetermined("kaggle_models")
    blocked = unreachable("poe")
    assert read.scope is blocked.scope is ResidencyScope.UNDETERMINED
    assert read.regions is blocked.regions is None
    assert read.checked and blocked.checked
    assert read.card_disclosure() is not blocked.card_disclosure()


def test_an_unreached_platform_is_outstanding_work_rather_than_a_finding():
    """It has a record, so `audit` passes; it is still not an answer."""
    store = [undetermined(slug) for slug in requires_determination()]
    store = [unreachable("poe") if r.platform == "poe" else r for r in store]
    assert "poe" not in unrecorded(store)
    assert "poe" in unreached(store)
    assert "poe" not in withheld(store)


# ── what the 50 cards say ───────────────────────────────────────────────────


def test_a_local_runtime_publishes_unresearched_rather_than_withheld():
    """`withheld` would advertise an answer no store holds and none can hold.

    Residency for a model on the operator's own machine has no region-shaped
    answer at all. The card has no state for that, Jamie declined to add a
    fourth, and of the three it has, `unresearched` is the only one that
    does not promise something obtainable.
    """
    states = disclosures([undetermined("poe")])
    assert all(states[slug] is DisclosureState.UNRESEARCHED for slug in LOCAL_RUNTIMES)


def test_a_platform_with_no_record_publishes_unresearched():
    assert disclosures([])["kaggle_models"] is DisclosureState.UNRESEARCHED


def test_the_disclosure_counts_cover_every_platform_and_publish_nothing():
    """A residency value on a public card would mean the enrichment split broke."""
    store = [determined("aws_bedrock", ["us-east-1"]), undetermined("kaggle_models"), unreachable("poe")]
    tally = disclosure_counts(store)
    assert sum(tally.values()) == len(platform_slugs())
    assert tally[DisclosureState.WITHHELD] == 2
    assert tally[DisclosureState.PUBLISHED] == 0
    assert tally[DisclosureState.UNRESEARCHED] == len(platform_slugs()) - 2


def test_the_scope_counts_are_unchanged_by_the_card_split():
    """The three-way classification MODEL-79 shipped still answers its question."""
    store = [undetermined("kaggle_models"), unreachable("poe")]
    tally = counts(store)
    assert tally[ResidencyScope.UNDETERMINED] == len(platform_slugs()) - len(LOCAL_RUNTIMES)
    assert tally[ResidencyScope.DETERMINED] == 0


def test_the_disclosure_report_lists_every_platform_and_its_state(tmp_path, capsys):
    path = tmp_path / "data_residency.jsonl"
    path.write_text(
        dump_store([determined("aws_bedrock", ["us-east-1"]), unreachable("poe")]),
        encoding="utf-8",
    )
    assert report.main(["disclosure", "--store", str(path)]) == 0
    out = capsys.readouterr().out
    assert "aws_bedrock            withheld" in out
    assert "poe                    unresearched" in out
    assert "could not be reached" in out


# ── the projection onto a card ──────────────────────────────────────────────


def test_a_determination_projects_onto_a_model_as_a_withheld_enrichment_record():
    """Per-platform determination, per-model record — and never published to git."""
    record = determined("google_vertex_ai", ["us-central1", "europe-west4"]).enrichment_for(
        "google/gemini-x"
    )
    assert record is not None
    assert record.model_id == "google/gemini-x"
    assert record.field == "data_residency"
    assert record.data_residency == ["us-central1", "europe-west4"]
    assert record.published is False

    fields = record.public_fields()
    assert fields["data_residency"] is None
    assert fields["data_residency_disclosure"] is DisclosureState.WITHHELD
    # and the card accepts exactly that, so the two halves cannot drift
    assert PrimaryProvider(**fields).data_residency_disclosure is DisclosureState.WITHHELD


def test_nothing_projects_from_an_undetermined_platform():
    """A no-commitment finding is not a region list, so it is not an EnrichmentRecord."""
    assert undetermined("poe").enrichment_for("some/model") is None


def test_withheld_is_exactly_what_the_paid_tier_can_resolve():
    """No card may publish withheld for a field the paid tier cannot resolve.

    Both withheld shapes must produce a paid answer: a cited region list, or
    the documents that were read and what they said instead. Unreached is not
    withheld and has nothing to sell.
    """
    listed = determined("google_vertex_ai", ["us-central1", "europe-west4"])
    negative = undetermined("kaggle_models")
    blocked = unreachable("poe")

    assert listed.card_disclosure() is DisclosureState.WITHHELD
    assert negative.card_disclosure() is DisclosureState.WITHHELD
    assert blocked.card_disclosure() is DisclosureState.UNRESEARCHED

    regions = listed.paid_answer()
    finding = negative.paid_answer()
    assert regions is not None and regions["kind"] == "regions"
    assert regions["regions"] == ["us-central1", "europe-west4"]
    assert regions["source"]["url"] and regions["source"]["read_on"]
    assert finding is not None and finding["kind"] == "no_commitment"
    assert finding["documents"]
    assert all(d["url"] and d["read_on"] for d in finding["documents"])
    assert finding["reason"]
    assert blocked.paid_answer() is None
    empty_list = determined("groq", []).paid_answer()
    assert empty_list is not None and empty_list["kind"] == "regions"
    assert empty_list["regions"] == []

    store = [listed, negative, blocked]
    assert unresolved_withheld(store) == ()
    assert set(withheld(store)) == {"google_vertex_ai", "kaggle_models"}


def test_every_withheld_shape_in_the_namespace_resolves_at_the_paid_tier():
    """The production counts, as an arrangement of fixtures, not the private store."""
    slugs = list(requires_determination())
    assert len(slugs) == 44
    store = (
        [determined(s, ["us-east-1"]) for s in slugs[:14]]
        + [undetermined(s) for s in slugs[14:42]]
        + [unreachable(s) for s in slugs[42:]]
    )
    assert unresolved_withheld(store) == ()
    assert len(withheld(store)) == 42
    answers = [r.paid_answer() for r in store]
    assert sum(1 for a in answers if a and a["kind"] == "regions") == 14
    assert sum(1 for a in answers if a and a["kind"] == "no_commitment") == 28
    assert sum(1 for a in answers if a is None) == 2


# ── the store ───────────────────────────────────────────────────────────────


def test_a_store_round_trips_through_json_lines(tmp_path):
    records = [determined("aws_bedrock", ["us-east-1"]), undetermined("poe")]
    path = tmp_path / "data_residency.jsonl"
    path.write_text(dump_store(records), encoding="utf-8")
    assert load_store(path) == records


def test_a_store_refuses_two_answers_for_one_platform(tmp_path):
    path = tmp_path / "data_residency.jsonl"
    path.write_text(
        dump_store([determined("aws_bedrock", ["us-east-1"]), undetermined("aws_bedrock")]),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="a second determination"):
        load_store(path)


def test_a_qualification_travels_with_the_value_in_either_scope(tmp_path):
    """Several providers scope their own list; the scope has to survive storage.

    One publishes storage regions and processing regions as different sets;
    another publishes regions for a product line that excludes the model being
    asked about. `EU` shorn of that qualification is worse than no answer.
    """
    scoped = determined("chatgpt", ["United States"])
    scoped.notes = "inference residency; the storage list is wider"
    refused = undetermined("cerebras")
    refused.notes = "an announcement of future sites is not a commitment"
    path = tmp_path / "data_residency.jsonl"
    path.write_text(dump_store([scoped, refused]), encoding="utf-8")
    assert [r.notes for r in load_store(path)] == [scoped.notes, refused.notes]


def test_a_malformed_line_names_itself_rather_than_being_skipped(tmp_path):
    path = tmp_path / "data_residency.jsonl"
    path.write_text(dump_store([undetermined("poe")]) + "{not json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r":2:"):
        load_store(path)


def test_counts_are_the_three_numbers_the_ticket_asks_for():
    tally = counts([determined("aws_bedrock", ["us-east-1"]), undetermined("poe")])
    assert sum(tally.values()) == len(platform_slugs())
    assert tally[ResidencyScope.DETERMINED] == 1
    assert tally[ResidencyScope.UNBOUNDED] == len(LOCAL_RUNTIMES)
    assert tally[ResidencyScope.UNDETERMINED] == len(platform_slugs()) - 1 - len(LOCAL_RUNTIMES)


def test_unrecorded_separates_never_looked_at_from_looked_at_and_empty():
    records = [undetermined("poe")]
    assert "poe" not in unrecorded(records)
    assert "kaggle_models" in unrecorded(records)


# ── the runnable acceptance check ───────────────────────────────────────────


def test_audit_fails_while_a_platform_has_no_determination(tmp_path, capsys):
    path = tmp_path / "data_residency.jsonl"
    path.write_text(dump_store([determined("aws_bedrock", ["us-east-1"])]), encoding="utf-8")
    assert report.main(["audit", "--store", str(path)]) == 1
    assert "have no determination on record" in capsys.readouterr().out


def test_audit_passes_once_every_platform_that_needs_one_has_one(tmp_path, capsys):
    records = [undetermined(slug) for slug in requires_determination()]
    path = tmp_path / "data_residency.jsonl"
    path.write_text(dump_store(records), encoding="utf-8")
    assert report.main(["audit", "--store", str(path)]) == 0
    assert "unbounded by construction" in capsys.readouterr().out


def test_report_runs_without_a_store_because_the_repository_has_none(capsys):
    """A clone of this public repository holds no determinations, and says so."""
    assert report.main(["counts"]) == 0
    out = capsys.readouterr().out
    assert f"{len(platform_slugs())} platforms" in out
    assert f"  {len(LOCAL_RUNTIMES)}  unbounded" in out


#: `data_residency: null` is the only residency *value* a committed card may
#: carry. The disclosure marker beside it is deliberately not matched: a card
#: may one day say `withheld`, which advertises a determination without
#: containing one. What may never appear in git is the list itself.
_RESIDENCY_LINE = re.compile(r"^[ \t]*data_residency:(?P<value>.*)$", re.MULTILINE)


def _committed_residency_values(text: str) -> list[str]:
    values = (m.group("value").strip() for m in _RESIDENCY_LINE.finditer(text))
    return [v for v in values if v != "null"]


def test_no_residency_determination_is_committed_to_this_repository():
    """Acceptance: the determinations are the product and are not in this repo.

    `docs/business/decision-record.md` §2.2 puts policy determinations in the
    enrichment layer permanently. This is that rule, enforced against the tree
    rather than trusted to a reviewer noticing a diff of 1,339 cards.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "models"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    offenders = [
        path
        for path in tracked
        if _committed_residency_values(
            (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
        )
    ]
    assert offenders == [], f"residency values are committed in {offenders[:5]}"
