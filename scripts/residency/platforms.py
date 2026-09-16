#!/usr/bin/env python3
"""The platform namespace residency is determined against (MODEL-79).

**The finding this module exists to encode.** `data_residency` is not a
property of a model. It is a property of the place the model is *served from*,
and `schema/card.py` says so twice over: the field lives on `PrimaryProvider`,
and the 50 named `PlatformEntry` fields on `Availability` are the same 50 places
seen from every card at once. Determining residency per card would be 1,339
determinations of which 1,339 would be the same answer repeated. Determining it
per platform is 50, and each one answers for every card that names it.

So this module owns exactly one thing: the list of platforms, and the partition
of that list into the classes a determination can fall into. The determinations
themselves are not here and are not in this repository at all — see
`scripts/residency/determination.py` and `docs/handoff/README.md` standing
rule 1.

**Why the slugs are read off the schema instead of written down here.** A
hand-copied list is a list that goes stale silently: someone adds a platform to
`Availability`, nothing fails, and the new platform is simply never determined.
`platform_slugs()` derives the namespace from `Availability` itself, so a new
platform lands in `UNDETERMINED` — visibly unanswered — on the day it is added.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.card import Availability, PlatformEntry  # noqa: E402


class ResidencyScope(str, Enum):
    """What kind of answer a platform's residency is — the sentinel lives here.

    Three states, and the whole point is that a consumer can tell them apart
    without inspecting the region list. `DisclosureState` on the public card
    answers a *different* question ("why is this field empty — has anyone
    looked?"); this answers "what kind of thing is the answer at all?".

    The distinction that matters, and that a bare `list[str]` cannot make:

    * `DETERMINED` with `regions == []` means the platform published its terms
      and commits to **no** region. That is an answer, and a bad one for a
      buyer with a residency requirement.
    * `UNDETERMINED` means nobody has published anything to read. The regions
      are `null`. Not the same as `[]`, and MODEL-77 removed the shape that
      made them indistinguishable.
    * `UNBOUNDED` means the question does not have a region-shaped answer,
      because the inference happens on hardware the operator owns. See
      `LOCAL_RUNTIMES`.
    """

    #: A published region list was read and cited. `regions` is a list, and an
    #: empty one is a determination ("commits to no region"), not an absence.
    DETERMINED = "determined"
    #: The platform publishes nothing to read. `regions` is `None` and the
    #: record says which documents were checked. This is a correct answer.
    UNDETERMINED = "undetermined"
    #: Unbounded by construction: the model runs on the operator's own machine,
    #: so residency is wherever that machine is. `regions` is `None`, and no
    #: country list can ever be truthful here.
    UNBOUNDED = "unbounded"


#: Platforms that ship the weights and run them on hardware the operator
#: controls. Their residency is not unknown and not unpublished — it is
#: **unanswerable as a region list**, because the answer is "wherever you put
#: the machine", which is different for every operator.
#:
#: This is not research and it does not belong in the enrichment store: it
#: follows from what the software *is*, and `determination.py` refuses a record
#: for any slug in this set precisely so that a plausible-looking country list
#: can never be attached to one. That refusal is the mechanical half of
#: standing rule 2.
LOCAL_RUNTIMES = frozenset(
    {
        "ollama",
        "lm_studio",
        "gpt4all",
        "jan_ai",
        "mlx_community",
        "open_webui",
    }
)


def platform_slugs() -> tuple[str, ...]:
    """Every named platform on `Availability`, in declaration order.

    `other_platforms` is excluded deliberately: it is a free-form overflow list
    on individual cards, not a member of the namespace, so it has no stable
    identity to hang a determination on. `primary_provider` is excluded for the
    opposite reason — it is not a platform but a per-card reference to one, and
    it is where the determined value is eventually read *out*.
    """
    return tuple(
        name
        for name, field in Availability.model_fields.items()
        if field.annotation is PlatformEntry
    )


def is_local_runtime(slug: str) -> bool:
    """True when residency is a property of the operator's machine, not the platform."""
    return slug in LOCAL_RUNTIMES


def requires_determination() -> tuple[str, ...]:
    """The platforms a human has to go and read a document for.

    Everything that is not a local runtime. Each of these ends up `DETERMINED`
    or `UNDETERMINED`; neither is a failure, and the second is far more common
    than the ticket that commissioned this work assumed.
    """
    return tuple(s for s in platform_slugs() if not is_local_runtime(s))


def unknown_slugs(slugs: object) -> tuple[str, ...]:
    """Any of `slugs` that is not a platform on `Availability`, sorted.

    Used to reject a determination for a platform that does not exist — a typo
    in a slug would otherwise produce a record that is never read and a
    platform that is never determined, and both would look fine.
    """
    known = set(platform_slugs())
    return tuple(sorted(s for s in slugs if s not in known))  # type: ignore[union-attr]
