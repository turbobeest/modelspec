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

A correction replaces a value, so a ``mismatch`` on the value it replaced (the value the gate
logged with its agreement, ``filed_value``; never the record's own ``previous_value``) does not
hold it (MODEL-491 E2, orchestrator 2026-11-27, J11): such a verdict
says the page did not support the old value, which is what the correction found. Any other
verdict still holds it: an ``unreachable`` on any value, and any verdict on a third value or on
the corrected value itself (``replaced_value_mismatch``).

A confirmation (rule 16, MODEL-558: ``two-readers-retained-agreement@1``, an agreement on the
filed value that no engine reader can read) is served as cited, never as verified, under the
same limits (MODEL-491 E1, orchestrator 2026-11-27, J11; ``confirmation_problem``): its logged
agreement is complete, through the harness, by two distinct known families, on the filed value,
on a page whose host retains copies, is the block's (``quarantine_clearing._block_is``), is on or
before the cutoff, sits in an epoch with no disagreement, and no attempt at the subject and facet
in another epoch but the record's own re-read epoch is logged after it; the fact is no licence
fact or identity field, carries no ruling or clearing, and no value of it holds a verdict. A
confirmation records no epoch or agreement hash, so its agreement is the first logged line that
made the block. Where the fact's own winning verdict is an independent ``verified``, the verified
path wins and the confirmation adds nothing (``confirmation_citation``). One that fails the test
adds nothing either: the fact is decided as if it carried no block. The build and the site loader
ask ``confirmation_citation``; the gate asks ``confirmation_problem`` of the record it files.
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
    from decision.cited_change import fact_epoch
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
    try:
        held = unresolved_holds(fact, subject, verdicts=verdicts, log=log, ids=ids)
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
    from decision.quarantine_clearing import line_kind

    if line_kind(attempt, str(facet)) != "correction":
        return "the agreement line does not show it filed a correction"
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


def _unordered(facet_id: Any) -> bool:
    from decision.model import unordered_facet
    from decision.registry import default

    try:
        return unordered_facet(default().facet(str(facet_id)))
    except KeyError:
        return False


def _binds(fact: Mapping[str, Any], value: Any, value_hash: str) -> bool:
    """Whether ``value_hash`` binds ``value`` as this fact's value (any order of a set's members
    for an unordered facet)."""
    from decision.model import fact_verification_value, matching_value_hashes

    bound = fact_verification_value({**fact, "value": value})
    return bool(matching_value_hashes(bound, [value_hash], unordered=_unordered(fact.get("facet"))))


def _agreement_index(fact: Mapping[str, Any], log: Any) -> int | None:
    """The position of the attempt line a correction's block names (``agreement``, by the hash
    of its exact bytes, first occurrence), or ``None``."""
    from decision.quarantine_clearing import line_hash

    agreement = (_block(fact) or {}).get("agreement")
    if not isinstance(agreement, str):
        return None
    for n, raw in enumerate(log.lines):
        if line_hash(raw) == agreement:
            return n
    return None


def mismatch_on(fact: Mapping[str, Any], key: Sequence[str], row: Mapping[str, Any],
                value: Any) -> bool:
    """Whether a held verdict (``key`` = ``(kind, id, value hash)``, ``row`` its winning row) is a
    ``mismatch`` whose hash binds ``value`` as this fact's value: the one test the gate (before a
    correction read) and the build (``replaced_value_mismatch``) ask (MODEL-491 E2)."""
    return row.get("outcome") == "mismatch" and len(key) == 3 and value is not None \
        and _binds(fact, value, str(key[2]))


def replaced_value_mismatch(fact: Mapping[str, Any], key: Sequence[str],
                            row: Mapping[str, Any], *, log: Any, subject: str) -> bool:
    """Whether a held verdict is a ``mismatch`` on a value this correction's lineage replaced, on
    no value the fact now has: such a verdict does not hold the correction (MODEL-491 E2).

    The replaced values come from the attempt log only, never from a field the record states
    about itself: the ``filed_value`` the gate logged on each complete two-reader agreement on
    the fact's current value, up to and including the line the block names (a re-read of a
    corrected fact logs the corrected value as filed, so the line that first corrected it is
    followed). The verdict must be dated on or before that agreement. A line logged without a
    ``filed_value`` releases nothing."""
    from decision.quarantine_clearing import _at, _canonical, agreement_problem

    if not is_correction(fact):
        return False
    index = _agreement_index(fact, log)
    if index is None:
        return False
    facet = str(fact.get("facet"))
    value = fact.get("value")
    if _binds(fact, value, str(key[2]) if len(key) == 3 else ""):
        return False
    day = str(row.get("date") or "9999")
    for entry in log.entries[:index + 1]:
        if (entry.get("subject"), entry.get("facet")) != (subject, facet) \
                or "filed_value" not in entry:
            continue
        replaced = entry["filed_value"]
        if replaced is None or _canonical(replaced, facet) == _canonical(value, facet):
            continue
        if agreement_problem(entry, value, facet) is not None:
            continue
        at = _at(entry.get("at"))
        if at is not None and day <= at.astimezone(UTC).date().isoformat() \
                and mismatch_on(fact, key, row, replaced):
            return True
    return False


def unresolved_holds(fact: Mapping[str, Any], subject: str, *,
                     verdicts: Mapping[tuple[str, str, str], Any], log: Any = None,
                     ids: Sequence[str] = ()) -> list[tuple[tuple[str, str, str], dict]]:
    """The verdicts that hold ``fact``: the one hold check that a retained-page correction
    (MODEL-573), a confirmation (MODEL-491 E1) and a cite-only reconfirmation (MODEL-572) are
    each tested with, in the gate, the build and the site loader. Every verdict that is not
    ``verified`` on any value of the fact's ids (``cited_change.held_rows``: ``ids``, its stored
    id and its location id), less, for a correction with ``log`` given, the mismatches on a value
    its lineage replaced (``replaced_value_mismatch``, MODEL-491 E2). A released verdict still
    holds here. Raises what ``held_rows`` raises on an unreadable record."""
    from decision.cited_change import held_rows

    facet = fact.get("facet")
    every = tuple(dict.fromkeys(str(i) for i in (*ids, fact.get("id"), f"{subject}#{facet}")
                                if isinstance(i, str) and i))
    held = held_rows(verdicts, every, fact)
    if log is not None and is_correction(fact):
        held = [h for h in held
                if not replaced_value_mismatch(fact, h[0], h[1], log=log, subject=subject)]
    return held


def is_confirmation(record: Mapping[str, Any]) -> bool:
    """The record carries a rule-16 retained-page agreement block (it may still fail the test)."""
    from decision.cited_change import RETAINED_RULE

    block = _block(record)
    return block is not None and block.get("rule") == RETAINED_RULE


def confirmation_problem(fact: Mapping[str, Any], subject: str, *, log: Any,
                         verdicts: Mapping[tuple[str, str, str], Any], sources: Mapping[str, str],
                         cutoff: date, ids: Sequence[str] = (),
                         clearings: Sequence[Mapping[str, Any]] = (),
                         history: Mapping[str, Sequence[Mapping[str, Any]]] | None = None
                         ) -> str | None:
    """Why ``fact`` is not a rule-16 confirmation this rule serves as cited, or ``None``
    (MODEL-491 E1). The arguments are ``correction_problem``'s, and the MODEL-552 clearing lines
    with the queue history of the targets they name (``clearing_inputs``).

    A confirmation held by a mismatch is served only when a valid clearing line releases every
    held verdict (MODEL-491 E4, ``quarantine_clearing.fact_released``): the fact carries the block
    the clearing's own fresh two-reader agreement made, read in the verdict's clearing epoch on a
    later day than the verdict. Any other hold, and a cleared block no valid line backs, refuses.
    """
    from decision.cited_change import fact_epoch
    from decision.owner_ruling import has_ruling
    from decision.quarantine_clearing import (
        _at,
        _block_is,
        agreement_problem,
        epoch_problem,
        line_hash,
        line_kind,
    )
    from decision.retention import cite_only_status

    if not is_confirmation(fact):
        return "the fact carries no retained-page agreement block"
    block = _block(fact) or {}
    facet = fact.get("facet")
    if owner_only(facet):
        return "a licence fact or an identity field is the owner's"
    if has_ruling(fact):
        return "a ruled fact is not a confirmation"
    cleared = "clearing_epoch" in block
    if fact.get("state") != "known" or fact.get("value") is None:
        return "a confirmation is of a known value"
    if cleared and not _own_clearing(fact, subject, block, log=log, verdicts=verdicts,
                                     sources=sources, cutoff=cutoff, clearings=clearings,
                                     history=history or {}):
        return "a cleared confirmation is admitted only through its own valid clearing line"
    try:
        held = unresolved_holds(fact, subject, verdicts=verdicts, log=log, ids=ids)
        if held and cleared:
            from decision.quarantine_clearing import fact_released

            rows = [h[1] for h in held]
            held = [h for h in held if not fact_released(
                fact, subject, verdict=h[1], clearings=clearings, log=log, sources=sources,
                history=history or {}, cutoff=cutoff, held=rows)]
    except (KeyError, TypeError, AttributeError, ValueError):
        return "the fact's verification record cannot be read"
    if held:
        return f"{len(held)} value(s) of the fact hold an unresolved verdict"
    value = fact.get("value")
    index = None
    for n, attempt in enumerate(log.entries):
        if (attempt.get("subject"), attempt.get("facet")) != (subject, facet):
            continue
        if cleared and attempt.get("epoch") != block.get("clearing_epoch"):
            continue  # a cleared confirmation rests on its clearing's own agreement (E4)
        try:
            made = agreement_problem(attempt, value, str(facet)) is None \
                and line_kind(attempt, str(facet)) == "confirmation" \
                and _block_is(fact, block, attempt, sources=sources)
        except (KeyError, TypeError, AttributeError):
            made = False
        if made:
            index = n  # the first logged line that made this block
            break
    if index is None:
        return "no logged two-reader agreement on this value made the block"
    attempt = log.entries[index]
    if cite_only_status(attempt.get("url")) is not False:
        return "the agreement did not read a page whose host retains copies"
    at = _at(attempt.get("at"))
    if at is None or at.astimezone(UTC).date() > cutoff:
        return "the agreement is after this build's cutoff"
    epoch = attempt.get("epoch")
    if not isinstance(epoch, str) or not epoch:
        return "the agreement names no epoch"
    problem = epoch_problem(log.keyed(subject, str(facet), epoch), value, str(facet))
    if problem is not None:
        return problem
    own = fact_epoch(fact)
    if own != epoch:
        # The record's own re-read epoch: any disagreement there, which is always later than the
        # agreement, voids the confirmation (MODEL-491 review).
        problem = epoch_problem(log.keyed(subject, str(facet), own), value, str(facet))
        if problem is not None:
            return f"in the current re-read epoch: {problem}"
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


def _own_clearing(fact: Mapping[str, Any], subject: str, block: Mapping[str, Any], *, log: Any,
                  verdicts: Mapping[tuple[str, str, str], Any], sources: Mapping[str, str],
                  cutoff: date, clearings: Sequence[Mapping[str, Any]],
                  history: Mapping[str, Sequence[Mapping[str, Any]]]) -> bool:
    """Whether a valid clearing line backs this cleared confirmation, held or not (MODEL-491 E4
    review): a line for this subject, facet, value and the block's own clearing epoch, naming a
    mismatch on the fact's location id that the verification log holds, which releases it for
    this record (``quarantine_clearing.fact_released``: the line is valid, its later epoch
    checked, and the record carries the block its agreement made). Any other line names
    nothing here."""
    from decision.quarantine_clearing import _canonical, fact_released, verdict_sha256

    facet = str(fact.get("facet"))
    location = f"{subject}#{facet}"
    want = _canonical(fact.get("value"), facet)
    rows = [entry[2] for (kind, rid, _h), entry in verdicts.items()
            if kind == "fact" and rid == location and entry[2].get("outcome") == "mismatch"]
    for line in clearings:
        if not isinstance(line, Mapping) or (line.get("subject"), line.get("facet"),
                                              line.get("epoch")) \
                != (subject, facet, block.get("clearing_epoch")) \
                or _canonical(line.get("value"), facet) != want:
            continue
        for row in rows:
            if verdict_sha256(row) != line.get("verdict_sha256"):
                continue
            try:
                if fact_released(fact, subject, verdict=row, clearings=clearings, log=log,
                                 sources=sources, history=history, cutoff=cutoff, held=rows):
                    return True
            except (KeyError, TypeError, AttributeError, ValueError):
                continue
    return False


def clearing_inputs(root: Any) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """The MODEL-552 clearing lines under a data directory and the queue history of the targets
    they name, as ``decision.snapshot.collect_repo`` reads them: what the gate and the site loader
    give ``confirmation_problem`` (MODEL-491 E4). Raises ``ValueError`` on a malformed file."""
    from pathlib import Path

    from decision.quarantine_clearing import (
        CLEARINGS_FILE,
        QUEUE_FILE,
        queue_history,
        read_clearings,
    )

    root = Path(root)
    path = root / CLEARINGS_FILE
    clearings = read_clearings(path) if path.is_file() else []
    targets = {str((c.get("target") or {}).get("id")) for c in clearings
               if isinstance(c.get("target"), Mapping)}
    return clearings, (queue_history(root / QUEUE_FILE, targets) if targets else {})


def verified_winner(fact: Mapping[str, Any], subject: str,
                    verdicts: Mapping[tuple[str, str, str], Any]) -> bool:
    """Whether the fact's own winning verdict (the latest counting row on its stored id whose
    hash binds its value, its inline verification included, as ``decision.snapshot._verdicts``
    ranks them) is ``verified``. A card that states no id has its location id, as
    ``decision.snapshot.collect_repo`` gives it, so the build and the site loader read the same
    rows."""
    from decision.model import fact_verification_value, matching_value_hashes
    from decision.snapshot import _counts

    rid = fact.get("id") or f"{subject}#{fact.get('facet')}"
    value = fact_verification_value(fact)
    unordered = _unordered(fact.get("facet"))
    entries = []
    inline = fact.get("verification")
    if isinstance(inline, Mapping) and isinstance(inline.get("target"), Mapping):
        target = inline["target"]
        if target.get("kind") == "fact" and target.get("id") == rid and _counts(inline) \
                and matching_value_hashes(value, [str(target.get("value_hash") or "")],
                                          unordered=unordered):
            entries.append((str(inline["date"]), 0, inline))
    for (kind, vid, vhash), entry in verdicts.items():
        if kind == "fact" and rid is not None and vid == str(rid) \
                and matching_value_hashes(value, [vhash], unordered=unordered):
            entries.append(entry)
    if not entries:
        return False
    return max(entries, key=lambda e: e[:2])[2].get("outcome") == "verified"


def confirmation_citation(fact: Mapping[str, Any], subject: str, *, log: Any,
                          verdicts: Mapping[tuple[str, str, str], Any],
                          sources: Mapping[str, str], cutoff: date,
                          ids: Sequence[str] = (),
                          clearings: Sequence[Mapping[str, Any]] = (),
                          history: Mapping[str, Sequence[Mapping[str, Any]]] | None = None
                          ) -> dict[str, Any] | None:
    """The served ``citation`` of a confirmation the test admits and no verified verdict
    outranks, or ``None``: the one decision the build and the site loader take (MODEL-491 E1)."""
    if confirmation_problem(fact, subject, log=log, verdicts=verdicts, sources=sources,
                            cutoff=cutoff, ids=ids, clearings=clearings,
                            history=history) is not None:
        return None
    if verified_winner(fact, subject, verdicts):
        return None
    try:
        return correction_citation(fact, sources)
    except ValueError:
        return None


def correction_citation(fact: Mapping[str, Any], sources: Mapping[str, str]) -> dict[str, Any]:
    """The served ``citation`` of an admitted correction: every reference, as a cited fact's
    (``decision.citation``). It says the value is not machine-verified. Raises ``ValueError`` on
    a reference the registry cannot resolve."""
    from decision.citation import citation_of

    return citation_of(fact, sources)
