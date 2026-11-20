"""Source retention policy shared by readers, stores and public data builders."""

from __future__ import annotations

import json
from collections.abc import Mapping
import logging
import os
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from urllib.parse import urlsplit


logger = logging.getLogger(__name__)

POLICY_PATH = Path(__file__).resolve().parents[1] / "registry" / "source-retention.json"


@cache
def _public_cite_only_hosts() -> tuple[str, ...]:
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


DATA_DIR_ENV = "MODELSPEC_DATA_DIR"
FORBIDS = "forbids"


@cache
def _register_forbidding(data_dir: str) -> tuple[str, ...]:
    path = Path(data_dir) / "registry" / "source-terms.json"
    try:
        terms = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ()
    except (OSError, ValueError):
        logger.warning("the private source-terms register could not be read")
        return ()
    if not isinstance(terms, dict):
        logger.warning("the private source-terms register is not an object")
        return ()
    return tuple(sorted(host for host, cls in terms.items()
                        if cls == FORBIDS and isinstance(host, str) and host
                        and host == host.lower().rstrip(".")
                        and not any(char in host for char in "/:@ ")))


@cache
def _register_classes(data_dir: str) -> frozenset[str] | None:
    path = Path(data_dir) / "registry" / "source-terms.json"
    try:
        terms = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("the private source-terms register could not be read")
        return None
    if not isinstance(terms, dict):
        logger.warning("the private source-terms register is not an object")
        return None
    return frozenset(host for host, cls in terms.items()
                     if isinstance(host, str) and host and isinstance(cls, str) and cls)


class TermsRegisterUnreadable(Exception):
    """A data directory is named but its terms register is missing or unreadable."""


def classified_hosts() -> frozenset[str] | None:
    """Hosts that carry a class in the private terms register (MODEL-509).

    None when no data directory is named: a caller then behaves as it did before
    the register existed. With a data directory and no readable register this
    raises ``TermsRegisterUnreadable``, so a caller fails closed.
    """
    data_dir = os.environ.get(DATA_DIR_ENV, "").strip()
    if not data_dir:
        return None
    classes = _register_classes(data_dir)
    if classes is None:
        raise TermsRegisterUnreadable
    return classes


def is_classified(host: str | None, classes: frozenset[str] | Mapping[str, str]) -> bool:
    """Whether ``host`` or a parent domain of it carries a class (the rule ``cite_only_status`` uses)."""
    return host is not None and any(host == c or host.endswith("." + c) for c in classes)


def use_data_dir(data_dir: object) -> None:
    """Name the private data directory for every reader in this process.

    Entry points that take ``--data-dir`` (the trust audit, ``pipeline.build``,
    ``api/worker/vendor.py``) call this so ``forbidding_hosts`` reads the same
    register on every path (MODEL-510). A subprocess inherits it.
    """
    os.environ[DATA_DIR_ENV] = str(data_dir)


@contextmanager
def using_data_dir(data_dir: object):
    """``use_data_dir`` for the length of a block; the previous value comes back."""
    previous = os.environ.get(DATA_DIR_ENV)
    use_data_dir(data_dir)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(DATA_DIR_ENV, None)
        else:
            os.environ[DATA_DIR_ENV] = previous


def forbidding_hosts() -> tuple[str, ...]:
    """Hosts the private terms register classes ``forbids`` (MODEL-510).

    Read from ``registry/source-terms.json`` under ``MODELSPEC_DATA_DIR``.
    With no data directory (a public build) the result is empty, so the
    public list alone decides, as before. ``cite_only_hosts`` adds these
    hosts to the public list, so every reading treats them alike.
    """
    data_dir = os.environ.get(DATA_DIR_ENV, "").strip()
    return _register_forbidding(data_dir) if data_dir else ()


def cite_only_hosts() -> tuple[str, ...]:
    """The public list, plus the hosts the private register classes ``forbids``.

    A forbids-class host behaves exactly like a listed one in both directions
    (MODEL-510): no bytes kept, and a cited claim from it is admitted. The
    register is read only when a data directory is named; with none the result
    is the public list alone.
    """
    public = _public_cite_only_hosts()
    return (*public, *(host for host in forbidding_hosts() if host not in public))


def _clear_caches() -> None:
    _public_cite_only_hosts.cache_clear()
    _register_forbidding.cache_clear()
    _register_classes.cache_clear()


cite_only_hosts.cache_clear = _clear_caches  # type: ignore[attr-defined]


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


# Two readings of one policy (MODEL-420). Pick by what cite-only status does
# at the call site:
# - GRANTING: it admits a fact as cited, skips verification, supersedes a
#   mismatch, dates a record by retrieval, or puts a fact in re-read scope.
#   Use ``cite_only_status`` / ``cite_only_origin_status`` and REFUSE on None.
# - RESTRICTIVE: it withholds bytes, keeps evidence out, refuses a fetch or a
#   draft, or discloses "not machine-verified". Use ``is_cite_only_restrictive``
#   / ``cite_only_origin_restrictive``, which count a malformed URL as
#   cite-only so one bad URL fails closed for its own record and never aborts
#   a build or job.


def cite_only_status(url: object) -> bool | None:
    """Whether a URL is cite-only, or None for an HTTP(S) URL that does not parse.

    For GRANTING call sites: None must refuse (exclude, invalid_citation, out
    of scope), never grant.
    """
    try:
        host = canonical_host(url)
    except ValueError:
        return None
    return host is not None and any(
        host == denied or host.endswith("." + denied) for denied in cite_only_hosts())


def is_cite_only_restrictive(url: object) -> bool:
    """Whether a URL is cite-only, counting a malformed HTTP(S) URL as cite-only.

    For RESTRICTIVE call sites only (retention, storage, display): no bytes
    are kept, evidence stays out and nothing reads as machine-verified. Never
    use it where cite-only status grants anything; use ``cite_only_status``.
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


def cite_only_origin_status(url: object, resolved_urls=()) -> bool | None:
    """Whether any origin is cite-only, or None when any origin is malformed.

    For GRANTING call sites: None must refuse, even if another origin is
    cite-only.
    """
    statuses = [cite_only_status(origin) for origin in (url, *resolved_urls)]
    return None if None in statuses else any(statuses)


def cite_only_origin_restrictive(url: object, resolved_urls=()) -> bool:
    """Whether any origin is cite-only, counting a malformed one as cite-only.

    For RESTRICTIVE call sites only (retention, storage, display).
    """
    return any(is_cite_only_restrictive(origin) for origin in (url, *resolved_urls))


def metadata_origins(metadata: dict) -> tuple[str, ...]:
    urls = [metadata[key] for key in ("sourceURL", "url", "final_url")
            if isinstance(metadata.get(key), str) and metadata[key]]
    resolved = metadata.get("resolved_urls", ())
    if not isinstance(resolved, (list, tuple)) or any(not isinstance(url, str) for url in resolved):
        raise ValueError("invalid redirect URL metadata")
    return tuple(dict.fromkeys((*urls, *resolved)))


def record_origin_status(record: object) -> bool | None:
    """Whether a stored citation record names a cite-only origin; None when malformed.

    For GRANTING call sites. Every origin the record carries is checked
    (``url``, ``sourceURL``, ``final_url`` and ``resolved_urls``): a present
    field that is not a well-formed HTTP(S) URL, or a record with no origin,
    gives None, never "no redirect" (MODEL-420).
    """
    if not isinstance(record, dict):
        return None
    for key in ("sourceURL", "url", "final_url"):
        if key in record and (not isinstance(record[key], str) or not record[key]):
            return None
    try:
        if "resolved_urls" in record:
            redirect_urls(record["resolved_urls"])
        origins = metadata_origins(record)
    except (TypeError, ValueError):
        return None
    if not origins:
        return None
    statuses = []
    for origin in origins:
        try:
            if canonical_host(origin) is None:
                return None
        except ValueError:
            return None
        statuses.append(cite_only_status(origin))
    return any(statuses)


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
    if is_cite_only_restrictive(url):
        raise ValueError("cite-only source requires a transient fetch; disk-writing scraper refused")


def open_retained_source(request, *, timeout):
    """Open a source only when every HTTP redirect permits retained content."""
    from urllib.request import HTTPRedirectHandler, build_opener

    url = request if isinstance(request, str) else request.full_url
    refusal = "cite-only source cannot supply retained content"
    if is_cite_only_restrictive(url):
        raise ValueError(refusal)

    class RetainedRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if is_cite_only_restrictive(newurl):
                fp.close()
                raise ValueError(refusal)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    response = build_opener(RetainedRedirect()).open(request, timeout=timeout)
    if is_cite_only_restrictive(response.geturl()):
        response.close()
        raise ValueError(refusal)
    return response
