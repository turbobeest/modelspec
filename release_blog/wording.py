"""Every sentence a breakdown says, as a fixed template (design §3.3, standard §5).

Prose is templated sentences over computed facts. A template takes numbers
already formatted, with their footnote markers, so a sentence cannot hold a
number that has no source. Nothing here decides a cause for a difference: a
difference is stated by size and direction only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from release_blog.model import Headline

#: How a unit reads after a difference: "2.1 points lower".
DIFFERENCE_UNITS = {"percent": "points", None: "points"}


def join(items: Sequence[str]) -> str:
    """"a", "a and b", "a, b and c"."""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _domains(names: Sequence[str]) -> str:
    """Domain names in a sentence, in the order given: "software engineering,
    and agentic and tool use" (a name may hold "and" itself)."""
    names = [name[:1].lower() + name[1:] for name in names]
    more = len(names) > 3
    names = names[:3]
    if len(names) <= 1:
        return "".join(names) + (" and more" if more else "")
    if more:
        return ", ".join(names) + " and more"
    if any(" and " in name for name in names):
        return ", ".join(names[:-1]) + ", and " + names[-1]
    return join(names)


def headline(
    *,
    name: str,
    best: Sequence[tuple[str, bool]],
    ranked_outside: Sequence[str],
    thin: Sequence[str],
    claims: int,
    claims_read: int,
    same_setup: int,
) -> Headline:
    """A neutral headline, chosen by the first rule that matches.

    ``best`` is ``(domain name, alone in the band)`` for each domain where the
    model is in the best band. No rule writes a digit or a superlative.
    """
    if best:
        alone = [domain for domain, sole in best if sole]
        shared = [domain for domain, sole in best if not sole]
        if shared:
            main, rule = f"{name} is in the leading band for {_domains(shared)}", "leading_band"
        else:
            main, rule = (
                f"{name} is the only model in the best band for {_domains(alone)}",
                "sole_best_band",
            )
    elif ranked_outside:
        main, rule = (
            f"{name} is ranked outside the leading band for {_domains(ranked_outside)}",
            "outside_leading_band",
        )
    elif thin:
        main, rule = f"{name}: evidence is too thin to rank yet in {_domains(thin)}", "thin"
    else:
        main, rule = f"{name}: first verified figures, no capability estimate yet", "no_estimate"
    if claims and same_setup:
        suffix, part = "; independent readings sit beside the lab's figures", "same_setup"
    elif claims and claims_read:
        suffix, part = "; independent readings use different setups from the lab's", "setup"
    elif claims:
        suffix, part = "; the lab's figures await independent readings", "awaiting"
    else:
        suffix, part = "", "no_claims"
    return Headline(text=main + suffix, rule=f"{rule}+{part}")


def difference(
    comparability: str,
    *,
    size: str | None = None,
    direction: str | None = None,
    unit: str | None = None,
    differs_in: Sequence[str] = (),
) -> str:
    """The one sentence that states how a reading relates to the lab's figure."""
    if comparability == "same_setup":
        if direction is None:
            return "The independent reading equals the lab's figure."
        label = DIFFERENCE_UNITS.get(unit, str(unit).replace("_", " "))
        return f"The independent reading is {size} {label} {direction} than the lab's figure."
    if comparability == "different_setup":
        return (
            f"The setups differ in {join(list(differs_in))}, "
            "so ModelSpec shows both numbers and computes no difference."
        )
    return (
        f"The two use a different {join(list(differs_in))}, "
        "so ModelSpec does not compare them."
    )


NO_READING = "No independent reading yet."


def standing(
    *, domain: str, band: str | None, others: str | None, rank: str | None,
    ranked: str | None, single: bool = False,
) -> str:
    """Where the model lands in one domain. Thin evidence is named before a rank."""
    if band == "thin":
        return (
            f"In {domain}, the estimate's interval is too wide to rank on; "
            f"the model's place among {ranked} ranked models is {rank}."
        )
    if band == "best" and others is not None:
        return (
            f"In {domain}, the model is in the leading band with {others} other "
            f"{'model' if single else 'models'}; "
            "the evidence does not separate them."
        )
    if band == "best":
        return f"In {domain}, the model is the only one in the best band."
    if band == "rest":
        return (
            f"In {domain}, the model is outside the leading band, "
            f"at place {rank} of {ranked} ranked models."
        )
    return f"In {domain}, the model has an estimate but is not ranked by the domain's decision."


def template_intro(unavailable: str | None, listed: bool) -> str:
    if unavailable:
        return unavailable
    if not listed:
        return "The model changes no decision template's answer."
    return (
        "Each row is a decision template whose answer differs between the two snapshots. "
        "Other catalogue changes between the snapshots can also move these answers."
    )


def plan_line(covers: bool | str, name: str) -> str:
    if covers == "unknown":
        return f"{name}: coverage not yet verified."
    if covers:
        return f"{name}: covers the model."
    return f"{name}: does not cover the model."


def held_back(counts: Mapping[str, object] | None, formatted: str | None) -> str:
    if counts is None:
        return (
            "This snapshot predates per-model held-back counts, so the number of this "
            "model's readings awaiting a second key is not available."
        )
    if not counts:
        return "ModelSpec holds no reading of this model that is waiting for a second key."
    return (
        f"ModelSpec holds readings of this model that have not yet passed the second key: "
        f"{formatted}. Their values are not shown."
    )
