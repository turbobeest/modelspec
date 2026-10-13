"""Escape-first Markdown for release posts, including tables and source footnotes."""

from __future__ import annotations

import re
from html import escape
from urllib.parse import urlsplit

REPO = "https://github.com/turbobeest/modelspec"
_INLINE = re.compile(
    r"`([^`]+)`|!?\[([^\]]*)\]\(([^)]+)\)|<(https://[^>]+)>|"
    r"\[\^([\w-]+)\]|\*\*(.+?)\*\*|\*([^*]+)\*"
)
_NOTE = re.compile(r"^\[\^([\w-]+)\]:\s*(.*)$")


def allowed_link(url: str, sources: set[str]) -> bool:
    if "\\" in url or any(ord(char) <= 32 for char in url):
        return False
    if url.startswith("#"):
        return True
    if re.fullmatch(r"charts/[a-z-]+\.svg|breakdown\.json", url):
        return True
    if url.startswith("/") and not url.startswith("//"):
        return ".." not in url.split("/")
    parts = urlsplit(url)
    return (
        parts.scheme == "https"
        and not parts.username
        and not parts.password
        and parts.port is None
        and (
            url in sources
            or parts.netloc == "modelspec.dev"
            or (
                parts.netloc == "github.com"
                and (
                    parts.path == "/turbobeest/modelspec"
                    or parts.path.startswith("/turbobeest/modelspec/")
                )
            )
        )
    )


def inline(text: str, sources: set[str]) -> str:
    parts, end = [], 0
    for match in _INLINE.finditer(text):
        parts.append(escape(text[end : match.start()]))
        code, label, url, auto, note, strong, emphasis = match.groups()
        if code is not None:
            parts.append(f"<code>{escape(code)}</code>")
        elif url is not None or auto is not None:
            href = url or auto
            if not allowed_link(href, sources):
                raise ValueError(f"outbound link is not a breakdown source: {href}")
            if match.group().startswith("!"):
                if not re.fullmatch(r"charts/[a-z-]+\.svg", href):
                    raise ValueError("a post image must be a generated chart")
                parts.append(f'<img src="{escape(href)}" alt="{escape(label)}" loading="lazy">')
            else:
                parts.append(f'<a href="{escape(href)}">{inline(label or href, sources)}</a>')
        elif note is not None:
            label = note.removeprefix("commentary-")
            parts.append(f'<sup><a href="#fn-{note}" aria-label="Source {label}">{label}</a></sup>')
        elif strong is not None:
            parts.append(f"<strong>{inline(strong, sources)}</strong>")
        else:
            parts.append(f"<em>{inline(emphasis, sources)}</em>")
        end = match.end()
    parts.append(escape(text[end:]))
    return "".join(parts)


def render(text: str, sources: set[str]) -> str:
    """Render the generator's Markdown dialect without executing authored HTML."""
    blocks, notes, paragraph, items = [], [], [], []
    lines = text.splitlines()

    def flush() -> None:
        if paragraph:
            blocks.append(f"<p>{inline(' '.join(paragraph), sources)}</p>")
            paragraph.clear()
        if items:
            blocks.append(
                "<ul>" + "".join(f"<li>{inline(x, sources)}</li>" for x in items) + "</ul>"
            )
            items.clear()

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        note = _NOTE.match(line)
        if line.startswith("```"):
            flush()
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            blocks.append(f'<pre tabindex="0"><code>{escape(chr(10).join(code))}</code></pre>')
        elif note:
            flush()
            notes.append((note.group(1), note.group(2)))
        elif (
            line.startswith("|")
            and index + 1 < len(lines)
            and re.fullmatch(r"[| :\-]+", lines[index + 1].strip())
        ):
            flush()
            headings = line.strip("|").split("|")
            rows = []
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = lines[index].strip().strip("|").split("|")
                rows.append(
                    "<tr>"
                    + "".join(f"<td>{inline(x.strip(), sources)}</td>" for x in cells)
                    + "</tr>"
                )
                index += 1
            blocks.append(
                '<div class="blog-table" tabindex="0" role="region" '
                'aria-label="Evidence table"><table><thead><tr>'
                + "".join(f'<th scope="col">{inline(x.strip(), sources)}</th>' for x in headings)
                + "</tr></thead><tbody>"
                + "".join(rows)
                + "</tbody></table></div>"
            )
            continue
        elif line.startswith("#"):
            flush()
            level = min(len(line) - len(line.lstrip("#")), 6)
            blocks.append(f"<h{level}>{inline(line.lstrip('#').strip(), sources)}</h{level}>")
        elif line.startswith("- "):
            if paragraph:
                flush()
            items.append(line[2:])
        elif line.startswith("> "):
            flush()
            blocks.append(f"<blockquote>{inline(line[2:], sources)}</blockquote>")
        elif not line:
            flush()
        else:
            if items:
                flush()
            paragraph.append(line)
        index += 1
    flush()
    if notes:
        blocks.append(
            '<section class="blog-footnotes" aria-label="Sources"><h2>Source notes</h2><ol>'
            + "".join(f'<li id="fn-{key}">{inline(value, sources)}</li>' for key, value in notes)
            + "</ol></section>"
        )
    return "\n".join(blocks)
