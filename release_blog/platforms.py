"""Platform drafts rendered from a release breakdown (MODEL-226).

``render_drafts`` returns one string per platform. A person posts them.
The function has no platform client and writes no image.

A draft is reviewed copy in this file, plus three slots: a display name,
a lab name, and the breakdown URL. Each name must match
``^[A-Za-z][A-Za-z .'-]{0,60}$`` and the editorial checks. Anything else
is replaced with "the new model" or "the lab", and the original is absent.
Supplier and early-access disclosures contribute a flag, not their text.
The URL is the only token that may contain a digit, and only when the
token is exactly the validated URL.

Each value is a string. ``posts_of`` splits a thread on a blank line and
joins it back to that same string.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from decision.excluded import excluded_publisher
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
_NAME = re.compile(r"^[A-Za-z][A-Za-z .'-]{0,60}$")
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
)
_SUPERLATIVE = re.compile(
    r"(?<!\w)(?:"
    + "|".join(re.escape(word) for word in _SUPERLATIVES)
    + r"|number[\s\-]+one|no\.\s*1|#1)(?!\w)",
    re.IGNORECASE,
)
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
_HOOK = "New model, new evidence: here is how it compares."
_GENERIC_MODEL = "the new model"
_GENERIC_LAB = "the lab"
_ANALYSIS = "ModelSpec is an analysis of alternatives."
_ANALYSIS_TEAMS = "ModelSpec is an analysis of alternatives for teams choosing a model."
_SUPPLIER_LINE = "ModelSpec has a supplier relationship with this lab; details in the breakdown."
_EARLY_LINE = "ModelSpec received early access to this model; details in the breakdown."
_NEUTRALITY = "No referral fees, no paid placement, no provider-paid visibility, permanently."


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


def _superlative_hits(text: str) -> list[str]:
    return [match.group(0) for match in _SUPERLATIVE.finditer(text)]


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


def _prose(text: str, post_url: str) -> str:
    return " ".join(token for token in text.split() if token != post_url)


def _reject_text(text: str, post_url: str, *, where: str, require_url: bool) -> None:
    if require_url and post_url not in text.split():
        raise ValueError(f"{where} is missing the breakdown url")
    prose = _prose(text, post_url)
    if "//" in prose or "[" in prose or "](" in prose or "://" in prose:
        raise ValueError(f"{where} does not use the exact breakdown url")
    if _superlative_hits(prose):
        raise ValueError(f"{where} contains a superlative")
    if mark := _number_mark(prose):
        raise ValueError(f"{where} contains a {mark}")
    if _percent_word(prose):
        raise ValueError(f"{where} contains a percent")
    if excluded_publisher(text):
        raise ValueError("draft names an excluded source")


def _default_url(breakdown: Breakdown) -> str:
    slug = breakdown.model.id.replace("/", "-")
    return f"https://modelspec.dev/blog/{slug}/"


def _blocked(value: str) -> bool:
    if _percent_word(value) or _number_mark(value):
        return True
    if _superlative_hits(value):
        return True
    if "[" in value or "](" in value or "//" in value:
        return True
    if excluded_publisher(value):
        return True
    return "router" in value.lower()


def _copyable(value: str) -> bool:
    return _NAME.fullmatch(value) is not None and not _blocked(value)


def _referent(breakdown: Breakdown) -> str:
    """Use the model name, then its vocabulary display name, when either is copyable."""
    candidates = (breakdown.model.name, breakdown.names.get(breakdown.model.id, ""))
    for name in candidates:
        if name and _copyable(name):
            return name
    return _GENERIC_MODEL


def _lab(breakdown: Breakdown) -> str:
    provider = breakdown.model.provider
    if provider and _copyable(provider):
        return provider
    return _GENERIC_LAB


def _flag(value: str | None) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _link_sentence(referent: str, post_url: str) -> str:
    if referent == _GENERIC_MODEL:
        return f"Read the full breakdown, with sources: {post_url}"
    return f"Read the full breakdown of {referent}, with sources: {post_url}"


def _parts(breakdown: Breakdown, platform: str, post_url: str) -> list[tuple[str, str]]:
    name = _referent(breakdown)
    lab = _lab(breakdown)
    cover = f"The breakdown covers {name} from {lab}."
    analysis = _ANALYSIS_TEAMS if platform == "linkedin" else _ANALYSIS
    supplier = _SUPPLIER_LINE if _flag(breakdown.disclosures.supplier) else ""
    early = _EARLY_LINE if _flag(breakdown.disclosures.early_access) else ""
    link = _link_sentence(name, post_url)
    shared = [
        ("model", cover),
        ("analysis", analysis),
        ("supplier", supplier),
        ("early", early),
    ]
    ending = [("neutrality", _NEUTRALITY), ("link", link)]
    if platform == "hackernews":
        return [("title", _HOOK), *shared, *ending, ("note", _JAMIE)]
    if platform == "reddit":
        return [
            ("title", _HOOK),
            ("identity", "This is ModelSpec."),
            *shared,
            ("rules", _REDDIT_RULES),
            *ending,
        ]
    lead: list[tuple[str, str]] = [("hand", _HAND)] if platform == "instagram" else []
    return [*lead, ("hook", _HOOK), *shared, *ending]


def _join(parts: list[tuple[str, str]], limit: int | None) -> str:
    body = _SEP.join(text for _, text in parts if text)
    if limit is not None and len(body) > limit:
        raise ValueError(f"required draft text is {len(body)} characters, limit {limit}")
    return body


def _draft_text(breakdown: Breakdown, platform: str, post_url: str) -> str:
    return _join(_parts(breakdown, platform, post_url), _WHOLE_LIMITS.get(platform))


def _assemble(breakdown: Breakdown, post_url: str) -> dict[str, str]:
    return {platform: _draft_text(breakdown, platform, post_url) for platform in _DRAFT_FILES}


def _guard(text: str) -> None:
    found = refused_words(text)
    if found:
        raise ValueError(f"draft contains refused wording: {found[0]}")
    if excluded_publisher(text):
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
