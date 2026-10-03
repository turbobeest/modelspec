"""The press and brand kit at /brand/ (MODEL-299).

    brand_page.write(tree)

Everything on the page is read from a source that already exists, so the page
cannot say something the package or the registry does not:

* the files: `brand/2a/` (the delivered package, `pipeline.brand.PACKAGE`), the
  social card `brand/og-card-2a.png`, and the images in `brand/social/`. Each
  is served byte for byte under `/brand/assets/`, at its path below `brand/`,
  with `shutil.copyfile`, the copy `pipeline.brand.write_icons` uses. Nothing
  is re-rendered or re-encoded.
* the words: the frozen sentence and the disambiguation from `pipeline.entity`,
  the boilerplate `pipeline.brand.POSITIONING`, and the operator's legal name
  from the published neutrality commitment (`api.ranking.engine`).
* the colours and the wordmark face: the package README's `Colors:` and
  `Wordmark:` lines, matched to the site's tokens in `landing.css`.
* the usage notes: the package README, rendered line by line, and the one
  avatar rule in `brand/social/README.md`.

`brand/social/profile-copy.md`, `profiles.json` and the social README are not
published: they hold profile text and handles, and nothing says that text is
public. Only the images go out.

`/brand/modelspec-brand-kit.zip` holds exactly the files under `/brand/assets/`,
stored (not deflated, so no zlib version can change a byte), in sorted order,
each with the same fixed timestamp and mode. Two builds of the same tree write
the same zip.
"""

from __future__ import annotations

import html
import re
import shutil
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from api.ranking.engine import neutrality_commitment
from pipeline import brand, entity, landing_chrome

ROOT = brand.ROOT
BRAND = ROOT / "brand"
SOCIAL = BRAND / "social"
PAGE_DIR = "brand"
PAGE_PATH = Path(PAGE_DIR) / "index.html"
CSS_PATH = Path(PAGE_DIR) / "brand.css"
ASSETS = Path(PAGE_DIR) / "assets"
ZIP_NAME = "modelspec-brand-kit.zip"
ZIP_PATH = Path(PAGE_DIR) / ZIP_NAME
#: Every entry in the zip sits under this folder.
ZIP_ROOT = "modelspec-brand-kit"
#: The earliest time a zip can record; any fixed value would do.
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
URL = f"{entity.SITE}/brand/"
SOURCE_URL = f"{entity.REPOSITORY}/tree/main/brand"
STYLESHEET = Path(__file__).resolve().parent / "brand_assets" / "brand.css"
LANDING_CSS = Path(__file__).resolve().parent / "landing_assets" / "landing.css"
#: Never published: profile text, handles, and the instructions for creating
#: the profiles. Only `brand/social/`'s images are.
SOCIAL_PRIVATE = ("README.md", "profile-copy.md", "profiles.json")
IMAGE_SUFFIXES = (".svg", ".png")
#: The theme rule of the decide page (web/src/decide/theme.ts): a `?theme=`
#: link, then the choice stored by /decide/, then dark. `prefers-color-scheme`
#: is not read. This page reads that key and never writes it: the privacy
#: statement names the decide page as what keeps it, so the toggle here lasts
#: for the visit only.
THEME_KEY = "modelspec-theme"


@dataclass(frozen=True)
class Asset:
    source: Path
    #: Path below `brand/`, which is also the path below `/brand/assets/`.
    rel: str
    group: str

    @property
    def href(self) -> str:
        return f"/{ASSETS.as_posix()}/{self.rel}"

    @property
    def kind(self) -> str:
        return {".svg": "SVG", ".png": "PNG", ".md": "Markdown"}[self.source.suffix]

    @property
    def size(self) -> str:
        """Pixel size, `vector`, or `text`."""
        if self.source.suffix == ".png":
            width, height = png_size(self.source.read_bytes())
            return f"{width} × {height} px"
        return "vector" if self.source.suffix == ".svg" else "text"

    @property
    def byte_count(self) -> int:
        return self.source.stat().st_size


def png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR chunk")
    return struct.unpack(">II", data[16:24])


def _png_order(path: Path) -> tuple[int, str]:
    digits = re.findall(r"\d+", path.stem)
    return (int(digits[-1]) if digits else 0, path.name)


def kit() -> tuple[Asset, ...]:
    """Every published file, in page order. The zip holds exactly these."""
    package = brand.PACKAGE
    rel = lambda path: path.relative_to(BRAND).as_posix()  # noqa: E731
    marks = [package / "modelspec-mark.svg", package / "modelspec-mark-transparent.svg"]
    lockups = sorted(package.glob("modelspec-lockup-*.svg"), reverse=True)  # light, dark
    known = {*marks, *lockups, package / "README.md"}
    rest = sorted(p for p in package.glob("*") if p.is_file() and p not in known)
    if rest:
        raise ValueError(f"brand/2a has files the page does not place: {rest}")
    pngs = sorted((package / "png").glob("*.png"), key=_png_order)
    social = sorted(p for p in SOCIAL.iterdir()
                    if p.is_file() and p.suffix in IMAGE_SUFFIXES)
    unplaced = sorted(p.name for p in SOCIAL.iterdir() if p.is_file()
                      and p.suffix not in IMAGE_SUFFIXES and p.name not in SOCIAL_PRIVATE)
    if unplaced:
        raise ValueError(f"brand/social has files neither published nor withheld: {unplaced}")
    rows = (
        *(Asset(p, rel(p), "mark") for p in marks),
        *(Asset(p, rel(p), "lockup") for p in lockups),
        *(Asset(p, rel(p), "png") for p in pngs),
        Asset(brand.SOCIAL_CARD, rel(brand.SOCIAL_CARD), "card"),
        *(Asset(p, rel(p), "social") for p in social),
        Asset(package / "README.md", rel(package / "README.md"), "readme"),
    )
    return rows


def human_bytes(count: int) -> str:
    if count < 1024:
        return f"{count} bytes"
    if count < 1024 * 1024:
        return f"{count / 1024:.1f} KB"
    return f"{count / (1024 * 1024):.1f} MB"


def zip_bytes(assets: tuple[Asset, ...]) -> bytes:
    """The kit as one zip: stored, sorted, fixed time and mode. Same input, same bytes."""
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for asset in sorted(assets, key=lambda a: a.rel):
            info = zipfile.ZipInfo(f"{ZIP_ROOT}/{asset.rel}", date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, asset.source.read_bytes())
    return buffer.getvalue()


# ── what the sources say ─────────────────────────────────────────────────────

def operator() -> str:
    """The operator's legal name, as the published neutrality commitment states it."""
    return str(neutrality_commitment()["operator"])


def readme_lines() -> list[str]:
    return (brand.PACKAGE / "README.md").read_text(encoding="utf-8").splitlines()


def _readme_field(label: str) -> str:
    for line in readme_lines():
        if line.startswith(f"{label}:"):
            return line.split(":", 1)[1].strip()
    raise ValueError(f"brand/2a/README.md has no {label}: line")


@dataclass(frozen=True)
class Colour:
    role: str
    hex: str
    note: str
    token: str | None

    @property
    def rgb(self) -> str:
        value = self.hex.lstrip("#")
        return ", ".join(str(int(value[i:i + 2], 16)) for i in (0, 2, 4))


def site_tokens() -> dict[str, str]:
    """`landing.css`'s `:root` colour tokens, by upper-case hex."""
    css = LANDING_CSS.read_text(encoding="utf-8")
    root = re.search(r":root\s*\{(.*?)\}", css, re.S)
    if not root:
        raise ValueError("landing.css has no :root block")
    return {value.upper(): name
            for name, value in re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", root.group(1))}


def palette() -> tuple[Colour, ...]:
    """The package README's `Colors:` line, one colour per `·`-separated part."""
    tokens = site_tokens()
    colours = []
    for part in _readme_field("Colors").split("·"):
        match = re.fullmatch(r"\s*(.+?)\s+(#[0-9A-Fa-f]{6})\s*(.*?)\s*", part)
        if not match:
            raise ValueError(f"brand/2a/README.md: cannot read colour {part!r}")
        role, hex_value, note = match.groups()
        colours.append(Colour(role, hex_value.upper(), note, tokens.get(hex_value.upper())))
    return tuple(colours)


def wordmark() -> str:
    return _readme_field("Wordmark")


def avatar_rule() -> str:
    """The one usage rule in brand/social/README.md: avatars are cropped to a circle."""
    text = (SOCIAL / "README.md").read_text(encoding="utf-8")
    for paragraph in re.split(r"\n\s*\n", text):
        if paragraph.startswith("The platform UI crops avatars"):
            return " ".join(paragraph.split())
    raise ValueError("brand/social/README.md no longer states the avatar rule")


def _inline(text: str) -> str:
    """Escaped text with `code` spans, the only inline Markdown the README uses."""
    parts = text.split("`")
    return "".join(f"<code>{html.escape(p, quote=False)}</code>" if i % 2
                   else html.escape(p, quote=False) for i, p in enumerate(parts))


def readme_html() -> str:
    """The package README, as delivered: its heading, list and lines, nothing added."""
    out, items = [], []
    for line in readme_lines() + [""]:
        if line.startswith("- "):
            items.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if items:
            out.append(f"<ul>{''.join(items)}</ul>")
            items = []
        if line.startswith("# "):
            out.append(f"<h3>{_inline(line[2:])}</h3>")
        elif line.strip():
            out.append(f"<p>{_inline(line)}</p>")
    return "".join(out)


# ── the page ─────────────────────────────────────────────────────────────────

GROUPS = (
    ("mark", "The mark", "The master on its navy tile, and the transparent cut for dark backgrounds."),
    ("lockup", "Lockups", "The mark with the wordmark, for light and for dark backgrounds."),
    ("png", "Mark, as PNG", "Every size in the package, from the 16 px favicon to 1024 px."),
    ("card", "Social card", "The card the site uses when a link is shared."),
    ("social", "Social profile images", "Avatars, logos and banners, each with its editable SVG source."),
)


PLATFORMS = {"x": "X", "instagram": "Instagram", "tiktok": "TikTok", "linkedin": "LinkedIn"}


def alt_text(asset: Asset) -> str:
    """A short description of the image, from its group and file name."""
    stem, kind = Path(asset.rel).stem, asset.kind
    if asset.group == "mark":
        return ("ModelSpec mark, transparent" if stem.endswith("transparent")
                else "ModelSpec mark on its navy tile")
    if asset.group == "lockup":
        return f"ModelSpec lockup, {stem.rsplit('-', 1)[-1]}"
    if asset.group == "png":
        return f"ModelSpec mark, {asset.size.removesuffix(' px')} px"
    if asset.group == "card":
        return "ModelSpec social card"
    platform, _, part = stem.partition("-")
    return f"ModelSpec {PLATFORMS.get(platform, platform)} {part}, {kind}"


def _asset_card(asset: Asset) -> str:
    name = Path(asset.rel).name
    if asset.source.suffix == ".png":
        width, height = png_size(asset.source.read_bytes())
        dims = f' width="{width}" height="{height}"'
    else:
        dims = ""
    dark = " on-dark" if name == "modelspec-mark-transparent.svg" else ""
    small = " natural" if asset.source.suffix == ".png" and png_size(asset.source.read_bytes())[0] <= 64 else ""
    return (f'<li class="asset"><a class="preview{dark}{small}" href="{asset.href}" tabindex="-1">'
            f'<img src="{asset.href}" alt="{html.escape(alt_text(asset))}"{dims}></a>'
            f'<div class="meta"><a class="name" href="{asset.href}" download><code>{html.escape(name)}</code></a>'
            f'<dl><dt>Format</dt><dd>{asset.kind}</dd><dt>Size</dt><dd>{asset.size}</dd>'
            f'<dt>File</dt><dd>{human_bytes(asset.byte_count)}</dd></dl></div></li>')


def _downloads(assets: tuple[Asset, ...], zipped: int) -> str:
    shown = sum(1 for a in assets if a.group != "readme")
    out = (f'<div class="zip"><a class="button primary" href="/{ZIP_PATH.as_posix()}" download>'
           f'Download the whole kit</a><p><code>{ZIP_NAME}</code> · {len(assets)} files · '
           f'{human_bytes(zipped)}. The {shown} files below and the package README, '
           'unchanged.</p></div>')
    for key, title, lede in GROUPS:
        cards = "".join(_asset_card(a) for a in assets if a.group == key)
        out += (f'<section class="group" id="{key}"><h3>{title}</h3><p>{lede}</p>'
                f'<ul class="assets">{cards}</ul></section>')
    return out


def _palette_html(colours: tuple[Colour, ...]) -> str:
    rows = ""
    for colour in colours:
        token = (f'<dt>Site token</dt><dd><code>{html.escape(colour.token)}</code></dd>'
                 if colour.token else "")
        note = f'<dt>Package note</dt><dd>{html.escape(colour.note)}</dd>' if colour.note else ""
        rows += (f'<li class="swatch"><span class="chip" style="background:{colour.hex}"></span>'
                 f'<div><b>{html.escape(colour.role)}</b><dl><dt>Hex</dt><dd><code>{colour.hex}</code></dd>'
                 f'<dt>RGB</dt><dd><code>{colour.rgb}</code></dd>{token}{note}</dl></div></li>')
    return f'<ul class="palette">{rows}</ul>'


def _theme_script() -> str:
    return ("<script>(function(){var d=document.documentElement,t=null;"
            "try{t=new URLSearchParams(location.search).get('theme')}catch(e){}"
            f"if(t!=='light'&&t!=='dark'){{try{{t=localStorage.getItem('{THEME_KEY}')}}catch(e){{}}}}"
            "if(t!=='light'&&t!=='dark')t='dark';d.dataset.theme=t;"
            "document.addEventListener('DOMContentLoaded',function(){"
            "var b=document.getElementById('theme-toggle');if(!b)return;b.hidden=false;"
            "var label=function(){b.textContent=d.dataset.theme==='dark'?'Light mode':'Dark mode'};label();"
            "b.addEventListener('click',function(){d.dataset.theme=d.dataset.theme==='dark'?'light':'dark';"
            "label()})})})();</script>")


def page(assets: tuple[Asset, ...], zipped: int) -> str:
    name = html.escape(entity.NAME)
    legal = html.escape(operator(), quote=False)
    sentence = html.escape(entity.ONE_SENTENCE, quote=False)
    boilerplate = html.escape(brand.POSITIONING, quote=False)
    disambiguation = html.escape(entity.DISAMBIGUATION, quote=False)
    title = f"Brand and press kit · {entity.NAME}"
    description = (f"The {entity.NAME} name, logo files, colours, boilerplate and usage notes, "
                   "for press and partners.")
    head = (f'<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><meta name="description" content="{html.escape(description)}">'
            f'<link rel="canonical" href="{URL}">{brand.head_links()}'
            f'{brand.social_meta(html.escape(title), path="/brand/")}'
            '<link rel="stylesheet" href="/landing-assets/landing.css">'
            f'<link rel="stylesheet" href="/{CSS_PATH.as_posix()}">{landing_chrome.lockup_style()}'
            f'{_theme_script()}</head>')
    header = (f'<header class="site-head">{landing_chrome.lockup()}<nav>'
              '<a href="/method/">How it decides</a><a href="/pricing/">Pricing</a>'
              '<button type="button" id="theme-toggle" class="theme-toggle" hidden>Light mode</button>'
              '<a class="button primary" href="/decide/">Open the board</a></nav></header>')
    typeface = (f'<p><b>Wordmark.</b> {_inline(wordmark())}. The lockup SVGs set it as live text '
                'in Segoe UI, so outline it before you use a lockup outside the site.</p>'
                '<p><b>On the site.</b> Text is set in Instrument Sans and code in JetBrains Mono, '
                'both self-hosted with their licences: '
                '<a href="/fonts/InstrumentSans-OFL.txt">Instrument Sans OFL</a>, '
                '<a href="/fonts/JetBrainsMono-OFL.txt">JetBrains Mono OFL</a>.</p>')
    main = (
        '<main class="brand-page">'
        f'<section class="intro"><p class="eyebrow">For press and partners</p><h1>Brand and press kit</h1>'
        f'<p>The name, the mark, the colours and the words to describe {name}. Every file here is '
        'served byte for byte from <code>brand/</code> in this repository. Take one file, or the '
        'whole kit as one zip.</p>'
        f'<p class="source">Source: <a href="{SOURCE_URL}"><code>brand/</code> in the repository</a>.</p></section>'
        '<section id="name"><h2>The name</h2>'
        f'<p class="name-rule">The name is written <b>{name}</b>.</p>'
        f'<p>{name} is operated by <b>{legal}</b>. Write the legal name with the ampersand.</p>'
        f'<p>{disambiguation}</p></section>'
        f'<section id="sentence"><h2>In one sentence</h2><blockquote class="entity">{sentence}</blockquote>'
        '<p>Quote it as written. The landing page, <a href="/method/">/method/</a>, '
        '<a href="/llms.txt">llms.txt</a> and the structured data use this sentence.</p></section>'
        f'<section id="boilerplate"><h2>Boilerplate</h2><div class="boilerplate"><p>{boilerplate}</p></div>'
        '<p>The paragraph the site gives agents in <a href="/llms.txt">llms.txt</a>.</p></section>'
        f'<section id="downloads"><h2>Downloads</h2>{_downloads(assets, zipped)}</section>'
        f'<section id="colours"><h2>Colours</h2><p>The colours of the mark, from the package README. '
        'Where the site uses the same colour, its stylesheet token is named.</p>'
        f'{_palette_html(palette())}</section>'
        f'<section id="typeface"><h2>Typeface</h2>{typeface}</section>'
        '<section id="usage"><h2>Usage</h2><p>The package README, <code>brand/2a/README.md</code>:</p>'
        f'<div class="readme">{readme_html()}</div>'
        f'<p>For the social images: {_inline(avatar_rule())}</p></section>'
        '</main>'
    )
    return (head + '<body><div class="axis" aria-hidden="true"></div>' + header + main
            + landing_chrome.footer(detail="Every file is served byte for byte from brand/ in this repository.")
            + "</body></html>\n")


def published() -> set[str]:
    """Every path `write` publishes, relative to the site root."""
    return {PAGE_PATH.as_posix(), CSS_PATH.as_posix(), ZIP_PATH.as_posix(),
            *((ASSETS / asset.rel).as_posix() for asset in kit())}


def write(tree: Path) -> dict[str, Any]:
    """Publish /brand/: the page, its stylesheet, every kit file, and the zip."""
    tree = Path(tree)
    assets = kit()
    for asset in assets:
        target = tree / ASSETS / asset.rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset.source, target)
    archive = zip_bytes(assets)
    (tree / ZIP_PATH).write_bytes(archive)
    shutil.copyfile(STYLESHEET, tree / CSS_PATH)
    (tree / PAGE_PATH).write_text(page(assets, len(archive)), encoding="utf-8")
    return {"path": "/brand/", "sitemap_paths": ["/brand/"], "files": len(assets),
            "zip_bytes": len(archive)}
