"""Dated comparisons from the public template decisions and named-model facts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

from decision.model_comparison import collect_models
from pipeline import build, render as r

MAX_PAIRS = 5


def _job_name(template: dict) -> str:
    name, separator, qualifier = template["name"].partition(", ")
    return f"{name} ({qualifier})" if separator else name


def _probability(entry: dict, field: str, *, include_article: bool = False) -> str:
    value = entry[field]
    if value is None:
        display = "Unavailable"
    elif value < 0.01:
        display = "under 1%"
    else:
        percent = (Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        display = f"{percent}%"
    span = (f'<span data-model="{r.esc(entry["model"])}" data-field="{field}" '
            f'data-probability="{json.dumps(value, allow_nan=False)}">{display}</span>')
    if include_article:
        article = "an" if display.startswith(("under ", "Unavailable", "8", "11%", "18%")) else "a"
        return f"{article} {span}"
    return span


def _measured(entry: dict) -> bool:
    return bool(entry["estimates"]) and all(row["benchmarks"] > 0 for row in entry["estimates"])


def select_pairs(decision: dict) -> list[tuple[str, str]]:
    """Compare only the leader, whose pair probabilities the engine supplies."""
    if not build._use_case_indexable(decision) or not decision.get("bands"):
        return []
    bands = decision["bands"]
    best = [row["model"] for row in bands["best"] if _measured(row)]
    leader = bands["leader"]
    if leader not in best:
        return []
    challengers = [model for model in best if model != leader]
    next_ranked = next((row["model"] for row in bands["rest"] if _measured(row)), None)
    if next_ranked is not None:
        challengers.append(next_ranked)
    return [tuple(sorted((leader, model))) for model in challengers[:MAX_PAIRS]]


def pair_path(template: dict, pair: tuple[str, str]) -> str:
    models = "-vs-".join(model.replace("/", "--") for model in sorted(pair))
    return f'/compare/{template["id"]}/{models}/'


def _evidence(model: dict, sources: dict[str, str]) -> str:
    rows = []
    for item in model["evidence"]:
        citations = " ".join(
            f'<a href="{r.esc(sources[source])}">Source</a>'
            for source in item["source_ids"] if source in sources
        )
        values = "".join(f'<td>{build._use_case_value(item.get(key))}</td>' for key in (
            "benchmark", "version", "value", "unit", "interval", "date",
        ))
        conditions = "".join(
            f'<li>{label}: {build._use_case_value(item.get(key))}</li>'
            for key, label in (("effort", "Effort"), ("subcategory", "Subcategory"),
                               ("harness", "Harness"), ("measured_by", "Measured by"),
                               ("n", "Sample size"))
        )
        rows.append(f'<tr>{values}<td><ul>{conditions}</ul></td><td>{citations}</td></tr>')
    if not rows:
        return '<p>Detailed benchmark evidence is unavailable in this comparison response.</p>'
    return ('<div class="use-case-table"><table><thead><tr><th>Benchmark</th><th>Version</th>'
            '<th>Measurement</th><th>Unit</th><th>Published interval</th><th>Evidence date</th>'
            '<th>Measurement conditions</th><th>Provenance</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table></div>')


def _missing(model: dict, entry: dict | None) -> str:
    facts = list(model["facts"])
    if entry:
        facts.extend(fact for offering in model["offerings"]
                     if offering["offering"] == entry["offering"] for fact in offering["facts"])
    missing = [fact for fact in facts if fact["state"] != "known"]
    if not missing:
        return '<p>No missing facts reported for this model and selected offering.</p>'
    return '<ul>' + "".join(
        f'<li><code>{r.esc(fact["facet"])}</code>: {r.esc(fact["state"])}</li>'
        for fact in missing
    ) + '</ul>'


def comparison_page(template: dict, decision: dict, comparison: dict, as_of: date,
                    *, model_names: dict[str, str] | None = None) -> str:
    pair = tuple(sorted(model["model"] for model in comparison["models"]))
    names = {model: (model_names or {}).get(model) or model for model in pair}
    job = _job_name(template)
    title = f'{names[pair[0]]} vs {names[pair[1]]} for {job}, as of {as_of.isoformat()}'
    bands = decision.get("bands") or {}
    entries = {row["model"]: row for band in ("best", "rest", "thin")
               for row in bands.get(band, [])}
    indexable = pair in select_pairs(decision)
    probabilities = [(entries[model], "p_best") for model in pair if model in entries]
    separation_note = ""
    body = '<h2>What the evidence says</h2>'
    if not indexable:
        body += '<p>No comparison: the public image has insufficient objective evidence for this pair.</p>'
    else:
        leader = entries[bands["leader"]]
        challenger = entries[next(model for model in pair if model != leader["model"])]
        probabilities.append((challenger, "p_beats_leader"))
        tied = challenger["model"] in {row["model"] for row in bands["best"]}
        if tied:
            body += '<p>The evidence can\'t separate them for this job.</p>'
        else:
            body += (f'<p>The evidence separates them: {r.esc(names[leader["model"]])} leads for '
                     f'{r.esc(job)}, with {_probability(leader, "p_best", include_article=True)} '
                     'chance of being the best model in the full lineup for this job, '
                     f'as of {as_of.isoformat()}.</p>')
            separation_note = ('Separation from this challenger need not mean a unique best '
                               'model across that lineup. ')
        if challenger["p_beats_leader"] is None:
            body += (f'<p>The chance of {r.esc(names[challenger["model"]])} matching or beating '
                     f'{r.esc(names[leader["model"]])} on this job\'s objective is '
                     f'{_probability(challenger, "p_beats_leader")}.</p>')
        else:
            body += (f'<p>{r.esc(names[challenger["model"]])} has '
                     f'{_probability(challenger, "p_beats_leader", include_article=True)} chance of matching or beating '
                     f'{r.esc(names[leader["model"]])} on this job\'s objective.</p>')
        body += f'<p>{r.esc(bands["basis"])}</p>'
    body += (f'<p>Decision status: {r.esc(decision["status"])}. '
             'P(best) and score intervals retain the full ranked lineup for this job, '
             'including models beyond this pair and models with thin evidence. '
             'Models with unknown objective values remain unranked and are outside this probability. '
             'P(best) is not a head-to-head probability. '
             f'{separation_note}</p>'
             '<p>Scores and score intervals use the objective\'s dimensionless normalised units. '
             'Cost per task is in USD for the selected offering and the applied spec\'s task size. '
             'When task size is omitted, the engine uses its documented default. '
             'Unavailable means the engine returned no value.</p>')
    rows = []
    for model in pair:
        entry = entries.get(model)
        if entry is None:
            continue
        values = "".join(
            f'<td>{_probability(entry, field) if field == "p_best" else build._use_case_value(entry[field])}</td>'
            for field in ("score", "score_interval", "p_best", "cost_per_task")
        )
        estimates = "".join(
            f'<li>{r.esc(estimate["dimension"])}: {build._use_case_value(estimate["value"])}; '
            f'interval {build._use_case_value(estimate["interval"])}; '
            f'benchmarks {build._use_case_value(estimate["benchmarks"])}; '
            f'direct benchmarks {build._use_case_value(estimate["direct_benchmarks"])}</li>'
            for estimate in entry["estimates"]
        )
        offering = " / ".join(str(entry["offering"].get(key) or "Unavailable")
                              for key in ("provider", "region", "tier"))
        rows.append(f'<tr class="comparison-model" data-model="{r.esc(model)}">'
                    f'<td class="use-case-model">{r.esc(names[model])}</td>'
                    f'{values}<td>{r.esc(offering)}</td><td><ul>{estimates}</ul></td></tr>')
    body += ('<div class="use-case-table"><table><thead><tr><th>Model</th><th>Score</th>'
             '<th>Score interval</th><th>P(best), ranked job lineup</th><th>Cost per task, USD</th>'
             '<th>Selected offering: provider / region / tier</th><th>Capability estimates and intervals</th>'
             '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')
    body += build._use_case_template_intro(template)
    sources = {source["id"]: source["url"] for source in comparison["sources"]}
    for model in sorted(comparison["models"], key=lambda row: row["model"]):
        body += (f'<h2>Evidence for {r.esc(names[model["model"]])}</h2>' + _evidence(model, sources)
                 + f'<h3>Missing facts for {r.esc(names[model["model"]])}</h3>'
                 + _missing(model, entries.get(model["model"])))
    body += (f'<h2>What this template teaches</h2><p>{r.esc(template["teaches"])}</p>'
             f'<p>Decision <code>{r.esc(decision["decision_id"])}</code> on public snapshot '
             f'<code>{r.esc(decision["snapshot"])}</code>.</p>'
             f'<p><a href="{build._use_case_path(template)}">Read the full dated job answer</a>.</p>'
             '<p>The live board uses current data. This link applies the template to its full lineup.</p>'
             f'<p><a class="button primary" href="/decide/details/?template={r.esc(template["id"])}">'
             'Apply this template on Decide</a></p>')
    url = "https://modelspec.dev" + pair_path(template, pair)
    dataset = {
        "@type": "Dataset", "@id": url + "#probabilities", "name": title,
        "description": template["purpose"], "dateModified": as_of.isoformat(),
        "isPartOf": {"@id": url + "#example"},
        "about": [{"@type": "Thing", "identifier": model, "name": names[model]} for model in pair],
        "variableMeasured": [{
            "@type": "PropertyValue", "propertyID": f'{entry["model"]}:{field}',
            "name": "P(best), ranked job lineup" if field == "p_best" else "chance",
            "value": entry[field],
            "unitText": "probability",
        } for entry, field in probabilities],
    }
    return build._use_case_shell(title, template["purpose"], pair_path(template, pair), body,
                                as_of, indexable=indexable, article=True, collection="compare",
                                extra_nodes=[dataset])


def write_examples(tree: Path, catalogue: dict, decisions: list[dict], as_of: date,
                   snapshot, registry, *, public_root: Path) -> dict:
    names = {model.model_id: model.display_name for model in build.load_models(public_root)}
    paths = ["/compare/"]
    sections = []
    for template, decision in zip(catalogue["templates"], decisions, strict=True):
        links = []
        for pair in select_pairs(decision):
            path = pair_path(template, pair)
            if path in paths:
                raise ValueError(f"comparison URL collision: {path}")
            comparison = collect_models(list(pair), snapshot, facets=registry.facet)
            entries = {row["model"]: row for band in ("best", "rest")
                       for row in decision["bands"][band]}
            for model in comparison["models"]:
                domains = [estimate["dimension"].lstrip("-")
                           for estimate in entries[model["model"]]["estimates"]]
                records = {evidence.record_id for domain in domains
                           for evidence in snapshot.evidence_for_domain(model["model"], domain)}
                model["evidence"] = [item for item in model["evidence"] if item["record_id"] in records]
            destination = tree / path.lstrip("/") / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(comparison_page(
                template, decision, comparison, as_of, model_names=names,
            ), encoding="utf-8")
            paths.append(path)
            links.append(f'<li><a href="{r.esc(path)}">{r.esc(names.get(pair[0], pair[0]))} '
                         f'vs {r.esc(names.get(pair[1], pair[1]))}</a></li>')
        if links:
            sections.append(f'<section><h2>{r.esc(_job_name(template))}</h2>'
                            f'<p>{r.esc(template["tradeoff"])}</p><ul>{"".join(links)}</ul>'
                            f'<p><a href="{build._use_case_path(template)}">Full dated job answer</a></p></section>')
    index = tree / "compare/index.html"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(build._use_case_shell(
        "Model comparisons", "Dated comparisons for jobs from the public Decide templates.",
        "/compare/", "".join(sections), as_of, indexable=True, article=False, collection="compare",
    ), encoding="utf-8")
    return {"sitemap_paths": paths, "sitemap_dates": {path: as_of.isoformat() for path in paths}}


def write(tree: Path, public_root: Path) -> dict:
    with build.public_use_case_image(public_root) as (catalogue, decisions, as_of, snapshot, registry):
        return write_examples(tree, catalogue, decisions, as_of, snapshot, registry,
                              public_root=public_root)
