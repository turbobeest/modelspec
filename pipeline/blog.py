"""Build the opt-in release blog from public, committed Markdown and breakdowns.

    python -m pipeline.blog preview <slug> --out <directory>

Normal builds include only approved published revisions and require BLOG_ENABLED=true.
Preview is explicit, noindex, and produces no feed or sitemap.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, date, datetime
from email.utils import format_datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from pipeline import blog_markdown, brand, social_cards, structured_data
from pipeline import render as r
from pipeline.export import Build
from release_blog.gates import guard_output, load_signed
from release_blog.model import Breakdown, Cited
from release_blog.render import Footnotes, _number
from release_blog.render import render as render_breakdown
from release_blog.tone import refused_words

BASE = "https://modelspec.dev"
SNAPSHOT_PATH = "/api/decision/snapshots/{snapshot_id}.json.gz"
_SLUG = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*")
_PLACEHOLDER = re.compile(r"\{\{(n|model):([^}]+)\}\}")
_CSS = """
.blog-post{max-width:900px;margin:0 auto;font-family:var(--sans);font-size:17px;line-height:1.7}
.blog-post h2{font-size:24px;letter-spacing:-.02em;text-transform:none;
color:var(--ink);margin-top:40px}
.blog-post h3{font-family:var(--sans);font-size:20px}.blog-post p{max-width:75ch}
.blog-post img{display:block;max-width:100%;height:auto;margin:24px 0}
.blog-post code{overflow-wrap:anywhere}
.blog-post pre{overflow:auto;max-width:100%;padding:16px;background:var(--surface)}
.blog-post pre code{white-space:pre-wrap}.blog-table{overflow:auto;max-width:100%;margin:24px 0}
.blog-table table{min-width:640px}
.blog-table th,.blog-table td{white-space:normal;padding:12px;vertical-align:top}
.blog-tags{display:flex;flex-wrap:wrap;gap:12px}.blog-footnotes{font-size:14px;overflow-wrap:anywhere}
.blog-corrections{border-left:3px solid var(--warn);padding-left:20px}
.blog-reproduce{overflow-wrap:anywhere}
@media(max-width:600px){.blog-post{font-size:16px}.blog-post h1{font-size:34px}
.blog-post h2{font-size:22px}}
"""


class Revision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)
    published: date | None
    approved_by: str | None
    approval: str | None


class Metadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal[1]
    model: str
    title: str
    status: Literal["draft", "published"]
    early_access: str | None = None
    revisions: list[Revision]


@dataclass(frozen=True)
class Post:
    slug: str
    metadata: Metadata
    revision: Revision
    breakdown: Breakdown
    markdown: str
    commentary: str
    charts: dict[str, str]
    corrections: list[dict]
    source: Path

    @property
    def path(self) -> str:
        return f"/blog/{self.slug}/r{self.revision.revision}/"

    @property
    def title(self) -> str:
        return prose(self.metadata.title, self.breakdown, title=True)

    @property
    def tags(self) -> list[tuple[str, str, str]]:
        b = self.breakdown
        return [
            ("lab", tag_slug(b.model.provider), b.model.provider),
            ("model", tag_slug(b.model.id), b.model.name),
            *(("domain", tag_slug(row.domain.id), row.domain.name) for row in b.standing),
        ]


def enabled() -> bool:
    return os.environ.get("BLOG_ENABLED") == "true"


def tag_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def prose(text: str, breakdown: Breakdown, *, title: bool = False) -> str:
    """Resolve human placeholders only after validating digits, tone and provenance."""
    plain = _PLACEHOLDER.sub("", text)
    if any(char.isdigit() for char in plain):
        raise ValueError("bare digit in blog title or commentary")
    if "{{" in plain or "}}" in plain:
        raise ValueError("unresolved blog pointer")
    if refused_words(text):
        raise ValueError("refused tone word in blog prose")
    notes = Footnotes(breakdown)
    body = breakdown.model_dump(mode="json", by_alias=True)

    def resolve(match):
        kind, pointer = match.groups()
        if kind == "model":
            names = {breakdown.model.id: breakdown.model.name, **breakdown.names}
            if pointer not in names:
                raise ValueError(f"unknown model pointer: {pointer}")
            return names[pointer]
        value = body
        try:
            if not pointer.startswith("/"):
                raise KeyError(pointer)
            for key in pointer[1:].split("/"):
                key = key.replace("~1", "/").replace("~0", "~")
                value = value[int(key)] if isinstance(value, list) else value[key]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise ValueError(f"unresolved blog pointer: {pointer}") from exc
        try:
            cited = Cited.model_validate(value)
        except ValueError as exc:
            raise ValueError(f"blog pointer must name a cited value: {pointer}") from exc
        if title:
            return _number(cited.value, cited.unit)
        return _number(cited.value, cited.unit) + notes.ref(cited).replace("[^", "[^commentary-")

    resolved = _PLACEHOLDER.sub(resolve, text)
    if not title and notes.notes:
        resolved += "\n\n" + notes.block().replace("[^", "[^commentary-")
    guard_output(breakdown.sources, resolved)
    return resolved


def _write(tree: Path, path: str, text: str) -> None:
    output = tree / path.lstrip("/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def _shell(title: str, body: str, path: str, build: Build, *, preview=False) -> str:
    html = r.shell(
        title=f"{title} · ModelSpec",
        description=title,
        canonical=BASE + path,
        body=body,
        build=build,
        site="ModelSpec",
        nav_links=[*r.LIVE_NAV, ("Blog", "/blog/")],
        robots="noindex, nofollow" if preview else "index, follow",
    )
    return html.replace(
        "</head>",
        f"{brand.head_links()}<style>{_CSS}</style>"
        '<link rel="alternate" type="application/atom+xml" href="/blog/feed.xml">'
        '<link rel="alternate" type="application/rss+xml" href="/blog/rss.xml">'
        "</head>",
    )


def _posts(root: Path, *, public_keys=None, preview_slug=None, today: date | None = None) -> list[Post]:
    published_through = today if today is not None else datetime.now(UTC).date()
    posts = []
    for path in sorted((root / "blog" / "posts").glob("*/post.yaml")):
        slug = path.parent.name
        if preview_slug is not None and slug != preview_slug:
            continue
        if not _SLUG.fullmatch(slug):
            raise ValueError(f"invalid blog slug: {slug}")
        metadata = Metadata.model_validate(yaml.safe_load(path.read_text()))
        if metadata.status != "published" and preview_slug is None:
            continue
        numbers = [row.revision for row in metadata.revisions]
        if len(set(numbers)) != len(numbers) or numbers != sorted(numbers):
            raise ValueError("blog revisions must be unique and ordered")
        commentary = path.parent / "commentary.md"
        corrections_file = path.parent / "corrections.yaml"
        corrections = (
            yaml.safe_load(corrections_file.read_text()) if corrections_file.exists() else []
        )
        for revision in metadata.revisions:
            if preview_slug is None:
                if revision.published is None:
                    continue
                if (
                    not revision.approved_by
                    or not revision.approval
                    or not revision.approval.startswith(blog_markdown.REPO + "/")
                ):
                    raise ValueError("published blog revision needs an approval")
                if revision.published > published_through:
                    raise ValueError("blog publication date is in the future")
            folder = path.parent / f"r{revision.revision}"
            b = Breakdown.model_validate_json((folder / "breakdown.json").read_bytes())
            if b.model.id != metadata.model or b.revision != revision.revision:
                raise ValueError("post metadata and breakdown disagree")
            first_published = metadata.revisions[0].published
            if first_published is not None and b.recheck.first_published != first_published:
                raise ValueError("regenerate the draft for its actual first publication date")
            expected, charts = render_breakdown(b)
            committed = folder / "post.md"
            if committed.read_text() != expected:
                raise ValueError("post.md differs from its reproducible breakdown rendering")
            for ref in (b.generated_from.after, b.generated_from.before):
                if ref is None:
                    continue
                if not re.fullmatch(r"snap_[0-9a-f]+", ref.snapshot_id):
                    raise ValueError("invalid snapshot ID")
                signed = load_signed(
                    root / "blog" / "snapshots" / f"{ref.snapshot_id}.json.gz",
                    public_keys=public_keys,
                )
                if (
                    signed.snapshot_id != ref.snapshot_id
                    or signed.content_hash != ref.content_hash
                    or signed.signature_key_id != ref.key_id
                ):
                    raise ValueError("blog snapshot provenance does not match")
            guard_output(b.sources, expected)
            post = Post(
                slug,
                metadata,
                revision,
                b,
                expected,
                prose(commentary.read_text(), b) if commentary.exists() else "",
                charts,
                corrections or [],
                folder,
            )
            post.title
            posts.append(post)
    return posts


def _corrections(post: Post) -> str:
    rows = []
    for correction in post.corrections:
        revision = int(correction["revision"])
        fix = correction["fix_pr"]
        if not fix.startswith(blog_markdown.REPO + "/"):
            raise ValueError("correction must link to this repository")
        effect = prose(correction["effect"], post.breakdown)
        values = json.dumps({"was": correction["was"], "now": correction["now"]}, sort_keys=True)
        rows.append(
            f'<li id="{r.esc(correction["id"])}"><time>{r.esc(correction["date"])}</time>: '
            f'<a href="/blog/{post.slug}/r{revision}/">Revision {revision}</a>. '
            f"{blog_markdown.render(effect, set(post.breakdown.sources.values()))}"
            f"<pre>{r.esc(values)}</pre>"
            f'<a href="{r.esc(fix)}">Correction review</a></li>'
        )
    return (
        (
            '<section class="blog-corrections"><h2>Corrections</h2><ul>'
            + "".join(rows)
            + "</ul></section>"
        )
        if rows
        else ""
    )


def _reproduce(post: Post) -> str:
    rows = []
    for ref in post.breakdown.decisions:
        rows.append(
            f'<details id="{r.esc(ref.decision_id)}"><summary>'
            f'<a href="#{r.esc(ref.decision_id)}">{r.esc(ref.decision_id)}</a> '
            f"{r.esc(ref.purpose)}</summary><pre><code>"
            f"{r.esc(json.dumps(ref.spec, indent=2, sort_keys=True))}</code></pre></details>"
        )
    command = "python -m release_blog render --breakdown breakdown.json --out reproduced.md"
    return (
        '<section class="blog-reproduce"><h2>Reproduce this</h2>'
        f'<p>Download <a href="{post.path}breakdown.json">breakdown.json</a> and run:</p>'
        f"<pre><code>{r.esc(command)}</code></pre>"
        "<p>The decision IDs link to the exact specs used for this revision.</p>"
        + "".join(rows)
        + "</section>"
    )


def _post_page(post: Post, revisions: list[Post], path: str, build: Build, *, preview=False) -> str:
    _, _, markdown = post.markdown.partition("\n\n")
    if not preview:
        _, _, markdown = markdown.partition("\n\n")  # the generator's draft-only introduction
    sources = set(post.breakdown.sources.values())
    history = " · ".join(
        f'<a href="{p.path}">Revision {p.revision.revision}</a>' for p in revisions
    )
    tags = "".join(
        f'<a href="/blog/tags/{kind}/{slug}/">{r.esc(label)}</a>' for kind, slug, label in post.tags
    )
    stamp = post.revision.published or post.breakdown.recheck.first_published
    modified = max([stamp, *(date.fromisoformat(str(c["date"])) for c in post.corrections)])
    body = (
        f'<article class="blog-post"><h1>{r.esc(post.title)}</h1>'
        f'<p><time datetime="{stamp}">{stamp}</time> · Revision {post.revision.revision}</p>'
        f'<p class="blog-tags">{tags}</p>{_corrections(post)}'
        f"<p>Revision history: {history}</p>"
        + blog_markdown.render(post.commentary, sources)
        + blog_markdown.render(markdown, sources)
        + _reproduce(post)
        + "</article>"
    )
    image = BASE + post.path + "og-card.png"
    nodes = [
        {
            "@type": "Article",
            "@id": BASE + path + "#article",
            "headline": post.title,
            "datePublished": stamp.isoformat(),
            "dateModified": modified.isoformat(),
            "mainEntityOfPage": BASE + path,
            "url": BASE + path,
            "image": image,
            "author": {"@type": "Organization", "name": "ModelSpec"},
            "publisher": {
                "@type": "Organization",
                "name": "ModelSpec",
                "logo": {"@type": "ImageObject", "url": BASE + "/icon-512.png"},
            },
            "keywords": [label for _, _, label in post.tags],
        }
    ]
    html = _shell(post.title, body, path, build, preview=preview)
    html = html.replace(
        'property="og:type" content="website"', 'property="og:type" content="article"'
    )
    # The document shell already owns og:title and og:url.
    meta = brand.social_meta(
        r.esc(post.title),
        path=path,
        image_name=(post.path + "og-card.png").lstrip("/"),
        image_alt=r.esc(post.title),
    )
    meta = "\n".join(
        line
        for line in meta.splitlines()
        if 'property="og:title"' not in line and 'property="og:url"' not in line
    )
    return html.replace("</head>", meta + structured_data.script(nodes) + "</head>")


def _feeds(tree: Path, posts: list[Post]) -> None:
    ns = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", ns)
    atom = ET.Element(f"{{{ns}}}feed")

    def add(parent, key, text):
        element = ET.SubElement(parent, f"{{{ns}}}{key}")
        element.text = text
        return element

    for key, text in (
        ("id", BASE + "/blog/"),
        ("title", "ModelSpec release breakdowns"),
        (
            "updated",
            max((str(p.revision.published) for p in posts), default="1970-01-01") + "T00:00:00Z",
        ),
    ):
        add(atom, key, text).text = text
    ET.SubElement(
        atom, f"{{{ns}}}link", href=BASE + "/blog/feed.xml", rel="self", type="application/atom+xml"
    )
    ET.SubElement(atom, f"{{{ns}}}link", href=BASE + "/blog/", rel="alternate")
    add(add(atom, "author", ""), "name", "ModelSpec").text = "ModelSpec"
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for key, text in (
        ("title", "ModelSpec release breakdowns"),
        ("link", BASE + "/blog/"),
        ("description", "Release evidence, costs and reproducible decisions."),
    ):
        ET.SubElement(channel, key).text = text
    events = [(p, p.path, p.revision.published, p.title) for p in posts]
    latest = {p.slug: p for p in posts}
    for post in latest.values():
        for correction in post.corrections:
            events.append(
                (
                    post,
                    f"/blog/{post.slug}/#{correction['id']}",
                    date.fromisoformat(str(correction["date"])),
                    f"Correction: {post.title}",
                )
            )
    atom.find(f"{{{ns}}}updated").text = (
        str(max((event[2] for event in events), default=date(1970, 1, 1))) + "T00:00:00Z"
    )
    for post, path, stamp, title in sorted(events, key=lambda e: (e[2], e[1]), reverse=True):
        entry = ET.SubElement(atom, f"{{{ns}}}entry")
        for key, text in (
            ("id", BASE + path),
            ("title", title),
            ("updated", str(stamp) + "T00:00:00Z"),
            ("summary", f"{post.breakdown.model.name}: evidence and decisions."),
        ):
            add(entry, key, text).text = text
        ET.SubElement(entry, f"{{{ns}}}link", href=BASE + path, rel="alternate")
        item = ET.SubElement(channel, "item")
        for key, text in (
            ("title", title),
            ("link", BASE + path),
            ("guid", BASE + path),
            ("description", f"{post.breakdown.model.name}: evidence and decisions."),
            ("pubDate", format_datetime(datetime.combine(stamp, datetime.min.time(), tzinfo=UTC))),
        ):
            ET.SubElement(item, key).text = text
    for path, element in (("/blog/feed.xml", atom), ("/blog/rss.xml", rss)):
        ET.indent(element)
        _write(tree, path, ET.tostring(element, encoding="unicode", xml_declaration=True) + "\n")


def write(tree: Path, root: Path, build: Build, *, public_keys=None, today: date | None = None) -> dict:
    # The snapshots are public committed artifacts, never read from a private data checkout.
    paths = []
    dates = {}
    source = root / "blog" / "snapshots"
    for snapshot in sorted(source.glob("snap_*.json.gz")):
        loaded = load_signed(snapshot, public_keys=public_keys)
        if snapshot.name != f"{loaded.snapshot_id}.json.gz":
            raise ValueError("retained snapshot filename disagrees with its signed ID")
        destination = tree / SNAPSHOT_PATH.format(snapshot_id=loaded.snapshot_id).lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot, destination)
    if not enabled():
        return {"posts": 0, "sitemap_paths": paths}
    posts = _posts(root, public_keys=public_keys, today=today)
    by_slug = {}
    for post in posts:
        by_slug.setdefault(post.slug, []).append(post)
        _write(
            tree,
            post.path + "index.html",
            _post_page(post, [p for p in posts if p.slug == post.slug], post.path, build),
        )
        shutil.copy2(
            post.source / "breakdown.json", tree / post.path.lstrip("/") / "breakdown.json"
        )
        for name, svg in post.charts.items():
            _write(tree, post.path + "charts/" + name, svg)
        if social_cards.render_enabled():
            card = social_cards.SocialCard(
                "og-card.png",
                post.title,
                r.esc(post.title),
                '<p class="tie-line">Release evidence, costs and reproducible decisions.</p>',
                "long",
            )
            social_cards.render_card(card, tree / post.path.lstrip("/") / "og-card.png")
        paths.append(post.path)
        dates[post.path] = post.revision.published.isoformat()
    latest = sorted(
        (rows[-1] for rows in by_slug.values()),
        key=lambda p: (p.revision.published, p.slug),
        reverse=True,
    )
    for post in latest:
        path = f"/blog/{post.slug}/"
        _write(tree, path + "index.html", _post_page(post, by_slug[post.slug], path, build))
        for name, svg in post.charts.items():
            _write(tree, path + "charts/" + name, svg)
        paths.append(path)
        dates[path] = max(
            [
                post.revision.published,
                *(date.fromisoformat(str(c["date"])) for c in post.corrections),
            ]
        ).isoformat()

    def listing(rows):
        return (
            "<ul>"
            + "".join(
                f'<li><a href="/blog/{p.slug}/">{r.esc(p.title)}</a> '
                f"<time>{p.revision.published}</time></li>"
                for p in rows
            )
            + "</ul>"
        )

    _write(
        tree,
        "/blog/index.html",
        _shell(
            "Release breakdowns",
            "<h1>Release breakdowns</h1><p>Lab figures beside independent evidence, "
            "costs and decisions you can reproduce.</p>" + listing(latest),
            "/blog/",
            build,
        ),
    )
    paths.insert(0, "/blog/")
    tags = sorted({(kind, slug, label) for post in latest for kind, slug, label in post.tags})
    for kind, slug, label in tags:
        path = f"/blog/tags/{kind}/{slug}/"
        rows = [p for p in latest if (kind, slug, label) in p.tags]
        _write(
            tree,
            path + "index.html",
            _shell(label, f"<h1>{r.esc(label)}</h1>" + listing(rows), path, build),
        )
        paths.append(path)
    standard = (root / "docs" / "method" / "release-breakdown-standard.md").read_text()
    _write(
        tree,
        "/blog/standard/index.html",
        _shell(
            "Release breakdown standard",
            "<h1>Release breakdown standard</h1>"
            + r.render_markdown_body(standard.partition("\n")[2]),
            "/blog/standard/",
            build,
        ),
    )
    paths.append("/blog/standard/")
    _feeds(tree, posts)
    newest = max(dates.values(), default=build.as_of.isoformat())
    return {
        "posts": len(latest),
        "sitemap_paths": paths,
        "sitemap_dates": {path: dates.get(path, newest) for path in paths},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["preview"])
    parser.add_argument("slug")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        posts = _posts(args.root, preview_slug=args.slug)
        if not posts:
            raise ValueError("no blog draft with that slug")
        build = Build("preview", date.today().isoformat(), date.today())
        for post in posts:
            _write(
                args.out,
                post.path + "index.html",
                _post_page(post, posts, post.path, build, preview=True),
            )
            shutil.copy2(
                post.source / "breakdown.json", args.out / post.path.lstrip("/") / "breakdown.json"
            )
            for name, svg in post.charts.items():
                _write(args.out, post.path + "charts/" + name, svg)
            for ref in (post.breakdown.generated_from.after, post.breakdown.generated_from.before):
                if ref is not None:
                    target = args.out / SNAPSHOT_PATH.format(snapshot_id=ref.snapshot_id).lstrip(
                        "/"
                    )
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(
                        args.root / "blog" / "snapshots" / f"{ref.snapshot_id}.json.gz", target
                    )
        return 0
    except (OSError, ValueError) as exc:
        print(f"blog: refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
