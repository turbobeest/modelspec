"""Build modelspec.dev, and the redirect tree for benchgraph.dev.

    python -m pipeline.build [--out dist]

Pages, the benchmark catalogue and the JSON export are one tree under
modelspec.dev. benchgraph.dev deploys `_redirects` only: `/` goes to the
modelspec.dev homepage, and every other path goes to the same path on
modelspec.dev.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

from decision import registry as decision_registry
from pipeline import agent_copy, brand, card_ids, data_source
from pipeline import export as exporter
from pipeline import render as r
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

#: Cloudflare Pages redirects. `/` is the modelspec.dev homepage; every other
#: path keeps its path on modelspec.dev. Order matters: the first match wins.
BENCHGRAPH_REDIRECTS = (
    "/   https://modelspec.dev/             301\n"
    "/*  https://modelspec.dev/:splat       301\n"
)

#: Rank API and MCP live on api.modelspec.dev, not on the Pages hosts, so both
#: sites' llms.txt point at the same URLs.
API_DOCS = "https://github.com/turbobeest/modelspec/blob/main/docs/api.md"
RANK_API = "https://api.modelspec.dev/v1/rank"
MCP_ENDPOINT = "https://api.modelspec.dev/mcp"
FEEDBACK_API = "https://api.modelspec.dev/v1/feedback"
MODEL_PAGE_MAX_BYTES = 512 * 1024


def write_model_page(destination: Path, page: str) -> None:
    """Write one model page only when it remains suitable for static delivery."""
    size = len(page.encode("utf-8"))
    if size > MODEL_PAGE_MAX_BYTES:
        raise ValueError(
            f"model page {destination} exceeds the {MODEL_PAGE_MAX_BYTES}-byte budget: {size}"
        )
    destination.write_text(page, encoding="utf-8")


def llms_txt(*, site: str, base: str, build: exporter.Build,
             coverage: dict | None = None) -> str:
    """llms.txt for one published tree. Null on a card still means not researched."""
    from pipeline.coverage import provider_summary, summary
    scope = f"{summary(coverage)}\n{provider_summary(coverage)}\n\n" if coverage else ""
    return (
        f"# {site}\n\n"
        f"> {base}\n\n"
        f"{brand.POSITIONING}\n\n"
        f"Decision data on AI models and benchmarks, served online. "
        f"Built {build.built_at} from commit {build.commit[:12]}. "
        f"Null means not researched.\n\n"
        f"{scope}"
        f"- Coverage, keyless: {base}/api/coverage.json\n\n"
        f"Access: a person looking a model up by hand on the site pays nothing. "
        f"{agent_copy.install_markdown()}\n"
        f"{agent_copy.key_procurement()}\n"
        f"{' '.join(agent_copy.CONDUCT_RULES)}\n\n"
        f"Current data is only available through the service, and the copy in the "
        f"public repository is a delayed image, about nine months old.\n\n"
        f"- Agent guide: {base}/agents.md\n"
        f"- Decide (for people): {base}/decide/\n"
        f"- How it decides: {base}/method/\n"
        f"- Orchestrator recipe: {base}/orchestrators/\n"
        f"- Pricing: {base}/pricing/\n"
        f"- Brand and press kit: {base}/brand/\n"
        f"- Ranking policy, keyless: {base}/api/rank/profiles.json\n"
        f"- Legacy v1 rank API: {RANK_API}\n"
        f"- API docs: {API_DOCS}\n"
        f"- MCP: {MCP_ENDPOINT}\n"
        f"- Feedback (no key): POST {FEEDBACK_API} with "
        f'{{"rating": "reliable|unreliable|trustworthy|untrustworthy|confusing", '
        f'"client": "agent", "decision_id": "dec_…"}}. '
        f"Schema: {base}/api/feedback/v1.schema.json. "
        f"MCP tool: feedback. "
        f"Send one after you act on an answer.\n"
        f"- Source: https://github.com/turbobeest/modelspec\n"
    )


def _schema_field_count(model_cls) -> int:
    """Every leaf field, not the 20 top-level sections.

    `len(ModelCard.model_fields)` counts sections and would have put "20 fields
    per card" on the front page of a project whose whole pitch is the depth of
    the schema.
    """
    total = 0
    for field in model_cls.model_fields.values():
        annotation = field.annotation
        if hasattr(annotation, "model_fields"):
            total += _schema_field_count(annotation)
        else:
            total += 1
    return total


_HREF = re.compile(r"""\bhref\s*=\s*['"]([^'"]+)['"]""", re.I)
_SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)


def _output_exists(tree: Path, url_path: str) -> bool:
    path = url_path.split("#", 1)[0].split("?", 1)[0]
    if not path.startswith("/") or path.startswith("//"):
        return True
    rel = path.lstrip("/")
    if not rel:
        return (tree / "index.html").is_file()
    target = tree / rel
    if target.is_file():
        return True
    if path.endswith("/"):
        return (target / "index.html").is_file()
    return (target / "index.html").is_file() or (tree / f"{rel}.html").is_file()


def missing_internal_hrefs(tree: Path) -> list[tuple[str, str]]:
    """Same-origin hrefs in HTML (not script) that have no file in this tree."""
    missing: list[tuple[str, str]] = []
    for html_path in sorted(tree.rglob("*.html")):
        text = _SCRIPT_OR_STYLE.sub(
            "", html_path.read_text(encoding="utf-8", errors="replace")
        )
        for href in _HREF.findall(text):
            if not href.startswith("/") or href.startswith("//"):
                continue
            if _output_exists(tree, href):
                continue
            missing.append((html_path.relative_to(tree).as_posix(), href))
    return missing


def _inject(src: Path, dest: Path, needle: str, html: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    if needle in text and html:
        text = text.replace(needle, html, 1)
    dest.write_text(text, encoding="utf-8")


_DIV = re.compile(r"<div\b|</div>")


def _div_end(html: str, start: int) -> int:
    """The index just past the </div> that closes the <div> opening at `start`."""
    depth = 0
    for tag in _DIV.finditer(html, start):
        depth += 1 if tag.group() == "<div" else -1
        if depth == 0:
            return tag.end()
    return -1


def with_site_nav(html: str, nav: str, page: str) -> str:
    """Fill a static page's nav from the one renderer every generated page uses.

    Each landing and the wizard used to carry its own hand-written list, and the
    four had drifted to four different sets of links. A page without the
    placeholder fails the build rather than shipping with no nav.
    """
    if r.NAV_PLACEHOLDER not in html:
        raise ValueError(f"{page} has no {r.NAV_PLACEHOLDER}; its nav must come from render.site_nav")
    return html.replace(r.NAV_PLACEHOLDER, nav, 1)


def wire_landing(html: str, stats: dict[str, int], freshness: str = "") -> str:
    """Point the front door at the site, and keep its numbers honest.

    The landing page was written before there was anything behind it. It was
    copied verbatim into the build, which meant every page this pipeline
    generates — the graph, the wizard, 1,225 model pages — was live and
    unreachable from modelspec.dev itself. A visitor saw the same holding page
    as before and reasonably concluded nothing had shipped.

    Its statistics were hand-written too, and had drifted. They are now injected
    from the build, so they cannot go stale again.
    """
    # A question with no way to answer it is a poster. Put the answer one click
    # away, immediately under the question the page asks.
    answer_anchor = ('<div class="a">That question, answered from evidence, '
                     'and kept current as the models change underneath you.</div>')
    if answer_anchor in html:
        html = html.replace(answer_anchor, answer_anchor + (
            '\n      <div class="btns go">'
            '<a class="btn primary" href="/downselect/">Answer it now &rarr;</a>'
            '<a class="btn" href="/models/">Browse every model</a>'
            "</div>"), 1)

    # Replace the hand-written statistics with the build's own counts.
    start = html.find('<div class="stats"')
    end = _div_end(html, start) if start != -1 else -1
    if end != -1:
        cells = [("model cards", f'{stats["models"]:,}'),
                 ("providers", f'{stats["providers"]}'),
                 ("relationships", f'{stats["edges"]:,}'),
                 ("benchmarks", f'{stats["benchmarks"]:,}'),
                 ("fields per card", f'{stats["fields"]}')]
        live = ('<div class="stats" aria-label="What the graph holds today" '
                f'style="grid-template-columns:repeat({len(cells)},minmax(0,1fr))">'
                + "".join(r._stat_cell(label, value) for label, value in cells) + "</div>")
        html = html[:start] + live + html[end:]
    if freshness:
        footer = html.find("<footer")
        if footer != -1:
            html = html[:footer] + freshness + html[footer:]
    return html


def benchgraph_headline_stats(models, benchmarks, coverage: dict | None = None) -> dict[str, int]:
    """The four figures at the top of the benchmark catalogue.

    `scored_benchmarks` is distinct keys with a numeric score on a card, not
    the number of published pages. Those two used to ship as one number. The
    three score figures count evidence records as well as flat card scores, so
    they agree with the coverage tables they summarise.
    """
    if coverage is None:
        coverage = exporter.models_by_benchmark(models, benchmarks)
    return {
        "pages": len(benchmarks),
        "scored_benchmarks": len(coverage),
        "scored_models": len({row["model_id"] for rows in coverage.values() for row in rows}),
        "scores": sum(len(rows) for rows in coverage.values()),
    }


def _ship_instrument(root: Path, *dests: Path) -> None:
    """Serve the shared stylesheet and its self-hosted faces.

    The generated pages inline `render.CSS`; the hand-written pages (the
    landing and the wizard) link `/instrument.css`, which is the same string.
    Their colours and fonts used to be copied in by hand and had drifted.
    """
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "instrument.css").write_text(r.CSS, encoding="utf-8")
    src = root / "site/fonts"
    if not src.is_dir():
        return
    for dest in dests:
        target = dest / "fonts"
        target.mkdir(parents=True, exist_ok=True)
        for item in src.glob("*.woff2"):
            shutil.copy2(item, target / item.name)
        for item in src.glob("*-OFL.txt"):
            shutil.copy2(item, target / item.name)


def _copy_static(src: Path, dest: Path) -> bool:
    """Copy a prebuilt landing page tree if it exists. Never overwrite generated pages."""
    if not (src / "index.html").is_file():
        return False
    for item in src.iterdir():
        if item.name == "build":
            continue
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    return True


def _fallback_home(site: str, headline: str, lede: str, links: list[tuple[str, str]],
                   build: exporter.Build, nav: list[tuple[str, str]], canonical: str) -> str:
    cards = "".join(
        f'<div class="card"><a href="{r.esc(h)}">{r.esc(t)}</a></div>' for t, h in links
    )
    body = (f"<h1>{r.esc(headline)}</h1><p class=\"lede\">{r.esc(lede)}</p>"
            f'<div class="grid">{cards}</div>')
    return r.shell(title=headline, description=lede, canonical=canonical, body=body,
                   build=build, site=site, nav_links=nav)


_FROM_ENV = object()


def write_decision_vocabulary(
    root: Path, snapshot_path: Path, *, key: bytes | None,
    ed25519_signer: object = _FROM_ENV,
) -> Path:
    """Write ``vocabulary.json`` beside the snapshot it describes (MODEL-153)."""
    import json

    from decision import snapshot as decision_snapshot
    from decision.vocabulary import build_vocabulary
    from pipeline.load import load_benchmarks, load_models

    loaded = decision_snapshot.load_snapshot(snapshot_path, key=key, include_archive=True)
    pages = {b.benchmark_id: b.front for b in load_benchmarks(root)}
    cards = {m.model_id: m.front for m in load_models(root)}
    target = snapshot_path.parent / "vocabulary.json"
    vocabulary = build_vocabulary(
        loaded,
        pages=pages,
        cards=cards,
        enforce_frontier_coverage=True,
    )
    signer = (decision_snapshot.env_ed25519_signer()
              if ed25519_signer is _FROM_ENV else ed25519_signer)
    if signer is not None:
        vocabulary = decision_snapshot.sign_vocabulary(vocabulary, signer)
    target.write_text(
        json.dumps(
            vocabulary,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )
    return target


def write_decision_snapshot_if_ready(
    root: Path,
    target: Path,
    *,
    premier: Path,
    as_of: date,
) -> bool:
    """Publish only a complete, signed snapshot; warn when it is not ready.

    The vocabulary (``vocabulary.json``) is published with it or not at all.
    """
    from decision import snapshot as decision_snapshot

    target.unlink(missing_ok=True)
    (target.parent / "vocabulary.json").unlink(missing_ok=True)
    key = decision_snapshot.env_key()
    if key is None:
        print(
            f"::warning::decision snapshot not published: {decision_snapshot.KEY_ENV} "
            "is not configured",
            file=sys.stderr,
        )
        return False

    try:
        built = decision_snapshot.build_from_repo(root, premier=premier, as_of=as_of)
    except decision_snapshot.CompletenessError as exc:
        gaps = " | ".join(str(gap) for gap in exc.gaps[:20])
        remainder = len(exc.gaps) - 20
        suffix = f" | {remainder} more gap(s) omitted" if remainder > 0 else ""
        print(
            "::warning::decision snapshot not published: completeness gate found "
            f"{len(exc.gaps)} gaps; first {min(20, len(exc.gaps))}: {gaps}{suffix}",
            file=sys.stderr,
        )
        return False
    except decision_snapshot.SnapshotError as exc:
        print(f"::warning::decision snapshot not published: {exc}", file=sys.stderr)
        return False
    except Exception as exc:  # noqa: BLE001 - the site still ships without this optional file
        print(
            f"::warning::decision snapshot not published: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return False

    try:
        built.write(target, key=key)
        write_decision_vocabulary(root, target, key=key)
    except Exception as exc:  # noqa: BLE001 - the site still ships without this optional file
        target.unlink(missing_ok=True)
        (target.parent / "vocabulary.json").unlink(missing_ok=True)
        print(
            f"::warning::decision snapshot not published: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return False
    return True


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="dist", help="output directory (default: dist)")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository root")
    parser.add_argument(
        "--data-dir", default=None,
        help="private data checkout (MODEL-246); default: the data in --root. "
             "Also read from MODELSPEC_DATA_DIR.",
    )
    # MODEL-138: off by default. Writes the decision snapshot beside the export,
    # linked from no page, and fails the build if the completeness gate fails.
    snapshot = parser.add_mutually_exclusive_group()
    snapshot.add_argument("--decision-snapshot", action="store_true",
                          help="also write api/decision/snapshot.json.gz (off by default)")
    snapshot.add_argument(
        "--decision-snapshot-if-ready",
        action="store_true",
        help="write a complete signed decision snapshot, or warn and continue",
    )
    parser.add_argument("--premier", default=None,
                        help="premier list for the snapshot gate (default premier/slice-1.yaml)")
    return parser.parse_args(argv)


def use_case_image_date(public_root: Path) -> date:
    """Read the frozen image's date, never the build clock or an overlay."""
    manifest = public_root / "data-image.json"
    source = (manifest if manifest.is_file() else
              public_root / "benchmarks/_census/eligibility/current-report.json")
    return date.fromisoformat(str(json.loads(source.read_text(encoding="utf-8"))["as_of"]))


def use_case_decisions(public_root: Path) -> tuple[dict, list[dict], date]:
    """Apply public templates through the same parse/decide path as /v1/decide."""
    from decision.contract import parse_spec
    from decision.engine import decide
    from decision.snapshot import build_from_repo, load_built_snapshot
    from decision.templates import load_catalogue as template_catalogue

    as_of = use_case_image_date(public_root)
    saved_root = decision_registry.REPO_ROOT
    decision_registry.use_root(public_root)
    try:
        registry = decision_registry.load(public_root / "registry", repo_root=public_root)
        catalogue = template_catalogue(public_root / "registry/templates.yaml", registry=registry)
        snapshot = load_built_snapshot(
            build_from_repo(public_root, premier=None, as_of=as_of, registry=registry, gate=False),
            include_archive=True, source="public use-case build",
        )
        decisions = [
            decide(parse_spec(template["spec"], facets=registry.facet), snapshot,
                   facets=registry.facet).model_dump(mode="json")
            for template in catalogue["templates"]
        ]
    finally:
        decision_registry.use_root(saved_root)
    return catalogue, decisions, as_of


def _use_case_path(template: dict) -> str:
    return f'/use-cases/{template["category"]}/{template["id"]}/'


def _use_case_indexable(decision: dict) -> bool:
    return bool(decision["results"] and decision["answer"])


def _use_case_value(value: object) -> str:
    """Render human values without rounding numbers or inventing missing data."""
    if value is None:
        return "Unavailable"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        value = re.sub(r" = (true|false)$",
                       lambda match: " = " + ("Yes" if match[1] == "true" else "No"), value)
        return r.esc(value)
    if isinstance(value, list):
        return "[" + ", ".join(_use_case_value(item) for item in value) + "]"
    return r.esc(json.dumps(value, ensure_ascii=False, allow_nan=False))


def _use_case_spec(value: object) -> str:
    if isinstance(value, dict):
        return '<dl>\n' + "".join(
            f'<dt><code>{r.esc(key)}</code></dt>\n<dd>{_use_case_spec(item)}</dd>\n'
            for key, item in value.items()
        ) + '</dl>'
    if isinstance(value, list):
        return '<ul>' + "".join(f'<li>{_use_case_spec(item)}</li>' for item in value) + '</ul>'
    return _use_case_value(value)


def _use_case_shell(title: str, description: str, path: str, body: str,
                    as_of: date, *, indexable: bool, article: bool) -> str:
    from pipeline import entity, landing_chrome, structured_data

    nodes = structured_data.use_case_graph(
        path, title, description, as_of.isoformat(), article=article,
    )
    robots = "index, follow" if indexable else "noindex, follow"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{r.esc(title)} · ModelSpec</title>
<meta name="description" content="{r.esc(description)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="https://modelspec.dev{r.esc(path)}">
{brand.head_links()}{r.FONTS}
<style>{r.CSS}
.use-case-table{{overflow-x:auto}}.use-case-table table{{min-width:720px}}
.use-case-table td{{vertical-align:top}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}
code{{overflow-wrap:anywhere}}.use-case-model{{min-width:180px}}
:where(.page) h2::before{{content:none}}
</style>{structured_data.script(nodes)}</head>
<body><div class="wrap">{r.site_nav([('Decide', '/decide/'), ('How we decide', '/method/'), ('Pricing', '/pricing/')])}<main class="page">
<p>{r.esc(entity.ONE_SENTENCE)}</p><h1>{r.esc(title)}</h1>
<p class="lede">{r.esc(description)}</p>
<p>Worked example as of {as_of.isoformat()}, from the public data image.</p>
{body}
<p>Human lookup is free on <a href="/decide/">Decide</a>.
CLI, API, and MCP access requires a key. <a href="/pricing/">Access and pricing</a>.</p>
<p><a href="/use-cases/">Use-case examples</a> · <a href="/method/">How we decide</a></p>
</main>{landing_chrome.footer()}</div></body></html>
'''


def use_case_page(template: dict, decision: dict, as_of: date) -> str:
    """Render a dated engine response with registry copy and no page-specific claims."""
    requirements = "".join(
        f'<li><code>{_use_case_value(row["condition"])}</code>: {r.esc(row["reason"])}</li>'
        for row in template["where"]
    )
    preferences = "".join(
        f'<li><code>{r.esc(facet)}</code>: {r.esc(row["reason"])}</li>'
        for facet, row in template["weights"].items()
    )
    body = (f'<p>{r.esc(template["tradeoff"])}</p>'
            f'<h2>Requirements</h2><ul>{requirements}</ul>'
            f'<h2>Preferences</h2><ul>{preferences}</ul>'
            '<details><summary>Applied template spec</summary>'
            f'{_use_case_spec(template["spec"])}</details>'
            f'<h2>Worked answer</h2><p>Decision status: {r.esc(decision["status"])}.</p>')
    answer = decision["answer"]
    if not _use_case_indexable(decision):
        body += '<p>No recommendation: the public image has no answer with enough evidence.</p>'
    else:
        label = "Tied on the evidence" if answer["kind"] == "tied" else "Separated on the evidence"
        body += f'<h3>{label}</h3><ul>' + "".join(
            f'<li><code>{r.esc(model)}</code></li>' for model in answer["members"]
        ) + f'</ul><p>{r.esc(answer["basis"])}</p>'
        if answer["kind"] == "tied":
            tie_breakers = []
            for key, label in (("cheapest", "Cheapest"), ("fastest", "Fastest"),
                               ("open_weights", "Open-weights"),
                               ("most_independently_measured", "Most independently measured")):
                value = answer["tie_breakers"][key]
                if value is not None:
                    tie_breakers.append(f'<li>{label} tie-breaker: {r.esc(value)}</li>')
            if tie_breakers:
                body += ('<p>Tie-breakers describe members of the tie. '
                         'They do not establish a winner.</p><ul>' + "".join(tie_breakers) + '</ul>')
    if decision["status"] == "partial":
        body += ('<p>This is a partial answer. Unknown facts or missing objective evidence '
                 'can leave eligible candidates unranked.</p>')
    bands = decision.get("bands")
    if bands:
        body += (f'<p>{r.esc(bands["basis"])}</p>'
                 '<p>Score and score interval use the objective\'s dimensionless normalised units. '
                 'Cost per task is for the engine-selected offering and the applied spec\'s task size. '
                 'When task size is omitted, the engine uses its documented default. '
                 'P(best) is the engine probability. Unavailable means the engine did not return a value. '
                 'Thin evidence is undetermined and is not a recommendation.</p>')
        for key, label in (("best", "Best band"), ("rest", "Rest band"),
                           ("thin", "Thin evidence: undetermined")):
            if not bands[key]:
                continue
            rows = []
            for entry in bands[key]:
                estimates = "".join(
                    f'<li>{r.esc(estimate["dimension"])}: {_use_case_value(estimate["value"])}; '
                    f'interval {_use_case_value(estimate["interval"])}; '
                    f'benchmarks {_use_case_value(estimate["benchmarks"])}; '
                    f'direct benchmarks {_use_case_value(estimate["direct_benchmarks"])}</li>'
                    for estimate in entry["estimates"]
                )
                cells = "".join(f'<td>{_use_case_value(entry[field])}</td>' for field in (
                    "score", "score_interval", "p_best", "cost_per_task",
                ))
                rows.append(f'<tr><td class="use-case-model"><code>{r.esc(entry["model"])}</code></td>'
                            f'{cells}<td><ul>{estimates}</ul></td></tr>')
            body += (f'<h3>{label}</h3><div class="use-case-table"><table><thead><tr>'
                     '<th>Model</th><th>Score</th><th>Score interval</th><th>P(best)</th>'
                     '<th>Cost per task, USD</th><th>Capability estimates and intervals</th>'
                     '</tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')
    unknown = sorted({facet for candidate in decision.get("may_qualify", [])
                      for facet in candidate["unknown"]})
    if unknown:
        body += '<h3>Unknown requirements</h3><p>Some candidates may qualify. Missing facts:</p><ul>'
        body += "".join(f'<li><code>{r.esc(facet)}</code></li>' for facet in unknown) + '</ul>'
    warnings = sorted(set(decision.get("warnings", [])) | {
        warning for result in decision["results"] for warning in result.get("warnings", [])
    })
    for heading, values in (("Engine warnings", warnings), ("Missing evidence and possible changes",
                                                           decision.get("relax", []))):
        if values:
            body += f'<h3>{heading}</h3><ul>' + "".join(
                f'<li>{r.esc(value)}</li>' for value in values
            ) + '</ul>'
    truncated = decision.get("truncated", {})
    if any(truncated.values()):
        body += (f'<p>Omitted result rows: models {_use_case_value(truncated["models"])}; '
                 f'offerings {_use_case_value(truncated["offerings"])}. '
                 'The bands above include all ranked models.</p>')
    body += (f'<p>Decision <code>{r.esc(decision["decision_id"])}</code> on public snapshot '
             f'<code>{r.esc(decision["snapshot"])}</code>.</p>'
             f'<h2>What this template teaches</h2><p>{r.esc(template["teaches"])}</p>'
             '<p>The live board uses current data. Its answer can change as evidence changes.</p>'
             f'<p><a class="button primary" href="/decide/?template={r.esc(template["id"])}">'
             'Apply this template on Decide</a></p>')
    return _use_case_shell(template["name"], template["purpose"], _use_case_path(template),
                           body, as_of, indexable=_use_case_indexable(decision), article=True)


def write_use_case_pages(tree: Path, public_root: Path) -> dict:
    """Write every template; only examples with an answer enter the sitemap."""
    catalogue, decisions, as_of = use_case_decisions(public_root)
    paths = ["/use-cases/"]
    groups = []
    for kind, label in (("use", "By use"), ("constraint", "By constraint")):
        categories = []
        for category in catalogue["categories"]:
            if category["kind"] != kind:
                continue
            links = []
            for template, decision in zip(catalogue["templates"], decisions, strict=True):
                if template["category"] != category["id"]:
                    continue
                path = _use_case_path(template)
                page = tree / path.lstrip("/") / "index.html"
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text(use_case_page(template, decision, as_of), encoding="utf-8")
                indexable = _use_case_indexable(decision)
                if indexable:
                    paths.append(path)
                note = "" if indexable else " No recommendation from this image."
                links.append(f'<li><a href="{path}">{r.esc(template["name"])}</a>: '
                             f'{r.esc(template["tradeoff"])}{note}</li>')
            categories.append(f'<h3>{r.esc(category["name"])}</h3><ul>{"".join(links)}</ul>')
        groups.append(f'<section data-kind="{kind}"><h2>{label}</h2>{"".join(categories)}</section>')
    index = tree / "use-cases/index.html"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(_use_case_shell(
        "Use-case examples", "Dated worked examples from the public Decide templates.",
        "/use-cases/", "".join(groups), as_of, indexable=True, article=False,
    ), encoding="utf-8")
    return {"sitemap_paths": paths, "sitemap_dates": {path: as_of.isoformat() for path in paths}}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    split = os.environ.get("DATA_SPLIT_ENABLED") == "true"
    data_dir = Path(args.data_dir) if args.data_dir else data_source.data_dir_from_env()
    if data_dir is None and os.environ.get(data_source.REQUIRE_DATA_ENV, "").strip() not in ("", "0"):
        print(f"build: {data_source.REQUIRE_DATA_ENV} is set but no --data-dir or "
              f"{data_source.DATA_DIR_ENV} was given; refusing to build from the public data image.",
              file=sys.stderr)
        return 2
    if split:
        if data_dir is not None:
            try:
                data_source.check_private(data_dir)
            except data_source.DataSourceError:
                print("build: private data checkout is missing or incomplete", file=sys.stderr)
                return 2
        # Public pages always render the frozen image, even on private deploys.
        args.decision_snapshot = False
        args.decision_snapshot_if_ready = False
        result = build_site(args, Path(args.root).resolve())
        if result == 0:
            from pipeline.public_data import restrict
            restrict(Path(args.out).resolve() / "modelspec")
        return result
    if data_dir is None:
        return build_site(args, Path(args.root).resolve())
    with tempfile.TemporaryDirectory(prefix="modelspec-root-") as tmp:
        try:
            composed = data_source.overlay(Path(args.root), data_dir, Path(tmp) / "root")
        except data_source.DataSourceError as exc:
            print(f"build: {exc}", file=sys.stderr)
            return 2
        saved = decision_registry.REPO_ROOT
        decision_registry.use_root(composed)
        try:
            return build_site(args, composed)
        finally:
            decision_registry.use_root(saved)


def build_day(build: exporter.Build) -> date:
    """UTC calendar day of the ``built_at`` instant. See ``exporter.build_day``."""
    return exporter.build_day(build)


def build_site(args: argparse.Namespace, root: Path) -> int:
    out = Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)

    models = load_models(root)
    benchmarks = load_benchmarks(root)
    catalogue = load_catalogue(root)
    build = exporter.make_build(catalogue, root)

    today = build_day(build)
    if catalogue.as_of > today:
        print(f"error: eligibility report is dated {catalogue.as_of}, which is in the future; "
              "refusing to publish", file=sys.stderr)
        return 2

    ms = out / "modelspec"
    bg = out / "benchgraph"
    _ship_instrument(root, ms)
    ms.mkdir(parents=True, exist_ok=True)
    bg.mkdir(parents=True, exist_ok=True)
    (bg / "_redirects").write_text(BENCHGRAPH_REDIRECTS, encoding="utf-8")

    counts = exporter.write(ms / "api", models, benchmarks, catalogue, build)

    if args.decision_snapshot:
        from decision import snapshot as decision_snapshot
        premier = Path(args.premier) if args.premier else root / "premier" / "slice-1.yaml"
        try:
            written = decision_snapshot.build_from_repo(
                root, premier=premier, as_of=today).write(ms / "api" / "decision" / "snapshot.json.gz")
            write_decision_vocabulary(root, written, key=decision_snapshot.env_key())
        except decision_snapshot.SnapshotError as exc:
            print(f"error: decision snapshot: {exc}", file=sys.stderr)
            return 2
    elif args.decision_snapshot_if_ready:
        premier = Path(args.premier) if args.premier else root / "premier" / "slice-1.yaml"
        write_decision_snapshot_if_ready(
            root,
            ms / "api" / "decision" / "snapshot.json.gz",
            premier=premier,
            as_of=today,
        )

    from pipeline import coverage as coverage_export
    coverage_payload = coverage_export.write_export(ms / "api", root=root, models=models, as_of=today)

    # The graph is derived through the same code path as the FalkorDB ingest, so
    # relations, competition, hardware fit and ranking read what the cards say.
    from pipeline import competition, hardware
    from schema.card import ModelCard
    from schema.graph import derive_graph
    cards = [ModelCard.from_yaml_file(str(m.path)) for m in models]
    devices = hardware.load_devices(root)
    # The device records are the only source of a device class, so they are
    # loaded before the derivation rather than after it (MODEL-76).
    derived = derive_graph(cards, hardware.device_classes(devices))
    competition_counts = competition.compute(derived, today)
    hardware_counts = hardware.compute(derived, cards, devices)
    model_ids = {c.identity.model_id for c in cards}
    card_ids.resolve_card_ids(
        derived, card_ids=model_ids,
        huggingface_ids=card_ids.huggingface_ids(cards),
    )
    graph_counts: dict = {
        "nodes": len(derived.nodes), "edges": len(derived.edges),
        "competition": competition_counts,
    }
    graph_counts["hardware"] = hardware_counts

    # Host profiles for offload-aware fit (MODEL-26). A new file; additive.
    from pipeline import hosts as host_layer
    graph_counts["hosts"] = host_layer.write_export(
        ms / "api", host_layer.load_hosts(root), build.to_json())

    # Per-model views of the derived graph, so a page can show what a model is
    # descended from, where it runs and what it fits on.
    from pipeline.relations import Relations
    relations = Relations(derived)
    graph_counts["relations"] = relations.counts()

    from pipeline import ranking
    ranking_counts = ranking.write_export(ms / "api" / "rank", cards, derived, build.to_json())

    # Which *class* of model a problem needs, before ranking within one
    # (MODEL-100). The whole decision rule as static data, keyless, beside
    # `profiles.json`. Called from here rather than from `ranking.write_export`
    # on purpose: the scorer must not import the class taxonomy in either
    # direction, and `tests/test_class_fit.py` walks its imports to prove it.
    from pipeline import class_export
    graph_counts["class_fit"] = class_export.write_export(
        ms / "api" / "rank", cards, build.to_json(), coverage=coverage_payload)

    # The public half of the compliance answer (MODEL-80): licence, origin,
    # commercial-use grant and per-platform availability, reshaped so
    # `POST /v1/policy-check` can read the whole catalogue in one fetch. Adds
    # no information — it republishes card fields, empty states included.
    from pipeline import policy_export
    graph_counts["policy"] = policy_export.write_export(
        ms / "api", cards, build.to_json())

    bench_by_id = {b.benchmark_id: b for b in benchmarks}
    coverage = exporter.models_by_benchmark(models, benchmarks)
    strip_assets = ms / "assets" / "benchmark-strips"
    strip_assets.mkdir(parents=True, exist_ok=True)
    for benchmark_id, rows in coverage.items():
        asset = r.benchmark_strip_asset(rows)
        if asset:
            (strip_assets / f"{benchmark_id}.svg").write_text(asset, encoding="utf-8")

    # modelspec.dev
    pages = {m.model_id for m in models}
    freshness = r.freshness_notice(models, build)
    ms_paths = ["/", "/models/", "/providers/"]
    for model in models:
        (ms / "m" / model.model_id).mkdir(parents=True, exist_ok=True)
        write_model_page(
            ms / "m" / model.model_id / "index.html",
            r.model_page(model, build, bench_by_id, catalogue,
                         relations.for_model(model.model_id), pages=pages,
                         evidence_coverage=coverage),
        )
        ms_paths.append(f"/m/{model.model_id}/")
    wizard = root / "web3d/downselect.v2.html"
    if wizard.is_file():
        _inject(wizard, ms / "downselect/index.html",
                "<!-- catalogue-freshness -->", freshness)
        page = ms / "downselect/index.html"
        page.write_text(with_site_nav(page.read_text(encoding="utf-8"), r.site_nav(r.MS_NAV),
                                      "web3d/downselect.v2.html"), encoding="utf-8")
        ms_paths.append("/downselect/")

    (ms / "models").mkdir(exist_ok=True)
    (ms / "models/index.html").write_text(r.models_index(models, build), encoding="utf-8")
    (ms / "providers").mkdir(exist_ok=True)
    (ms / "providers/index.html").write_text(r.providers_index(models, build), encoding="utf-8")
    by_provider: dict[str, list] = {}
    for model in models:
        by_provider.setdefault(model.provider, []).append(model)
    for slug, group in by_provider.items():
        (ms / "p" / slug).mkdir(parents=True, exist_ok=True)
        (ms / "p" / slug / "index.html").write_text(r.provider_page(slug, group, build), encoding="utf-8")
        ms_paths.append(f"/p/{slug}/")

    # Terms, the neutrality commitment and the privacy statement (MODEL-70), at
    # stable URLs. Adopted 2026-09-19, so they are indexable and in the sitemap;
    # while `legal.DRAFT` is true they would be `noindex` and left out of it.
    # `legal.DRAFT` is the single switch.
    from pipeline import legal
    legal_counts = legal.write(ms, root, build)
    ms_paths.extend(legal_counts["sitemap_paths"])

    from pipeline import pricing
    pricing_counts = pricing.write(ms, root, build)
    ms_paths.extend(pricing_counts["sitemap_paths"])

    # Benchmark pages sit beside /m/ and /p/. The catalogue carries the headline
    # figures the build computes, so those counts cannot drift from the cards.
    ms_paths.append("/benchmarks/")
    for bench in benchmarks:
        (ms / "b" / bench.benchmark_id).mkdir(parents=True, exist_ok=True)
        (ms / "b" / bench.benchmark_id / "index.html").write_text(
            r.benchmark_page(bench, build, catalogue, coverage.get(bench.benchmark_id, [])),
            encoding="utf-8")
        ms_paths.append(f"/b/{bench.benchmark_id}/")
    (ms / "benchmarks").mkdir(exist_ok=True)
    (ms / "benchmarks/index.html").write_text(
        r.catalogue_page(benchmarks, catalogue, build, coverage,
                         benchgraph_headline_stats(models, benchmarks, coverage)),
        encoding="utf-8")

    # Landing pages: use the designed ones when present, else a plain index.
    if _copy_static(root / "site/holding", ms):
        landing = ms / "index.html"
        from schema.card import ModelCard
        landing.write_text(wire_landing(landing.read_text(encoding="utf-8"), {
            "models": len(models),
            "providers": len(by_provider),
            "edges": graph_counts["edges"],
            "benchmarks": len(benchmarks),
            "fields": _schema_field_count(ModelCard),
        }, freshness=freshness), encoding="utf-8")
        landing.write_text(with_site_nav(landing.read_text(encoding="utf-8"),
                                         r.site_nav(r.MS_NAV),
                                         "site/holding/index.html"), encoding="utf-8")
    elif True:
        (ms / "index.html").write_text(_fallback_home(
            "ModelSpec", "ModelSpec",
            f"The open knowledge graph of AI models. {len(models)} cards, "
            f"{counts['score_keys']} benchmarks reported.",
            [("Every model", "/models/"), ("Providers", "/providers/"),
             ("Benchmark catalogue", "/benchmarks/"), ("API", "/openapi.yaml" if os.environ.get("DATA_SPLIT_ENABLED") == "true" else "/api/index.json")],
            build, r.MS_NAV, "https://modelspec.dev/"), encoding="utf-8")

    # MODEL-186 replaces the old catalogue home. The deploy workflow adds the
    # separately built decide app at /decide/ after holding derives from here.
    from pipeline import landing as landing_page
    from dataclasses import replace
    landing_data = replace(landing_page.build_data(str(root), today), coverage=coverage_payload)
    landing_page.write(ms, landing_data, variant="live")
    from pipeline import method
    method_counts = method.write(ms, root, landing_data)
    ms_paths.extend(method_counts["sitemap_paths"])
    use_case_counts = write_use_case_pages(ms, Path(args.root).resolve())
    ms_paths.extend(use_case_counts["sitemap_paths"])
    method_page = ms / "method/index.html"
    method_page.write_text(method_page.read_text(encoding="utf-8").replace(
        "</main>", '<p><a href="/use-cases/">Explore dated use-case examples</a></p></main>', 1,
    ), encoding="utf-8")
    from pipeline import orchestrators
    ms_paths.extend(orchestrators.write(ms)["sitemap_paths"])
    from pipeline import social_cards
    template_previews = social_cards.build_template_previews(Path(args.root).resolve(), today)
    social_cards.write_template_previews(ms, template_previews)
    if social_cards.render_enabled():
        social_cards.render(ms, landing_data)
        social_cards.render_template_cards(ms, template_previews)
    (ms / "decide").mkdir(exist_ok=True)
    from pipeline.live import decide_capsule
    (ms / "decide/index.html").write_text(
        '<!doctype html><html><head><meta name="robots" content="noindex">'
        '<link rel="canonical" href="https://modelspec.dev/decide/"></head>'
        f'<body>{decide_capsule()}</body></html>\n',
        encoding="utf-8",
    )
    ms_paths.append("/decide/")
    # MODEL-221. /feedback/, its assets and the published request schema.
    from pipeline import feedback_page
    feedback_counts = feedback_page.write(ms, root)
    ms_paths.extend(feedback_counts["sitemap_paths"])
    # MODEL-299. The press and brand kit: the package files, served unchanged.
    from pipeline import brand_page
    brand_counts = brand_page.write(ms)
    ms_paths.extend(brand_counts["sitemap_paths"])

    from pipeline import blog
    # Posts and retained snapshots are public repository artifacts. A data
    # overlay must never provide the source of blog content.
    blog_counts = blog.write(ms, Path(args.root).resolve(), build, today=today)
    ms_paths.extend(blog_counts["sitemap_paths"])

    (ms / "sitemap.xml").write_text(
        r.sitemap("https://modelspec.dev", ms_paths, today,
                  lastmods={**blog_counts.get("sitemap_dates", {}),
                            **use_case_counts["sitemap_dates"]}), encoding="utf-8")
    from pipeline import blog_indexnow
    blog_indexnow.write_key(ms)
    # robots.txt is written once, by agent_ready.ship below (MODEL-253).
    (ms / "404.html").write_text(
        r.not_found("ModelSpec", build, r.MS_NAV, "https://modelspec.dev/"), encoding="utf-8")
    (ms / "llms.txt").write_text(
        llms_txt(site="ModelSpec", base="https://modelspec.dev", build=build,
                 coverage=coverage_payload), encoding="utf-8")

    from pipeline import agent_ready
    agent_counts = agent_ready.ship(
        root=root, ms=ms, models=models, benchmarks=benchmarks,
        catalogue=catalogue, build=build, by_provider=by_provider)
    # Here as well as in `live.build`: the holding and live trees copy the legal
    # pages from this tree, and the deploy workflow diffs them byte for byte.
    from pipeline import structured_data
    # The Feedback control on every page, just before the JSON-LD: live.build
    # strips and re-inserts that block at the end of <head>, so the two trees
    # only match byte for byte if the control's stylesheet link comes first.
    feedback_counts["pages_with_control"] = feedback_page.inject_tree(ms)
    structured_data.inject(ms, root)

    missing = missing_internal_hrefs(ms)
    if missing:
        print(f"error: modelspec has {len(missing)} internal href(s) with no output page:",
              file=sys.stderr)
        for src, href in missing[:20]:
            print(f"  {src}: {href}", file=sys.stderr)
        if len(missing) > 20:
            print(f"  … and {len(missing) - 20} more", file=sys.stderr)
        return 2

    summary = {
        **counts,
        "graph": graph_counts,
        "ranking": ranking_counts,
        "legal": legal_counts,
        "pricing": pricing_counts,
        "commit": build.commit[:12],
        "export_schema_version": exporter.EXPORT_SCHEMA_VERSION,
        "modelspec_urls": len(ms_paths),
        "agent_ready": agent_counts,
        "feedback": feedback_counts,
        "brand": brand_counts,
        "blog": blog_counts,
        "use_cases": use_case_counts,
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
