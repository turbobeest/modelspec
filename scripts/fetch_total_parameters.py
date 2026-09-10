#!/usr/bin/env python3
"""Re-derive architecture.total_parameters from the Hugging Face Hub.

Capacity gates feasibility. A total parsed from the model name is how
Mixtral-8x7B was stored as 7B and told it fitted on an 8 GB card. The Hub
safetensors aggregate is an exact count; a README figure is next; otherwise
the field is left null. The filename is never a source.

    python scripts/fetch_total_parameters.py --dry-run --limit 40
    python scripts/fetch_total_parameters.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import yaml  # noqa: E402

from schema.card import ModelCard  # noqa: E402
from scripts.fetch_geometry import (  # noqa: E402
    _NUM,
    _UNIT,
    _base_models_from_readme,
    _card_paths,
    _get_with_retry,
    _hf_headers,
    _name_patterns,
    _params_from_num_unit,
    _parse_size_token,
    _write_architecture,
    fetch_readme,
    repo_id_of,
)

MODEL_INFO_URL = "https://huggingface.co/api/models/{repo_id}?blobs=true"

#: The seeder's name regex. First `Nb` in the id — Mixtral-8x7B → 7B.
SEED_NAME_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[bB](?:\b|[-_])")
#: fill_total_parameters.py accepted a hyphen as a decimal (`1-5b` → 1.5B).
FILL_B_RE = re.compile(r"(\d+(?:[.-]\d+)?)b(?:-|$|[^a-z])")
FILL_M_RE = re.compile(r"(\d+(?:[.-]\d+)?)m(?:-|$|[^a-z])")


@dataclass(frozen=True)
class TotalDecision:
    """What to do to one card's total_parameters."""

    action: str  # write | null | keep
    value: int | None
    source: str
    reason: str


def extract_safetensors_total(payload: dict[str, Any] | None) -> int | None:
    """Hub `safetensors.total` — exact, per-tensor. None if absent or unusable.

    A 429 must never reach here as an empty payload; the fetcher retries it.
    Missing metadata is not a zero.
    """
    if not isinstance(payload, dict):
        return None
    safetensors = payload.get("safetensors")
    if not isinstance(safetensors, dict):
        return None
    total = safetensors.get("total")
    if isinstance(total, bool) or total is None:
        return None
    if isinstance(total, int) and total > 0:
        return total
    if isinstance(total, float) and total > 0 and total.is_integer():
        return int(total)
    return None


def name_parser_values(*names: str) -> set[int]:
    """Every total the historical name parsers would have written for `names`."""
    out: set[int] = set()
    for raw in names:
        if not raw:
            continue
        lower = raw.lower()
        match = SEED_NAME_RE.search(lower)
        if match:
            out.add(int(float(match.group(1)) * 1_000_000_000))
        match = FILL_B_RE.search(lower)
        if match:
            out.add(int(float(match.group(1).replace("-", ".")) * 1_000_000_000))
        match = FILL_M_RE.search(lower)
        if match:
            out.add(int(float(match.group(1).replace("-", ".")) * 1_000_000))
    return out


def is_name_parsed_total(total: int | None, *names: str) -> bool:
    """True when `total` is exactly what the name parser would emit."""
    if total is None:
        return False
    return total in name_parser_values(*names)


def published_total_from_readme(
    text: str, repo_id: str = ""
) -> tuple[int, str] | None:
    """A total the model card states, or None if absent or ambiguous.

    Active/activated figures are ignored. Comparison tables that list several
    models' totals are refused unless a named row already decided.
    """
    if not text:
        return None
    slug = repo_id.rsplit("/", 1)[-1].strip()
    plain = re.sub(r"\*\*", "", text)

    for row in re.findall(r"<tr>(.*?)</tr>", plain, flags=re.I | re.S):
        if re.search(r"activ(?:e|ated)\s+parameters", row, re.I):
            continue
        if not re.search(r"total\s+parameters", row, re.I):
            continue
        cells = [
            re.sub(r"<[^>]+>", "", cell).strip()
            for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        ]
        if len(cells) == 2 and re.search(r"total\s+parameters", cells[0], re.I):
            parsed = _parse_size_token(cells[1])
            if parsed:
                return parsed, "html_two_cell_total"

    table_hits: list[int] = []
    for match in re.finditer(
        r"^\|\s*(?:#\s*)?total\s+(?:parameters|params)"
        r"(?:\s+count)?\s*\|\s*"
        r"~?" + _NUM + r"\s*(" + _UNIT + r")\s*\|?\s*$",
        plain,
        flags=re.I | re.M,
    ):
        parsed = _params_from_num_unit(match.group(1), match.group(2))
        if parsed:
            table_hits.append(parsed)
    if len(set(table_hits)) == 1:
        return table_hits[0], "property_table"

    named = _total_from_named_markdown_row(plain, slug)
    if named:
        return named, "named_markdown_row"

    votes: dict[int, str] = {}
    prose_patterns = (
        r"(?:with|has)\s+" + _NUM + r"\s*(" + _UNIT + r")\s+total\s+parameters?",
        r"of\s+" + _NUM + r"\s*(" + _UNIT + r")\s+total\s+parameters?",
        _NUM + r"\s*(" + _UNIT + r")\s+total\s+parameters?",
        r"total\s+parameters?\s*(?:of|:)?\s*" + _NUM + r"\s*(" + _UNIT + r")",
        _NUM + r"\s*(" + _UNIT + r")\s+parameters?\s+with\s+"
        + _NUM + r"\s*(?:" + _UNIT + r")\s+activ",
        _NUM + r"\s*(billion|million|trillion)\s+total\s+parameters?",
    )
    for pattern in prose_patterns:
        for match in re.finditer(pattern, plain, flags=re.I):
            parsed = _params_from_num_unit(match.group(1), match.group(2))
            if parsed:
                votes[parsed] = "prose"
    if len(votes) == 1:
        value, why = next(iter(votes.items()))
        return value, why

    self_total = _self_total_token(plain, slug)
    if not votes and self_total:
        return self_total, "size_token_total"
    return None


def _total_from_named_markdown_row(text: str, slug: str) -> int | None:
    """Total from a row that starts with this model's name.

    `355B-A32B` is total-A-active; the first figure is the total. A
    DeepSeek-style `| name | 671B | 37B |` row puts total first.
    """
    if not slug:
        return None
    for name in _name_patterns(slug):
        row_re = re.compile(
            r"^\|\s*" + re.escape(name) + r"\s*\|(.*)$",
            flags=re.I | re.M,
        )
        for row in row_re.finditer(text):
            rest = row.group(1)
            pair = re.search(
                r"\b(\d+(?:\.\d+)?)B-A" + _NUM + r"(" + _UNIT + r")\b",
                rest,
                flags=re.I,
            )
            if pair:
                parsed = _params_from_num_unit(pair.group(1), "B")
                if parsed:
                    return parsed
            sizes = [
                _params_from_num_unit(num, unit)
                for num, unit in re.findall(
                    r"~?" + _NUM + r"\s*(" + _UNIT + r")\b", rest, flags=re.I
                )
            ]
            sizes = [value for value in sizes if value]
            if len(sizes) >= 1:
                return sizes[0]
    return None


def _self_total_token(text: str, slug: str) -> int | None:
    """`355B-A32B` only when it names this model, not a neighbour in a table."""
    pattern = re.compile(
        r"(\d+(?:\.\d+)?)B-A" + _NUM + r"(" + _UNIT + r")\b", flags=re.I
    )
    slug_hit = pattern.search(slug)
    if slug_hit:
        return _params_from_num_unit(slug_hit.group(1), "B")
    heading = re.search(r"^#\s+(.+)$", text, flags=re.M)
    if heading:
        hit = pattern.search(heading.group(1))
        if hit:
            return _params_from_num_unit(hit.group(1), "B")
    intro = re.search(
        r"is a\s+" + _NUM + r"B-A" + _NUM + r"(" + _UNIT + r")\b",
        text,
        flags=re.I,
    )
    if intro:
        return _params_from_num_unit(intro.group(1), "B")
    return None


def already_decided(source: str) -> bool:
    """True when a previous run already wrote a Hub or published source.

    Re-running then skips the Hub for that card, so an interrupted fetch
    resumes instead of starting over. An empty source is not a decision:
    the total may still be a name-parsed guess, a legacy fill, or null.
    """
    return bool(source and source.strip())


def decide_total(
    existing: int | None,
    fetched: int | None,
    fetched_source: str,
    name_parsed: bool,
    active: int | None,
) -> TotalDecision:
    """Prefer an exact Hub count; never keep a name-parsed guess."""
    if fetched is not None:
        if existing == fetched:
            return TotalDecision("write", fetched, fetched_source, "already_matches")
        return TotalDecision("write", fetched, fetched_source, "overwrite")
    if name_parsed:
        return TotalDecision("null", None, "", "unverified_name_parsed")
    if (
        existing is not None
        and active is not None
        and active > existing
    ):
        return TotalDecision("null", None, "", "active_exceeds_unverified_total")
    return TotalDecision("keep", existing, "", "no_source")


def fetch_model_info(
    client: httpx.Client, repo_id: str
) -> tuple[str, dict[str, Any] | None, str]:
    """GET Hub model info. 429 is retried; it is never an absent field."""
    url = MODEL_INFO_URL.format(repo_id=repo_id)
    status, response, detail = _get_with_retry(client, url)
    if status != "ok" or response is None:
        return status, None, detail
    try:
        payload = response.json()
    except ValueError:
        return "error", None, "non-json model info"
    if not isinstance(payload, dict):
        return "error", None, "model info is not an object"
    return "ok", payload, "ok"


def _names_for(card: ModelCard, path: Path, repo_id: str) -> tuple[str, ...]:
    return (
        card.identity.model_id,
        path.stem,
        repo_id,
        card.availability.huggingface.model_id or "",
    )


def _resolve_total(
    client: httpx.Client, repo_id: str, card: ModelCard
) -> tuple[int | None, str, dict[str, Any]]:
    """Safetensors, else README, else base-model repo. Never the filename.

    A Hub error (including a 429 that exhausted retries) is not an absent
    field: the caller must leave the card unchanged so a later resume retries.
    """
    trail: dict[str, Any] = {"repo_id": repo_id}
    had_error = False
    status, payload, detail = fetch_model_info(client, repo_id)
    time.sleep(0.65)
    trail["info_status"] = status
    trail["info_detail"] = detail
    if status == "error" and "rate-limited" in detail:
        return None, "rate_limited", trail
    if status == "error":
        had_error = True
    if status == "ok" and payload is not None:
        total = extract_safetensors_total(payload)
        if total is not None:
            trail["safetensors_total"] = total
            return total, "safetensors", trail

    readme_status, readme = fetch_readme(client, repo_id)
    time.sleep(0.65)
    trail["readme_status"] = readme_status
    if readme_status == "error":
        # 429 is retried inside _get_with_retry. Exhaustion is not a miss.
        had_error = True
    if readme_status == "ok" and readme:
        published = published_total_from_readme(readme, repo_id)
        if published:
            value, why = published
            trail["readme_why"] = why
            return value, f"model_card_published:{why}", trail

    parents: list[str] = []
    base = (card.lineage.base_model or "").strip()
    if base and "/" in base:
        parents.append(base)
    if readme_status == "ok" and readme:
        for parent in _base_models_from_readme(readme):
            if parent not in parents:
                parents.append(parent)
    for parent in parents[:1]:
        trail["base_model"] = parent
        pst, parent_payload, pdetail = fetch_model_info(client, parent)
        time.sleep(0.65)
        trail["base_info_status"] = pst
        trail["base_info_detail"] = pdetail
        if pst == "error" and "rate-limited" in pdetail:
            return None, "rate_limited", trail
        if pst == "error":
            had_error = True
        if pst == "ok" and parent_payload is not None:
            total = extract_safetensors_total(parent_payload)
            if total is not None:
                trail["safetensors_total"] = total
                return total, f"safetensors:base_model:{parent}", trail
        rst, parent_readme = fetch_readme(client, parent)
        time.sleep(0.65)
        trail["base_readme_status"] = rst
        if rst == "error":
            had_error = True
        if rst == "ok" and parent_readme:
            published = published_total_from_readme(parent_readme, parent)
            if published:
                value, why = published
                trail["readme_why"] = why
                return value, f"model_card_published:base_model:{parent}:{why}", trail
    if had_error:
        return None, "error", trail
    return None, "", trail


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--limit", type=int, default=0, help="only the first N cards"
    )
    parser.add_argument(
        "--report", default="benchmarks/_census/total_parameters.json"
    )
    args = parser.parse_args(argv)

    targets: list[tuple[Path, ModelCard, str]] = []
    no_repo: list[tuple[Path, ModelCard]] = []
    unreadable = 0
    for path in _card_paths():
        try:
            card = ModelCard.from_yaml_file(path)
        except Exception as exc:
            print(f"  SKIP unreadable {path.relative_to(PROJECT_ROOT)}: {exc}")
            unreadable += 1
            continue
        repo_id = repo_id_of(card)
        if repo_id:
            targets.append((path, card, repo_id))
        else:
            no_repo.append((path, card))

    cards_report: dict[str, dict[str, Any]] = {}
    written = 0
    nulled = 0
    kept = 0
    overwritten = 0
    sourced_safetensors = 0
    sourced_published = 0
    skipped_decided = 0
    rate_limited = 0
    fetch_errors = 0
    errors: list[dict[str, str]] = []
    out = PROJECT_ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)

    pending: list[tuple[Path, ModelCard, str]] = []
    for path, card, repo_id in targets:
        source = card.architecture.total_parameters_source
        if already_decided(source):
            skipped_decided += 1
            cards_report[card.identity.model_id] = {
                "action": "skip_already_decided",
                "existing": card.architecture.total_parameters,
                "source": source,
                "reason": "resume",
                "repo_id": repo_id,
            }
        else:
            pending.append((path, card, repo_id))
    if args.limit:
        pending = pending[: args.limit]

    no_repo_pending: list[tuple[Path, ModelCard]] = []
    for path, card in no_repo:
        source = card.architecture.total_parameters_source
        if already_decided(source):
            skipped_decided += 1
            cards_report[card.identity.model_id] = {
                "action": "skip_already_decided",
                "existing": card.architecture.total_parameters,
                "source": source,
                "reason": "resume",
                "repo_id": "",
            }
        else:
            no_repo_pending.append((path, card))

    def dump_report() -> None:
        report = {
            "dry_run": args.dry_run,
            "considered_with_repo": len(targets),
            "considered_without_repo": len(no_repo),
            "pending_with_repo": len(pending),
            "unreadable": unreadable,
            "skipped_already_decided": skipped_decided,
            "written": written,
            "overwritten": overwritten,
            "nulled": nulled,
            "kept": kept,
            "sourced_safetensors": sourced_safetensors,
            "sourced_published": sourced_published,
            "rate_limited": rate_limited,
            "fetch_errors": fetch_errors,
            "errors": errors,
            "cards": cards_report,
        }
        out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    print(
        f"resume: already decided {skipped_decided}; "
        f"fetching {len(pending)} with-repo; "
        f"{len(no_repo_pending)} no-repo"
    )
    dump_report()

    with httpx.Client(
        timeout=30, follow_redirects=True, headers=_hf_headers()
    ) as client:
        for index, (path, card, repo_id) in enumerate(pending, 1):
            model_id = card.identity.model_id
            existing = card.architecture.total_parameters
            active = card.architecture.active_parameters
            name_parsed = is_name_parsed_total(
                existing, *_names_for(card, path, repo_id)
            )
            fetched, source, trail = _resolve_total(client, repo_id, card)
            if source == "rate_limited":
                rate_limited += 1
                errors.append({"model_id": model_id, "detail": "rate-limited"})
                cards_report[model_id] = {
                    "action": "error",
                    "existing": existing,
                    "name_parsed": name_parsed,
                    **trail,
                }
                dump_report()
                print(f"  RATE LIMITED on {model_id}; stopping so 429 is not a miss")
                break
            if source == "error":
                fetch_errors += 1
                errors.append(
                    {
                        "model_id": model_id,
                        "detail": trail.get("info_detail")
                        or trail.get("readme_status")
                        or "error",
                    }
                )
                cards_report[model_id] = {
                    "action": "error",
                    "existing": existing,
                    "name_parsed": name_parsed,
                    **trail,
                }
                print(
                    f"  ERROR on {model_id}; leaving unchanged so a miss is not invented"
                )
                continue
            decision = decide_total(
                existing, fetched, source, name_parsed, active
            )
            entry: dict[str, Any] = {
                "existing": existing,
                "fetched": fetched,
                "source": source,
                "name_parsed": name_parsed,
                "action": decision.action,
                "value": decision.value,
                "reason": decision.reason,
                **trail,
            }
            if decision.action == "write":
                if source.startswith("safetensors"):
                    sourced_safetensors += 1
                elif source.startswith("model_card_published"):
                    sourced_published += 1
                if existing is not None and existing != decision.value:
                    overwritten += 1
                if not args.dry_run:
                    patch: dict[str, Any] = {
                        "total_parameters": decision.value,
                        "total_parameters_source": decision.source,
                    }
                    _write_architecture(path, patch)
                    written += 1
            elif decision.action == "null":
                nulled += 1
                if not args.dry_run:
                    _write_architecture(
                        path,
                        {
                            "total_parameters": None,
                            "total_parameters_source": "",
                        },
                    )
                    written += 1
            else:
                kept += 1
            cards_report[model_id] = entry
            if index % 25 == 0:
                dump_report()
                print(
                    f"  {index}/{len(pending)}  "
                    f"write={overwritten + sourced_safetensors} "
                    f"null={nulled} keep={kept} errors={fetch_errors}"
                )

    for path, card in no_repo_pending:
        model_id = card.identity.model_id
        existing = card.architecture.total_parameters
        active = card.architecture.active_parameters
        name_parsed = is_name_parsed_total(existing, *_names_for(card, path, ""))
        decision = decide_total(existing, None, "", name_parsed, active)
        cards_report[model_id] = {
            "existing": existing,
            "fetched": None,
            "source": "",
            "name_parsed": name_parsed,
            "action": decision.action,
            "value": decision.value,
            "reason": decision.reason,
            "repo_id": "",
        }
        if decision.action == "null":
            nulled += 1
            if not args.dry_run:
                _write_architecture(
                    path,
                    {"total_parameters": None, "total_parameters_source": ""},
                )
                written += 1
        else:
            kept += 1

    dump_report()
    print(
        f"\nwith-repo {len(targets)}  no-repo {len(no_repo)}  "
        f"skipped {skipped_decided}  "
        f"overwritten {overwritten}  nulled {nulled}  kept {kept}"
        f"  safetensors {sourced_safetensors}  published {sourced_published}"
        f"  errors {fetch_errors}"
        + ("" if args.dry_run else f"  written={written}")
    )
    if rate_limited:
        print(f"stopped after rate-limit errors={rate_limited}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
