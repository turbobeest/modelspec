"""Which licence governs a card, and therefore what its `commercial_use` is.

The hard part of MODEL-78 is not reading licences. It is knowing *which*
licence to read for a given model, and being willing to answer "we do not
know".

`license_type` on a card looked like the answer, and the ticket was scoped on
that assumption. Measured against the corpus it does not hold. Of the 683 cards
typed `apache-2.0` or `mit`, 27 are declared `cc-by-nc-4.0` or
`cc-by-nc-sa-4.0` at the point the weights are actually distributed. A
deterministic map from `license_type` would have published "commercial use
allowed" for 27 models whose distributor says NonCommercial — into the paid
compliance answer, which is the one place this project cannot afford to be
wrong. Standing rule 2 exists because that failure mode has already happened
here once, at a scale of 1,589 rows.

So the licence of record is established from two pieces of evidence, and
disagreement is fatal rather than resolved:

* the **distribution declaration** — the licence the model's Hugging Face
  repository declares, which is attached to the artifact a user actually
  downloads; and
* the card's **`license_type`**, this project's own curated baseline fact.

`licence_of_record` returns a key for `licences.reading_for`, or `None`. It
returns `None` whenever the two disagree about the outcome, whenever the
distribution point names a licence that has not been read, and whenever
neither piece of evidence identifies a document. `None` means the card keeps
`unspecified` and is counted in the published remaining total. That is standing
rule 1: absence is data, and a null beats a guess.

Note what is *not* here: no inference from a model's name. "hermes-4-405b" is a
Llama 3.1 derivative and "llama-3-3-8b-instruct" is not a Llama 3.3 model in
the sense the licence means; a regex over model ids would get both wrong and
would be exactly the filename-parsing mistake standing rule 2 names.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schema.enrichment import EnrichmentRecord  # noqa: E402
from schema.enums import UsePermission  # noqa: E402

from .licences import LicenceReading, reading_for  # noqa: E402

#: `license_type` values that name exactly one licence document, and so can
#: establish the licence of record on their own.
#:
#: The families are deliberately absent. `llama-community` names six different
#: agreements, `qwen` covers the Qwen LICENSE AGREEMENT and Tongyi Qianwen
#: (and Apache-2.0 Qwen3 releases), `deepseek` covers both the DeepSeek Model
#: License and plain MIT depending on the release, and `other` and
#: `proprietary` name nothing at all. A card typed with one of those needs the
#: distribution declaration to say which document applies.
CARD_TYPE_TO_LICENCE: dict[str, str] = {
    "apache-2.0": "apache-2.0",
    "mit": "mit",
    "cc-by-nc-4.0": "cc-by-nc-4.0",
    "gemma": "gemma",
}

#: Providers whose terms of service have been read, for cards typed
#: `proprietary`. A closed model has no licence file; the agreement covering
#: the API it is served through is the governing document.
#:
#: `voyage` is absent on purpose. Re-checked 2026-09-18: voyageai.com/terms
#: 404s, the dashboard ToS is behind login, MongoDB's Terms of Use do not
#: mention Voyage embeddings, and no archived Voyage terms page was found.
#: Assuming MongoDB's customer agreement applies because of the acquisition
#: would be inference, not a reading.
PROPRIETARY_PROVIDERS = frozenset(
    {
        "openai",
        "google",
        "anthropic",
        "xai",
        "amazon",
        "perplexity",
        "mistral",
        "inception",
        "upstage",
    }
)


@dataclass(frozen=True)
class Resolution:
    """Why a card did or did not get a determination.

    The reason matters as much as the key: `conflict` is a data-quality bug
    worth a ticket, while `unread-licence` is simply work not yet done, and
    collapsing them into "no answer" would hide the first behind the second.
    """

    licence_key: str | None
    reason: str

    @property
    def determined(self) -> bool:
        return self.licence_key is not None


def _normalise(declared: object) -> str | None:
    """The distribution declaration as a single lowercase key, or `None`."""
    if isinstance(declared, list):
        declared = declared[0] if declared else None
    if not isinstance(declared, str):
        return None
    key = declared.strip().lower()
    return key or None


def licence_of_record(
    card_license_type: str | None,
    provider: str | None = None,
    declared_licence: object = None,
    declared_licence_name: object = None,
) -> Resolution:
    """Establish which licence document governs a card.

    `declared_licence` / `declared_licence_name` are the `license` and
    `license_name` the model's distribution repository declares. Pass `None`
    for both when the card names no repository, or the repository declares
    nothing — that is an absence of contradicting evidence, not a conflict.
    """
    card_type = (card_license_type or "").strip().lower() or None

    if card_type == "proprietary":
        if provider and provider.strip().lower() in PROPRIETARY_PROVIDERS:
            return Resolution(f"terms:{provider.strip().lower()}", "provider-terms")
        return Resolution(None, "unread-provider-terms")

    # `license: other` on a repository means "see license_name"; anything else
    # is the key itself.
    declared = _normalise(declared_licence)
    if declared == "other":
        declared = _normalise(declared_licence_name)
    declared_anything = declared is not None and declared != "unknown"

    from_card = CARD_TYPE_TO_LICENCE.get(card_type or "")
    from_repo = declared if (declared_anything and reading_for(declared)) else None

    if from_repo and from_card:
        card_reading = reading_for(from_card)
        repo_reading = reading_for(from_repo)
        assert card_reading is not None and repo_reading is not None
        if card_reading.permission is not repo_reading.permission:
            # Two sources, two different answers. Neither is trustworthy enough
            # to sell, and picking one would be the guess this refuses to make.
            return Resolution(None, "conflict")
        # They agree on the outcome. Cite the distribution declaration, which
        # is attached to the artifact the user actually downloads.
        return Resolution(from_repo, "corroborated")

    if from_repo:
        return Resolution(from_repo, "distribution-declaration")

    if from_card:
        if declared_anything:
            # The repository named a licence, and it is not one that has been
            # read. It may well be permissive; it may be the NonCommercial
            # licence 27 cards in this corpus turned out to carry. Unread is
            # unread.
            return Resolution(None, "unread-licence")
        return Resolution(from_card, "card-license-type")

    return Resolution(None, "unread-licence" if declared_anything else "no-licence-evidence")


def determine(
    model_id: str,
    resolution: Resolution,
    determined_by: str,
    determined_on: str,
) -> EnrichmentRecord | None:
    """The enrichment record for a resolved card, or `None` if unresolved.

    The record is the product and does not belong in this repository; see
    `schema.enrichment`. This function only builds it.
    """
    reading: LicenceReading | None = reading_for(resolution.licence_key)
    if reading is None:
        return None
    return EnrichmentRecord(
        model_id=model_id,
        field="commercial_use",
        commercial_use=reading.permission,
        conditions=reading.conditions,
        source=reading.source,
        determined_by=determined_by,
        determined_on=determined_on,
        published=False,
    )


def public_marker(record: EnrichmentRecord | None) -> dict:
    """What the public card carries: the withheld marker, or nothing changed.

    A card with no determination keeps `unspecified` — "not yet researched",
    which is true. A card with a withheld determination publishes `withheld`,
    which is also true and is the only honest thing to say once the answer
    exists but is not in this file.
    """
    if record is None:
        return {
            "commercial_use": UsePermission.UNSPECIFIED,
            "commercial_use_source": None,
            "commercial_use_conditions": "",
        }
    return record.public_fields()
