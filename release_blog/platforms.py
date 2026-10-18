"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one text draft per platform. A person posts them.
The function has no platform client and writes no image. Instagram is a
caption: three review rounds found digits in generated cards that were not
the fact they claimed to be, so the caption says to make the image by hand.

Every draft is a manifest of digit-free literals and fact slots. After it
is rendered, the same manifest and the breakdown are rendered again and the
bytes must match. A digit that did not come from a slot fails the render.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from decision.excluded import excluded_sources
from release_blog.model import Breakdown
from release_blog.slots import (
    Fact,
    Literal,
    Piece,
    Slot,
    assemble,
    bind,
    catalogue,
    needs_unit_suffix,
    piece_text,
)
from release_blog.tone import refused_words

AUTOMATIC_POSTING = False

_X_LIMIT = 280
_LINKEDIN_LIMIT = 3000
_FACEBOOK_LIMIT = 500
_INSTAGRAM_CAPTION_LIMIT = 2200
_REDDIT_TITLE_LIMIT = 300
_REDDIT_BODY_LIMIT = 40_000
_HN_TITLE_LIMIT = 80
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
_HAND = "Make the image by hand."
_JAMIE = "Jamie decides whether to submit."
_PROSE_FIELDS = (
    ("headline.text", "headline"),
    ("disclosures.supplier", "supplier"),
    ("disclosures.early_access", "early_access"),
    ("disclosures.neutrality", "neutrality"),
)


@dataclass(frozen=True)
class Draft:
    platform: str
    posts: tuple[str, ...]
    link: str
    output: str
    manifest: tuple[Piece, ...]
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
        if self.posts:
            return "\n\n".join(self.posts)
        return self.submission


def _emit(pieces: Sequence[Piece], breakdown: Breakdown, post_url: str) -> str:
    return assemble(pieces, breakdown, post_url)


def _prove(pieces: Sequence[Piece], breakdown: Breakdown, post_url: str) -> str:
    output = _emit(pieces, breakdown, post_url)
    bind(output, pieces, breakdown, post_url)
    return output


def _require_digit_free(breakdown: Breakdown) -> None:
    values = {
        "headline": breakdown.headline.text,
        "supplier": breakdown.disclosures.supplier,
        "early_access": breakdown.disclosures.early_access,
        "neutrality": breakdown.disclosures.neutrality,
    }
    for label, key in _PROSE_FIELDS:
        text = values[key]
        if text and any(character.isdigit() for character in text):
            raise ValueError(f"{label} contains a digit")


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _render(pieces: Sequence[Piece], book: dict[str, Fact]) -> str:
    return "".join(piece_text(piece, book) for piece in pieces)


def _flatten(blocks: Sequence[Sequence[Piece]], sep: str = "\n\n") -> list[Piece]:
    pieces: list[Piece] = []
    for block in blocks:
        if not block:
            continue
        if pieces:
            pieces.append(Literal(sep))
        pieces.extend(block)
    return pieces


def _citation_lines(pieces: Sequence[Piece], book: dict[str, Fact]) -> list[list[Piece]]:
    lines: list[list[Piece]] = []
    seen: set[tuple[str, str]] = set()
    for piece in pieces:
        if not isinstance(piece, Slot) or piece.formatter != "value":
            continue
        fact = book[piece.fact_id]
        if not fact.source_url:
            continue
        key = (fact.source_url, fact.read_date)
        if key in seen:
            continue
        seen.add(key)
        lines.append(
            [
                Literal("Source: "),
                Slot(piece.fact_id, "source_url"),
                Literal(" (read "),
                Slot(piece.fact_id, "read_date"),
                Literal(")."),
            ]
        )
    return lines


def _cite_block(pieces: Sequence[Piece], book: dict[str, Fact]) -> list[Piece]:
    block: list[Piece] = []
    for line in _citation_lines(pieces, book):
        if block:
            block.append(Literal("\n"))
        block.extend(line)
    return block


def _compose(
    lead: Sequence[Sequence[Piece]],
    middle: Sequence[Sequence[Piece]],
    tail: Sequence[Sequence[Piece]],
    book: dict[str, Fact],
) -> list[Piece]:
    story = _flatten([*lead, *middle])
    cites = _cite_block(story, book)
    blocks: list[Sequence[Piece]] = [*lead, *middle]
    if cites:
        blocks.append(cites)
    blocks.extend(tail)
    return _flatten(blocks)


def _fit(
    lead: Sequence[Sequence[Piece]],
    optional: Sequence[Sequence[Piece]],
    tail: Sequence[Sequence[Piece]],
    book: dict[str, Fact],
    limit: int,
) -> list[Piece]:
    kept: list[Sequence[Piece]] = []
    for block in optional:
        if not block:
            continue
        trial = _compose(lead, [*kept, block], tail, book)
        if len(_render(trial, book)) > limit:
            break
        kept.append(block)
    pieces = _compose(lead, kept, tail, book)
    size = len(_render(pieces, book))
    if size > limit:
        raise ValueError(f"required draft text is {size} characters, limit {limit}")
    return pieces


def _file(body: Sequence[Piece]) -> list[Piece]:
    return [*body, Literal("\n")]


def _within(label: str, text: str, limit: int) -> str:
    if len(text) > limit:
        raise ValueError(f"{label} is {len(text)} characters, limit {limit}")
    return text


def _gap(breakdown: Breakdown):
    for row in breakdown.claims_vs_evidence.claims:
        for index, reading in enumerate(row.readings):
            change = reading.difference
            if reading.comparability == "same_setup" and change is not None and change.value != 0:
                return row, index, reading
    return None


def _hook_pieces(breakdown: Breakdown) -> list[Piece]:
    found = _gap(breakdown)
    if found is None:
        return [Literal(breakdown.headline.text)]
    row, index, reading = found
    change = reading.difference
    assert change is not None
    direction = "lower" if change.value < 0 else "higher"
    return [
        Slot("model.name"),
        Literal(": on "),
        Slot(f"label.benchmark.{row.benchmark}"),
        Literal(" the lab reports "),
        Slot(f"claims.{row.benchmark}.claim"),
        Literal(" and the independent reading is "),
        Slot(f"claims.{row.benchmark}.readings[{index}].value"),
        Literal(", "),
        Slot(f"claims.{row.benchmark}.readings[{index}].difference"),
        Literal(f" points {direction}."),
    ]


def _short_hook(breakdown: Breakdown) -> list[Piece]:
    """The two readings, without the model version or the point gap.

    Facebook's post limit cannot also hold the snapshot URL those two would
    pull in, and the longer drafts carry both.
    """
    found = _gap(breakdown)
    if found is None:
        return [Literal(breakdown.headline.text)]
    row, index, _reading = found
    return [
        Literal("On "),
        Slot(f"label.benchmark.{row.benchmark}"),
        Literal(" the lab reports "),
        Slot(f"claims.{row.benchmark}.claim"),
        Literal(" and the independent reading is "),
        Slot(f"claims.{row.benchmark}.readings[{index}].value"),
        Literal("."),
    ]


def _standing_pieces(breakdown: Breakdown, index: int) -> list[Piece]:
    row = breakdown.standing[index]
    lead = [Literal("In "), Slot(f"label.standing[{index}].domain")]
    if row.band == "best":
        return [
            *lead,
            Literal(", "),
            Slot("model.name"),
            Literal(" is in the leading band. The band holds "),
            Slot(f"standing[{index}].band_size"),
            Literal(" models, and the evidence does not separate them."),
        ]
    if row.band in ("rest", "thin") and row.rank is not None:
        if row.band == "thin":
            return [
                *lead,
                Literal(", the estimate's interval is too wide to rank on. The place among "),
                Slot(f"standing[{index}].ranked_models"),
                Literal(" ranked models is "),
                Slot(f"standing[{index}].rank"),
                Literal("."),
            ]
        return [
            *lead,
            Literal(", "),
            Slot("model.name"),
            Literal(" is outside the leading band, at place "),
            Slot(f"standing[{index}].rank"),
            Literal(" of "),
            Slot(f"standing[{index}].ranked_models"),
            Literal(" ranked models."),
        ]
    return [
        *lead,
        Literal(", "),
        Slot("model.name"),
        Literal(" has an estimate and the domain's decision does not rank it."),
    ]


def _first_priced(breakdown: Breakdown) -> int | None:
    for index, offering in enumerate(breakdown.cost.offerings):
        if offering.task.basis == "contract_default" and offering.cost_per_task is not None:
            return index
    return None


def _cost_pieces(breakdown: Breakdown) -> list[Piece] | None:
    index = _first_priced(breakdown)
    if index is None:
        return None
    return [
        Literal("At "),
        Slot(f"cost.offerings[{index}].task.input"),
        Literal(" input tokens and "),
        Slot(f"cost.offerings[{index}].task.output"),
        Literal(" output tokens, the list price is "),
        Slot(f"cost.offerings[{index}].cost_per_task"),
        Literal(" a task."),
    ]


def _comparison_pieces(breakdown: Breakdown) -> list[list[Piece]]:
    blocks: list[list[Piece]] = []
    for row in breakdown.claims_vs_evidence.claims:
        for index, reading in enumerate(row.readings):
            if reading.comparability == "same_setup":
                continue
            pieces: list[Piece] = [
                Literal("On "),
                Slot(f"label.benchmark.{row.benchmark}"),
                Literal(", "),
                Slot(f"label.relation.{row.benchmark}[{index}]"),
                Literal(" The lab reports "),
                Slot(f"claims.{row.benchmark}.claim"),
                Literal(" and the independent reading is "),
                Slot(f"claims.{row.benchmark}.readings[{index}].value"),
            ]
            if needs_unit_suffix(reading.value.unit):
                pieces.append(Slot(f"label.unit.{row.benchmark}[{index}]"))
            pieces.append(Literal("."))
            blocks.append(pieces)
    return blocks


def _held_pieces(breakdown: Breakdown) -> list[Piece]:
    gaps = breakdown.not_yet_measured
    if gaps.held_back is None:
        return [
            Literal(
                "This snapshot predates per-model held-back counts, so the number of this "
                "model's readings awaiting a second key is not available."
            )
        ]
    if not gaps.held_back:
        return [
            Literal("ModelSpec holds no reading of this model that is waiting for a second key.")
        ]
    pieces = [
        Literal("ModelSpec holds readings of this model that have not yet passed the second key: ")
    ]
    for index, reason in enumerate(gaps.held_back):
        if index:
            pieces.append(Literal(", "))
        pieces.append(Slot(f"label.held.{reason}"))
        pieces.append(Literal(": "))
        pieces.append(Slot(f"held_back.{reason}"))
    pieces.append(Literal(". Their values are not shown."))
    return pieces


def _unreported_pieces(breakdown: Breakdown) -> list[list[Piece]]:
    blocks = []
    for item in breakdown.claims_vs_evidence.unreported:
        blocks.append(
            [
                Slot(f"label.benchmark.{item.benchmark}"),
                Literal(" has an independent reading of "),
                Slot(f"claims.unreported.{item.benchmark}.reading"),
                Literal(" and no lab figure."),
            ]
        )
    return blocks


def _list_pieces(prefix: str, fact_ids: Sequence[str], sep: str = ", ") -> list[Piece] | None:
    if not fact_ids:
        return None
    pieces: list[Piece] = [Literal(prefix)]
    for index, fact_id in enumerate(fact_ids):
        if index:
            pieces.append(Literal(sep))
        pieces.append(Slot(fact_id))
    pieces.append(Literal("."))
    return pieces


def _unread_pieces(breakdown: Breakdown) -> list[Piece] | None:
    names = breakdown.not_yet_measured.claims_without_reading
    return _list_pieces(
        "Lab figures with no independent reading yet: ",
        [f"label.benchmark.{name}" for name in names],
    )


def _domains_pieces(breakdown: Breakdown) -> list[Piece] | None:
    names = breakdown.not_yet_measured.domains_without_estimate
    return _list_pieces(
        "Domains with no estimate yet: ",
        [f"label.domain[{index}]" for index, _name in enumerate(names)],
    )


def _speed_pieces(breakdown: Breakdown) -> list[Piece] | None:
    gaps = breakdown.not_yet_measured
    if any(
        item.time_to_first_token == "unknown" and item.throughput == "unknown"
        for item in gaps.speed
    ):
        return [Literal("Speed is not measured yet.")]
    return None


def _facets_pieces(breakdown: Breakdown) -> list[Piece] | None:
    rows = breakdown.not_yet_measured.unknown_facets
    return _list_pieces(
        "Guaranteed facts still unknown: ",
        [f"label.facet[{index}]" for index, _row in enumerate(rows)],
    )


def _inapplicable_pieces(breakdown: Breakdown) -> list[Piece] | None:
    rows = breakdown.not_yet_measured.domains_inapplicable
    if not rows:
        return None
    pieces: list[Piece] = [Literal("Domains this class cannot be measured on, so not a gap: ")]
    for index, _row in enumerate(rows):
        if index:
            pieces.append(Literal("; "))
        pieces.append(Slot(f"label.inapplicable[{index}].domain"))
        pieces.append(Literal(", because "))
        pieces.append(Slot(f"label.inapplicable[{index}].reason"))
    pieces.append(Literal("."))
    return pieces


def _plan_pieces(breakdown: Breakdown) -> list[list[Piece]]:
    return [[Slot(f"label.plan[{index}]")] for index, _plan in enumerate(breakdown.cost.plans)]


def _intro_pieces(breakdown: Breakdown, *, teams: bool) -> list[Piece]:
    if teams:
        tail = " is an analysis of alternatives for teams choosing a "
    else:
        tail = " is an analysis of alternatives for a "
    return [Slot("model.name"), Literal(tail), Slot("label.class"), Literal(".")]


def _disclosure_blocks(breakdown: Breakdown) -> list[list[Piece]]:
    blocks = []
    for text in (breakdown.disclosures.supplier, breakdown.disclosures.early_access):
        if text:
            blocks.append([Literal(text)])
    return blocks


def _neutrality(breakdown: Breakdown) -> list[Piece]:
    return [Literal(breakdown.disclosures.neutrality)]


def _url() -> list[Piece]:
    return [Slot("post.url")]


def _headline(breakdown: Breakdown) -> list[Piece]:
    return [Literal(breakdown.headline.text)]


def _present(blocks: Sequence[list[Piece] | None]) -> list[list[Piece]]:
    return [block for block in blocks if block]


def _posts_from(
    blocks: Sequence[Sequence[Piece]],
    book: dict[str, Fact],
    limit: int,
    label: str,
) -> list[str]:
    texts = []
    for index, block in enumerate(blocks):
        text = _render(block, book)
        if len(text) > limit:
            raise ValueError(f"{label} post {index} is {len(text)} characters, limit {limit}")
        texts.append(text)
    return texts


def _x_pieces(breakdown: Breakdown, book: dict[str, Fact]) -> tuple[list[Piece], tuple[str, ...]]:
    standing = [_standing_pieces(breakdown, index) for index in range(len(breakdown.standing))]
    gaps = _present(
        [
            _unread_pieces(breakdown),
            _held_pieces(breakdown),
            *_unreported_pieces(breakdown),
        ]
    )
    blocks = _present(
        [
            _hook_pieces(breakdown),
            _headline(breakdown),
            *standing,
            _cost_pieces(breakdown),
            *gaps,
            *_disclosure_blocks(breakdown),
            _neutrality(breakdown),
            _url(),
        ]
    )
    story = _flatten(blocks)
    cites = _citation_lines(story, book)
    posts = [*blocks, *cites]
    texts = tuple(_posts_from(posts, book, _X_LIMIT, "X"))
    return _file(_flatten(posts)), texts


def _story(breakdown: Breakdown, *, teams: bool) -> tuple[list[list[Piece]], list[list[Piece]]]:
    standing = [_standing_pieces(breakdown, index) for index in range(len(breakdown.standing))]
    gaps = _present(
        [
            _unread_pieces(breakdown),
            _held_pieces(breakdown),
            *_unreported_pieces(breakdown),
            _speed_pieces(breakdown),
            _domains_pieces(breakdown),
        ]
    )
    lead = [*_disclosure_blocks(breakdown), _intro_pieces(breakdown, teams=teams)]
    optional = _present(
        [
            _headline(breakdown),
            _hook_pieces(breakdown),
            *standing,
            _cost_pieces(breakdown),
            *_comparison_pieces(breakdown),
            *gaps,
            *_plan_pieces(breakdown),
            _facets_pieces(breakdown),
            _inapplicable_pieces(breakdown),
        ]
    )
    return lead, optional


def _guard(text: str) -> None:
    found = refused_words(text)
    if found:
        raise ValueError(f"draft contains refused wording: {found[0]}")
    if excluded_sources().text.search(text):
        raise ValueError("draft names an excluded source")
    if "router" in text.lower():
        raise ValueError("draft names a router")


def _hn_title(headline: str) -> str:
    if len(headline) <= _HN_TITLE_LIMIT:
        return headline
    main = headline.split(";", 1)[0].strip()
    if len(main) <= _HN_TITLE_LIMIT:
        return main
    cut = main[:_HN_TITLE_LIMIT]
    space = cut.rfind(" ")
    return cut[:space] if space > 0 else cut


def render_drafts(breakdown: Breakdown, *, post_url: str | None = None) -> dict[str, Draft]:
    """Six text drafts for one breakdown. Nothing is posted."""
    _require_digit_free(breakdown)
    url = post_url or _default_url(breakdown)
    book = catalogue(breakdown, url)
    tail = [_neutrality(breakdown), _url()]

    x_pieces, x_posts = _x_pieces(breakdown, book)
    x_output = _prove(x_pieces, breakdown, url)

    linkedin_lead, linkedin_optional = _story(breakdown, teams=True)
    linkedin_body = _fit(linkedin_lead, linkedin_optional, tail, book, _LINKEDIN_LIMIT)
    linkedin_text = _render(linkedin_body, book)
    linkedin_pieces = _file(linkedin_body)
    linkedin_output = _prove(linkedin_pieces, breakdown, url)

    facebook_body = _fit(
        [*_disclosure_blocks(breakdown), _short_hook(breakdown)],
        [],
        tail,
        book,
        _FACEBOOK_LIMIT,
    )
    facebook_text = _render(facebook_body, book)
    facebook_output = _prove(_file(facebook_body), breakdown, url)

    instagram_lead, instagram_optional = _story(breakdown, teams=False)
    instagram_body = _fit(
        [[Literal(_HAND)], *instagram_lead],
        instagram_optional,
        tail,
        book,
        _INSTAGRAM_CAPTION_LIMIT,
    )
    instagram_text = _render(instagram_body, book)
    instagram_output = _prove(_file(instagram_body), breakdown, url)

    reddit_lead, reddit_optional = _story(breakdown, teams=False)
    reddit_lead = [[Literal("This is ModelSpec.")], *reddit_lead]
    reddit_body = _fit(
        reddit_lead,
        reddit_optional,
        [[Literal(_REDDIT_RULES)], *tail],
        book,
        _REDDIT_BODY_LIMIT,
    )
    reddit_text = _render(reddit_body, book)
    title = _within("Reddit title", breakdown.headline.text, _REDDIT_TITLE_LIMIT)
    reddit_pieces = [Literal(title), Literal("\n\n"), *reddit_body, Literal("\n")]
    reddit_output = _prove(reddit_pieces, breakdown, url)

    hn_title = _within("Hacker News title", _hn_title(breakdown.headline.text), _HN_TITLE_LIMIT)
    hn_blocks: list[list[Piece]] = [[Literal(hn_title)], _url()]
    if hn_title != breakdown.headline.text:
        hn_blocks.append(_headline(breakdown))
    hn_blocks.extend(
        [
            _hook_pieces(breakdown),
            *_disclosure_blocks(breakdown),
            _neutrality(breakdown),
            [Literal(_JAMIE)],
        ]
    )
    hn_story = _flatten(hn_blocks)
    hn_cites = _cite_block(hn_story, book)
    if hn_cites:
        hn_blocks.insert(3, hn_cites)
    hn_body = _flatten(hn_blocks)
    hn_output = _prove(_file(hn_body), breakdown, url)
    submission = hn_output[:-1]

    drafts = {
        "x": Draft(
            platform="x",
            posts=x_posts,
            link=url,
            output=x_output,
            manifest=tuple(x_pieces),
        ),
        "linkedin": Draft(
            platform="linkedin",
            posts=(linkedin_text,),
            link=url,
            output=linkedin_output,
            manifest=tuple(_file(linkedin_body)),
        ),
        "facebook": Draft(
            platform="facebook",
            posts=(facebook_text,),
            link=url,
            output=facebook_output,
            manifest=tuple(_file(facebook_body)),
        ),
        "instagram": Draft(
            platform="instagram",
            posts=(instagram_text,),
            link=url,
            output=instagram_output,
            manifest=tuple(_file(instagram_body)),
        ),
        "reddit": Draft(
            platform="reddit",
            posts=(reddit_text,),
            link=url,
            output=reddit_output,
            manifest=tuple(reddit_pieces),
            title=title,
            subreddit="r/LocalLLaMA",
            rules=_REDDIT_RULES,
            cross_post=False,
        ),
        "hackernews": Draft(
            platform="hackernews",
            posts=(),
            link=url,
            output=hn_output,
            manifest=tuple(_file(hn_body)),
            title=hn_title,
            submission=submission,
            note=_JAMIE,
            jamie_decides=True,
        ),
    }
    for draft in drafts.values():
        _guard(draft.output)
    return drafts


def generate_from_breakdown(
    *,
    breakdown_path: str | Path,
    post_url: str,
    output_dir: str | Path,
) -> dict[str, str]:
    """Write the six text drafts the release hook asks for. Nothing is posted."""
    breakdown = Breakdown.model_validate_json(Path(breakdown_path).read_bytes())
    drafts = render_drafts(breakdown, post_url=post_url)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for platform, filename in _DRAFT_FILES.items():
        target = destination / filename
        target.write_text(drafts[platform].output, encoding="utf-8")
        written[filename] = str(target)
    return written
