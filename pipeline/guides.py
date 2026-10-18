"""Method guides with one worked example from the frozen public image."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

from decision.contract import DEFAULT_TASK_TOKENS, parse_spec
from pipeline import build, entity, render as r

INDEX = "/guides/"
CHOOSE = INDEX + "how-to-choose-an-ai-model/"
COMPARE = INDEX + "analysis-of-alternatives-vs-model-router-vs-hard-coded-model/"
TEMPLATE = "budget-coding"
TERM = "analysis of alternatives for AI models"
DEFINITION = (
    "An analysis of alternatives for AI models decides which models fit a job and shows its work, "
    "using the job's requirements, sourced benchmarks and real cost."
)
CHOOSE_TITLE = "How to choose an AI model for a job"
COMPARE_TITLE = "Analysis of alternatives, model router or hard-coded model: which job each does"


def _letters(index: int) -> str:
    label = ""
    while index:
        index, digit = divmod(index - 1, 26)
        label = chr(65 + digit) + label
    return label


def _table(identifier: str, headings: tuple[str, ...], rows: list[list[str]]) -> str:
    head = "".join(f'<th scope="col">{r.esc(heading)}</th>' for heading in headings)
    body = "".join('<tr>' + "".join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows)
    return (f'<div class="use-case-table" tabindex="0" role="region" '
            f'aria-label="{r.esc(identifier.replace("-", " "))}">'
            f'<table id="{identifier}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def _example(template: dict, decision: dict, tokens, exclusions: list[dict]) -> str:
    value = build._use_case_value
    bands = decision.get("bands")
    examples = exclusions[:10]
    models = {row["model"] for row in decision["by_model"]}
    models.update(row["model"] for row in examples)
    if bands:
        models.update(entry["model"] for band in ("best", "rest", "thin") for entry in bands[band])
    aliases = {model: f"Alternative {_letters(index)}" for index, model in enumerate(sorted(models), 1)}
    offerings = {tuple(row["offering"].values()) for row in examples}
    routes = {key: f"Offering {_letters(index)}" for index, key in
              enumerate(sorted(offerings, key=lambda key: tuple(part or "" for part in key)), 1)}
    body = (f'<p>This delayed example applies the <a href="{build._use_case_path(template)}">'
            f'{r.esc(template["name"])}</a> template. Alternative labels replace product names '
            'throughout this guide. The linked dated use-case page names the models.</p>'
            f'<p>{r.esc(template["teaches"])}</p><ul>')
    for row in template["where"]:
        body += f'<li>Must: <code>{value(row["condition"])}</code>. {r.esc(row["reason"])}</li>'
    for facet, row in template["weights"].items():
        body += (f'<li>Prefer: <code>{r.esc(facet)}</code>, weight {value(row["weight"])}. '
                 f'{r.esc(row["reason"])}</li>')
    body += (f'</ul><p>Decision status: {r.esc(decision["status"])}. '
             f'Decision <code>{r.esc(decision["decision_id"])}</code> on public snapshot '
             f'<code>{r.esc(decision["snapshot"])}</code>.</p>')
    answer = decision["answer"]
    if answer:
        label = "Tied on the evidence" if answer["kind"] == "tied" else "Separated on the evidence"
        body += f'<p>{label}: ' + ", ".join(aliases[mid] for mid in answer["members"]) + '.</p>'
    else:
        body += '<p>No recommendation: the public image has no answer with enough evidence.</p>'
    if bands:
        body += f'<p>{r.esc(bands["basis"])}</p>'
    body += ('<p>Tie-breakers describe members of the tie. They do not establish a winner. '
             'Unavailable means the engine did not return a value or a unique tie-breaker.</p>')
    if answer and answer["kind"] == "tied":
        body += '<ul>'
        for key, label in (("cheapest", "Lowest task cost"), ("fastest", "Highest throughput"),
                           ("open_weights", "Sole open-weights member"),
                           ("most_independently_measured", "Most independently measured member")):
            member = answer["tie_breakers"][key]
            body += f'<li>{label}: {aliases[member] if member else "Unavailable"}.</li>'
        body += '</ul>'
    body += (f'<p>Cost per task is in USD for the engine-selected offering at '
             f'{tokens.input} input tokens and {tokens.output} output tokens. '
             'The engine applies the offering\'s input and output prices to that task size. '
             'This template uses the engine\'s default task size. It does not measure retries '
             'or the cost of correcting an answer. Unavailable cost is not free.</p>'
             '<p>Scores and score intervals use dimensionless normalised objective units. '
             'P(best) is the engine probability. Thin evidence is undetermined and is not a recommendation.</p>')
    rows = []
    if bands:
        for band, label in (("best", "Leading evidence band"), ("rest", "Other ranked alternatives"),
                            ("thin", "Thin evidence, undetermined")):
            for entry in bands[band]:
                rows.append([aliases[entry["model"]], label, *[
                    value(entry[key]) for key in ("score", "score_interval", "p_best", "cost_per_task")]])
    if rows:
        body += _table("example-results", ("Alternative", "Evidence band", "Score", "Score interval",
                                           "P(best)", "Cost per task, USD"), rows)
    else:
        body += '<p>No candidates have ranked scores in this image.</p>'
    body += ('<h3>Which alternatives were screened out?</h3>'
             '<p>These counts group exclusion rows by failed condition. A model can appear under '
             'more than one condition or offering, so the counts are not distinct model totals. '
             'An offering can fail while another offering of the same model qualifies.</p>')
    rows = [[aliases[row["model"]], routes[tuple(row["offering"].values())],
             value(row["condition"]), value(row["values"] or row["value"]), value(row["unit"])]
            for row in examples]
    if rows:
        counts = Counter(row["condition"] for row in exclusions)
        body += _table("example-exclusion-counts", ("Failed condition", "Exclusion rows"),
                       [[value(condition), value(count)] for condition, count in sorted(counts.items())])
        body += (f'<p>Showing {len(rows)} of {len(exclusions)} exclusion rows. '
                 'Offering labels identify routes within this example.</p>'
                 + _table("example-excluded", ("Alternative", "Route", "Failed condition", "Observed value", "Unit"), rows))
    else:
        body += '<p>No candidates were screened out by a known failed condition.</p>'
    body += (f'<p><a href="{build._use_case_path(template)}#screened-out">'
             'Read the full screened-out list on the dated use-case page</a>.</p>')
    unknown = sorted({facet for candidate in decision["may_qualify"] for facet in candidate["unknown"]})
    if unknown:
        body += ('<p>Some candidates may qualify but lack a required fact or objective value: '
                 + ", ".join(f'<code>{r.esc(facet)}</code>' for facet in unknown) + '.</p>')
    body += ('<p>The live board uses current data. Its answer can change as evidence changes.</p>'
             f'<p><a class="button primary" href="/decide/?template={r.esc(template["id"])}">'
             'Apply this template on Decide</a></p>')
    return body


def _choose(example: str) -> str:
    return f'''<h2>What is an analysis of alternatives for AI models?</h2>
<p>{r.esc(DEFINITION)} ModelSpec performs this analysis per job or role.
Read <a href="/about/">about ModelSpec</a> for its entity facts.</p>
<h2>How do you state the job's requirements?</h2>
<p>Put non-negotiable requirements in Must and tradeable priorities in Prefer.
A Must screens candidates for a condition such as a licence, context capacity or self-hosting support.
A Prefer tells the engine how to weigh the candidates that remain. Start with an existing
<a href="/use-cases/">use-case template</a>, then change it to match the job.</p>
<h2>What evidence decides which models fit?</h2>
<p>Requirements, sourced benchmark measurements and real task cost decide the result.
Check whether a benchmark measures the capability your job needs and whether the facts cover
the offering you can actually use. Missing facts stay unknown; they are not proof of compliance.
Use <a href="/compare/">dated model comparisons</a> to inspect the evidence.</p>
<h2>Why is the top often a tie?</h2>
<p>The top is a tie when the evidence cannot separate the leading alternatives under the engine's
probability rule. Task cost, throughput, open weights and independent measurements can help choose
within that tie. A tie-breaker does not turn uncertainty into an evidence-supported winner.
The worked example below prints the engine's rule and available tie-breakers.</p>
<h2>Why compare cost per task?</h2>
<p>Cost per task prices the input and output your job actually uses.
A token price alone leaves out task size and the offering's price schedule. Set a realistic workload
before comparing costs. Check retries and correction work separately when estimating total operating cost.</p>
<h2>What does the screened-out list tell you?</h2>
<p>The screened-out list explains which candidates failed a requirement and why.
Read it before relaxing a Must. Keep failed requirements separate from unknown facts and missing
objective evidence. A model that may qualify still needs evidence before it becomes a recommendation.</p>
<p><a href="/method/">Read the full decision method</a> for Must, Prefer, uncertainty and reproducibility.</p>
<h2>What does a dated budget-coding decision show?</h2>
{example}'''


def _comparison(as_of: date) -> str:
    rows = [
        ["When do you decide?", "Before deployment or when a job's requirements change.",
         "For each request on live traffic.", "During implementation or a planned configuration change."],
        ["What does it optimise?", "Fit to explicit job requirements and preferences.",
         "The routing policy's quality, cost, latency or availability objective.",
         "A stable integration with the chosen model."],
        ["What evidence does it use?", "Sourced facts, admitted benchmarks and offering costs in a snapshot.",
         "Request features and whatever evaluations, feedback or telemetry the router uses.",
         "The tests and operational experience used to choose and retain that model."],
        ["Can you reproduce the decision?", "The same spec and snapshot reproduce the answer.",
         "Reproduction needs the policy version, request and relevant runtime state.",
         "The configured choice is repeatable; model outputs and service versions can still change."],
        ["How are licence, self-hosting and VRAM constraints handled?",
         "Express supported constraints as Must and inspect unknown facts and exclusions.",
         "Restrict the candidate pool and enforce policy checks; routing alone does not prove compliance or hardware fit.",
         "Validate the chosen licence, deployment route and memory fit before release and after changes."],
        ["What per-request latency and cost does it add?", "The analysis runs per job and adds no routing hop to model requests.",
         "Selection can add compute, latency or service cost; the amount depends on the implementation.",
         "No model-selection step runs per request; the model's serving latency and cost remain."],
        ["How can it fail?", "Incomplete evidence or an inaccurate job spec can leave the decision unresolved or unsuitable.",
         "A miscalibrated policy or stale feedback can route requests to an unsuitable model.",
         "A fixed choice can become unsuitable as the job, model or service changes."],
        ["When is it the right fit?", "A defensible choice for a job with constraints and alternatives worth evaluating.",
         "Per-request routing on live traffic with varying needs.",
         "One model already fits and the cost of change outweighs the expected benefit."],
    ]
    return ('''<h2>Which approach fits the decision you need to make?</h2>
<p>Use an analysis of alternatives to choose models for a job, a model router to select a model
for each request, and a hard-coded model to keep an already suitable integration stable.
A router is the better tool for per-request routing on live traffic.
A hard-coded model is the better tool when one model already fits and change is costly.</p>'''
            + f'<p>Updated <time datetime="{as_of.isoformat()}">{as_of.isoformat()}</time>.</p>'
            + _table("category-comparison", ("Question", "Analysis of alternatives", "Model router", "Hard-coded model"),
                     [[r.esc(cell) for cell in row] for row in rows])
            + '''<h2>Can these approaches work together?</h2>
<p>An analysis of alternatives can establish an eligible set for a router or justify a fixed model choice.
The router still needs a policy for live requests, and a fixed choice still needs monitoring when
requirements change. ModelSpec decides per job or role and does not proxy model requests.</p>
<p>Read <a href="/method/">the decision method</a>, try a <a href="/use-cases/">dated use-case example</a>,
or inspect <a href="/compare/">model comparisons</a>. <a href="/about/">About ModelSpec</a> states its claims.</p>''')


def write_examples(tree: Path, catalogue: dict, decisions: list[dict], as_of: date,
                   snapshot, registry, *, exclusions: list[dict] | None = None) -> dict:
    template, decision = next((template, decision) for template, decision in
                              zip(catalogue["templates"], decisions, strict=True)
                              if template["id"] == TEMPLATE)
    spec = parse_spec(template["spec"], facets=registry.facet)
    if exclusions is None:
        exclusions = build.use_case_exclusions(template, snapshot, registry)
    term = {"@type": "DefinedTerm", "@id": entity.SITE + CHOOSE + "#term",
            "name": TERM, "description": DEFINITION, "url": entity.SITE + CHOOSE}
    index = (f'<p>Start with <a href="{CHOOSE}">{CHOOSE_TITLE}</a> to turn a job into requirements '
             'and read a worked decision from the delayed public image.</p>'
             f'<p>Read <a href="{COMPARE}">{COMPARE_TITLE}</a> to decide when each category fits. '
             'The comparison covers the timing of the decision, the evidence it needs, constraints, '
             'operating overhead and failure modes.</p>'
             '<p>These guides explain how to evaluate a job. For depth, read <a href="/method/">the method</a>; '
             'for entity facts, read <a href="/about/">about ModelSpec</a>.</p>')
    pages = (
        (INDEX, "Guides", "Choose models for a job and understand which decision tools fit.", index, []),
        (CHOOSE, CHOOSE_TITLE, "State Must and Prefer, read the evidence, and inspect a dated worked example.",
         _choose(_example(template, decision, spec.task_tokens or DEFAULT_TASK_TOKENS, exclusions)), [term]),
        (COMPARE, COMPARE_TITLE, "Choose a decision method for the job and the moment a model must be selected.",
         _comparison(as_of), []),
    )
    for path, title, description, body, nodes in pages:
        page = tree / path.lstrip("/") / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(build._use_case_shell(
            title, description, path, body, as_of, indexable=True, article=path != INDEX,
            collection="guides", extra_nodes=nodes, worked_example=path == CHOOSE,
        ), encoding="utf-8")
    paths = [row[0] for row in pages]
    return {"sitemap_paths": paths, "sitemap_dates": {path: as_of.isoformat() for path in paths}}


def write(tree: Path, public_root: Path) -> dict:
    with build.public_use_case_image(public_root) as (catalogue, decisions, as_of, snapshot, registry):
        template = next(t for t in catalogue["templates"] if t["id"] == TEMPLATE)
        exclusions = build.use_case_exclusions(template, snapshot, registry)
        build.write_use_case_pages(tree, public_root, examples=(catalogue, decisions, as_of),
                                   exclusions={TEMPLATE: exclusions})
        return write_examples(tree, catalogue, decisions, as_of, snapshot, registry,
                              exclusions=exclusions)
