"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one text draft per platform. A person posts them.
The function has no platform client and writes no image. Numbers stay in the
breakdown post. A draft says what changed, which model, and where to read
the post. Instagram is a caption and says to make the image by hand.

Each draft is one string. A thread is that string split on a blank line,
joined back, and compared. The post URL is the only place a digit may appear.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path

from decision.excluded import excluded_sources
from release_blog.model import Breakdown
from release_blog.tone import refused_words

AUTOMATIC_POSTING = False

_X_LIMIT = 280
_LINKEDIN_LIMIT = 3000
_FACEBOOK_LIMIT = 500
_INSTAGRAM_CAPTION_LIMIT = 2200
_REDDIT_TITLE_LIMIT = 300
_REDDIT_BODY_LIMIT = 40_000
_HN_TITLE_LIMIT = 80
_SEP = "\n\n"
_NUMBER_CATEGORIES = frozenset({"Nd", "No", "Nl"})
_PERCENT = re.compile(r"%|(?<!\w)per\s*cent", re.IGNORECASE)
_OPTIONAL = frozenset({"change"})
_WHOLE_LIMITS = {
    "linkedin": _LINKEDIN_LIMIT,
    "facebook": _FACEBOOK_LIMIT,
    "instagram": _INSTAGRAM_CAPTION_LIMIT,
}
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
_GENERIC_MODEL = "the new model"
_PROSE_FIELDS = (
    ("headline.text", "headline"),
    ("disclosures.supplier", "supplier"),
    ("disclosures.early_access", "early_access"),
    ("disclosures.neutrality", "neutrality"),
)


@dataclass(frozen=True, slots=True)
class Draft:
    """The draft copy. ``text`` is the only string on the object."""

    text: str


def posts_of(text: str) -> tuple[str, ...]:
    """Split one draft into posts and require the join to reproduce it."""
    posts = tuple(text.split(_SEP))
    if _SEP.join(posts) != text:
        raise ValueError("draft posts do not rejoin to the draft")
    return posts


def _number_mark(text: str) -> str | None:
    for character in text:
        if (
            unicodedata.category(character) in _NUMBER_CATEGORIES
            or character.isdigit()
            or character.isnumeric()
        ):
            return "digit"
    if _PERCENT.search(unicodedata.normalize("NFKC", text)):
        return "percent"
    return None


def _reject_field(label: str, text: str | None) -> None:
    if text and (mark := _number_mark(text)):
        raise ValueError(f"{label} contains a {mark}")


def _reject_text(text: str, post_url: str, *, where: str, require_url: bool) -> None:
    if require_url and post_url not in text:
        raise ValueError(f"{where} is missing the breakdown url")
    if mark := _number_mark(text.replace(post_url, "")):
        raise ValueError(f"{where} contains a {mark}")


def _iter_strings(value: object, prefix: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix or "text", value
        return
    if value is None or isinstance(value, (int, float, bool)):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            key_label = f"{prefix}.key" if prefix else "key"
            yield from _iter_strings(key, key_label)
            item_label = f"{prefix}.{key}" if prefix else str(key)
            yield from _iter_strings(item, item_label)
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from _iter_strings(item, f"{prefix}[{index}]")
        return
    names: list[str] = []
    if is_dataclass(value):
        names.extend(field.name for field in fields(value))
    slots = getattr(value, "__slots__", ())
    if isinstance(slots, str):
        slots = (slots,)
    names.extend(slots)
    names.extend(getattr(value, "__dict__", {}))
    seen: set[str] = set()
    for name in names:
        if not name or name.startswith("_") or name in seen:
            continue
        seen.add(name)
        try:
            item = getattr(value, name)
        except AttributeError:
            continue
        if callable(item):
            continue
        label = f"{prefix}.{name}" if prefix else name
        yield from _iter_strings(item, label)


def _reject_inputs(breakdown: Breakdown) -> None:
    values = {
        "headline": breakdown.headline.text,
        "supplier": breakdown.disclosures.supplier,
        "early_access": breakdown.disclosures.early_access,
        "neutrality": breakdown.disclosures.neutrality,
    }
    for label, key in _PROSE_FIELDS:
        _reject_field(label, values[key])


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _referent(breakdown: Breakdown) -> str:
    """Use a digit-free name. Otherwise say "the new model".

    ``model.name`` is the name field. ``names`` holds the vocabulary display
    name for this model. "Alpha 2.5" has a digit, and so does a superscript
    or circled digit in that field. Neither is copied. The link names the
    model only when the chosen name is digit-free.
    """
    candidates = (breakdown.model.name, breakdown.names.get(breakdown.model.id, ""))
    for name in candidates:
        if name and _number_mark(name) is None:
            return name
    return _GENERIC_MODEL


def _class_label(breakdown: Breakdown) -> str:
    label = breakdown.model.class_.replace("-", " ")
    _reject_field("model.class", label)
    return label


def _gap(breakdown: Breakdown):
    for row in breakdown.claims_vs_evidence.claims:
        for reading in row.readings:
            change = reading.difference
            if reading.comparability == "same_setup" and change is not None and change.value != 0:
                return row, reading
    return None


def _change_sentence(breakdown: Breakdown) -> str:
    found = _gap(breakdown)
    if found is None:
        return ""
    row, reading = found
    change = reading.difference
    assert change is not None
    direction = "lower" if change.value < 0 else "higher"
    sentence = f"an independent reading of the same setup is {direction} than the lab's figure."
    if _number_mark(row.benchmark):
        return sentence[:1].upper() + sentence[1:]
    return f"On {row.benchmark}, {sentence}"


def _link_sentence(referent: str, post_url: str) -> str:
    if referent == _GENERIC_MODEL:
        return f"Read the full breakdown, with sources: {post_url}"
    return f"Read the full breakdown of {referent}, with sources: {post_url}"


def _analysis(class_label: str, *, teams: bool) -> str:
    if teams:
        return f"ModelSpec is an analysis of alternatives for teams choosing a {class_label}."
    return f"ModelSpec is an analysis of alternatives for a {class_label}."


def _hn_title(headline: str) -> str:
    if len(headline) <= _HN_TITLE_LIMIT:
        return headline
    main = headline.split(";", 1)[0].strip()
    if len(main) <= _HN_TITLE_LIMIT:
        return main
    cut = main[:_HN_TITLE_LIMIT]
    space = cut.rfind(" ")
    return cut[:space] if space > 0 else cut


def _parts(breakdown: Breakdown, platform: str, post_url: str) -> list[tuple[str, str]]:
    referent = _referent(breakdown)
    class_label = _class_label(breakdown)
    headline = breakdown.headline.text
    change = _change_sentence(breakdown)
    cover = f"The breakdown covers {referent}."
    analysis = _analysis(class_label, teams=platform == "linkedin")
    supplier = breakdown.disclosures.supplier or ""
    early = breakdown.disclosures.early_access or ""
    neutrality = breakdown.disclosures.neutrality
    link = _link_sentence(referent, post_url)
    shared = [
        ("model", cover),
        ("analysis", analysis),
        ("supplier", supplier),
        ("early", early),
    ]
    ending = [("neutrality", neutrality), ("link", link)]
    if platform == "hackernews":
        title = _hn_title(headline)
        parts = [("title", title)]
        if title != headline:
            parts.append(("headline", headline))
        return [*parts, ("change", change), *shared, *ending, ("note", _JAMIE)]
    if platform == "reddit":
        return [
            ("title", headline),
            ("identity", "This is ModelSpec."),
            ("change", change),
            *shared,
            ("rules", _REDDIT_RULES),
            *ending,
        ]
    lead: list[tuple[str, str]] = [("hand", _HAND)] if platform == "instagram" else []
    return [*lead, ("change", change), ("headline", headline), *shared, *ending]


def _join(parts: list[tuple[str, str]], limit: int | None) -> str:
    selected = [(role, text) for role, text in parts if text]
    while True:
        body = _SEP.join(text for _, text in selected)
        if limit is None or len(body) <= limit:
            return body
        optional = [index for index, (role, _) in enumerate(selected) if role in _OPTIONAL]
        if not optional:
            raise ValueError(f"required draft text is {len(body)} characters, limit {limit}")
        del selected[optional[-1]]


def _draft_text(breakdown: Breakdown, platform: str, post_url: str) -> str:
    return _join(_parts(breakdown, platform, post_url), _WHOLE_LIMITS.get(platform))


def _assemble(breakdown: Breakdown, post_url: str) -> dict[str, Draft]:
    return {
        platform: Draft(_draft_text(breakdown, platform, post_url)) for platform in _DRAFT_FILES
    }


def _guard(text: str) -> None:
    found = refused_words(text)
    if found:
        raise ValueError(f"draft contains refused wording: {found[0]}")
    if excluded_sources().text.search(text):
        raise ValueError("draft names an excluded source")
    if "router" in text.lower():
        raise ValueError("draft names a router")


def _check_limits(platform: str, posts: tuple[str, ...], text: str) -> None:
    if platform == "x":
        for index, post in enumerate(posts):
            if len(post) > _X_LIMIT:
                raise ValueError(f"X post {index} is {len(post)} characters, limit {_X_LIMIT}")
        return
    if platform == "reddit":
        if len(posts[0]) > _REDDIT_TITLE_LIMIT:
            raise ValueError(
                f"Reddit title is {len(posts[0])} characters, limit {_REDDIT_TITLE_LIMIT}"
            )
        if len(text) > _REDDIT_BODY_LIMIT:
            raise ValueError(f"Reddit draft is {len(text)} characters, limit {_REDDIT_BODY_LIMIT}")
        return
    if platform == "hackernews":
        if len(posts[0]) > _HN_TITLE_LIMIT:
            raise ValueError(
                f"Hacker News title is {len(posts[0])} characters, limit {_HN_TITLE_LIMIT}"
            )
        return
    limit = _WHOLE_LIMITS[platform]
    if len(text) > limit:
        raise ValueError(f"{platform} draft is {len(text)} characters, limit {limit}")


def _seal(drafts: dict[str, object], post_url: str) -> None:
    for label, text in _iter_strings(drafts):
        _reject_text(
            text,
            post_url,
            where=label,
            require_url=label == "text" or label.endswith(".text"),
        )
    for name, draft in drafts.items():
        text = draft.text
        posts = posts_of(text)
        for index, post in enumerate(posts):
            _reject_text(post, post_url, where=f"{name} post {index}", require_url=False)
        _check_limits(name, posts, text)
        _guard(text)


def render_drafts(breakdown: Breakdown, *, post_url: str | None = None) -> dict[str, Draft]:
    """Six text drafts for one breakdown. Nothing is posted."""
    _reject_inputs(breakdown)
    url = post_url or _default_url(breakdown)
    drafts = _assemble(breakdown, url)
    _seal(drafts, url)
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
        body = drafts[platform].text
        if not body.endswith("\n"):
            body += "\n"
        _reject_text(body, post_url, where=filename, require_url=True)
        target = destination / filename
        target.write_text(body, encoding="utf-8")
        written[filename] = str(target)
    return written
