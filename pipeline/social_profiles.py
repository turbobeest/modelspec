"""Opt-in social profile URLs for the site's JSON-LD metadata."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "brand" / "social" / "profiles.json"
_JSON_LD = re.compile(
    r'(<script\s+type="application/ld\+json"\s*>)(.*?)(</script>)',
    re.DOTALL,
)


@dataclass(frozen=True)
class Platform:
    pattern: re.Pattern[str]
    url: str


PLATFORMS = {
    "x": Platform(re.compile(r"[A-Za-z0-9_]{1,15}"), "https://x.com/{handle}"),
    "instagram": Platform(
        re.compile(r"(?!.*\.\.)(?!.*\.$)[A-Za-z0-9._]{1,30}"),
        "https://www.instagram.com/{handle}/",
    ),
    "tiktok": Platform(
        re.compile(r"(?!.*\.\.)(?!.*\.$)[A-Za-z0-9._]{2,24}"),
        "https://www.tiktok.com/@{handle}",
    ),
    "linkedin": Platform(
        re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{1,98}[A-Za-z0-9]"),
        "https://www.linkedin.com/company/{handle}/",
    ),
}


def profile_urls(path: Path = DEFAULT_CONFIG) -> tuple[str, ...]:
    """Return configured canonical profile URLs in config order.

    Empty strings are intentional before account creation. A malformed handle
    fails the build instead of publishing a broken or unintended identity URL.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected an object")
    expected = set(PLATFORMS)
    if set(raw) != expected:
        missing = sorted(expected - set(raw))
        unknown = sorted(set(raw) - expected)
        raise ValueError(f"{path}: missing={missing}, unknown={unknown}")

    urls: list[str] = []
    for name, handle in raw.items():
        if not isinstance(handle, str):
            raise ValueError(f"{name}: handle must be a string")
        if not handle:
            continue
        platform = PLATFORMS[name]
        if platform.pattern.fullmatch(handle) is None:
            raise ValueError(f"{name}: invalid handle {handle!r}")
        urls.append(platform.url.format(handle=handle))
    return tuple(urls)


def add_same_as(html: str, path: Path = DEFAULT_CONFIG) -> str:
    """Add configured profile URLs to the first JSON-LD object in ``html``."""
    urls = profile_urls(path)
    if not urls:
        return html
    match = _JSON_LD.search(html)
    if match is None:
        raise ValueError("social profiles are configured, but the page has no JSON-LD object")
    data = json.loads(match.group(2))
    if not isinstance(data, dict):
        raise ValueError("the page's JSON-LD value is not an object")
    data["sameAs"] = list(urls)
    replacement = f"{match.group(1)}\n{json.dumps(data, indent=2)}\n{match.group(3)}"
    return html[:match.start()] + replacement + html[match.end():]
