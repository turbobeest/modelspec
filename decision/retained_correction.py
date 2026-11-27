"""A logged two-reader agreement may correct a served value read from a retaining page (MODEL-573).

``decision.cited_change.retained_agreement`` (MODEL-558) runs the rule-15 gate on a page whose
host retains copies, and only confirms: an agreed value other than the filed one was refused
(``value_differs``). The decision (orchestrator, 2026-11-26, J11): a served value that is not a
licence fact may be corrected by a complete rule-15 agreement on such a page, only when all of
these hold:

1. The agreement is in the fact's current epoch: the gate reads only there, and no attempt at the
   subject and facet is logged after it in any other epoch but the corrected record's own re-read
   epoch.
2. Its two readers are of two distinct known families (``cited_change._check_identities``),
   through the harness, with the page, text and prompt hashes logged
   (``quarantine_clearing.agreement_problem``), on the gate's own fetch: the line records
   ``own_fetch`` (logged only for bytes the gate fetched with its own transport) and the
   cited-region hash the gate computed, which the block repeats. The agreement is its line's
   first occurrence; a later byte-identical copy is the same line.
3. No disagreement is logged in that epoch: every complete attempt there agreed, on this value,
   and every answer recorded there, complete or not, is this value
   (``quarantine_clearing.epoch_problem``).
4. Not a licence fact and not a facet the registry classes as identity (``identity: true``; S15
   keeps both the owner's), not a fact that
   carries an owner's ruling or a quarantine clearing, and not a held fact: no value of the
   fact's ids has an unresolved verdict (``cited_change.held_rows``, the gate's and the build's
   own hold, MODEL-552 and MODEL-566). A released verdict is still held here.

The gate (``retained_agreement(correct=True)``) writes the record with rule ``RULE``; its block
names the epoch it was read in (``epoch``) and the agreement by the hash of its exact line in the
attempt log (``agreement``, as a clearing line does). The gate asks ``correction_problem`` of the
record as it will be filed, and so does the build (``decision.snapshot``) and the site loader
(``pipeline.load``): one test. The build serves an admitted correction as a plain cited fact:
``verification`` null, a ``citation`` naming its references, no ``derivation``
(``owner_ruling.served_fact``). It is never served as verified. A correction that fails the test
adds nothing: the fact is decided as if it carried no block. Nothing here writes.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import UTC, date
from typing import Any

RULE = "two-readers-retained-correction@1"
DECIDED_BY = "orchestrator 2026-11-26 (MODEL-573, J11)"
_HEX = re.compile(r"[0-9a-f]{64}")


def owner_only(facet_id: Any) -> bool:
    """A licence fact or a facet the facet registry classes as identity (``identity: true`` in
    ``registry/facets.yaml``): a change to either stays the owner's (S15), and no agreement
    corrects it. A facet the registry does not know is the owner's too."""
    from decision.registry import default

    if not isinstance(facet_id, str) or facet_id.startswith("licence."):
        return True
    try:
        return bool(default().facet(facet_id).identity)
    except KeyError:
        return True


def _block(record: Mapping[str, Any]) -> Mapping[str, Any] | None:
    derivation = record.get("derivation") if isinstance(record, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def is_correction(record: Mapping[str, Any]) -> bool:
    """The record carries a cited-change block this rule made (it may still fail the test)."""
    block = _block(record)
    return block is not None and block.get("rule") == RULE


def filed_fact(old: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    """The fact as a writer files the gate's record (``scripts.cited_offering.new_fact``): the
    value, state, the one source reference read and the block; every other key as it was."""
    import json

    from decision.model import SourceRef

    source = record["source"]
    block = record["derivation"]["cited_change"]
    ref = SourceRef(source_id=source["source_id"], snapshot_ref=source["snapshot_ref"],
                    cited_regions=list(source["cited_regions"]),
                    retrieved_at=source["retrieved_at"],
                    resolved_urls=list(block.get("resolved_urls") or [])).model_dump(mode="json")
    fact = {key: value for key, value in old.items() if key != "derivation"}
    fact.update(value=record["value"], state=record["state"], sources=[ref])
    fact["derivation"] = json.loads(json.dumps({"cited_change": dict(block)}))
    return fact


def correction_problem(fact: Mapping[str, Any], subject: str, *, log: Any,
                       verdicts: Mapping[tuple[str, str, str], Any], sources: Mapping[str, str],
                       cutoff: date, ids: Sequence[str] = ()) -> str | None:
    """Why ``fact`` is not a correction this rule admits, or ``None``.

    ``log`` is the attempt log (``quarantine_clearing.AttemptLog``), ``verdicts`` the verification
    log ranked by the build's own rule (``_Compiler._verification_log``), ``sources`` the source
    registry's URLs, ``cutoff`` the last day the caller may know, ``ids`` further identities the
    fact may carry in the verification log (its location id and stored id are always checked).
    """
    from decision.cited_change import fact_epoch, held_rows
    from decision.owner_ruling import has_ruling
    from decision.quarantine_clearing import (
        _at,
        _block_is,
        agreement_problem,
        epoch_problem,
        line_hash,
    )
    from decision.retention import cite_only_status

    block = _block(fact)
    if block is None or block.get("rule") != RULE:
        return "the fact carries no correction block"
    facet = fact.get("facet")
    if owner_only(facet):
        return "a licence fact or an identity field is the owner's"
    if has_ruling(fact) or "clearing_epoch" in block:
        return "a ruled or cleared fact is not corrected"
    if fact.get("state") != "known" or fact.get("value") is None:
        return "a correction files a known value"
    every = tuple(dict.fromkeys(str(i) for i in (*ids, fact.get("id"), f"{subject}#{facet}")
                                if isinstance(i, str) and i))
    try:
        held = held_rows(verdicts, every, fact)
    except (KeyError, TypeError, AttributeError, ValueError):
        return "the fact's verification record cannot be read"
    if held:
        return f"{len(held)} value(s) of the fact hold an unresolved verdict"
    epoch, agreement = block.get("epoch"), block.get("agreement")
    if not isinstance(epoch, str) or not epoch or not isinstance(agreement, str):
        return "the block names no epoch or agreement"
    # The agreement by its exact bytes, at its first position: a later byte-identical copy is
    # the same line, and never moves the count of later attempts forward.
    found = [n for n, raw in enumerate(log.lines) if line_hash(raw) == agreement]
    if not found:
        return "the agreement is not a line of the attempt log"
    index = found[0]
    attempt = log.entries[index]
    if (attempt.get("subject"), attempt.get("facet"), attempt.get("epoch")) \
            != (subject, facet, epoch):
        return "the agreement is not this fact's, in the epoch the block names"
    value = fact.get("value")
    problem = agreement_problem(attempt, value, str(facet))
    if problem is not None:
        return problem
    if cite_only_status(attempt.get("url")) is not False:
        return "the agreement did not read a page whose host retains copies"
    # The gate's own fetch record (as MODEL-562 and MODEL-555 require of a read that opens or
    # settles an epoch): the gate logs ``own_fetch`` only for bytes it fetched with its own
    # transport, and the cited-region hash it computed; the block carries the same region.
    region = attempt.get("region_sha256")
    if attempt.get("own_fetch") is not True or not _HEX.fullmatch(str(region or "")) \
            or block.get("region_sha256") != region:
        return "the agreement is not the gate's own fetch with its recorded region"
    if not _block_is(fact, block, attempt, sources=sources):
        return "the record is not the block that agreement made"
    at = _at(attempt.get("at"))
    if at is None or at.astimezone(UTC).date() > cutoff:
        return "the agreement is after this build's cutoff"
    problem = epoch_problem(log.keyed(subject, str(facet), epoch), value, str(facet))
    if problem is not None:
        return problem
    own = fact_epoch(fact)
    # A line byte-identical to an earlier line is a copy of that line, not a later attempt: an
    # older epoch's line appended again neither suppresses the correction here nor, by fix 3's
    # first occurrence, revives an older agreement.
    seen = {line_hash(raw) for raw in log.lines[:index + 1]}
    for raw, later in zip(log.lines[index + 1:], log.entries[index + 1:], strict=True):
        digest = line_hash(raw)
        if digest in seen:
            continue
        seen.add(digest)
        if (later.get("subject"), later.get("facet")) == (subject, facet) \
                and later.get("epoch") not in {epoch, own}:
            return "an attempt in a later epoch was logged after the agreement"
    return None


def correction_citation(fact: Mapping[str, Any], sources: Mapping[str, str]) -> dict[str, Any]:
    """The served ``citation`` of an admitted correction: every reference, as a cited fact's
    (``decision.citation``). It says the value is not machine-verified. Raises ``ValueError`` on
    a reference the registry cannot resolve."""
    from decision.citation import citation_of

    return citation_of(fact, sources)
