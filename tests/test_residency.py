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
    PlatformResidency,
    classify,
    counts,
    dump_store,
    load_store,
    unrecorded,
)
from scripts.residency.platforms import (  # noqa: E402
    LOCAL_RUNTIMES,
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


def undetermined(platform: str) -> PlatformResidency:
    return PlatformResidency(
        platform=platform,
        scope=ResidencyScope.UNDETERMINED,
        checked=["https://example.com/privacy"],
        reason="privacy policy names no processing location",
        determined_by="tests",
        determined_on="2026-09-16",
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
            reason="nothing published",
            determined_by="tests",
            determined_on="2026-09-16",
        )
    with pytest.raises(ValidationError, match="states what the checked"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
            checked=["https://poe.com/tos"],
            determined_by="tests",
            determined_on="2026-09-16",
        )


def test_an_undetermined_platform_cannot_smuggle_a_value_or_a_source():
    with pytest.raises(ValidationError, match="regions carries a value"):
        PlatformResidency(
            platform="poe",
            scope=ResidencyScope.UNDETERMINED,
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
    assert undetermined("poe").enrichment_for("some/model") is None


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

    The private business decision record, §2.2, puts policy determinations in
    the enrichment layer permanently. This is that rule, enforced against the
    tree rather than trusted to a reviewer noticing a diff of 1,339 cards.
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
