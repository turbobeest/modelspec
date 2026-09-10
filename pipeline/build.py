"""Build both sites from the repository.

    python -m pipeline.build [--out dist]

Produces one tree per domain, each self-contained and deployable as static
files. The JSON export is written inside each tree under /api/, so the pages and
any consumer of the API always read the same build.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from pipeline import export as exporter
from pipeline import graph as graph_export
from pipeline import render as r
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

ROBOTS = "User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


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
    nav_old = '<a href="https://github.com/turbobeest/modelspec">GitHub</a>'
    nav_new = (
        '<a href="/graph/">Graph</a>\n'
        '      <a href="/downselect/">Downselect</a>\n'
        '      <a href="/models/">Models</a>\n'
        '      <a href="/providers/">Providers</a>\n'
        '      <a href="https://benchgraph.dev/benchmarks/">Benchmarks</a>\n'
        '      <a href="https://github.com/turbobeest/modelspec">GitHub</a>'
    )
    if nav_old in html:
        html = html.replace(nav_old, nav_new, 1)

    # A question with no way to answer it is a poster. Put the answer one click
    # away, immediately under the question the page asks.
    answer_anchor = ('<div class="a">That question, answered from evidence, '
                     'and kept current as the models change underneath you.</div>')
    if answer_anchor in html:
        html = html.replace(answer_anchor, answer_anchor + (
            '\n      <div class="go" style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap">'
            '<a href="/downselect/" style="background:#f5b342;color:#1a1200;padding:11px 20px;'
            'border-radius:9px;font-weight:700;text-decoration:none">Answer it now &rarr;</a>'
            '<a href="/graph/" style="border:1px solid #2a3140;padding:11px 20px;border-radius:9px;'
            'text-decoration:none">Explore the graph</a>'
            '<a href="/models/" style="border:1px solid #2a3140;padding:11px 20px;border-radius:9px;'
            'text-decoration:none">Browse every model</a>'
            "</div>"), 1)

    # Replace the hand-written statistics with the build's own counts.
    start = html.find('<div class="stats"')
    if start != -1:
        end = html.find("</div>", html.rfind("<div>", start, html.find("</section>", start)))
        end = html.find("</div>", end + 6)
        if end != -1:
            live = (
                f'<div class="stats" aria-label="What the graph holds today">'
                f'<div><b>{stats["models"]:,}</b>model cards</div>'
                f'<div><b>{stats["providers"]}</b>providers</div>'
                f'<div><b>{stats["edges"]:,}</b>relationships</div>'
                f'<div><b>{stats["benchmarks"]:,}</b>benchmarks</div>'
                f'<div><b>{stats["fields"]}</b>fields per card</div>'
                f"</div>"
            )
            html = html[:start] + live + html[end + 6:]
    if freshness:
        footer = html.find("<footer")
        if footer != -1:
            html = html[:footer] + freshness + html[footer:]
    return html


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="dist", help="output directory (default: dist)")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository root")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)

    models = load_models(root)
    benchmarks = load_benchmarks(root)
    catalogue = load_catalogue(root)
    build = exporter.make_build(catalogue, root)

    today = date.today()
    if catalogue.as_of > today:
        print(f"error: eligibility report is dated {catalogue.as_of}, which is in the future; "
              "refusing to publish", file=sys.stderr)
        return 2

    ms = out / "modelspec"
    bg = out / "benchgraph"
    ms.mkdir(parents=True, exist_ok=True)
    bg.mkdir(parents=True, exist_ok=True)

    counts = exporter.write(ms / "api", models, benchmarks, catalogue, build,
                            parts=("index", "models"))
    exporter.write(bg / "api", models, benchmarks, catalogue, build,
                   parts=("catalogue", "benchmarks"))

    # The graph is derived through the same code path as the FalkorDB ingest, so
    # the published graph and the database cannot disagree about the cards.
    from schema.card import ModelCard
    from schema.graph import derive_graph
    from pipeline import competition, hardware
    cards = [ModelCard.from_yaml_file(str(m.path)) for m in models]
    derived = derive_graph(cards)
    competition_counts = competition.compute(derived, today)
    hardware_counts = hardware.compute(derived, cards, hardware.load_devices(root))
    card_ids = {c.identity.model_id for c in cards}
    graph_export.resolve_card_ids(
        derived, card_ids=card_ids,
        huggingface_ids=graph_export.huggingface_ids(cards),
    )
    graph_counts = graph_export.write(
        ms / "api" / "graph", derived, build.to_json(), card_ids=card_ids)
    graph_counts["competition"] = competition_counts
    graph_counts["hardware"] = hardware_counts

    # Per-model views of the derived graph, so a page can show what a model is
    # descended from, where it runs and what it fits on.
    from pipeline.relations import Relations
    relations = Relations(derived)
    graph_counts["relations"] = relations.counts()

    from pipeline import ranking
    ranking_counts = ranking.write_export(ms / "api" / "rank", cards, derived, build.to_json())

    bench_by_id = {b.benchmark_id: b for b in benchmarks}
    coverage = exporter.models_by_benchmark(models)

    # modelspec.dev
    pages = {m.model_id for m in models}
    freshness = r.freshness_notice(models, build)
    ms_paths = ["/", "/models/", "/providers/"]
    for model in models:
        (ms / "m" / model.model_id).mkdir(parents=True, exist_ok=True)
        (ms / "m" / model.model_id / "index.html").write_text(
            r.model_page(model, build, bench_by_id, catalogue,
                         relations.for_model(model.model_id), pages=pages),
            encoding="utf-8")
        ms_paths.append(f"/m/{model.model_id}/")
    # The graph explorer: a full-viewport canvas app, so it is copied rather
    # than rendered through the document shell. Its libraries are vendored so
    # the page does not depend on a CDN at runtime.
    wizard = root / "web3d/downselect.v2.html"
    if wizard.is_file():
        _inject(wizard, ms / "downselect/index.html",
                "<!-- catalogue-freshness -->", freshness)
        ms_paths.append("/downselect/")

    explorer = root / "web3d/explorer.html"
    if explorer.is_file():
        _inject(explorer, ms / "graph/index.html",
                "<!-- catalogue-freshness -->", freshness)
        vendor = root / "web3d/vendor"
        if vendor.is_dir():
            shutil.copytree(vendor, ms / "graph/vendor", dirs_exist_ok=True)
        ms_paths.append("/graph/")

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

    # benchgraph.dev
    bg_paths = ["/", "/benchmarks/"]
    for bench in benchmarks:
        (bg / "b" / bench.benchmark_id).mkdir(parents=True, exist_ok=True)
        (bg / "b" / bench.benchmark_id / "index.html").write_text(
            r.benchmark_page(bench, build, catalogue, coverage.get(bench.benchmark_id, [])),
            encoding="utf-8")
        bg_paths.append(f"/b/{bench.benchmark_id}/")
    (bg / "benchmarks").mkdir(exist_ok=True)
    (bg / "benchmarks/index.html").write_text(
        r.catalogue_page(benchmarks, catalogue, build, coverage), encoding="utf-8")

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
    elif True:
        (ms / "index.html").write_text(_fallback_home(
            "ModelSpec", "ModelSpec",
            f"The open knowledge graph of AI models. {len(models)} cards, "
            f"{counts['score_keys']} benchmarks reported.",
            [("Every model", "/models/"), ("Providers", "/providers/"),
             ("Benchmark catalogue", "https://benchgraph.dev/benchmarks/"), ("API", "/api/index.json")],
            build, r.MS_NAV, "https://modelspec.dev/"), encoding="utf-8")
    if not _copy_static(root / "site/benchgraph", bg):
        (bg / "index.html").write_text(_fallback_home(
            "benchgraph", "benchgraph",
            f"Every AI benchmark, as a graph you can read. {len(benchmarks)} pages, "
            f"{counts['active']} in the active catalogue.",
            [("Benchmark catalogue", "/benchmarks/"), ("Models", "https://modelspec.dev/models/"),
             ("API", "/api/catalogue.json")],
            build, r.BG_NAV, "https://benchgraph.dev/"), encoding="utf-8")

    for tree, base, paths, site, nav in [
        (ms, "https://modelspec.dev", ms_paths, "ModelSpec", r.MS_NAV),
        (bg, "https://benchgraph.dev", bg_paths, "benchgraph", r.BG_NAV),
    ]:
        (tree / "sitemap.xml").write_text(r.sitemap(base, paths, today), encoding="utf-8")
        (tree / "robots.txt").write_text(ROBOTS.format(base=base), encoding="utf-8")
        (tree / "404.html").write_text(r.not_found(site, build, nav, base + "/"), encoding="utf-8")
        (tree / "llms.txt").write_text(
            f"# {site}\n\n> {base}\n\nOpen data on AI models and benchmarks. "
            f"Built {build.built_at} from commit {build.commit[:12]}.\n\n"
            f"- Machine-readable index: {base}/api/index.json\n"
            f"- Benchmark catalogue: {base}/api/catalogue.json\n"
            f"- Source: https://github.com/turbobeest/modelspec\n", encoding="utf-8")

    for tree, name in ((ms, "modelspec"), (bg, "benchgraph")):
        missing = missing_internal_hrefs(tree)
        if missing:
            print(f"error: {name} has {len(missing)} internal href(s) with no output page:",
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
        "commit": build.commit[:12],
        "export_schema_version": exporter.EXPORT_SCHEMA_VERSION,
        "modelspec_urls": len(ms_paths),
        "benchgraph_urls": len(bg_paths),
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
