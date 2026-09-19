"""Publish the legal documents at stable URLs (MODEL-70).

`docs/legal/*.md` is the source. This renders each one through the site's own
Markdown renderer and document shell, so the terms look like the rest of the
site and are written in a format that reads correctly on GitHub too — one text,
two surfaces, no second copy to fall out of date.

Two things this module is careful about:

1. **A draft does not present itself as terms in force.** While `DRAFT` is true
   the pages are served `noindex, nofollow`, carry a draft banner and are kept
   out of `sitemap.xml`. The URL is stable from the first build — a caller or a
   crawler that has it keeps it. Sparks & Sawdust LLC adopted version 1.0 on
   2026-09-19, so `DRAFT` is false: the pages are indexable and in the sitemap.
   A future unadopted revision belongs on a branch, not behind this flag.
2. **The prose and the JSON say the same thing.** The honest-broker rule and the
   neutrality pledge exist once, in `api.ranking.engine`, and are asserted to
   appear verbatim in the rendered terms by `tests/test_legal.py`. The published
   commitment an agent fetches from `/api/rank/profiles.json` and the sentence a
   person reads on `/legal/terms/` cannot drift apart without a test failing.

Adopted 2026-09-19. See `docs/legal/README.md` for how, and what is still open.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pipeline import render as r

if TYPE_CHECKING:  # pragma: no cover - annotations only
    from pipeline.export import Build

#: False since 2026-09-19, when Sparks & Sawdust LLC adopted version 1.0 of all
#: three documents. True would publish them unindexed, out of the sitemap and
#: under a banner saying they bind nobody.
DRAFT = False

#: Where the documents live on modelspec.dev. `engine.LEGAL_BASE_URL` is the
#: absolute form of the same thing, and `tests/test_legal.py` keeps them equal.
LEGAL_ROOT = "legal"

_H1 = re.compile(r"^#\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True)
class LegalDoc:
    """One published legal document."""

    slug: str
    source: str
    nav_label: str
    description: str

    @property
    def url_path(self) -> str:
        return f"/{LEGAL_ROOT}/{self.slug}/"

    def absolute_url(self, base: str) -> str:
        return base.rstrip("/") + self.url_path


DOCS: tuple[LegalDoc, ...] = (
    LegalDoc(
        slug="terms",
        source="terms-of-service.md",
        nav_label="Terms",
        description=(
            "Terms of service for the ModelSpec API, operated by Sparks & Sawdust LLC. "
            "Only successful results are charged, and the subjects of a ranking are never "
            "charged at all."
        ),
    ),
    LegalDoc(
        slug="neutrality",
        source="neutrality.md",
        nav_label="Neutrality",
        description=(
            "No referral fees, no paid placement, no provider-paid visibility, permanently — "
            "published as machine-readable data beside the ranking floors so it can be checked "
            "rather than trusted."
        ),
    ),
    LegalDoc(
        slug="privacy",
        source="privacy.md",
        nav_label="Privacy",
        description=(
            "What the ModelSpec API records today, with the file behind each claim. "
            "Profiles, not prompts; nothing from a request's content is stored."
        ),
    ),
)


def source_dir(root: Path) -> Path:
    return Path(root) / "docs" / LEGAL_ROOT


def split_title(text: str) -> tuple[str, str]:
    """Take the leading `# Title` off a document, leaving the body.

    The title becomes the page `<h1>` through the shell, so leaving it in the
    body would render it twice.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        heading = _H1.match(line.strip())
        if heading:
            return heading.group(1), "\n".join(lines[index + 1:])
        break
    return "", text


def cross_links(current: LegalDoc) -> str:
    """The other two documents, so each page reaches the rest of the set."""
    others = [d for d in DOCS if d.slug != current.slug]
    links = " &middot; ".join(
        f'<a href="{r.esc(d.url_path)}">{r.esc(d.nav_label)}</a>' for d in others
    )
    return f'<p class="lede">Also: {links}</p>' if links else ""


def page(doc: LegalDoc, text: str, build: Build, base: str = "https://modelspec.dev") -> str:
    """One rendered legal page."""
    title, body = split_title(text)
    title = title or doc.nav_label
    banner = ""
    if DRAFT:
        # Said in the page's own voice, above the document, because a reader who
        # lands here from a link deserves to know before the first clause that
        # this binds nobody.
        banner = (
            '<p class="lede"><strong>Draft.</strong> This document has not been adopted '
            "and is not in force. It is published here so it can be read and reviewed "
            "before it is.</p>"
        )
    return r.shell(
        title=f"{title} — ModelSpec",
        description=doc.description,
        canonical=doc.absolute_url(base),
        body=f"<h1>{r.esc(title)}</h1>{banner}{cross_links(doc)}{r.render_markdown_body(body)}",
        build=build,
        site="ModelSpec",
        nav_links=r.MS_NAV,
        robots="noindex, nofollow" if DRAFT else "index, follow",
    )


def write(tree: Path, root: Path, build: Build,
          base: str = "https://modelspec.dev") -> dict[str, Any]:
    """Render every legal document into the site tree.

    Returns the paths written and the paths that belong in `sitemap.xml`. A
    draft is published but not advertised, so the second list is empty until
    `DRAFT` is false — the caller decides what to do with that, which keeps the
    decision in one place rather than duplicated at the call site.
    """
    src = source_dir(root)
    written: list[str] = []
    for doc in DOCS:
        path = src / doc.source
        if not path.is_file():
            raise FileNotFoundError(
                f"{path} is missing; the published legal documents are generated from "
                "docs/legal/ and a missing one would silently unpublish a page callers "
                "were told is stable"
            )
        out = Path(tree) / LEGAL_ROOT / doc.slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(doc, path.read_text(encoding="utf-8"), build, base),
                       encoding="utf-8")
        written.append(doc.url_path)
    return {
        "documents": len(written),
        "paths": written,
        "draft": DRAFT,
        "sitemap_paths": [] if DRAFT else list(written),
    }
