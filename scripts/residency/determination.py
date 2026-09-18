#!/usr/bin/env python3
"""One platform's residency determination, and the store they are read from.

**Where the determinations are.** Not in this repository, and this module holds
no path to them. Residency is a policy determination, and policy determinations
live in the private enrichment layer permanently — the same rule, and for the
same reason, that `schema/enrichment.py` records for `commercial_use`. What is
public is this shape, the platform namespace it is keyed by, and the counts.
`load_store()` takes a path from its caller; nothing here defaults to one.

**Why a separate record from `EnrichmentRecord`.** An `EnrichmentRecord` is
keyed by `model_id`, because a licence grant really is per model — two models
from the same lab can carry different terms. Residency is not: every model
served from a platform is served from that platform's regions. Keying a
residency determination by model would mean writing the same answer 1,339 times
and letting 1,339 copies drift. So the determination is per platform.
`paid_answer()` is what the paid policy-check serves: a cited region list, or
the negative finding (documents + what they said). `enrichment_for()` is only
the list-shaped half of that — a no-commitment finding is not a region list
and does not fit `EnrichmentRecord`.

**What makes a record legal** is `ResidencyScope` and nothing else. A
determined list cites the document it was read from and the day it was read. An
undetermined platform names the documents that were checked and says what they
contained instead — a null with a reason, which is an answer. And an
unbounded platform gets no record at all: `_reject_local_runtime` refuses one,
so no amount of later carelessness can attach a country list to Ollama.

**What a card says, and why two unlike things both say `withheld`.**
`card_disclosure()` is the mapping, and `CARD_DISCLOSURE` is the half of it
that carries Jamie's 2026-09-17 decision: a platform whose documents were read
and commit to no region publishes `withheld`, because "no commitment exists" is
a researched answer and `unresearched` would deny the reading. A platform
nobody could reach publishes `unresearched`, because nobody looked. The two
are never allowed to converge — `non_disclosure` has no default, and
`disclosures()`/`withheld()`/`unreached()` keep them countable apart.
"""

from __future__ import annotations

import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, model_validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.card import PolicySource  # noqa: E402
from schema.enrichment import EnrichmentRecord  # noqa: E402
from schema.enums import DisclosureState  # noqa: E402
from scripts.residency.platforms import (  # noqa: E402
    NonDisclosure,
    ResidencyScope,
    is_local_runtime,
    platform_slugs,
    requires_determination,
)

#: What a public card says about a platform that has no region list, by the
#: reason it has none. This table *is* Jamie's decision of 2026-09-17, and it is
#: a table rather than an `if` so that a new `NonDisclosure` member raises
#: `KeyError` here instead of quietly inheriting somebody else's meaning.
#:
#: `NO_COMMITMENT` reads to a buyer as "we looked, and there is nothing to tell
#: you" — determined, and determined by us. `UNREACHED` reads as "nobody has
#: looked", which is the truth when the network refused every connection.
#: Collapsing them would publish the first as the second and make the
#: catalogue understate its own work on 25 platforms, or publish the second as
#: the first and claim a determination nobody made on two.
CARD_DISCLOSURE: dict[NonDisclosure, DisclosureState] = {
    NonDisclosure.NO_COMMITMENT: DisclosureState.WITHHELD,
    NonDisclosure.UNREACHED: DisclosureState.UNRESEARCHED,
}


class PlatformResidency(BaseModel):
    """Where one platform says it processes data, or why that is not known.

    Every scope requires enough to defend itself, and the validator below is
    where "enough" is defined rather than in a reviewer's head.
    """

    platform: str
    scope: ResidencyScope

    #: The published regions, verbatim as the platform prints them. A list only
    #: when `scope` is `DETERMINED`; `[]` there means the platform commits to
    #: no region, which is a determination. `None` otherwise.
    regions: list[str] | None = None

    #: The document the list was read from, and the day it was read. Required
    #: for `DETERMINED`, forbidden otherwise — there is nothing to cite.
    source: PolicySource | None = None

    #: For `UNDETERMINED`: which of the two non-disclosures this is — the
    #: provider publishing no commitment, or nobody having reached it. Required
    #: there and forbidden elsewhere, with no default, because a default is
    #: exactly how an unreached platform would come to claim a determination.
    non_disclosure: NonDisclosure | None = None

    #: For `UNDETERMINED`: the documents actually opened, so the next reader
    #: starts where this one stopped instead of repeating the search. For
    #: `UNREACHED` these are the documents that were *attempted*, and the
    #: reason says so.
    checked: list[str] = []
    #: For `UNDETERMINED`: what those documents said instead of a region list.
    reason: str = ""

    #: What the list does and does not cover, when the platform's own page
    #: scopes it. Several do: one publishes storage regions and processing
    #: regions as different sets, another publishes regions for a product line
    #: that excludes the model in question. A buyer told "EU" without the
    #: qualification the provider itself printed has been given a worse answer
    #: than no answer, so the qualification travels with the value.
    notes: str = ""

    #: A person or an agent id. Never "the pipeline".
    determined_by: str
    #: The day the determination was made. ISO `YYYY-MM-DD`.
    determined_on: str

    @model_validator(mode="after")
    def _scope_decides_what_is_required(self) -> PlatformResidency:
        if self.platform not in set(platform_slugs()):
            raise ValueError(
                f"{self.platform!r} is not a platform on Availability. A "
                "determination for a slug that does not exist is never read, "
                "and the platform it was meant for stays undetermined."
            )
        self._reject_local_runtime()

        if self.scope is ResidencyScope.DETERMINED:
            if self.regions is None:
                raise ValueError(
                    "scope is 'determined' but regions is null. An empty list "
                    "is a legitimate determination ('commits to no region'); "
                    "null is not a determination at all."
                )
            if self.source is None:
                raise ValueError(
                    "a determined region list must cite the document it was "
                    "read from. Standing rule 2: no region list comes from "
                    "recollection of what a provider offers."
                )
            if not self.source.is_evidence:
                raise ValueError(
                    "'legacy-import' is the admission that nothing was cited. "
                    "No residency value predates this work, so no residency "
                    "determination may claim one."
                )
            if self.non_disclosure is not None:
                raise ValueError(
                    "scope is 'determined' but carries a non_disclosure. That "
                    "field says why there is no region list; this record has one."
                )
        else:
            if self.regions is not None:
                raise ValueError(
                    f"scope is {self.scope.value!r} but regions carries a "
                    "value. Only a determined platform has one."
                )
            if self.source is not None:
                raise ValueError(
                    f"scope is {self.scope.value!r} but carries a source. "
                    "Nothing was determined, so there is nothing to cite."
                )

        if self.scope is ResidencyScope.UNDETERMINED:
            if self.non_disclosure is None:
                raise ValueError(
                    "an undetermined platform says which non-disclosure this "
                    "is: 'no-commitment' when its documents were read and "
                    "commit to nothing, 'unreached' when nobody could open "
                    "them. The first is an answer and publishes 'withheld'; "
                    "the second is unfinished work and publishes "
                    "'unresearched'. There is no default, because a default "
                    "would eventually let an unreached platform claim a "
                    "determination nobody made."
                )
            if not self.checked:
                raise ValueError(
                    "an undetermined platform lists the documents that were "
                    "checked. 'Nobody published anything' is a finding, and a "
                    "finding nobody can retrace is an assumption."
                )
            if not self.reason.strip():
                raise ValueError(
                    "an undetermined platform states what the checked "
                    "documents contained instead of a region list"
                )

        if not self.determined_by.strip():
            raise ValueError("determined_by is required: a determination has an author")
        try:
            date.fromisoformat(self.determined_on)
        except ValueError as exc:
            raise ValueError(
                f"determined_on must be an exact ISO date, got {self.determined_on!r}"
            ) from exc
        return self

    def _reject_local_runtime(self) -> None:
        """A locally-run platform cannot acquire a researched region list.

        `UNBOUNDED` is not a determination and is not stored: it follows from
        what the software is, and `platforms.LOCAL_RUNTIMES` already says so in
        public code. Allowing a record here would open the one door that
        matters — someone writing `["US"]` against Ollama because most of its
        users happen to be there.
        """
        if not is_local_runtime(self.platform):
            return
        raise ValueError(
            f"{self.platform!r} runs on the operator's own hardware, so its "
            "residency is unbounded by construction and is not a determination "
            "to be stored. See scripts/residency/platforms.LOCAL_RUNTIMES."
        )

    def enrichment_for(self, model_id: str) -> EnrichmentRecord | None:
        """This platform's region list, as the per-model record of that list.

        `None` unless the platform is `DETERMINED`. A no-commitment finding is
        still an answer the paid tier sells, but it is not a region list, so it
        does not fit `EnrichmentRecord` (which requires `data_residency` to be
        a list). `paid_answer()` is the projection MODEL-80 serves; this method
        stays the list-shaped half of that.
        """
        if self.scope is not ResidencyScope.DETERMINED:
            return None
        assert self.source is not None  # the validator guarantees it
        return EnrichmentRecord(
            model_id=model_id,
            field="data_residency",
            data_residency=list(self.regions or []),
            source=self.source,
            determined_by=self.determined_by,
            determined_on=self.determined_on,
            published=False,
        )

    def paid_answer(self) -> dict[str, Any] | None:
        """What the paid policy-check serves for this platform.

        A card that publishes `withheld` is a promise that this is not `None`:
        either a cited region list, or the negative finding (the documents that
        were read, and what they said instead of a region). Unreached platforms
        and local runtimes are not withheld and return `None` here.

        Per-document read dates are not stored; `determined_on` is the date the
        finding was made from these URLs, and that is the date each document
        carries. Inventing a different day is forbidden.
        """
        if self.scope is ResidencyScope.DETERMINED:
            assert self.source is not None
            return {
                "kind": "regions",
                "scope": self.scope.value,
                "regions": list(self.regions or []),
                "source": {
                    "kind": self.source.kind,
                    "url": self.source.url,
                    "read_on": self.source.read_on,
                    "quote": self.source.quote,
                },
                "determined_on": self.determined_on,
                "notes": self.notes,
            }
        if self.non_disclosure is NonDisclosure.NO_COMMITMENT:
            return {
                "kind": "no_commitment",
                "scope": self.scope.value,
                "non_disclosure": self.non_disclosure.value,
                "regions": None,
                "documents": [
                    {"url": url, "read_on": self.determined_on}
                    for url in self.checked
                ],
                "reason": self.reason,
                "determined_on": self.determined_on,
                "notes": self.notes,
            }
        return None


    def card_disclosure(self) -> DisclosureState:
        """What a public card must say about this platform's residency.

        Three record shapes, two card states, and the mapping is the decision:

        * `DETERMINED` → `withheld`. The list exists, was cited and dated, and
          is a policy determination, so it never ages out into git
          (`decision-record.md` §2.2). The card advertises that it exists.
        * `UNDETERMINED` / `NO_COMMITMENT` → `withheld`. Nothing is being held
          back for sale here; what is withheld is a *finding* — that the
          provider's documents, named in `checked`, commit to no region. Saying
          `unresearched` instead would deny work that was done.
        * `UNDETERMINED` / `UNREACHED` → `unresearched`. Nobody looked
          successfully, so the catalogue claims nothing.

        `UNBOUNDED` is absent because it is not a record; see
        `disclosures()` for what a local runtime's card says and why.
        """
        if self.scope is ResidencyScope.DETERMINED:
            return DisclosureState.WITHHELD
        assert self.non_disclosure is not None  # the validator guarantees it
        return CARD_DISCLOSURE[self.non_disclosure]

    def card_fields(self) -> dict[str, Any]:
        """The `PrimaryProvider` residency fields for this platform.

        Splat into `PrimaryProvider(...)`, the way callers splat
        `EnrichmentRecord.public_fields()`. The value and the source are always
        null: a residency determination is a policy determination and is never
        mirrored onto a public card, so the only thing that varies is the
        disclosure marker — which is precisely the field MODEL-77 added to
        carry it.
        """
        return {
            "data_residency": None,
            "data_residency_disclosure": self.card_disclosure(),
            "data_residency_source": None,
        }


def load_store(path: Path) -> list[PlatformResidency]:
    """Read a JSON Lines store of determinations, one record per line.

    Blank lines are skipped; anything else that will not parse raises, naming
    the line. A store that silently drops a malformed record is a store that
    silently loses a platform.
    """
    records: list[PlatformResidency] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = PlatformResidency.model_validate_json(line)
        except Exception as exc:  # pragma: no cover - message is the point
            raise ValueError(f"{path}:{number}: {exc}") from exc
        if record.platform in seen:
            raise ValueError(
                f"{path}:{number}: a second determination for {record.platform!r}. "
                "One platform, one current answer; correct the record rather "
                "than appending a rival to it."
            )
        seen.add(record.platform)
        records.append(record)
    return records


def dump_store(records: Iterable[PlatformResidency]) -> str:
    """The JSON Lines text for `records`, newline-terminated."""
    return "".join(r.model_dump_json() + "\n" for r in records)


def classify(records: Sequence[PlatformResidency]) -> dict[str, ResidencyScope]:
    """Every platform on `Availability`, mapped to its scope.

    Local runtimes are `UNBOUNDED` without consulting the store, because that
    is not a stored fact. Everything else takes its scope from its record, and
    a platform with no record is `UNDETERMINED` — the honest default, and the
    one that shows up in the counts as work not yet done rather than as an
    answer nobody made.
    """
    by_slug = {r.platform: r for r in records}
    scopes: dict[str, ResidencyScope] = {}
    for slug in platform_slugs():
        if is_local_runtime(slug):
            scopes[slug] = ResidencyScope.UNBOUNDED
        elif slug in by_slug:
            scopes[slug] = by_slug[slug].scope
        else:
            scopes[slug] = ResidencyScope.UNDETERMINED
    return scopes


def counts(records: Sequence[PlatformResidency]) -> dict[ResidencyScope, int]:
    """How many platforms fall in each scope. The three numbers the ticket asks for."""
    tally = Counter(classify(records).values())
    return {scope: tally.get(scope, 0) for scope in ResidencyScope}


def unrecorded(records: Sequence[PlatformResidency]) -> tuple[str, ...]:
    """Platforms that need a determination and have no record of one.

    Distinct from `UNDETERMINED`: a platform with an `UNDETERMINED` record was
    looked at and found to publish nothing. A platform in this list was never
    looked at. Both end up null on a card; only one of them is finished.
    """
    have = {r.platform for r in records}
    return tuple(s for s in requires_determination() if s not in have)



def disclosures(records: Sequence[PlatformResidency]) -> dict[str, DisclosureState]:
    """Every platform on `Availability`, mapped to what its cards should say.

    The card-facing companion to `classify()`. Two classes have no record and
    both publish `unresearched`, for different reasons worth keeping straight:

    * a **local runtime** is unbounded by construction, and the card has no
      state for "the question has no region-shaped answer". `withheld` would be
      a lie — it would advertise an answer that no store holds and that nobody
      could ever write down — so `unresearched` stands, and
      `scripts/residency/platforms.LOCAL_RUNTIMES` remains where the real
      reason is recorded;
    * a platform with **no record at all** was never looked at, which is what
      `unresearched` says.
    """
    by_slug = {r.platform: r for r in records}
    states: dict[str, DisclosureState] = {}
    for slug in platform_slugs():
        record = by_slug.get(slug)
        if is_local_runtime(slug) or record is None:
            states[slug] = DisclosureState.UNRESEARCHED
        else:
            states[slug] = record.card_disclosure()
    return states


def disclosure_counts(records: Sequence[PlatformResidency]) -> dict[DisclosureState, int]:
    """How many platforms publish each disclosure state.

    `published` is always zero and is reported anyway: a residency
    determination that appeared on a public card would mean the enrichment
    split had broken, and a count that cannot show that is a count nobody can
    check.
    """
    tally = Counter(disclosures(records).values())
    return {state: tally.get(state, 0) for state in DisclosureState}


def withheld(records: Sequence[PlatformResidency]) -> tuple[str, ...]:
    """Platforms whose cards say `withheld` — the answers, determined and held.

    Both kinds of answer are here: a cited region list, and a finding that the
    provider commits to nothing. A platform nobody reached is never in this
    tuple, which is the property `tests/test_residency.py` pins.
    """
    states = disclosures(records)
    return tuple(s for s in platform_slugs() if states[s] is DisclosureState.WITHHELD)


def unresolved_withheld(records: Sequence[PlatformResidency]) -> tuple[str, ...]:
    """Withheld platforms the paid tier cannot resolve. Must be empty.

    `withheld` on a card is a promise that the paid tier has an answer — a
    region list, or the documents that were read and what they said instead.
    A withheld platform whose `paid_answer()` is `None` is that promise broken.
    """
    return tuple(
        r.platform
        for r in records
        if r.card_disclosure() is DisclosureState.WITHHELD and r.paid_answer() is None
    )


def unreached(records: Sequence[PlatformResidency]) -> tuple[str, ...]:
    """Platforms recorded as unreachable from the network the work was done on.

    Distinct from `unrecorded()` — somebody tried — and distinct from a
    `NO_COMMITMENT` finding: nothing was read, so nothing was established about
    what the provider publishes. These are outstanding work, and they publish
    `unresearched` until a reader on a network that can reach them says
    otherwise.
    """
    return tuple(
        r.platform
        for r in records
        if r.non_disclosure is NonDisclosure.UNREACHED
    )
