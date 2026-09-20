"""Organisations ModelSpec buys from, and what a purchase costs us (MODEL-101).

ModelSpec pays TypeSafe for API access and runs **Jev — TypeSafe's own model —**
over ambiguous creator attributions (`scripts/attribution.py`). Then the
catalogue acquired a TypeSafe card, so the supplier is now also a subject.

Money flows *to* the vendor, so nothing in `neutrality_commitment()`
(`api/ranking/engine.py`) is contradicted: no referral fee, no paid placement,
no provider-paid visibility, and a purchase buys a supplier nothing in a
ranking. Two things follow anyway, and neither is a promise — both are
mechanisms:

1. **The reader is told.** A card whose provider is named here carries the
   disclosure on its page, derived from this table rather than authored per
   card, so it cannot be left off the next one (`pipeline/render.py`).
2. **A supplier's model never writes a field on that supplier's card.**
   `scripts/attribution.py` refuses the judgment before it is asked, and
   refuses a stored one before it is applied. `tests/test_attribution.py`
   fails if either refusal is removed.

What is *not* refused: deterministic attribution. An id prefix that names
TypeSafe is code reading a string — no model call and no opinion — and it stays
allowed. The rule is about the judgment, and the judgment alone.

One table, two readers, so the org the page discloses and the org the guard
protects cannot drift apart.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Supplier:
    """A vendor ModelSpec pays, that the catalogue also documents."""

    #: The catalogue's provider slug: `models/<slug>/`.
    slug: str
    display: str
    #: What we buy. Shown to a reader, so it is a sentence, not a label.
    relationship: str
    #: The rule that follows from it, in the same words on the page and here.
    rule: str


SUPPLIERS: dict[str, Supplier] = {
    "typesafe": Supplier(
        slug="typesafe",
        display="TypeSafe AI",
        relationship=(
            "ModelSpec is a paying TypeSafe customer. The catalogue's own pipeline sends "
            "ambiguous creator attributions to Jev and pays per input token for the answer "
            "(scripts/attribution.py, MODEL-82)."
        ),
        rule=(
            "No field on a TypeSafe card may be written by a Jev judgment. TypeSafe listings "
            "are attributed by code or by a person, or they are left unattributed; the "
            "judgment is refused before it is asked."
        ),
    ),
}

#: Provider slugs under the rule. The guard and the page read the same set.
SUPPLIER_SLUGS: frozenset[str] = frozenset(SUPPLIERS)


def supplier_for(provider: str | None) -> Supplier | None:
    """The supplier a card's `provider` names, or `None` for every other card."""
    if not provider:
        return None
    return SUPPLIERS.get(str(provider).strip().lower())
