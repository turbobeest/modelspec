"""Build modelspec.dev, and the redirect tree for benchgraph.dev.

    python -m pipeline.build [--out dist]

Pages, the benchmark catalogue and the JSON export are one tree under
modelspec.dev. benchgraph.dev deploys `_redirects` only: `/` goes to the
catalogue, and every other path goes to the same path on modelspec.dev.
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

#: Cloudflare Pages redirects. `/` is the catalogue; every other path keeps
#: its path on modelspec.dev. Order matters: the first match wins.
BENCHGRAPH_REDIRECTS = (
    "/   https://modelspec.dev/benchmarks/  301\n"
    "/*  https://modelspec.dev/:splat       301\n"
)

#: Rank API and MCP live on api.modelspec.dev, not on the Pages hosts, so both
#: sites' llms.txt point at the same URLs.
API_DOCS = "https://github.com/turbobeest/modelspec/blob/main/docs/api.md"
RANK_API = "https://api.modelspec.dev/v1/rank"
MCP_ENDPOINT = "https://api.modelspec.dev/mcp"


def llms_txt(*, site: str, base: str, build: exporter.Build) -> str:
    """llms.txt for one published tree. Null on a card still means not researched."""
    return (
        f"# {site}\n\n"
        f"> {base}\n\n"
        f"Open data on AI models and benchmarks. "
        f"Built {build.built_at} from commit {build.commit[:12]}. "
        f"Null means not researched.\n\n"
        f"- Machine-readable index: {base}/api/index.json\n"
        f"- Benchmark catalogue: {base}/api/catalogue.json\n"
        f"- Rank API: {RANK_API}\n"
        f"- API docs: {API_DOCS}\n"
        f"- MCP: {MCP_ENDPOINT}\n"
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


def ship_explorer(root: Path, ms: Path, freshness: str) -> bool:
    """Write the graph explorer to /graph/ with the site nav and its vendored libraries.

    A full-viewport canvas app, so it is copied rather than rendered through the
    document shell. Its libraries are vendored so the page does not depend on a
    CDN at runtime.
    """
    explorer = root / "web3d/explorer.html"
    if not explorer.is_file():
        return False
    page = ms / "graph/index.html"
    _inject(explorer, page, "<!-- catalogue-freshness -->", freshness)
    page.write_text(with_site_nav(page.read_text(encoding="utf-8"), r.site_nav("ModelSpec", r.MS_NAV),
                                  "web3d/explorer.html"), encoding="utf-8")
    vendor = root / "web3d/vendor"
    if vendor.is_dir():
        shutil.copytree(vendor, ms / "graph/vendor", dirs_exist_ok=True)
    return True


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
            '<a class="btn" href="/graph/">Explore the graph</a>'
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


def write_decision_snapshot_if_ready(
    root: Path,
    target: Path,
    *,
    premier: Path,
    as_of: date,
) -> bool:
    """Publish only a complete, signed snapshot; warn when it is not ready."""
    from decision import snapshot as decision_snapshot

    target.unlink(missing_ok=True)
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
    except Exception as exc:  # noqa: BLE001 - the site still ships without this optional file
        target.unlink(missing_ok=True)
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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

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
    _ship_instrument(root, ms)
    ms.mkdir(parents=True, exist_ok=True)
    bg.mkdir(parents=True, exist_ok=True)
    (bg / "_redirects").write_text(BENCHGRAPH_REDIRECTS, encoding="utf-8")

    counts = exporter.write(ms / "api", models, benchmarks, catalogue, build)

    if args.decision_snapshot:
        from decision import snapshot as decision_snapshot
        premier = Path(args.premier) if args.premier else root / "premier" / "slice-1.yaml"
        try:
            decision_snapshot.build_from_repo(root, premier=premier, as_of=today).write(
                ms / "api" / "decision" / "snapshot.json.gz")
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

    # The graph is derived through the same code path as the FalkorDB ingest, so
    # the published graph and the database cannot disagree about the cards.
    from schema.card import ModelCard
    from schema.graph import derive_graph
    from pipeline import competition, hardware
    cards = [ModelCard.from_yaml_file(str(m.path)) for m in models]
    devices = hardware.load_devices(root)
    # The device records are the only source of a device class, so they are
    # loaded before the derivation rather than after it (MODEL-76).
    derived = derive_graph(cards, hardware.device_classes(devices))
    competition_counts = competition.compute(derived, today)
    hardware_counts = hardware.compute(derived, cards, devices)
    card_ids = {c.identity.model_id for c in cards}
    graph_export.resolve_card_ids(
        derived, card_ids=card_ids,
        huggingface_ids=graph_export.huggingface_ids(cards),
    )
    graph_counts = graph_export.write(
        ms / "api" / "graph", derived, build.to_json(), card_ids=card_ids)
    graph_counts["competition"] = competition_counts
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
        ms / "api" / "rank", cards, build.to_json())

    # The public half of the compliance answer (MODEL-80): licence, origin,
    # commercial-use grant and per-platform availability, reshaped so
    # `POST /v1/policy-check` can read the whole catalogue in one fetch. Adds
    # no information — it republishes card fields, empty states included.
    from pipeline import policy_export
    graph_counts["policy"] = policy_export.write_export(
        ms / "api", cards, build.to_json())

    bench_by_id = {b.benchmark_id: b for b in benchmarks}
    coverage = exporter.models_by_benchmark(models, benchmarks)

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
    wizard = root / "web3d/downselect.v2.html"
    if wizard.is_file():
        _inject(wizard, ms / "downselect/index.html",
                "<!-- catalogue-freshness -->", freshness)
        page = ms / "downselect/index.html"
        page.write_text(with_site_nav(page.read_text(encoding="utf-8"), r.site_nav("ModelSpec", r.MS_NAV),
                                      "web3d/downselect.v2.html"), encoding="utf-8")
        ms_paths.append("/downselect/")

    if ship_explorer(root, ms, freshness):
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
                                         r.site_nav("ModelSpec", r.MS_NAV),
                                         "site/holding/index.html"), encoding="utf-8")
    elif True:
        (ms / "index.html").write_text(_fallback_home(
            "ModelSpec", "ModelSpec",
            f"The open knowledge graph of AI models. {len(models)} cards, "
            f"{counts['score_keys']} benchmarks reported.",
            [("Every model", "/models/"), ("Providers", "/providers/"),
             ("Benchmark catalogue", "/benchmarks/"), ("API", "/api/index.json")],
            build, r.MS_NAV, "https://modelspec.dev/"), encoding="utf-8")

    (ms / "sitemap.xml").write_text(
        r.sitemap("https://modelspec.dev", ms_paths, today), encoding="utf-8")
    (ms / "robots.txt").write_text(
        ROBOTS.format(base="https://modelspec.dev"), encoding="utf-8")
    (ms / "404.html").write_text(
        r.not_found("ModelSpec", build, r.MS_NAV, "https://modelspec.dev/"), encoding="utf-8")
    (ms / "llms.txt").write_text(
        llms_txt(site="ModelSpec", base="https://modelspec.dev", build=build), encoding="utf-8")

    from pipeline import agent_ready
    agent_counts = agent_ready.ship(
        root=root, ms=ms, models=models, benchmarks=benchmarks,
        catalogue=catalogue, build=build, by_provider=by_provider)

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
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
