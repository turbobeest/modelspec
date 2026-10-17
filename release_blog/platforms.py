"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one draft per platform. A person posts them.
The function has no platform client. Every number in claim text is a fact
slot. ``release_blog.slots`` binds the slot and rejects any other digit in
that text.

Instagram cards are SVG at 1080 by 1080. Each card's words are a
``SocialCard`` passed through ``pipeline.social_cards.render_card_html``,
the MODEL-195 renderer. That renderer's Playwright viewport is 1200 by 630,
and this module leaves the viewport alone.

Square-shell attributes (the 1080 canvas, coordinates, colours) are chrome.
``CHROME_TOKENS`` names them. Claim text is not matched against that set,
and geometry attributes are not scanned.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path

from pipeline.social_cards import SocialCard, render_card_html
from release_blog.model import Breakdown
from release_blog.render import charts
from release_blog.slots import (
    FilledSlot,
    Piece,
    audit,
    catalogue,
    claims_chart_slots,
    claims_chart_tokens,
    cost_chart_slots,
    cost_chart_tokens,
    html_claim_text,
    identity_strings,
    needs_unit_suffix,
    standing_chart_slots,
    standing_chart_tokens,
    svg_claim_text,
)
from release_blog.wording import difference, held_back, plan_line

AUTOMATIC_POSTING = False

_X_LIMIT = 280
_LINKEDIN_LIMIT = 3000
_FACEBOOK_LIMIT = 500
_INSTAGRAM_CAPTION_LIMIT = 2200
_REDDIT_TITLE_LIMIT = 300
_REDDIT_BODY_LIMIT = 40_000
_HN_TITLE_LIMIT = 80
_CARD = 1080
_SVG_SIZE = re.compile(r'<svg\b[^>]*\bwidth="(\d+)"[^>]*\bheight="(\d+)"')
# Posted SVG limits, read 2026-10-17. Bytes are decimal, matching the caps below.
# X bytes, 5 MB: https://docs.x.com/x-api/media/introduction
#   and https://docs.x.com/x-api/media/quickstart/best-practices
# X pixels, 8192 square: https://help.x.com/en/using-x/media-studio-faqs
# LinkedIn pixels, strictly under 36,152,320 (Images API, view=li-lms-2026-09):
#   https://learn.microsoft.com/en-us/linkedin/marketing/community-management/
#   shares/images-api
# LinkedIn bytes, 5 MB, and aspect from 3:1 to 4:5 (width:height):
#   https://www.linkedin.com/help/linkedin/answer/a526313
#   The 552 by 276 minimum is not applied. The claims chart is 680 by 248,
#   and the draft keeps that file.
# Facebook bytes, 10MB, no published pixel maximum:
#   https://developers.facebook.com/docs/graph-api/reference/page/photos/
#   The shared claims file also stays inside the X 8192 box, so one chart
#   cannot be a draft X's library refuses.
# Instagram, 8 MB, aspect 4:5 to 1.91:1, width 320 to 1440:
#   https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/
#   reference/ig-user/media
_X_IMAGE_BYTES = 5_000_000
_X_IMAGE_SIDE = 8192
_LINKEDIN_IMAGE_BYTES = 5_000_000
_LINKEDIN_MAX_PIXELS = 36_152_320
_LINKEDIN_MIN_ASPECT = 4 / 5
_LINKEDIN_MAX_ASPECT = 3 / 1
_FACEBOOK_IMAGE_BYTES = 10_000_000
_INSTAGRAM_IMAGE_BYTES = 8_000_000
_INSTAGRAM_MIN_WIDTH = 320
_INSTAGRAM_MAX_WIDTH = 1440
_INSTAGRAM_MIN_ASPECT = 4 / 5
_INSTAGRAM_MAX_ASPECT = 1.91
_DRAFT_FILES = {
    "x": "x.txt",
    "linkedin": "linkedin.txt",
    "facebook": "facebook.txt",
    "instagram": "instagram.txt",
    "reddit": "reddit.md",
    "hackernews": "hn.txt",
}
_REDDIT_RULES = (
    "Target subreddit: r/LocalLLaMA. "
    "Its Limit Self-Promotion rule requires affiliation to be disclosed, "
    "and self-promotion to stay a small share of the account's posts and comments. "
    "No engagement farming. "
    "Its low-effort rule refuses undisclosed LLM-written copy. "
    "This draft is for a person to post, and only in r/LocalLLaMA. "
    "Do not cross-post."
)
_CARD_STATES = "The card states each source URL and read date."
# Square-shell attributes only. Claim text is not matched against this set.
CHROME_TOKENS = frozenset(
    {
        "1080",
        "96",
        "40",
        "42",
        "24",
        "16",
        "6",
        "150",
        "640",
        "28",
        "46",
        "12",
        "8",
        "0B1426",
        "EEF2F7",
        "C7D1E0",
        "F2C94C",
    }
)
if CHROME_TOKENS & {"70", "67.9", "70%", "67.9%"}:
    raise ValueError("chrome allowlist contains a claim token")


@dataclass(frozen=True)
class DraftImage:
    role: str
    alt: str
    svg: str
    width: int
    height: int
    card: SocialCard | None = None

    @property
    def html(self) -> str | None:
        if self.card is None:
            return None
        return render_card_html(self.card)


@dataclass(frozen=True)
class Draft:
    platform: str
    posts: tuple[str, ...]
    images: tuple[DraftImage, ...]
    link: str
    title: str = ""
    submission: str = ""
    subreddit: str = ""
    rules: str = ""
    note: str = ""
    cross_post: bool = False
    jamie_decides: bool = False
    posted: bool = False
    manifest: tuple[FilledSlot, ...] = ()

    @property
    def text(self) -> str:
        return "\n\n".join(self.posts)


@dataclass(frozen=True)
class Block:
    text: str
    slots: tuple[FilledSlot, ...] = ()
    tokens: tuple[str, ...] = ()
    identity: tuple[str, ...] = ()


def _block(piece: Piece) -> Block:
    return Block(piece.text, tuple(piece.slots), tuple(piece.tokens), tuple(piece.identity))


def _data_block(text: str) -> Block:
    if not text:
        return Block("")
    piece = Piece("label")
    _say(piece, text)
    return _block(piece)


def _say(piece: Piece, text: str) -> None:
    if any(character.isdigit() for character in text):
        piece.data(text)
    else:
        piece.lit(text)


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _labels(breakdown: Breakdown, url: str) -> tuple[FilledSlot, ...]:
    return (
        FilledSlot("model.name", "", "", breakdown.model.name, "label"),
        FilledSlot("headline.text", "", "", breakdown.headline.text, "label"),
        FilledSlot("post.url", "", "", url, "link"),
    )


def _gap(breakdown: Breakdown):
    for row in breakdown.claims_vs_evidence.claims:
        for index, reading in enumerate(row.readings):
            change = reading.difference
            if reading.comparability == "same_setup" and change is not None and change.value != 0:
                return row, index, reading
    return None


def _hook_piece(breakdown: Breakdown) -> Piece:
    piece = Piece("hook")
    _hook_sentence(breakdown, piece)
    return piece


def _hook_sentence(breakdown: Breakdown, piece: Piece) -> None:
    found = _gap(breakdown)
    if found is None:
        _say(piece, breakdown.headline.text)
        return
    row, index, reading = found
    change = reading.difference
    assert change is not None
    book = catalogue(breakdown)
    direction = "lower" if change.value < 0 else "higher"
    _say(piece, breakdown.model.name)
    piece.lit(": on ")
    _say(piece, row.benchmark)
    piece.lit(" the lab reports ")
    piece.put(book[f"claims.{row.benchmark}.claim"])
    piece.lit(" and the independent reading is ")
    piece.put(book[f"claims.{row.benchmark}.readings[{index}].value"])
    piece.lit(", ")
    piece.put(book[f"claims.{row.benchmark}.readings[{index}].difference"])
    piece.lit(f" points {direction}.")


def _hook(breakdown: Breakdown) -> str:
    return _hook_piece(breakdown).text


def _require_hook(breakdown: Breakdown) -> Piece:
    piece = _hook_piece(breakdown)
    if _hook(breakdown) != piece.text:
        raise ValueError("hook text does not match its fact slots")
    return piece


def _domain(name: str) -> str:
    return name[:1].lower() + name[1:]


def _standing_block(breakdown: Breakdown, index: int, book: dict) -> Block:
    row = breakdown.standing[index]
    piece = Piece("standing")
    domain = _domain(row.domain.name)
    _say(piece, "In ")
    _say(piece, domain)
    if row.band == "best":
        piece.lit(", ")
        _say(piece, breakdown.model.name)
        piece.lit(" is in the leading band. The band holds ")
        piece.put(book[f"standing[{index}].band_size"])
        piece.lit(" models, and the evidence does not separate them.")
        return _block(piece)
    if row.band in ("rest", "thin") and row.rank is not None:
        if row.band == "thin":
            piece.lit(", the estimate's interval is too wide to rank on. ")
            piece.lit("The place among ")
            piece.put(book[f"standing[{index}].ranked_models"])
            piece.lit(" ranked models is ")
            piece.put(book[f"standing[{index}].rank"])
            piece.lit(".")
            return _block(piece)
        piece.lit(", ")
        _say(piece, breakdown.model.name)
        piece.lit(" is outside the leading band, at place ")
        piece.put(book[f"standing[{index}].rank"])
        piece.lit(" of ")
        piece.put(book[f"standing[{index}].ranked_models"])
        piece.lit(" ranked models.")
        return _block(piece)
    piece.lit(", ")
    _say(piece, breakdown.model.name)
    piece.lit(" has an estimate and the domain's decision does not rank it.")
    return _block(piece)


def _first_priced(breakdown: Breakdown) -> tuple[int, object] | None:
    for index, offering in enumerate(breakdown.cost.offerings):
        if offering.task.basis == "contract_default" and offering.cost_per_task is not None:
            return index, offering
    return None


def _cost_block(breakdown: Breakdown, book: dict) -> Block | None:
    found = _first_priced(breakdown)
    if found is None:
        return None
    index, _offering = found
    piece = Piece("cost")
    piece.lit("At ")
    piece.put(book[f"cost.offerings[{index}].task.input"])
    piece.lit(" input tokens and ")
    piece.put(book[f"cost.offerings[{index}].task.output"])
    piece.lit(" output tokens, the list price is ")
    piece.put(book[f"cost.offerings[{index}].cost_per_task"])
    piece.lit(" a task.")
    return _block(piece)


def _comparison_blocks(breakdown: Breakdown, book: dict) -> list[Block]:
    blocks: list[Block] = []
    for row in breakdown.claims_vs_evidence.claims:
        for index, reading in enumerate(row.readings):
            if reading.comparability == "same_setup":
                continue
            sentence = difference(reading.comparability, differs_in=reading.differs_in)
            sentence = sentence[:1].lower() + sentence[1:]
            piece = Piece("comparisons")
            piece.lit("On ")
            _say(piece, row.benchmark)
            piece.lit(", ")
            _say(piece, sentence)
            piece.lit(" The lab reports ")
            piece.put(book[f"claims.{row.benchmark}.claim"])
            piece.lit(" and the independent reading is ")
            value = book[f"claims.{row.benchmark}.readings[{index}].value"]
            piece.put(value)
            if needs_unit_suffix(reading.value.unit):
                _say(piece, " " + (reading.value.unit or "").replace("_", " "))
            piece.lit(".")
            blocks.append(_block(piece))
    return blocks


def _held_block(breakdown: Breakdown, book: dict) -> Block:
    gaps = breakdown.not_yet_measured
    piece = Piece("gaps")
    if gaps.held_back is None:
        piece.lit(held_back(None, None))
        return _block(piece)
    if not gaps.held_back:
        piece.lit(held_back({}, None))
        return _block(piece)
    piece.lit("ModelSpec holds readings of this model that have not yet passed the second key: ")
    for index, (reason, _cited) in enumerate(gaps.held_back.items()):
        if index:
            piece.lit(", ")
        _say(piece, reason.replace("_", " "))
        piece.lit(": ")
        piece.put(book[f"held_back.{reason}"])
    piece.lit(". Their values are not shown.")
    return _block(piece)


def _unreported_blocks(breakdown: Breakdown, book: dict) -> list[Block]:
    blocks = []
    for item in breakdown.claims_vs_evidence.unreported:
        piece = Piece("gaps")
        _say(piece, item.benchmark)
        piece.lit(" has an independent reading of ")
        piece.put(book[f"claims.unreported.{item.benchmark}.reading"])
        piece.lit(" and no lab figure.")
        blocks.append(_block(piece))
    return blocks


def _unread_block(breakdown: Breakdown) -> Block | None:
    names = breakdown.not_yet_measured.claims_without_reading
    if not names:
        return None
    piece = Piece("gaps")
    piece.lit("Lab figures with no independent reading yet: ")
    for index, name in enumerate(names):
        if index:
            piece.lit(", ")
        _say(piece, name)
    piece.lit(".")
    return _block(piece)


def _domains_block(breakdown: Breakdown) -> Block | None:
    names = breakdown.not_yet_measured.domains_without_estimate
    if not names:
        return None
    piece = Piece("gaps")
    piece.lit("Domains with no estimate yet: ")
    for index, name in enumerate(names):
        if index:
            piece.lit(", ")
        _say(piece, name)
    piece.lit(".")
    return _block(piece)


def _speed_block(breakdown: Breakdown) -> Block | None:
    gaps = breakdown.not_yet_measured
    if any(
        item.time_to_first_token == "unknown" and item.throughput == "unknown"
        for item in gaps.speed
    ):
        piece = Piece("gaps")
        piece.lit("Speed is not measured yet.")
        return _block(piece)
    return None


def _facets_block(breakdown: Breakdown) -> Block | None:
    rows = breakdown.not_yet_measured.unknown_facets
    if not rows:
        return None
    piece = Piece("gaps")
    piece.lit("Guaranteed facts still unknown: ")
    for index, row in enumerate(rows):
        if index:
            piece.lit(", ")
        _say(piece, row.facet)
    piece.lit(".")
    return _block(piece)


def _inapplicable_block(breakdown: Breakdown) -> Block | None:
    rows = breakdown.not_yet_measured.domains_inapplicable
    if not rows:
        return None
    piece = Piece("gaps")
    piece.lit("Domains this class cannot be measured on, so not a gap: ")
    for index, row in enumerate(rows):
        if index:
            piece.lit("; ")
        _say(piece, row.domain)
        piece.lit(", because ")
        _say(piece, row.reason)
    piece.lit(".")
    return _block(piece)


def _plan_blocks(breakdown: Breakdown) -> list[Block]:
    return [_data_block(plan_line(plan.covers, plan.plan["name"])) for plan in breakdown.cost.plans]


def _class_name(breakdown: Breakdown) -> str:
    return breakdown.model.class_.replace("-", " ")


def _intro_block(breakdown: Breakdown, *, teams: bool) -> Block:
    piece = Piece("label")
    _say(piece, breakdown.model.name)
    if teams:
        piece.lit(" is an analysis of alternatives for teams choosing a ")
    else:
        piece.lit(" is an analysis of alternatives for a ")
    _say(piece, _class_name(breakdown))
    piece.lit(".")
    return _block(piece)


def _headline_block(breakdown: Breakdown) -> Block:
    return _data_block(breakdown.headline.text)


def _within(label: str, text: str, limit: int) -> str:
    if len(text) > limit:
        raise ValueError(f"{label} is {len(text)} characters, limit {limit}")
    return text


def _join(parts: list[str]) -> str:
    return "\n\n".join(part for part in parts if part)


def _join_blocks(blocks: list[Block]) -> str:
    return _join([block.text for block in blocks])


def _fit_blocks(
    lead: list[Block], optional: list[Block], tail: list[Block], limit: int
) -> list[Block]:
    """Keep the lead and the tail. Drop optional blocks that do not fit."""
    fixed = [block for block in (*lead, *tail) if block.text]
    if len(_join_blocks(fixed)) > limit:
        raise ValueError("required draft text exceeds the platform limit")
    kept: list[Block] = []
    for block in optional:
        if not block.text:
            continue
        trial = [item for item in (*lead, *kept, block, *tail) if item.text]
        if len(_join_blocks(trial)) <= limit:
            kept.append(block)
    return [block for block in (*lead, *kept, *tail) if block.text]


def _tokens(blocks: list[Block]) -> list[str]:
    found: list[str] = []
    for block in blocks:
        found.extend(block.tokens)
    return found


def _identity(blocks: list[Block]) -> list[str]:
    found: list[str] = []
    for block in blocks:
        found.extend(block.identity)
    return found


def _slots(blocks: list[Block]) -> list[FilledSlot]:
    found: list[FilledSlot] = []
    for block in blocks:
        found.extend(block.slots)
    return found


def _citations(slots: list[FilledSlot]) -> list[str]:
    lines: list[str] = []
    seen: set[tuple[str, str]] = set()
    for slot in slots:
        if not slot.source_url:
            continue
        key = (slot.source_url, slot.read_date)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"Source: {slot.source_url} (read {slot.read_date}).")
    return lines


def _citation_blocks(lines: list[str]) -> list[Block]:
    return [_data_block(line) for line in lines]


def _disclosure_texts(breakdown: Breakdown) -> list[str]:
    return [
        text
        for text in (breakdown.disclosures.supplier, breakdown.disclosures.early_access)
        if text
    ]


def _disclosure_blocks(breakdown: Breakdown) -> list[Block]:
    return [_data_block(text) for text in _disclosure_texts(breakdown)]


def _manifest(
    breakdown: Breakdown,
    url: str,
    blocks: list[Block],
    *,
    claims: bool,
    standing: bool,
    cost: bool,
    book: dict,
) -> tuple[FilledSlot, ...]:
    slots = list(_labels(breakdown, url))
    slots.extend(_slots(blocks))
    if claims:
        slots.extend(claims_chart_slots(breakdown, book))
    if standing:
        slots.extend(standing_chart_slots(breakdown, book))
    if cost:
        slots.extend(cost_chart_slots(breakdown, book))
    return tuple(slots)


def _enforce_image_limits(platform: str, image: DraftImage) -> None:
    """Reject an image the platform's current upload rules will not accept."""
    width, height = _svg_size(image.svg)
    width = max(width, image.width)
    height = max(height, image.height)
    if width < 1 or height < 1:
        raise ValueError(f"{platform} image is {width}x{height}")
    nbytes = len(image.svg.encode("utf-8"))
    aspect = width / height
    if platform == "x":
        if width > _X_IMAGE_SIDE or height > _X_IMAGE_SIDE or nbytes > _X_IMAGE_BYTES:
            raise ValueError(f"x image is {width}x{height}, {nbytes} bytes")
        return
    if platform == "linkedin":
        pixels = width * height
        if (
            pixels >= _LINKEDIN_MAX_PIXELS
            or aspect < _LINKEDIN_MIN_ASPECT
            or aspect > _LINKEDIN_MAX_ASPECT
            or nbytes > _LINKEDIN_IMAGE_BYTES
        ):
            raise ValueError(f"linkedin image is {width}x{height}, {nbytes} bytes")
        return
    if platform == "facebook":
        if width > _X_IMAGE_SIDE or height > _X_IMAGE_SIDE or nbytes > _FACEBOOK_IMAGE_BYTES:
            raise ValueError(f"facebook image is {width}x{height}, {nbytes} bytes")
        return
    if platform == "instagram":
        if (
            width < _INSTAGRAM_MIN_WIDTH
            or width > _INSTAGRAM_MAX_WIDTH
            or aspect < _INSTAGRAM_MIN_ASPECT
            or aspect > _INSTAGRAM_MAX_ASPECT
            or nbytes > _INSTAGRAM_IMAGE_BYTES
        ):
            raise ValueError(f"instagram image is {width}x{height}, {nbytes} bytes")
        return
    raise ValueError(f"{platform} has no image limit")


def _svg_size(svg: str) -> tuple[int, int]:
    match = _SVG_SIZE.search(svg)
    if match is None:
        raise ValueError("chart svg has no width and height")
    return int(match.group(1)), int(match.group(2))


def _claims_image(svg: str, alt: str) -> DraftImage:
    width, height = _svg_size(svg)
    return DraftImage(role="claims", alt=alt, svg=svg, width=width, height=height)


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if len(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def _square(title: str, lines: list[str], chart: str | None) -> str:
    chunks: list[str] = []
    y = 150

    def add(text: str, size: int, color: str) -> None:
        nonlocal y
        chunks.append(
            f'<text x="96" y="{y}" fill="{color}" font-family="Arial,sans-serif" '
            f'font-size="{size}">{escape(text)}</text>'
        )
        y += size + 16

    add("ModelSpec", 40, "#EEF2F7")
    y += 24
    for piece in _wrap(title, 28):
        add(piece, 42, "#EEF2F7")
    y += 8
    for line in lines:
        for piece in _wrap(line, 46):
            add(piece, 24, "#C7D1E0")
        y += 6
    chart_block = ""
    if chart:
        chart_block = (
            f'<g transform="translate(40,{min(y + 12, 640)})">'
            f"<!-- chart -->{chart}<!-- /chart --></g>"
        )
    label = escape(title, quote=True)
    body = "\n".join(chunks)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" '
        f'viewBox="0 0 1080 1080" role="img" aria-label="{label}">\n'
        f'<rect width="1080" height="1080" fill="#0B1426"/>\n'
        f'<rect x="42" y="0" width="6" height="1080" fill="#F2C94C"/>\n'
        f"{body}\n{chart_block}\n</svg>\n"
    )


def _social_card(filename: str, headline: str, sentence: str) -> SocialCard:
    content = f'<p class="tie-line">{escape(sentence)}</p>' if sentence else ""
    card = SocialCard(filename=filename, alt=headline, headline=headline, content=content)
    rendered = render_card_html(card)
    if "<svg" not in rendered or "ModelSpec" not in rendered:
        raise ValueError("social card renderer returned an unexpected document")
    return card


def _square_image(
    role: str,
    alt: str,
    lines: list[str],
    chart: str | None,
    *,
    title: str,
    sentence: str,
) -> DraftImage:
    return DraftImage(
        role=role,
        alt=alt,
        svg=_square(title, lines, chart),
        width=_CARD,
        height=_CARD,
        card=_social_card(f"instagram-{role}.svg", title, sentence),
    )


def _hn_title(headline: str) -> str:
    if len(headline) <= _HN_TITLE_LIMIT:
        return headline
    main = headline.split(";", 1)[0].strip()
    if len(main) <= _HN_TITLE_LIMIT:
        return main
    cut = main[:_HN_TITLE_LIMIT]
    space = cut.rfind(" ")
    return cut[:space] if space > 0 else cut


def _with_notes(text: str, notes: list[str]) -> str:
    extra = [note for note in notes if note and note not in text]
    if not extra:
        return text
    return _join([text, *extra]) if text else _join(extra)


def _x(
    breakdown: Breakdown,
    url: str,
    image: DraftImage,
    hook: Block,
    headline: Block,
    standing: list[Block],
    cost: Block | None,
    gaps: list[Block],
    book: dict,
) -> tuple[Draft, list[str]]:
    gap_text = " ".join(block.text for block in gaps if block.text)
    cost_text = (
        cost.text if cost is not None else "ModelSpec holds no priced offering of this model."
    )
    piece = Piece("label")
    piece.lit("ModelSpec. ")
    _say(piece, breakdown.disclosures.neutrality)
    piece.lit(" " + _CARD_STATES + " ")
    _say(piece, url)
    disclosure = _block(piece)
    posts = [
        hook.text,
        headline.text,
        *(block.text for block in standing),
        cost_text,
        gap_text,
        disclosure.text,
    ]
    posts = [post for post in posts if post]
    if not 5 <= len(posts) <= 7:
        raise ValueError(f"X thread length {len(posts)}")
    for index, post in enumerate(posts):
        _within(f"X post {index}", post, _X_LIMIT)
    shown = [hook, headline, *standing]
    if cost is not None:
        shown.append(cost)
    shown.extend(gaps)
    manifest = _manifest(breakdown, url, shown, claims=True, standing=False, cost=False, book=book)
    draft = Draft(platform="x", posts=tuple(posts), images=(image,), link=url, manifest=manifest)
    return draft, _tokens(shown)


def _linkedin(
    breakdown: Breakdown,
    url: str,
    image: DraftImage,
    book: dict,
    intro: Block,
    optional: list[Block],
    cites: list[str],
) -> tuple[Draft, list[str]]:
    tail = [
        *_citation_blocks(cites),
        *_disclosure_blocks(breakdown),
        _data_block(breakdown.disclosures.neutrality),
        _data_block(url),
    ]
    kept = _fit_blocks([intro], optional, tail, _LINKEDIN_LIMIT)
    text = _within("LinkedIn", _join_blocks(kept), _LINKEDIN_LIMIT)
    manifest = _manifest(breakdown, url, kept, claims=True, standing=False, cost=False, book=book)
    draft = Draft(platform="linkedin", posts=(text,), images=(image,), link=url, manifest=manifest)
    return draft, _tokens(kept)


def _facebook(
    breakdown: Breakdown,
    url: str,
    image: DraftImage,
    hook: Block,
    headline: Block,
    book: dict,
) -> tuple[Draft, list[str]]:
    piece = Piece("label")
    piece.lit("ModelSpec.")
    parts = [
        _block(piece),
        headline,
        hook,
        _data_block(breakdown.disclosures.neutrality),
        _data_block(_CARD_STATES),
        _data_block(url),
    ]
    text = _within("Facebook", _join_blocks(parts), _FACEBOOK_LIMIT)
    manifest = _manifest(
        breakdown, url, [hook, headline], claims=True, standing=False, cost=False, book=book
    )
    draft = Draft(platform="facebook", posts=(text,), images=(image,), link=url, manifest=manifest)
    return draft, _tokens([hook])


def _instagram(
    breakdown: Breakdown,
    url: str,
    made: dict[str, str],
    standing: list[Block],
    cost: Block | None,
    gap_blocks: list[Block],
    cites: list[str],
    book: dict,
) -> tuple[Draft, list[str]]:
    standing_lines = [block.text for block in standing]
    gap_lines = [block.text for block in gap_blocks if block.text]
    notes = [*cites, *_disclosure_texts(breakdown)]
    images: list[DraftImage] = [
        _square_image(
            "headline",
            _with_notes(breakdown.headline.text, notes),
            [],
            None,
            title=breakdown.headline.text,
            sentence="",
        )
    ]
    show_standing = bool(standing_lines) and "standing.svg" in made
    show_cost = cost is not None and "cost.svg" in made
    if show_standing:
        prose = " ".join(standing_lines)
        images.append(
            _square_image(
                "standing",
                _with_notes(prose, notes),
                standing_lines,
                made["standing.svg"],
                title="Where it stands",
                sentence=prose,
            )
        )
    if show_cost and cost is not None:
        images.append(
            _square_image(
                "cost",
                _with_notes(cost.text, notes),
                [cost.text],
                made["cost.svg"],
                title="Cost per task",
                sentence=cost.text,
            )
        )
    gap_prose = " ".join(gap_lines)
    images.append(
        _square_image(
            "gaps",
            _with_notes(gap_prose, notes),
            gap_lines,
            None,
            title="Not measured yet",
            sentence=gap_prose,
        )
    )
    if not 3 <= len(images) <= 5:
        raise ValueError(f"Instagram carousel length {len(images)}")
    caption_piece = Piece("label")
    _say(caption_piece, breakdown.model.name)
    caption_piece.lit(", a release breakdown from ModelSpec.")
    caption = _block(caption_piece)
    blurb = _data_block(
        "The cards are the headline, where the model stands, the list price, "
        "and what is not measured yet. The link is in this caption. "
        "The cards do not link."
    )
    tail = [
        *_citation_blocks(cites),
        *_disclosure_blocks(breakdown),
        _data_block(breakdown.disclosures.neutrality),
        _data_block(url),
    ]
    caption_blocks = [caption, blurb, *tail]
    text = _within("Instagram caption", _join_blocks(caption_blocks), _INSTAGRAM_CAPTION_LIMIT)
    shown = [*standing, *gap_blocks]
    if show_cost and cost is not None:
        shown.append(cost)
    manifest = _manifest(
        breakdown,
        url,
        shown,
        claims=False,
        standing=show_standing,
        cost=show_cost,
        book=book,
    )
    draft = Draft(
        platform="instagram",
        posts=(text,),
        images=tuple(images),
        link=url,
        manifest=manifest,
    )
    return draft, []


def _reddit(
    breakdown: Breakdown,
    url: str,
    blocks: list[Block],
    book: dict,
) -> tuple[Draft, list[str]]:
    title = _within("Reddit title", breakdown.headline.text, _REDDIT_TITLE_LIMIT)
    body = _within("Reddit", _join_blocks(blocks), _REDDIT_BODY_LIMIT)
    manifest = _manifest(
        breakdown, url, blocks, claims=False, standing=False, cost=False, book=book
    )
    draft = Draft(
        platform="reddit",
        posts=(body,),
        images=(),
        link=url,
        title=title,
        subreddit="r/LocalLLaMA",
        rules=_REDDIT_RULES,
        cross_post=False,
        manifest=manifest,
    )
    return draft, _tokens(blocks)


def _hackernews(breakdown: Breakdown, url: str) -> Draft:
    title = _hn_title(breakdown.headline.text)
    _within("Hacker News title", title, _HN_TITLE_LIMIT)
    note = "Jamie decides whether to submit"
    extra = _disclosure_texts(breakdown)
    if extra:
        note = "\n".join([note, *extra])
    return Draft(
        platform="hackernews",
        posts=(),
        images=(),
        link=url,
        title=title,
        submission=f"{title}\n{url}",
        note=note,
        jamie_decides=True,
        manifest=_labels(breakdown, url),
    )


def _surface(draft: Draft) -> str:
    return "\n".join(
        [draft.text, draft.title, draft.submission, draft.note, draft.rules, draft.link]
    )


def _audit_draft(
    draft: Draft,
    breakdown: Breakdown,
    book: dict,
    text_tokens: list[str],
    base_identity: list[str],
    standing_tokens: list[str],
    cost_tokens: list[str],
    gap_tokens: list[str],
) -> None:
    identity = [*base_identity, *identity_strings(breakdown, draft.link)]
    audit(_surface(draft), text_tokens, identity, f"{draft.platform} text")
    for image in draft.images:
        if image.role == "claims":
            svg_expected: list[str] = claims_chart_tokens(breakdown, book)
            alt_expected: list[str] = []
            html_expected: list[str] = []
        elif image.role == "standing":
            svg_expected = [*standing_tokens, *standing_chart_tokens(breakdown, book)]
            alt_expected = list(standing_tokens)
            html_expected = list(standing_tokens)
        elif image.role == "cost":
            svg_expected = [*cost_tokens, *cost_chart_tokens(breakdown, book)]
            alt_expected = list(cost_tokens)
            html_expected = list(cost_tokens)
        elif image.role == "gaps":
            svg_expected = list(gap_tokens)
            alt_expected = list(gap_tokens)
            html_expected = list(gap_tokens)
        elif image.role == "headline":
            svg_expected = []
            alt_expected = []
            html_expected = []
        else:
            raise ValueError(f"unknown card {image.role}")
        audit(
            svg_claim_text(image.svg),
            svg_expected,
            identity,
            f"{draft.platform} {image.role} svg",
        )
        audit(image.alt, alt_expected, identity, f"{draft.platform} {image.role} alt")
        if image.html:
            audit(
                html_claim_text(image.html),
                html_expected,
                identity,
                f"{draft.platform} {image.role} html",
            )


def render_drafts(breakdown: Breakdown, *, post_url: str | None = None) -> dict[str, Draft]:
    """Six drafts for one breakdown. Nothing is posted."""
    url = post_url or _default_url(breakdown)
    hook = _block(_require_hook(breakdown))
    book = catalogue(breakdown)
    headline = _headline_block(breakdown)
    standing = [_standing_block(breakdown, index, book) for index in range(len(breakdown.standing))]
    cost = _cost_block(breakdown, book)
    comparisons = _comparison_blocks(breakdown, book)
    unread = _unread_block(breakdown)
    held = _held_block(breakdown, book)
    unreported = _unreported_blocks(breakdown, book)
    speed = _speed_block(breakdown)
    domains = _domains_block(breakdown)
    facets = _facets_block(breakdown)
    inapplicable = _inapplicable_block(breakdown)
    plans = _plan_blocks(breakdown)
    x_gaps = [block for block in (unread, held, *unreported) if block is not None]
    long_gaps = [
        block for block in (unread, held, *unreported, speed, domains) if block is not None
    ]
    made = charts(breakdown)
    story_slots = _slots(
        [
            hook,
            *standing,
            *([cost] if cost is not None else []),
            *comparisons,
            *x_gaps,
            *long_gaps,
        ]
    )
    story_slots.extend(claims_chart_slots(breakdown, book))
    if "standing.svg" in made:
        story_slots.extend(standing_chart_slots(breakdown, book))
    if cost is not None and "cost.svg" in made:
        story_slots.extend(cost_chart_slots(breakdown, book))
    cites = _citations(story_slots)
    alt = " ".join(
        [
            "Lab-reported and independent readings",
            *cites,
            *_disclosure_texts(breakdown),
        ]
    )
    image = _claims_image(made["claims.svg"], alt)
    linkedin_optional = [
        headline,
        hook,
        *standing,
        *([cost] if cost is not None else []),
        *comparisons,
        *([unread] if unread is not None else []),
        held,
        *unreported,
        *([speed] if speed is not None else []),
        *([domains] if domains is not None else []),
        *plans,
        *([facets] if facets is not None else []),
        *([inapplicable] if inapplicable is not None else []),
    ]
    reddit_blocks = [
        _data_block("This is ModelSpec."),
        _intro_block(breakdown, teams=False),
        headline,
        hook,
        *standing,
        *([cost] if cost is not None else []),
        *comparisons,
        *long_gaps,
        *([facets] if facets is not None else []),
        *([inapplicable] if inapplicable is not None else []),
        *plans,
        *_citation_blocks(cites),
        *_disclosure_blocks(breakdown),
        _data_block(breakdown.disclosures.neutrality),
        _data_block(url),
        _data_block(_REDDIT_RULES),
    ]
    x_draft, x_tokens = _x(breakdown, url, image, hook, headline, standing, cost, x_gaps, book)
    linkedin_draft, linkedin_tokens = _linkedin(
        breakdown, url, image, book, _intro_block(breakdown, teams=True), linkedin_optional, cites
    )
    facebook_draft, facebook_tokens = _facebook(breakdown, url, image, hook, headline, book)
    instagram_draft, instagram_tokens = _instagram(
        breakdown, url, made, standing, cost, long_gaps, cites, book
    )
    reddit_draft, reddit_tokens = _reddit(breakdown, url, reddit_blocks, book)
    hn_draft = _hackernews(breakdown, url)
    drafts = {
        "x": x_draft,
        "linkedin": linkedin_draft,
        "facebook": facebook_draft,
        "instagram": instagram_draft,
        "reddit": reddit_draft,
        "hackernews": hn_draft,
    }
    text_tokens = {
        "x": x_tokens,
        "linkedin": linkedin_tokens,
        "facebook": facebook_tokens,
        "instagram": instagram_tokens,
        "reddit": reddit_tokens,
        "hackernews": [],
    }
    standing_tokens = _tokens(standing)
    cost_tokens = _tokens([cost] if cost is not None else [])
    gap_tokens = _tokens(long_gaps)
    cite_identity = list(cites)
    for name, draft in drafts.items():
        _audit_draft(
            draft,
            breakdown,
            book,
            text_tokens[name],
            cite_identity,
            standing_tokens,
            cost_tokens,
            gap_tokens,
        )
    for name, draft in drafts.items():
        for picture in draft.images:
            _enforce_image_limits(name, picture)
    return drafts


def _draft_text(draft: Draft) -> str:
    if draft.platform == "reddit":
        body = f"{draft.title}\n\n{draft.text}"
    elif draft.platform == "hackernews":
        body = draft.submission
    else:
        body = draft.text
    if not body.endswith("\n"):
        body += "\n"
    return body


def generate_from_breakdown(
    *,
    breakdown_path: str | Path,
    post_url: str,
    output_dir: str | Path,
) -> dict[str, str]:
    """Write the six drafts the release hook asks for. Nothing is posted."""
    breakdown = Breakdown.model_validate_json(Path(breakdown_path).read_bytes())
    drafts = render_drafts(breakdown, post_url=post_url)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for platform, filename in _DRAFT_FILES.items():
        target = destination / filename
        target.write_text(_draft_text(drafts[platform]), encoding="utf-8")
        written[filename] = str(target)
        for image in drafts[platform].images:
            picture = destination / f"{platform}-{image.role}.svg"
            picture.write_text(image.svg, encoding="utf-8")
            written[picture.name] = str(picture)
    return written
