"""Source retention policy shared by readers, stores and public data builders."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from urllib.parse import urlsplit


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


def is_cite_only(url: object) -> bool:
    parsed = urlsplit(str(url))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    host = parsed.hostname.rstrip(".").lower().encode("idna").decode("ascii")
    return any(host == denied or host.endswith("." + denied) for denied in cite_only_hosts())


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
