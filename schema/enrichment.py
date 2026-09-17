"""The private enrichment record — the shape a policy determination is kept in.

MODEL-77. A determination has two halves and they are one decision:

* what the **public** card says (`schema/card.py`: `commercial_use`,
  `commercial_use_source`, `commercial_use_conditions`, and the
  `data_residency` trio), and
* the determination itself, which is the product being sold and therefore is
  **not** in this repository.

Defining only the first half is how the two drift: the public marker starts
meaning something the private store does not carry, or the store gains a field
the card cannot express, and nobody notices until a customer is told something
untrue. So the record is defined here, next to the card, and
`EnrichmentRecord.public_fields()` is the *only* mapping from one to the other.
`tests/test_policy_shape.py` feeds that mapping straight into the card models,
so a divergence is a test failure rather than a support ticket.

**Where the records live.** Not here. This repository is public and the
determinations are the paid product (the private business decision record, §3
and §5). The store is a JSON Lines file outside the repo — one
`EnrichmentRecord` per line, serialised with `model_dump_json()`. This module
is the schema for those lines and nothing else: it reads no file, names no
path, and holds no data. Serving them is MODEL-80.

**What a public card shows.** A determination that is withheld publishes
`commercial_use: withheld` — not `unspecified`, which would claim nobody had
looked, and not `null`, which the field no longer allows. See
`UsePermission.WITHHELD` and `docs/cli-contract.md`.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from .card import PolicySource
from .enums import DisclosureState, UsePermission

#: The fields a determination can be made about. Both are policy answers a
#: buyer pays for; both are `unspecified`/`unresearched` across the corpus
#: until the determinations are made (MODEL-78, MODEL-79).
EnrichedField = Literal["commercial_use", "data_residency"]


class EnrichmentRecord(BaseModel):
    """One determination about one model, with everything needed to defend it.

    Every field except `conditions` is required. A record that cannot say who
    decided, from what document, and on what day is not a determination — it is
    an opinion, and the catalogue's whole value is that it does not sell those.
    """

    model_id: str
    field: EnrichedField

    #: Set exactly one, matching `field`.
    commercial_use: UsePermission | None = None
    data_residency: list[str] | None = None

    #: Short and structured, the same line the public card would carry. Required
    #: for a `restricted` commercial grant: "restricted" without the restriction
    #: tells a buyer nothing they can act on.
    conditions: str = ""

    #: The document read, and the day it was read. Never `legacy-import`: that
    #: kind exists only to mark the eight uncited values MODEL-77 inherited on
    #: public cards, and a new determination has no excuse for it.
    source: PolicySource
    #: Who made the call. A person or an agent id — not "the pipeline".
    determined_by: str
    #: The day the determination was made, which is not necessarily the day the
    #: document was read (`source.read_on`).
    determined_on: str

    #: False (the default) means the public card shows the withheld marker.
    #: True means the determination is mirrored onto the public card in full.
    published: bool = False

    @model_validator(mode="after")
    def _one_determination_fully_defended(self) -> EnrichmentRecord:
        values = {
            "commercial_use": self.commercial_use,
            "data_residency": self.data_residency,
        }
        for name, value in values.items():
            if name == self.field and value is None:
                raise ValueError(f"field is {self.field!r} but {name} is not set")
            if name != self.field and value is not None:
                raise ValueError(
                    f"field is {self.field!r} but {name} is also set; one record "
                    "carries one determination, so that it can be withheld, "
                    "published or corrected on its own"
                )

        if self.commercial_use is not None and self.commercial_use not in (
            UsePermission.ALLOWED,
            UsePermission.RESTRICTED,
            UsePermission.PROHIBITED,
        ):
            raise ValueError(
                f"commercial_use {self.commercial_use.value!r} is not a "
                "determination. 'unspecified' and 'withheld' describe a public "
                "card's contents; a record exists because something was decided."
            )

        if self.source.kind == "legacy-import":
            raise ValueError(
                "a determination cites the document it was read from. "
                "'legacy-import' marks the uncited values inherited on public "
                "cards, and may not be used to record new work."
            )

        if not self.determined_by.strip():
            raise ValueError("determined_by is required: a determination has an author")
        try:
            date.fromisoformat(self.determined_on)
        except ValueError as exc:
            raise ValueError(
                f"determined_on must be an exact ISO date, got {self.determined_on!r}"
            ) from exc

        if self.commercial_use is UsePermission.RESTRICTED and not self.conditions.strip():
            raise ValueError(
                "a 'restricted' grant must state its restriction in `conditions`"
            )
        return self

    def public_fields(self) -> dict[str, Any]:
        """Exactly what the public card must carry for this determination.

        The single source of truth for the public/private relationship. Callers
        splat it into `Licensing(...)` or `PrimaryProvider(...)`; the card
        validators then decide whether it is legal, so the two halves cannot
        drift apart without a test going red.
        """
        if self.field == "commercial_use":
            if not self.published:
                return {
                    "commercial_use": UsePermission.WITHHELD,
                    "commercial_use_source": None,
                    "commercial_use_conditions": "",
                }
            return {
                "commercial_use": self.commercial_use,
                "commercial_use_source": self.source,
                "commercial_use_conditions": self.conditions,
            }

        if not self.published:
            return {
                "data_residency": None,
                "data_residency_disclosure": DisclosureState.WITHHELD,
                "data_residency_source": None,
            }
        return {
            "data_residency": list(self.data_residency or []),
            "data_residency_disclosure": DisclosureState.PUBLISHED,
            "data_residency_source": self.source,
        }
