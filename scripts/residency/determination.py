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
and letting 1,339 copies drift. So the determination is per platform, and
`PlatformResidency.enrichment_for()` is the *only* way it becomes a per-model
record. That projection is the seam; everything else about the public/private
relationship is already settled by `EnrichmentRecord.public_fields()`, which it
delegates to rather than restating.

**What makes a record legal** is `ResidencyScope` and nothing else. A
determined list cites the document it was read from and the day it was read. An
undetermined platform names the documents that were checked and says what they
contained instead — a null with a reason, which is an answer. And an
unbounded platform gets no record at all: `_reject_local_runtime` refuses one,
so no amount of later carelessness can attach a country list to Ollama.
"""

from __future__ import annotations

import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path

from pydantic import BaseModel, model_validator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.card import PolicySource  # noqa: E402
from schema.enrichment import EnrichmentRecord  # noqa: E402
from scripts.residency.platforms import (  # noqa: E402
    ResidencyScope,
    is_local_runtime,
    platform_slugs,
    requires_determination,
)


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

    #: For `UNDETERMINED`: the documents actually opened, so the next reader
    #: starts where this one stopped instead of repeating the search.
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
        """This platform's determination, as the per-model record MODEL-80 serves.

        `None` unless the platform is `DETERMINED`: an undetermined platform
        has nothing to sell and an unbounded one has nothing region-shaped to
        say. The record is `published=False` because residency is a policy
        determination and those never age out into git
        (`schema/enrichment.py`); the public card therefore shows the withheld
        marker, which `EnrichmentRecord.public_fields()` derives — this method
        does not restate it.
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

