"""Source retention policy shared by readers, stores and public data builders."""

from __future__ import annotations

import json
import logging
from functools import cache
from pathlib import Path
from urllib.parse import urlsplit


logger = logging.getLogger(__name__)

POLICY_PATH = Path(__file__).resolve().parents[1] / "registry" / "source-retention.json"


@cache
def cite_only_hosts() -> tuple[str, ...]:
    data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "cite_only_hosts"} \
            or type(data["schema_version"]) is not int or data["schema_version"] != 1 \
            or not isinstance(data["cite_only_hosts"], list):
        raise ValueError("invalid source retention policy")
    hosts = data["cite_only_hosts"]
    if any(not isinstance(host, str) or not host or host != host.lower().rstrip(".")
           or any(char in host for char in "/:@ ") for host in hosts):
        raise ValueError("source retention policy requires canonical host names")
    return tuple(hosts)


_C0_OR_SPACE = "".join(chr(code) for code in range(0x21))


def canonical_host(url: object) -> str | None:
    """The host an HTTP(S) URL names, as the repository's ``HttpUrl`` reads it.

    One parser decides both admission and restriction (MODEL-420): the URL is
    parsed as ``HttpUrl`` (WHATWG rules, IDNA), then a terminal dot is dropped.
    Returns None for a URL whose scheme is not http or https. An HTTP(S) URL
    that does not parse, has an invalid port or carries userinfo raises
    ValueError, so callers fail closed instead of guessing a host.
    """
    text = str(url)
    scheme, colon, _rest = text.lstrip(_C0_OR_SPACE).partition(":")
    scheme = scheme.replace("\t", "").replace("\n", "").replace("\r", "").lower()
    if not colon or scheme not in {"http", "https"}:
        return None
    from pydantic import HttpUrl, ValidationError

    try:
        parsed = HttpUrl(text)
    except ValidationError:
        raise ValueError("invalid HTTP URL") from None
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("HTTP URL carries userinfo")
    host = (parsed.host or "").lower().rstrip(".")
    if not host:
        raise ValueError("HTTP URL has no host")
    return host


def cite_only_status(url: object) -> bool | None:
    """Whether a URL is cite-only, or None for an HTTP(S) URL that does not parse.

    Use this where cite-only status GRANTS something (admission without
    verification, a supersession, a retrieval date): None must then refuse.
    """
    try:
        host = canonical_host(url)
    except ValueError:
        return None
    return host is not None and any(
        host == denied or host.endswith("." + denied) for denied in cite_only_hosts())


def is_cite_only(url: object) -> bool:
    """Whether a URL is cite-only, counting a malformed HTTP(S) URL as cite-only.

    This is the restrictive reading for retention and display: no bytes are
    kept, evidence stays out and nothing reads as machine-verified, and one
    bad URL never aborts a build or job (MODEL-420). Never use it where
    cite-only status grants admission; use ``cite_only_status`` there.
    """
    status = cite_only_status(url)
    if status is None:
        # The URL itself is not logged: it may come from private data.
        logger.warning("a malformed HTTP(S) URL is treated as cite-only")
        return True
    return status


def redirect_urls(value: object) -> tuple[str, ...]:
    """Validated redirect URLs: a list of HTTP(S) URL strings, or ValueError.

    A malformed value is never read as "no redirects": ``None``, ``{}``,
    ``False`` or ``""`` raise like any other non-list.
    """
    if not isinstance(value, (list, tuple)):
        raise ValueError("invalid redirect URL metadata")
    for url in value:
        if not isinstance(url, str) or canonical_host(url) is None:
            raise ValueError("invalid redirect URL metadata")
    return tuple(value)


def cite_only_origin(url: object, resolved_urls=()) -> bool:
    return any(is_cite_only(origin) for origin in (url, *resolved_urls))


def metadata_origins(metadata: dict) -> tuple[str, ...]:
    urls = [metadata[key] for key in ("sourceURL", "url", "final_url")
            if isinstance(metadata.get(key), str) and metadata[key]]
    resolved = metadata.get("resolved_urls", ())
    if not isinstance(resolved, (list, tuple)) or any(not isinstance(url, str) for url in resolved):
        raise ValueError("invalid redirect URL metadata")
    return tuple(dict.fromkeys((*urls, *resolved)))


def require_source_url(url: object) -> str:
    value = str(url)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("retaining source bytes requires an HTTP source URL")
    return value


def citation_metadata(url: object, snapshot_ref: str, *, retrieved_at=None,
                      resolved_urls=()) -> dict:
    when = retrieved_at
    return {
        "url": require_source_url(url),
        "retrieved_at": when.isoformat() if hasattr(when, "isoformat") else when,
        "snapshot_ref": snapshot_ref,
        "resolved_urls": list(dict.fromkeys(str(item) for item in resolved_urls)),
    }


def refuse_disk_scrape(url: object) -> None:
    if is_cite_only(url):
        raise ValueError("cite-only source requires a transient fetch; disk-writing scraper refused")


def open_retained_source(request, *, timeout):
    """Open a source only when every HTTP redirect permits retained content."""
    from urllib.request import HTTPRedirectHandler, build_opener

    url = request if isinstance(request, str) else request.full_url
    refusal = "cite-only source cannot supply retained content"
    if is_cite_only(url):
        raise ValueError(refusal)

    class RetainedRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if is_cite_only(newurl):
                fp.close()
                raise ValueError(refusal)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    response = build_opener(RetainedRedirect()).open(request, timeout=timeout)
    if is_cite_only(response.geturl()):
        response.close()
        raise ValueError(refusal)
    return response
