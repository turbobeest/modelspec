"""The licence readings, and the rule that decides when not to answer (MODEL-78).

Two things are pinned here, and the second is the one that matters.

1. Every entry in `scripts/policy/licences.py` says what the cited document
   says, carries a URL and a read date, and is the *kind* of answer that
   licence gives. A licence with no entry produces no value.
2. `licence_of_record` refuses to answer when its two pieces of evidence
   disagree. The corpus contains 27 cards typed `apache-2.0` or `mit` whose
   distribution repository declares a NonCommercial licence. A mapping keyed on
   `license_type` alone would sell "commercial use allowed" for every one of
   them.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.enums import UsePermission  # noqa: E402
from scripts.policy.commercial_use import (  # noqa: E402
    CARD_TYPE_TO_LICENCE,
    PROPRIETARY_PROVIDERS,
    determine,
    licence_of_record,
    public_marker,
)
from scripts.policy.licences import READINGS, LicenceReading, reading_for  # noqa: E402

DETERMINER = "claude-opus-5/MODEL-78"
TODAY = "2026-09-16"


# ── The table ───────────────────────────────────────────────────────────────


def test_every_reading_cites_a_document_and_a_date():
    """Standing rule 2, as a test. An uncited reading is an opinion."""
    for key, reading in READINGS.items():
        assert reading.source.kind != "legacy-import", key
        assert reading.source.url.startswith("https://"), key
        date.fromisoformat(reading.source.read_on)  # raises if not an exact date
        assert reading.source.quote.strip(), (
            f"{key} has no quoted clause. The quote is what lets a reader check "
            "the determination without refetching the document."
        )


def test_every_reading_is_an_actual_determination():
    for key, reading in READINGS.items():
        assert reading.permission in (
            UsePermission.ALLOWED,
            UsePermission.RESTRICTED,
            UsePermission.PROHIBITED,
        ), key


def test_restricted_readings_state_their_restriction():
    for key, reading in READINGS.items():
        if reading.permission is UsePermission.RESTRICTED:
            assert reading.conditions.strip(), key
        else:
            assert not reading.conditions.strip(), key


@pytest.mark.parametrize(
    "key,permission",
    [
        ("apache-2.0", UsePermission.ALLOWED),
        ("mit", UsePermission.ALLOWED),
        ("bsd-3-clause", UsePermission.ALLOWED),
        ("cc-by-nc-4.0", UsePermission.PROHIBITED),
        ("cc-by-nc-sa-4.0", UsePermission.PROHIBITED),
        ("gemma", UsePermission.RESTRICTED),
        ("deepseek", UsePermission.RESTRICTED),
        ("llama2", UsePermission.RESTRICTED),
        ("llama3", UsePermission.RESTRICTED),
        ("llama3.1", UsePermission.RESTRICTED),
        ("llama3.2", UsePermission.RESTRICTED),
        ("llama3.3", UsePermission.RESTRICTED),
        ("llama4", UsePermission.RESTRICTED),
        ("terms:openai", UsePermission.RESTRICTED),
        ("terms:google", UsePermission.RESTRICTED),
        ("terms:anthropic", UsePermission.RESTRICTED),
        ("terms:xai", UsePermission.RESTRICTED),
        ("terms:amazon", UsePermission.RESTRICTED),
        ("terms:perplexity", UsePermission.RESTRICTED),
        ("terms:mistral", UsePermission.RESTRICTED),
        ("qwen", UsePermission.RESTRICTED),
        ("qwen-research", UsePermission.PROHIBITED),
        ("tongyi-qianwen", UsePermission.RESTRICTED),
        ("tongyi-qianwen-license-agreement", UsePermission.RESTRICTED),
        ("mrl", UsePermission.PROHIBITED),
        ("mnpl", UsePermission.PROHIBITED),
    ],
)
def test_each_licence_reads_the_way_its_clause_reads(key, permission):
    reading = reading_for(key)
    assert reading is not None, f"{key} is missing from the table"
    assert reading.permission is permission


def test_qwen_commercial_and_research_licences_are_different_documents():
    commercial = reading_for("qwen")
    research = reading_for("qwen-research")
    assert commercial is not None and research is not None
    assert commercial.source.url != research.source.url
    assert commercial.permission is UsePermission.RESTRICTED
    assert research.permission is UsePermission.PROHIBITED


def test_the_llama_licences_are_six_documents_not_one():
    """Llama 2, 3, 3.1, 3.2, 3.3 and 4 agree on the threshold and are still six
    separate agreements. Citing one for another manufactures evidence."""
    urls = {k: READINGS[k].source.url for k in READINGS if k.startswith("llama")}
    assert len(urls) == 6, urls
    assert len(set(urls.values())) == 6, "two Llama versions share a citation"


def test_an_unread_licence_produces_no_value_and_never_a_default():
    for unknown in ("openrail", "gpl-3.0", "cc-by-4.0", "", None, "APACHE-3.0"):
        assert reading_for(unknown) is None


def test_the_table_cannot_be_mutated_into_a_default():
    with pytest.raises(TypeError):
        READINGS["anything-goes"] = READINGS["mit"]  # type: ignore[index]


def test_a_restricted_reading_without_conditions_is_rejected_at_construction():
    with pytest.raises(ValueError, match="no conditions"):
        LicenceReading(
            permission=UsePermission.RESTRICTED,
            source=READINGS["mit"].source,
        )


# ── The rule ────────────────────────────────────────────────────────────────


def test_card_type_and_distribution_declaration_agreeing_is_answered():
    r = licence_of_record("apache-2.0", declared_licence="apache-2.0")
    assert r.licence_key == "apache-2.0"
    assert r.reason == "corroborated"


def test_agreement_on_outcome_between_two_permissive_licences_is_answered():
    """A card typed `mit` distributed under Apache-2.0 is still `allowed`; the
    citation follows the artifact."""
    r = licence_of_record("mit", declared_licence="apache-2.0")
    assert r.licence_key == "apache-2.0"
    assert r.reason == "corroborated"


def test_a_noncommercial_declaration_beats_a_permissive_card_type_by_refusing():
    """The 27-card case. `apache-2.0` on the card, NonCommercial at the point of
    distribution: the answer is that there is no answer."""
    for declared in ("cc-by-nc-4.0", "cc-by-nc-sa-4.0"):
        r = licence_of_record("apache-2.0", declared_licence=declared)
        assert r.licence_key is None
        assert r.reason == "conflict"
        assert determine("x/y", r, DETERMINER, TODAY) is None


def test_a_family_card_type_is_resolved_by_the_distribution_declaration():
    """`llama-community` names six agreements, so the card alone answers
    nothing; the repository says which one."""
    assert licence_of_record("llama-community").licence_key is None
    r = licence_of_record("llama-community", declared_licence="llama3.1")
    assert r.licence_key == "llama3.1"
    assert r.reason == "distribution-declaration"


def test_llama_named_via_license_other_and_license_name():
    r = licence_of_record(
        "llama-community", declared_licence="other", declared_licence_name="llama4"
    )
    assert r.licence_key == "llama4"


def test_a_deepseek_card_distributed_under_mit_is_allowed_not_restricted():
    """13 of the 30 `deepseek` cards are MIT on the Hub. Calling them
    `restricted` because the family usually is would be a wrong answer in the
    cautious direction, which is still a wrong answer."""
    r = licence_of_record("deepseek", declared_licence="mit")
    record = determine("deepseek/x", r, DETERMINER, TODAY)
    assert record is not None
    assert record.commercial_use is UsePermission.ALLOWED


def test_card_type_answers_when_nothing_contradicts_it():
    r = licence_of_record("apache-2.0", declared_licence=None)
    assert r.licence_key == "apache-2.0"
    assert r.reason == "card-license-type"


def test_an_unread_declaration_silences_a_known_card_type():
    """The repository named a licence nobody has read. It might be permissive;
    27 cards in this corpus show it might equally be NonCommercial."""
    r = licence_of_record(
        "apache-2.0", declared_licence="other", declared_licence_name="some-vendor-eula"
    )
    assert r.licence_key is None
    assert r.reason == "unread-licence"


def test_a_list_valued_declaration_is_read_not_stringified():
    assert licence_of_record("deepseek", declared_licence=["mit"]).licence_key == "mit"


def test_other_and_null_card_types_get_nothing():
    for card_type in ("other", None, "", "qwen", "openrail", "gpl-3.0"):
        r = licence_of_record(card_type)
        assert r.licence_key is None, card_type
        assert determine("x/y", r, DETERMINER, TODAY) is None


def test_proprietary_resolves_by_provider_terms():
    for provider in sorted(PROPRIETARY_PROVIDERS):
        r = licence_of_record("proprietary", provider=provider)
        assert r.licence_key == f"terms:{provider}"
        record = determine(f"{provider}/m", r, DETERMINER, TODAY)
        assert record is not None
        assert record.commercial_use is UsePermission.RESTRICTED
        assert record.conditions.strip()


def test_a_provider_whose_terms_were_not_found_gets_nothing():
    """Voyage AI publishes no locatable terms document. Reaching for MongoDB's
    because MongoDB bought Voyage would be inference."""
    r = licence_of_record("proprietary", provider="voyage")
    assert r.licence_key is None
    assert r.reason == "unread-provider-terms"
    assert determine("voyage/voyage-3", r, DETERMINER, TODAY) is None


def test_no_card_type_in_the_map_is_a_family_licence():
    """A family name must never be able to answer on its own."""
    for family in ("llama-community", "deepseek", "qwen", "other", "proprietary"):
        assert family not in CARD_TYPE_TO_LICENCE


# ── What reaches the public card ────────────────────────────────────────────


def test_a_determination_publishes_the_withheld_marker_and_no_citation():
    r = licence_of_record("apache-2.0", declared_licence="apache-2.0")
    record = determine("a/b", r, DETERMINER, TODAY)
    assert record is not None and record.published is False
    marker = public_marker(record)
    assert marker["commercial_use"] is UsePermission.WITHHELD
    assert marker["commercial_use_source"] is None
    assert marker["commercial_use_conditions"] == ""


def test_an_undetermined_card_keeps_unspecified_not_withheld():
    """`withheld` claims an answer exists. On a card nobody has determined, that
    is a lie in the other direction."""
    marker = public_marker(None)
    assert marker["commercial_use"] is UsePermission.UNSPECIFIED
    assert marker["commercial_use_source"] is None


def test_records_carry_author_and_determination_date():
    r = licence_of_record("proprietary", provider="openai")
    record = determine("openai/gpt-x", r, DETERMINER, TODAY)
    assert record is not None
    assert record.determined_by == DETERMINER
    assert record.determined_on == TODAY
    assert record.source.read_on
    assert record.source.url.startswith("https://")


# ── The published remaining count ───────────────────────────────────────────


def test_coverage_counts_every_card_and_separates_the_three_states(tmp_path):
    """`unspecified` is the remaining tail; `withheld` is an answer that lives
    elsewhere. A report that merged them would let the tail be hidden by
    determining things and not saying so."""
    from scripts.policy.coverage import DETERMINED, card_states

    models = tmp_path / "models"
    (models / "p").mkdir(parents=True)
    for name, value in [
        ("a", "unspecified"),
        ("b", "withheld"),
        ("c", "allowed"),
        ("d", "prohibited"),
    ]:
        (models / "p" / f"{name}.md").write_text(
            f"---\nmodel_id: p/{name}\nlicensing:\n  commercial_use: {value}\n---\nbody\n"
        )
    counts = card_states(models)
    assert sum(counts.values()) == 4
    assert counts["unspecified"] == 1
    assert sum(n for v, n in counts.items() if v in DETERMINED) == 3


def test_coverage_ignores_the_corpus_licence_notice(tmp_path):
    from scripts.policy.coverage import card_states

    models = tmp_path / "models"
    models.mkdir()
    (models / "LICENSE.md").write_text("# Licence for this corpus\n")
    assert sum(card_states(models).values()) == 0
