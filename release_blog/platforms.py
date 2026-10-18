"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one string per platform. A person posts them.
The function has no platform client and writes no image. Numbers stay in the
breakdown post. A draft says what changed, which model, and where to read
the post. Instagram is a caption and says to make the image by hand.

Each value is a string. ``posts_of`` splits a thread on a blank line and
joins it back to that same string. The post URL is the only token that may
contain a digit, and only when the token is exactly the validated URL.
"""

from __future__ import annotations

import re
import unicodedata
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
_POST_URL = re.compile(r"^https://modelspec\.dev/blog/[a-z0-9-]+/$")
_SUPERLATIVES = (
    "best",
    "fastest",
    "cheapest",
    "top",
    "leading",
    "greatest",
    "strongest",
    "smartest",
    "unbeatable",
    "unmatched",
    "number one",
    "#1",
)
_SUPERLATIVE = re.compile(
    r"(?<!\w)(?:" + "|".join(re.escape(word) for word in _SUPERLATIVES) + r")(?!\w)",
    re.IGNORECASE,
)
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


def _letters(text: str) -> str:
    normal = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normal if character.isalpha())


def _percent_word(text: str) -> bool:
    letters = _letters(text)
    return "percent" in letters or "percentage" in letters


def _superlative_hits(text: str, *, allow_band: bool) -> list[str]:
    hits: list[str] = []
    for match in _SUPERLATIVE.finditer(text):
        word = match.group(0)
        if allow_band and word.casefold() in {"leading", "best"}:
            rest = text[match.end() :]
            if re.match(r"\s+band(?!\w)", rest, re.IGNORECASE):
                continue
        hits.append(word)
    return hits


def _validate_post_url(post_url: str) -> None:
    if _POST_URL.fullmatch(post_url) is None:
        raise ValueError("post_url is not a modelspec blog url")


def _require_text(name: str, value: object) -> str:
    if type(value) is str:
        return value
    carried = sorted(
        key
        for key in getattr(value, "__dict__", {})
        if isinstance(key, str) and not key.startswith("_")
    )
    found = carried[0] if carried else "object"
    raise ValueError(f"{name} draft carries {found}")


def _prose(text: str, post_url: str, where: str) -> str:
    kept: list[str] = []
    for token in text.split():
        if token == post_url:
            continue
        if "://" in token or post_url in token:
            raise ValueError(f"{where} does not use the exact breakdown url")
        kept.append(token)
    return " ".join(kept)


def _reject_field(label: str, text: str | None, *, allow_band: bool = False) -> None:
    if not text:
        return
    if _superlative_hits(text, allow_band=allow_band):
        raise ValueError(f"{label} contains a superlative")
    if _percent_word(text):
        raise ValueError(f"{label} contains a percent")
    if mark := _number_mark(text):
        raise ValueError(f"{label} contains a {mark}")


def _reject_text(text: str, post_url: str, *, where: str, require_url: bool) -> None:
    prose = _prose(text, post_url, where)
    if require_url and post_url not in text.split():
        raise ValueError(f"{where} is missing the breakdown url")
    if _superlative_hits(prose, allow_band=False):
        raise ValueError(f"{where} contains a superlative")
    if _percent_word(prose):
        raise ValueError(f"{where} contains a percent")
    if mark := _number_mark(prose):
        raise ValueError(f"{where} contains a {mark}")


def _reject_inputs(breakdown: Breakdown) -> None:
    # "leading band" and "best band" name a band in the breakdown post.
    # A draft does not repeat that headline. Any other banned stem fails here.
    _reject_field("headline.text", breakdown.headline.text, allow_band=True)
    _reject_field("disclosures.supplier", breakdown.disclosures.supplier)
    _reject_field("disclosures.early_access", breakdown.disclosures.early_access)
    _reject_field("disclosures.neutrality", breakdown.disclosures.neutrality)


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _copyable_name(name: str) -> bool:
    if not name or _number_mark(name) or _percent_word(name):
        return False
    return not _superlative_hits(name, allow_band=False)


def _referent(breakdown: Breakdown) -> str:
    """Use a digit-free name. Otherwise say "the new model".

    ``model.name`` is the name field. ``names`` holds the vocabulary display
    name for this model. A digit, a percent word, or a superlative is not
    copied. The link names the model only when the chosen name is copyable.
    """
    candidates = (breakdown.model.name, breakdown.names.get(breakdown.model.id, ""))
    for name in candidates:
        if _copyable_name(name):
            return name
    return _GENERIC_MODEL


def _class_label(breakdown: Breakdown) -> str:
    label = breakdown.model.class_.replace("-", " ")
    _reject_field("model.class", label)
    return label


def _public_headline(text: str) -> str:
    """Keep a band claim in the breakdown. A draft does not repeat it."""
    if _superlative_hits(text, allow_band=False):
        return ""
    return text


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


def _short_title(change: str, cover: str) -> str:
    sentence = change
    if sentence.lower().startswith("on ") and ", " in sentence:
        rest = sentence.split(", ", 1)[1]
        sentence = rest[:1].upper() + rest[1:]
    if not sentence:
        sentence = cover
    if len(sentence) <= _HN_TITLE_LIMIT:
        return sentence
    cut = sentence[:_HN_TITLE_LIMIT]
    space = cut.rfind(" ")
    return cut[:space] if space > 0 else cut


def _without(parts: list[tuple[str, str]], role: str) -> list[tuple[str, str]]:
    return [item for item in parts if item[0] != role]


def _parts(breakdown: Breakdown, platform: str, post_url: str) -> list[tuple[str, str]]:
    referent = _referent(breakdown)
    class_label = _class_label(breakdown)
    headline = _public_headline(breakdown.headline.text)
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
        if headline:
            title = _hn_title(headline)
            parts = [("title", title)]
            if title != headline:
                parts.append(("headline", headline))
            return [*parts, ("change", change), *shared, *ending, ("note", _JAMIE)]
        title = _short_title(change, cover)
        parts = [("title", title)]
        if change and change != title:
            parts.append(("change", change))
        body = _without(shared, "model") if title == cover else shared
        return [*parts, *body, *ending, ("note", _JAMIE)]
    if platform == "reddit":
        if headline:
            return [
                ("title", headline),
                ("identity", "This is ModelSpec."),
                ("change", change),
                *shared,
                ("rules", _REDDIT_RULES),
                *ending,
            ]
        title = change or cover
        parts = [("title", title), ("identity", "This is ModelSpec.")]
        if change and change != title:
            parts.append(("change", change))
        body = _without(shared, "model") if title == cover else shared
        return [*parts, *body, ("rules", _REDDIT_RULES), *ending]
    lead: list[tuple[str, str]] = [("hand", _HAND)] if platform == "instagram" else []
    middle: list[tuple[str, str]] = [("change", change)]
    if headline:
        middle.append(("headline", headline))
    return [*lead, *middle, *shared, *ending]


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


def _assemble(breakdown: Breakdown, post_url: str) -> dict[str, str]:
    return {platform: _draft_text(breakdown, platform, post_url) for platform in _DRAFT_FILES}


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


def _seal(drafts: dict[str, object], post_url: str) -> dict[str, str]:
    sealed: dict[str, str] = {}
    for name, value in drafts.items():
        text = _require_text(name, value)
        _reject_text(text, post_url, where=f"{name}.text", require_url=True)
        posts = posts_of(text)
        for index, post in enumerate(posts):
            _reject_text(post, post_url, where=f"{name} post {index}", require_url=False)
        _check_limits(name, posts, text)
        _guard(text)
        sealed[name] = text
    return sealed


def render_drafts(breakdown: Breakdown, *, post_url: str | None = None) -> dict[str, str]:
    """Six text drafts for one breakdown. Nothing is posted.

    A thread is ``posts_of(text)``: a tuple of strings whose join is ``text``.
    """
    url = post_url if post_url is not None else _default_url(breakdown)
    _validate_post_url(url)
    _reject_inputs(breakdown)
    return _seal(_assemble(breakdown, url), url)


def generate_from_breakdown(
    *,
    breakdown_path: str | Path,
    post_url: str,
    output_dir: str | Path,
) -> dict[str, str]:
    """Write the six text drafts the release hook asks for. Nothing is posted."""
    _validate_post_url(post_url)
    breakdown = Breakdown.model_validate_json(Path(breakdown_path).read_bytes())
    drafts = render_drafts(breakdown, post_url=post_url)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for platform, filename in _DRAFT_FILES.items():
        body = _require_text(filename, drafts[platform])
        if not body.endswith("\n"):
            body += "\n"
        _reject_text(body, post_url, where=filename, require_url=True)
        target = destination / filename
        target.write_text(body, encoding="utf-8")
        written[filename] = str(target)
    return written
