"""Build both sites from the repository.

    python -m pipeline.build [--out dist]

Produces one tree per domain, each self-contained and deployable as static
files. The JSON export is written inside each tree under /api/, so the pages and
any consumer of the API always read the same build.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from pipeline import export as exporter
from pipeline import graph as graph_export
from pipeline import render as r
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

ROBOTS = "User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


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
    from pipeline import competition
    cards = [ModelCard.from_yaml_file(str(m.path)) for m in models]
    derived = derive_graph(cards)
    competition_counts = competition.compute(derived, today)
    graph_counts = graph_export.write(ms / "api" / "graph", derived, build.to_json())
    graph_counts["competition"] = competition_counts

    bench_by_id = {b.benchmark_id: b for b in benchmarks}
    coverage = exporter.models_by_benchmark(models)

    # modelspec.dev
    ms_paths = ["/", "/models/", "/providers/"]
    for model in models:
        (ms / "m" / model.model_id).mkdir(parents=True, exist_ok=True)
        (ms / "m" / model.model_id / "index.html").write_text(
            r.model_page(model, build, bench_by_id, catalogue), encoding="utf-8")
        ms_paths.append(f"/m/{model.model_id}/")
    # The graph explorer: a full-viewport canvas app, so it is copied rather
    # than rendered through the document shell. Its libraries are vendored so
    # the page does not depend on a CDN at runtime.
    explorer = root / "web3d/explorer.html"
    if explorer.is_file():
        (ms / "graph").mkdir(parents=True, exist_ok=True)
        shutil.copy2(explorer, ms / "graph/index.html")
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
    if not _copy_static(root / "site/holding", ms):
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

    summary = {
        **counts,
        "graph": graph_counts,
        "commit": build.commit[:12],
        "modelspec_urls": len(ms_paths),
        "benchgraph_urls": len(bg_paths),
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
