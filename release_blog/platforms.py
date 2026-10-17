"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one draft per platform. A person posts them.
The function has no platform client.

Instagram cards are SVG at 1080 by 1080. Each card's words are a
``SocialCard`` passed through ``pipeline.social_cards.render_card_html``,
the MODEL-195 renderer. That renderer's Playwright viewport is 1200 by 630,
and this module leaves the viewport alone.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

from pipeline.social_cards import SocialCard, render_card_html
from release_blog.model import Breakdown, Cited
from release_blog.render import _number, charts
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

_REDDIT_RULES = (
    "Target subreddit: r/LocalLLaMA. "
    "Its Limit Self-Promotion rule requires affiliation to be disclosed, "
    "and self-promotion to stay a small share of the account's posts and comments. "
    "No engagement farming. "
    "Its low-effort rule refuses undisclosed LLM-written copy. "
    "This draft is for a person to post, and only in r/LocalLLaMA. "
    "Do not cross-post."
)


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

    @property
    def text(self) -> str:
        return "\n\n".join(self.posts)


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _shown(cited: Cited) -> str:
    return _number(cited.value, cited.unit)


def _gap(breakdown: Breakdown):
    """The first same-setup reading whose difference is not zero."""
    for row in breakdown.claims_vs_evidence.claims:
        for reading in row.readings:
            change = reading.difference
            if reading.comparability == "same_setup" and change is not None and change.value != 0:
                return row, reading
    return None


def _hook(breakdown: Breakdown) -> str:
    found = _gap(breakdown)
    if found is None:
        return breakdown.headline.text
    row, reading = found
    change = reading.difference
    assert change is not None
    size = _number(abs(change.value), change.unit).rstrip("%")
    direction = "lower" if change.value < 0 else "higher"
    return (
        f"{breakdown.model.name}: on {row.benchmark} the lab reports {_shown(row.claim)} "
        f"and the independent reading is {_shown(reading.value)}, {size} points {direction}."
    )


def _domain(name: str) -> str:
    return name[:1].lower() + name[1:]


def _standing_line(breakdown: Breakdown, row) -> str:
    name = breakdown.model.name
    domain = _domain(row.domain.name)
    if row.band == "best":
        count = _shown(row.band_size)
        return (
            f"In {domain}, {name} is in the leading band. "
            f"The band holds {count} models, and the evidence does not separate them."
        )
    if row.band in ("rest", "thin") and row.rank is not None:
        place = _shown(row.rank)
        ranked = _shown(row.ranked_models)
        if row.band == "thin":
            return (
                f"In {domain}, the estimate's interval is too wide to rank on. "
                f"The place among {ranked} ranked models is {place}."
            )
        return (
            f"In {domain}, {name} is outside the leading band, "
            f"at place {place} of {ranked} ranked models."
        )
    return f"In {domain}, {name} has an estimate and the domain's decision does not rank it."


def _cost_line(breakdown: Breakdown) -> str | None:
    rows = [
        offering
        for offering in breakdown.cost.offerings
        if offering.task.basis == "contract_default" and offering.cost_per_task is not None
    ]
    if not rows:
        return None
    offering = rows[0]
    cost = offering.cost_per_task
    assert cost is not None
    return (
        f"At {offering.task.input:,} input tokens and {offering.task.output:,} output tokens, "
        f"the list price is {_shown(cost)} a task."
    )


def _comparisons(breakdown: Breakdown) -> list[str]:
    lines = []
    for row in breakdown.claims_vs_evidence.claims:
        for reading in row.readings:
            if reading.comparability == "same_setup":
                continue
            sentence = difference(reading.comparability, differs_in=reading.differs_in)
            sentence = sentence[:1].lower() + sentence[1:]
            lines.append(
                f"On {row.benchmark}, {sentence} The lab reports {_shown(row.claim)} "
                f"and the independent reading is {_reading(reading.value)}."
            )
    return lines


def _reading(cited: Cited) -> str:
    """A value whose unit is not already inside ``_number``."""
    shown = _shown(cited)
    if cited.unit in (None, "percent", "USD", "USD per month", "usd_per_1m_tokens", "probability"):
        return shown
    return f"{shown} {cited.unit.replace('_', ' ')}"


def _unreported(breakdown: Breakdown) -> list[str]:
    return [
        f"{item.benchmark} has an independent reading of {_shown(item.reading)} and no lab figure."
        for item in breakdown.claims_vs_evidence.unreported
    ]


def _held(breakdown: Breakdown) -> str:
    gaps = breakdown.not_yet_measured
    formatted = None
    if gaps.held_back:
        formatted = ", ".join(
            f"{reason.replace('_', ' ')}: {_shown(count)}"
            for reason, count in gaps.held_back.items()
        )
    return held_back(gaps.held_back, formatted)


def _unread(breakdown: Breakdown) -> str | None:
    names = breakdown.not_yet_measured.claims_without_reading
    if not names:
        return None
    return "Lab figures with no independent reading yet: " + ", ".join(names) + "."


def _domains(breakdown: Breakdown) -> str | None:
    names = breakdown.not_yet_measured.domains_without_estimate
    if not names:
        return None
    return "Domains with no estimate yet: " + ", ".join(names) + "."


def _speed(breakdown: Breakdown) -> str | None:
    gaps = breakdown.not_yet_measured
    if any(
        item.time_to_first_token == "unknown" and item.throughput == "unknown"
        for item in gaps.speed
    ):
        return "Speed is not measured yet."
    return None


def _facets(breakdown: Breakdown) -> str | None:
    rows = breakdown.not_yet_measured.unknown_facets
    if not rows:
        return None
    names = [row.facet for row in rows]
    return "Guaranteed facts still unknown: " + ", ".join(names) + "."


def _inapplicable(breakdown: Breakdown) -> str | None:
    rows = breakdown.not_yet_measured.domains_inapplicable
    if not rows:
        return None
    rendered = "; ".join(f"{row.domain}, because {row.reason}" for row in rows)
    return f"Domains this class cannot be measured on, so not a gap: {rendered}."


def _plans(breakdown: Breakdown) -> list[str]:
    return [plan_line(plan.covers, plan.plan["name"]) for plan in breakdown.cost.plans]


def _source_line(breakdown: Breakdown, cited: Cited) -> str | None:
    for source_id in cited.source_ids:
        url = breakdown.sources.get(source_id)
        if url and url.startswith("https://"):
            return f"Source: {url} (read {cited.read_date.isoformat()})."
    return None


def _hook_sources(breakdown: Breakdown) -> list[str]:
    found = _gap(breakdown)
    if found is None:
        return []
    row, reading = found
    lines = []
    for cited in (row.claim, reading.value):
        line = _source_line(breakdown, cited)
        if line and line not in lines:
            lines.append(line)
    return lines


def _class_name(breakdown: Breakdown) -> str:
    return breakdown.model.class_.replace("-", " ")


def _within(label: str, text: str, limit: int) -> str:
    if len(text) > limit:
        raise ValueError(f"{label} is {len(text)} characters, limit {limit}")
    return text


def _join(parts: list[str]) -> str:
    return "\n\n".join(part for part in parts if part)


def _fit(parts: list[str], limit: int) -> str:
    """Keep parts in order while the text stays inside ``limit``."""
    kept: list[str] = []
    for part in parts:
        if not part:
            continue
        trial = _join([*kept, part])
        if len(trial) <= limit:
            kept.append(part)
    if not kept:
        raise ValueError("draft has no text that fits the platform limit")
    return _join(kept)


def _svg_size(svg: str) -> tuple[int, int]:
    match = _SVG_SIZE.search(svg)
    if match is None:
        raise ValueError("chart svg has no width and height")
    return int(match.group(1)), int(match.group(2))


def _claims_image(breakdown: Breakdown) -> DraftImage:
    svg = charts(breakdown)["claims.svg"]
    width, height = _svg_size(svg)
    return DraftImage(
        role="claims",
        alt="Lab-reported and independent readings",
        svg=svg,
        width=width,
        height=height,
    )


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


def _x(breakdown: Breakdown, url: str, image: DraftImage) -> Draft:
    gaps = [
        line for line in (_unread(breakdown), _held(breakdown), *_unreported(breakdown)) if line
    ]
    disclosure = (
        f"ModelSpec. {breakdown.disclosures.neutrality} "
        f"Sources and read dates are in the breakdown. {url}"
    )
    posts = [
        _hook(breakdown),
        breakdown.headline.text,
        *(_standing_line(breakdown, row) for row in breakdown.standing),
        _cost_line(breakdown) or "ModelSpec holds no priced offering of this model.",
        " ".join(gaps),
        disclosure,
    ]
    posts = [post for post in posts if post]
    if not 5 <= len(posts) <= 7:
        raise ValueError(f"X thread length {len(posts)}")
    for index, post in enumerate(posts):
        _within(f"X post {index}", post, _X_LIMIT)
    return Draft(platform="x", posts=tuple(posts), images=(image,), link=url)


def _linkedin(breakdown: Breakdown, url: str, image: DraftImage) -> Draft:
    intro = (
        f"{breakdown.model.name} is an analysis of alternatives for teams choosing "
        f"a {_class_name(breakdown)}."
    )
    required = [
        intro,
        breakdown.headline.text,
        _hook(breakdown),
        *_hook_sources(breakdown),
        *(_standing_line(breakdown, row) for row in breakdown.standing),
        _cost_line(breakdown) or "",
        *_comparisons(breakdown),
        _unread(breakdown) or "",
        _held(breakdown),
        *_unreported(breakdown),
        _speed(breakdown) or "",
        _domains(breakdown) or "",
        *_plans(breakdown),
        breakdown.disclosures.neutrality,
        url,
    ]
    text = _fit(required, _LINKEDIN_LIMIT)
    extra = _fit([text, _facets(breakdown) or "", _inapplicable(breakdown) or ""], _LINKEDIN_LIMIT)
    # The link and the framing stay even when optional gaps are long.
    if url not in extra or "analysis of alternatives" not in extra:
        extra = text
    return Draft(
        platform="linkedin",
        posts=(_within("LinkedIn", extra, _LINKEDIN_LIMIT),),
        images=(image,),
        link=url,
    )


def _facebook(breakdown: Breakdown, url: str, image: DraftImage) -> Draft:
    text = _within(
        "Facebook",
        _join(
            [
                "ModelSpec.",
                breakdown.headline.text,
                _hook(breakdown),
                breakdown.disclosures.neutrality,
                url,
            ]
        ),
        _FACEBOOK_LIMIT,
    )
    return Draft(platform="facebook", posts=(text,), images=(image,), link=url)


def _instagram(breakdown: Breakdown, url: str) -> Draft:
    made = charts(breakdown)
    standing = [_standing_line(breakdown, row) for row in breakdown.standing]
    cost = _cost_line(breakdown)
    gap_lines = [
        line
        for line in (
            _unread(breakdown),
            _held(breakdown),
            *_unreported(breakdown),
            _speed(breakdown),
            _domains(breakdown),
        )
        if line
    ]
    images = [
        _square_image(
            "headline",
            breakdown.headline.text,
            [],
            None,
            title=breakdown.headline.text,
            sentence="",
        )
    ]
    if standing and "standing.svg" in made:
        images.append(
            _square_image(
                "standing",
                " ".join(standing),
                standing,
                made["standing.svg"],
                title="Where it stands",
                sentence=" ".join(standing),
            )
        )
    if cost and "cost.svg" in made:
        images.append(
            _square_image(
                "cost",
                cost,
                [cost],
                made["cost.svg"],
                title="Cost per task",
                sentence=cost,
            )
        )
    images.append(
        _square_image(
            "gaps",
            " ".join(gap_lines),
            gap_lines,
            None,
            title="Not measured yet",
            sentence=" ".join(gap_lines),
        )
    )
    if not 3 <= len(images) <= 5:
        raise ValueError(f"Instagram carousel length {len(images)}")
    caption = _within(
        "Instagram caption",
        _join(
            [
                f"{breakdown.model.name}, a release breakdown from ModelSpec.",
                "The cards are the headline, where the model stands, the list price, "
                "and what is not measured yet. The link is in this caption. "
                "The cards do not link.",
                breakdown.disclosures.neutrality,
                url,
            ]
        ),
        _INSTAGRAM_CAPTION_LIMIT,
    )
    return Draft(
        platform="instagram",
        posts=(caption,),
        images=tuple(images),
        link=url,
    )


def _reddit(breakdown: Breakdown, url: str) -> Draft:
    title = _within("Reddit title", breakdown.headline.text, _REDDIT_TITLE_LIMIT)
    body = _within(
        "Reddit",
        _join(
            [
                "This is ModelSpec.",
                f"{breakdown.model.name} is an analysis of alternatives for a "
                f"{_class_name(breakdown)}.",
                breakdown.headline.text,
                _hook(breakdown),
                *_hook_sources(breakdown),
                *(_standing_line(breakdown, row) for row in breakdown.standing),
                _cost_line(breakdown) or "",
                *_comparisons(breakdown),
                _unread(breakdown) or "",
                _held(breakdown),
                *_unreported(breakdown),
                _speed(breakdown) or "",
                _domains(breakdown) or "",
                _facets(breakdown) or "",
                _inapplicable(breakdown) or "",
                *_plans(breakdown),
                breakdown.disclosures.neutrality,
                url,
                _REDDIT_RULES,
            ]
        ),
        _REDDIT_BODY_LIMIT,
    )
    return Draft(
        platform="reddit",
        posts=(body,),
        images=(),
        link=url,
        title=title,
        subreddit="r/LocalLLaMA",
        rules=_REDDIT_RULES,
        cross_post=False,
    )


def _hackernews(breakdown: Breakdown, url: str) -> Draft:
    title = _hn_title(breakdown.headline.text)
    _within("Hacker News title", title, _HN_TITLE_LIMIT)
    return Draft(
        platform="hackernews",
        posts=(),
        images=(),
        link=url,
        title=title,
        submission=f"{title}\n{url}",
        note="Jamie decides whether to submit",
        jamie_decides=True,
    )


def render_drafts(breakdown: Breakdown, *, post_url: str | None = None) -> dict[str, Draft]:
    """Six drafts for one breakdown. Nothing is posted."""
    url = post_url or _default_url(breakdown)
    image = _claims_image(breakdown)
    return {
        "x": _x(breakdown, url, image),
        "linkedin": _linkedin(breakdown, url, image),
        "facebook": _facebook(breakdown, url, image),
        "instagram": _instagram(breakdown, url),
        "reddit": _reddit(breakdown, url),
        "hackernews": _hackernews(breakdown, url),
    }
