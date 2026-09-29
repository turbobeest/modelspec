"""Run an offline decision and optionally write a self-contained HTML explanation."""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any, Optional

import typer

from cli.modelspec.offline import SCHEMA_VERSION
from decision import contract
from decision.engine import decide as run_decision
from decision.engine import validate as validate_decision
from decision.registry import facet

from .vocabulary_cache import (
    VocabularyInvalidError,
    VocabularyMissingError,
    load_cached_vocabulary,
)

EXIT_ERROR = 1
FRESHNESS_KEYS = (
    "fetched_at", "age_days", "stale", "stale_after_days", "origin",
    "build_commit", "built_at",
)


def _facet_lookup() -> contract.FacetLookup:
    return facet


def _leaf_conditions(condition: Any, path: str):
    if isinstance(condition, contract.AnyOf | contract.AllOf):
        name = "any" if isinstance(condition, contract.AnyOf) else "all"
        for index, child in enumerate(getattr(condition, name)):
            yield from _leaf_conditions(child, f"{path}.{name}[{index}]")
    elif isinstance(condition, contract.NotOf):
        yield from _leaf_conditions(condition.not_, f"{path}.not")
    else:
        yield condition, path


def _vocabulary_warnings(spec: contract.Spec, vocabulary: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    published = {
        row["id"]
        for section in ("facets", "benchmarks", "domains")
        for row in vocabulary.get(section, [])
    }
    providers = set(vocabulary.get("providers", {}))
    domains = {row["id"] for row in vocabulary.get("domains", [])}

    def add(path: str, value: str) -> None:
        warning = (
            f"{path}: {value!r} has no verified evidence in this snapshot; "
            "results will be empty or may_qualify"
        )
        if warning not in warnings:
            warnings.append(warning)

    for domain in spec.capabilities or {}:
        if domain not in domains:
            add(f"capabilities.{domain}", domain)
    if spec.task_type is not None and spec.task_type not in set(vocabulary.get("task_types", [])):
        add("task_type", spec.task_type)
    if isinstance(spec.profile, contract.InventoryProfile):
        for index, offering in enumerate(spec.profile.offerings):
            if offering.provider not in providers:
                add(f"profile.offerings[{index}].provider", offering.provider)

    conditions = list(enumerate(spec.where))
    if isinstance(spec.profile, contract.InventoryProfile):
        for index, condition in enumerate(spec.profile.rules):
            for leaf, path in _leaf_conditions(condition, f"profile.rules[{index}]"):
                conditions.append((path, leaf))
    for index, condition in conditions:
        path = f"where[{index}]" if isinstance(index, int) else index
        leaves = (
            _leaf_conditions(condition, path)
            if isinstance(index, int)
            else [(condition, path)]
        )
        for leaf, leaf_path in leaves:
            facet_id = leaf.known if isinstance(leaf, contract.Known) else leaf.facet
            if facet_id == "offering.provider" and not isinstance(leaf, contract.Known):
                values = (
                    (leaf.in_ or leaf.not_in)
                    if isinstance(leaf, contract.InSet)
                    else [getattr(leaf, "value", None)]
                )
                for value in values or []:
                    if isinstance(value, str) and value not in providers:
                        add(leaf_path, value)
            if facet_id not in published:
                add(leaf_path, facet_id)
    objective = spec.optimize
    objective_facets = [objective.max, objective.min]
    objective_facets += list(objective.weights or {}) + list(objective.pareto or [])
    objective_facets += [step.facet for step in objective.lexicographic or []]
    for facet_id in objective_facets:
        if facet_id and facet_id.removeprefix("-") not in published:
            add("optimize", facet_id.removeprefix("-"))
    return warnings


def _issues(exc: contract.SpecError, vocabulary: dict[str, Any] | None) -> list[dict[str, Any]]:
    known = set()
    if vocabulary is not None:
        known = {
            row["id"]
            for section in ("facets", "benchmarks", "domains")
            for row in vocabulary.get(section, [])
        }
    rendered = []
    for issue in exc.issues:
        reason = issue.reason
        if issue.field and "unknown facet" in reason:
            close = difflib.get_close_matches(issue.field, sorted(known), n=3, cutoff=0.6)
            extra = [item for item in close if repr(item) not in reason]
            if extra:
                reason += f"; cached vocabulary suggests {', '.join(repr(item) for item in extra)}"
        rendered.append({
            "path": issue.path, "condition": issue.condition,
            "field": issue.field, "reason": reason,
        })
    return rendered


def _summary(spec: contract.Spec) -> str:
    objective = spec.optimize
    prefers = (len(objective.weights or {}) + len(objective.pareto or [])
               + len(objective.lexicographic or [])
               + int(objective.max is not None) + int(objective.min is not None))
    return f"musts: {len(spec.where)}, prefers: {prefers}, snapshot: {spec.snapshot}"


def _fail(payload: dict[str, Any], lines: list[str], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2), err=True)
    else:
        for line in lines:
            typer.echo(line, err=True)
    raise typer.Exit(EXIT_ERROR)


def _template(templates: list[dict[str, Any]], template_id: str, as_json: bool) -> dict[str, Any]:
    for row in templates:
        if row.get("id") == template_id:
            spec = row.get("spec")
            if isinstance(spec, dict):
                return row
    valid = sorted(str(row.get("id")) for row in templates if isinstance(row.get("id"), str))
    message = f"unknown template {template_id!r}; valid ids: {', '.join(valid)}"
    _fail(
        {"contract_version": contract.CONTRACT_VERSION, "command": "decide",
         "error": {"code": "unknown_template", "message": message, "valid_ids": valid}},
        [f"error: {message}"],
        as_json,
    )


def _merge_template(template: dict[str, Any], raw: Any) -> dict[str, Any]:
    fragment = dict(template["spec"])
    if raw is None:
        return fragment
    if not isinstance(raw, dict):
        return raw
    template_where = fragment.get("where") or []
    file_where = raw.get("where") or []
    merged = fragment | raw
    merged["where"] = [*template_where, *file_where]
    return merged


def _cache_freshness() -> dict[str, Any]:
    """Return the common CLI cache provenance, not decision snapshot metadata."""
    from .snapshot import load

    freshness = load().freshness()
    return {key: freshness[key] for key in FRESHNESS_KEYS}


def _cost(value: float | None) -> str:
    return "no known price" if value is None else f"${value:.4g}/task"


def _offering_name(ref: contract.OfferingRef) -> str:
    return "/".join(part for part in (ref.provider, ref.region, ref.tier) if part) or "(model)"


def _percent(value: float | None) -> str:
    return "unknown" if value is None else f"{value:.0%}"


def _measured(entry: contract.BandEntry) -> str:
    if not entry.estimates:
        return "no capability estimate"
    fewest = min(entry.estimates, key=lambda estimate: estimate.direct_benchmarks)
    number, direct = fewest.benchmarks, fewest.direct_benchmarks
    text = f"measured on {number} benchmark{'' if number == 1 else 's'}"
    return text if direct == number else f"{text}, {direct} direct"


def _term_lead(term: contract.BlendTerm) -> str:
    if not term.leaders:
        return "no model has enough evidence"
    if not term.estimated:
        value = "" if term.value is None else f" ({term.value:g})"
        return " / ".join(term.leaders) + value
    text = f"{term.leaders[0]} leads, {_percent(term.p_best)} chance of being best"
    if term.runner_up is not None:
        text += f"; {term.runner_up} is ahead of it with probability {_percent(term.p_runner_up)}"
    return text


def _readable_lines(result: contract.Decision) -> list[str]:
    """A short, human summary: status, the answer, the top rows, and the leader's reasons.

    ``--json`` is the whole decision; this is what a person reads first.
    """
    lines = [f"status: {result.status}"]
    if result.status == "no_feasible":
        lines.append("relax: " + "; ".join(result.relax[:3]))
        return lines
    if len(result.blend) > 1:
        lines.append("blend: " + ", ".join(
            f"{term.share:.0%} {term.dimension}" for term in result.blend))
    answer = result.answer
    bands = result.bands
    if isinstance(answer, contract.TiedAnswer):
        lines.append(f"answer: tied, {' / '.join(answer.members)}")
        if bands is not None and any(entry.p_best is not None for entry in bands.best):
            lines.append("  chance of being best: " + ", ".join(
                f"{entry.model} {_percent(entry.p_best)}" for entry in bands.best))
        lines.append(f"  {answer.basis}")
        named = {key: value for key, value in answer.tie_breakers.model_dump().items() if value}
        if named:
            lines.append("  " + "; ".join(f"{key.replace('_', ' ')}: {value}"
                                          for key, value in named.items()))
    elif isinstance(answer, contract.SeparatedAnswer):
        lines.append(f"answer: {answer.leader}")
        lines.append(f"  {answer.basis}")
    elif bands is not None and bands.thin:
        lines.append("answer: none; no ranked model has enough evidence to lead")
    if bands is not None and bands.thin:
        lines.append("not enough evidence yet: " + ", ".join(
            f"{entry.model} ({_measured(entry)})" for entry in bands.thin))
    if len(result.blend) > 1:
        for term in result.blend:
            lines.append(f"  {term.dimension} alone: {_term_lead(term)}")
    lines.append("top:")
    for row in result.results[:5]:
        lines.append(
            f"  {row.rank}. {row.offering.model} via {_offering_name(row.offering)}"
            f"  {_cost(row.cost_per_task)}"
        )
    if len(result.results) > 5:
        lines.append(f"  ... and {len(result.results) - 5} more")
    if result.results and result.results[0].contributions:
        parts = sorted(
            result.results[0].contributions,
            key=lambda part: -(part.weight or 0) * (part.value or 0),
        )[:3]
        lines.append("why:")
        for part in parts:
            value = "unknown" if part.raw_value is None else f"{part.raw_value:g}"
            unit = f" {part.unit}" if part.unit else ""
            weight = "" if part.weight is None else f" (weight {part.weight:g})"
            lines.append(f"  {part.dimension} {value}{unit}{weight}")
    if result.may_qualify:
        models = sorted({row.model for row in result.may_qualify})
        lines.append(f"{len(result.may_qualify)} may qualify: {', '.join(models[:5])}")
    lines.append("--json prints the whole decision; --why-not MODEL_ID explains one model.")
    return lines


def _why_not_lines(answer: Any) -> list[str]:
    lines = [answer.summary]
    for failed in answer.failed:
        figure = "" if failed.value is None else f": {failed.value}{' ' + failed.unit if failed.unit else ''}"
        lines.append(f"  failed {failed.condition}{figure}")
    for point in answer.tipping_points[:3]:
        lines.append(f"  {point.description} ({point.dimension}, {point.threshold})")
    for offering in answer.offerings:
        detail = f"#{offering.rank}" if offering.rank else offering.status
        lines.append(
            f"  {_offering_name(offering.offering)}: {detail}, {_cost(offering.cost_per_task)}"
        )
    return lines


def _check_router_options(
    base: dict[str, Any], router_format: str | None, out: Path | None,
    include_rest: bool, include_thin: bool, *, as_json: bool, other: bool,
) -> None:
    from decision.router_config import FORMATS

    def fail(message: str) -> None:
        _fail(base | {"error": {"code": "router_config_usage", "message": message}},
              [f"error: {message}"], as_json)

    if router_format is None:
        if out is not None or include_rest or include_thin:
            fail("--out, --include-rest and --include-thin need --emit-router-config")
        return
    if router_format not in FORMATS:
        fail(f"unknown router config format {router_format!r}; valid: {', '.join(FORMATS)}")
    if other:
        fail("--emit-router-config cannot be combined with --check, --compare-to or --why-not")
    if as_json and out is None:
        # stdout carries one document: --json keeps the decision, so the config needs --out.
        fail("--emit-router-config with --json needs --out PATH")


def _regenerate_command(spec_path: Path | None, template: str | None, router_format: str,
                        include_rest: bool, include_thin: bool) -> str:
    parts = ["modelspec", "decide"]
    if spec_path is not None:
        parts.append(str(spec_path))
    if template is not None:
        parts += ["--template", template]
    parts += ["--emit-router-config", router_format]
    parts += ["--include-rest"] if include_rest else []
    parts += ["--include-thin"] if include_thin else []
    return " ".join(parts)


def _emit_router_config(
    base: dict[str, Any], result: contract.Decision, router_format: str, out: Path | None,
    include_rest: bool, include_thin: bool, *, as_json: bool,
    spec_path: Path | None, template: str | None,
) -> None:
    from decision.router_config import EmptyAllowListError, listed, render

    base = base | {"decision_id": result.decision_id, "snapshot": result.snapshot}
    try:
        text = render(
            result, router_format,  # type: ignore[arg-type] - checked in _check_router_options
            include_rest=include_rest, include_thin=include_thin,
            command=_regenerate_command(spec_path, template, router_format,
                                        include_rest, include_thin),
        )
    except EmptyAllowListError as exc:
        _fail(base | {"error": {"code": exc.code, "message": str(exc)}},
              [f"error: {exc}"], as_json)
    rows = listed(result, include_rest=include_rest, include_thin=include_thin)
    routes = sum(len(row.routes) for row in rows)
    thin = sum(row.band == "thin" for row in rows)
    note = (f"{router_format} router config: {len(rows)} model"
            f"{'' if len(rows) == 1 else 's'}, {routes} route{'' if routes == 1 else 's'}")
    if thin:
        note += f", {thin} thin (not enough evidence yet)"
    typer.echo("warning: replace every <...> placeholder with the router's own model ID "
               "before use; this snapshot does not publish them", err=True)
    if out is None:
        typer.echo(text, nl=False)
        return
    try:
        out.write_text(text, encoding="utf-8")
    except OSError as exc:
        _fail(base | {"error": {"code": "unwritable", "message": str(exc)}},
              [f"error: cannot write {out}: {exc.strerror or exc}"], as_json)
    typer.echo(f"wrote {note} to {out}", err=True)


def _note_outcome_recording(result: contract.Decision) -> None:
    """When outcome recording is on, keep this decision's stub and say how to record.

    It records no outcome: only ``modelspec outcome record`` does that.
    """
    from . import outcome

    if not outcome.enabled():
        return
    try:
        outcome.save_stub(outcome.stub_from_decision(result.model_dump(mode="json")))
    except (OSError, ValueError):
        pass
    typer.echo(f"outcome recording is on: after the task, run `modelspec outcome record "
               f"{result.decision_id} --adopted MODEL --result success|partial|failure`",
               err=True)


def decide(
    spec_path: Optional[Path] = typer.Argument(  # noqa: UP045 - Typer reads the annotation
        None, help="The optional spec, as YAML. Required without --template."
    ),
    template: Optional[str] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--template", help="Start from a template in the cached vocabulary."
    ),
    explain: Optional[str] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--explain", help="Override the spec's explain: none, summary or full."
    ),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
    snapshot_file: Optional[Path] = typer.Option(  # noqa: UP045 - Typer annotation
        None,
        "--snapshot-file",
        envvar="MODELSPEC_DECISION_SNAPSHOT",
        help="Local decision snapshot (.gz).",
    ),
    html: Optional[Path] = typer.Option(  # noqa: UP045 - Typer annotation
        None, "--html", help="Write a self-contained HTML report."
    ),
    check: bool = typer.Option(
        False, "--check", help="Validate against the cached vocabulary without deciding."
    ),
    compare_to: Optional[str] = typer.Option(  # noqa: UP045 - Typer annotation
        None, "--compare-to", help="Compare with a cached snapshot ID, previous, or a .gz path."
    ),
    why_not: Optional[str] = typer.Option(  # noqa: UP045 - Typer annotation
        None,
        "--why-not",
        metavar="MODEL_ID",
        help="Say why one model failed a Must, may qualify, or ranked where it did.",
    ),
    router_format: Optional[str] = typer.Option(  # noqa: UP045 - Typer annotation
        None,
        "--emit-router-config",
        metavar="FORMAT",
        help="Write the best band as a router allow-list: litellm, openrouter or json.",
    ),
    out: Optional[Path] = typer.Option(  # noqa: UP045 - Typer annotation
        None, "--out", help="Write the router config here instead of stdout."
    ),
    include_rest: bool = typer.Option(
        False, "--include-rest",
        help="Also list the rest band: the other models that passed every Must.",
    ),
    include_thin: bool = typer.Option(
        False, "--include-thin",
        help="Also list models with not enough evidence yet, labelled thin.",
    ),
) -> None:
    """Decide which model or offering fits a spec (the decision contract, v1)."""
    base = {"contract_version": contract.CONTRACT_VERSION, "command": "decide"}
    if spec_path is None and template is None:
        _fail(
            base | {"error": {
                "code": "spec_required", "message": "pass SPEC.yaml or --template ID"
            }},
            ["error: pass SPEC.yaml or --template ID"],
            as_json,
        )
    text = ""
    if spec_path is not None:
        try:
            text = spec_path.read_text()
        except OSError as exc:
            _fail(
                base | {"error": {"code": "unreadable", "message": str(exc)}},
                [f"error: cannot read {spec_path}: {exc.strerror or exc}"],
                as_json,
            )

    vocabulary: dict[str, Any] | None = None
    if check or template is not None:
        try:
            vocabulary = load_cached_vocabulary()
        except VocabularyMissingError as exc:
            _fail(base | {"error": {"code": "snapshot_required", "message": str(exc)}},
                  [f"error: {exc}"], as_json)
        except VocabularyInvalidError as exc:
            _fail(base | {"error": {"code": "decision_failed", "message": str(exc)}},
                  [f"error: {exc}"], as_json)
    templates = vocabulary.get("templates", []) if vocabulary is not None else []
    if template is not None and not isinstance(templates, list):
        message = "cached decision vocabulary has an invalid templates field"
        _fail(base | {"error": {"code": "decision_failed", "message": message}},
              [f"error: {message}"], as_json)
    facets = _facet_lookup()
    selected_template: dict[str, Any] | None = None
    try:
        raw = contract.load_yaml(text) if spec_path is not None else None
        if template is not None:
            selected_template = _template(templates, template, as_json)
            raw = _merge_template(selected_template, raw)
        if explain is not None and isinstance(raw, dict):
            raw = raw | {"explain": explain}
        spec = contract.parse_spec(raw, facets=facets)
    except contract.SpecError as exc:
        issues = _issues(exc, vocabulary)
        _fail(
            base | {"error": {"code": "invalid_spec", "issues": issues}},
            ["error: invalid spec", *(f"  {issue}" for issue in exc.issues)],
            as_json,
        )

    base |= {"spec_hash": contract.spec_hash(spec), "explain": spec.explain}
    if why_not is not None:
        if check or compare_to is not None:
            message = "--why-not cannot be combined with --check or --compare-to"
            _fail(base | {"error": {"code": "decision_failed", "message": message}},
                  [f"error: {message}"], as_json)
        # Eliminated models are only listed at full; the answer needs them.
        spec = spec.model_copy(update={"explain": "full"})
    _check_router_options(base, router_format, out, include_rest, include_thin,
                          as_json=as_json, other=check or compare_to is not None
                          or why_not is not None)
    template_warning = None
    if selected_template is not None and not selected_template.get("available", True):
        template_warning = selected_template.get("unavailable_reason") or (
            "this template is unavailable against the cached snapshot"
        )
        typer.echo(f"warning: {template_warning}", err=True)
    if compare_to is not None and html is not None:
        _fail(
            base | {"error": {"code": "comparison_html", "message":
                               "--html is not available with --compare-to"}},
            ["error: --html is not available with --compare-to"], as_json,
        )
    using_cached_snapshot = snapshot_file is None
    if using_cached_snapshot:
        from .snapshot import decision_snapshot_path

        snapshot_file = decision_snapshot_path()
        if not snapshot_file.is_file():
            message = (
                "no cached decision snapshot. Run `modelspec snapshot fetch`, "
                "pass --snapshot-file, or set MODELSPEC_DECISION_SNAPSHOT"
            )
            _fail(
                base | {"error": {"code": "snapshot_required", "message": message}},
                [f"error: {message}"],
                as_json,
            )
    if html is not None and spec.explain != "full":
        _fail(
            base
            | {"error": {"code": "full_required", "message": "--html requires --explain full"}},
            ["error: --html requires --explain full"],
            as_json,
        )
    from decision.snapshot import load_snapshot

    try:
        index = (load_snapshot(snapshot_file, key=None, include_archive=True)
                 if using_cached_snapshot
                 else load_snapshot(snapshot_file, include_archive=True))
        if check:
            validate_decision(spec, index, facets=facets)
            assert vocabulary is not None
            warnings = _vocabulary_warnings(spec, vocabulary)
            if template_warning is not None and template_warning not in warnings:
                warnings.insert(0, template_warning)
            cached_snapshot = vocabulary.get("snapshot")
            if spec.snapshot != "latest" and spec.snapshot != cached_snapshot:
                warnings.append(
                    f"spec pins {spec.snapshot}, but the cached vocabulary describes "
                    f"{cached_snapshot}"
                )
            for warning in warnings:
                typer.echo(f"warning: {warning}", err=True)
            summary = _summary(spec)
            if as_json:
                payload = base | {
                    "ok": True, "summary": summary, "snapshot": cached_snapshot,
                    "warnings": warnings,
                }
                typer.echo(json.dumps(payload, indent=2))
            else:
                typer.echo(f"ok: {summary}")
            return
        if compare_to is not None:
            from decision.compare import compare

            from .snapshot import resolve_decision_generation

            candidate = Path(compare_to).expanduser()
            explicit_path = candidate.is_file()
            old_path = candidate if explicit_path else resolve_decision_generation(compare_to)
            old_index = (load_snapshot(old_path, include_archive=True) if explicit_path else
                         load_snapshot(old_path, key=None, include_archive=True))
            comparison_spec = spec.model_copy(
                update={"snapshot": "latest", "explain": "full", "estate": None})
            old_result = run_decision(
                comparison_spec, old_index, facets=facets, comparison=True
            )
            new_result = run_decision(
                comparison_spec, index, facets=facets, comparison=True
            )
            result = compare(
                old_result, new_result,
                old_as_of=old_index.as_of.isoformat() if old_index.as_of else None,
                new_as_of=index.as_of.isoformat() if index.as_of else None,
            )
            result["spec_snapshot_ignored"] = spec.snapshot != "latest"
        else:
            result = run_decision(spec, index, facets=facets)
        if html is not None:
            from decision.explain import render_html

            html.write_text(render_html(result, index), encoding="utf-8")
    except contract.SpecError as exc:
        issues = _issues(exc, vocabulary)
        _fail(
            base | {"error": {"code": "decision_failed", "issues": issues}},
            ["error: decision failed", *(f"  {i['path']}: {i['reason']}" for i in issues)],
            as_json,
        )
    except (OSError, ValueError, KeyError) as exc:
        _fail(
            base | {"error": {"code": "decision_failed", "message": str(exc)}},
            [f"error: {exc}"],
            as_json,
        )
    if compare_to is None:
        _note_outcome_recording(result)
    if router_format is not None:
        _emit_router_config(base, result, router_format, out, include_rest, include_thin,
                            as_json=as_json, spec_path=spec_path, template=template)
        if out is None:
            return
    if why_not is not None:
        from decision.why_not import why_not as answer_why_not

        answer = answer_why_not(result, why_not)
        if as_json:
            typer.echo(json.dumps(
                {"contract_version": contract.CONTRACT_VERSION, "command": "decide",
                 "why_not": answer.model_dump(mode="json")},
                ensure_ascii=False, separators=(",", ":"),
            ))
        else:
            for line in _why_not_lines(answer):
                typer.echo(line)
    elif as_json:
        if compare_to is not None:
            typer.echo(json.dumps({
                "schema_version": SCHEMA_VERSION,
                "command": "decide",
                "freshness": _cache_freshness(),
                "result": result,
            }, ensure_ascii=False, separators=(",", ":")))
        else:
            # The Worker's body byte for byte (api/worker/src/decide_service.serialise).
            typer.echo(json.dumps(result.model_dump(mode="json"), ensure_ascii=False,
                                  separators=(",", ":")))
    elif compare_to is not None:
        counts = result["counts"]
        old_top = old_result.results[0].offering.model if old_result.results else "none"
        new_top = new_result.results[0].offering.model if new_result.results else "none"
        headline = f"{counts['entered']} entered, {counts['left']} left"
        if old_top != new_top:
            headline += f", top changed from {old_top} to {new_top}"
        typer.echo(headline)
        if result["spec_snapshot_ignored"]:
            typer.echo("Spec snapshot pin ignored; compared the requested snapshots.")
        for row in result["models"]:
            parts = []
            if row["entered"]:
                parts.append("entered")
            if row["left"]:
                parts.append(f"left: {row['left']['reason']}")
            if row["rank_changed"]:
                parts.append(f"rank {row['rank_changed']['old']} -> {row['rank_changed']['new']}")
            if row["may_qualify"]:
                parts.append("may qualify changed")
            parts.extend(
                (change.get("facet") or change.get("domain") or change["kind"]) + " changed"
                for change in row["values"]
            )
            typer.echo(f"{row['model']}: " + "; ".join(parts))
    else:
        for line in _readable_lines(result):
            typer.echo(line)
