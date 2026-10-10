"""Bounded, opt-in raw HTML fallback for the weekly price re-read."""

from __future__ import annotations

import json
import os
from urllib.parse import urlsplit

import httpx

from decision.normalise import canonical_url
from decision.sources import FetchResult

# Exact canonical registry hosts, never a suffix match or a registry-controlled flag.
FIRECRAWL_HOSTS = frozenset(
    {
        "chatgpt.com",
        "learn.chatgpt.com",
        "help.openai.com",
        "x.ai",
        "docs.x.ai",
    }
)
FIRECRAWL_MAX_CREDITS_PER_RUN = 12
FIRECRAWL_MAX_CREDITS_PER_MONTH = 60
MAX_FIRECRAWL_RESPONSE_BYTES = 20 * 1024 * 1024

# https://docs.firecrawl.dev/api-reference/endpoint/scrape documents POST /v2/scrape,
# formats: ["rawHtml"], data.rawHtml, metadata.statusCode, maxAge and parsers: [].
# https://docs.firecrawl.dev/features/scrape and
# https://docs.firecrawl.dev/features/enhanced-mode price this
# request at 1 credit, including automatic proxy escalation. Disable file parsers
# to prevent per-page PDF charges. No actions or LLM formats are requested.
# https://docs.firecrawl.dev/api-reference/endpoint/credit-usage reports
# team-wide remainingCredits, shared with other work. Scrape has no documented
# total creditsUsed field. Reserve the documented
# maximum before every request, including timeouts/errors, and never refund it.
FIRECRAWL_CREDITS_PER_CALL = 1
FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"


def firecrawl_allowed(url: str) -> bool:
    try:
        parsed = urlsplit(canonical_url(url))
        return (
            parsed.scheme in {"http", "https"}
            and parsed.hostname in FIRECRAWL_HOSTS
            and parsed.username is None
            and parsed.password is None
            and parsed.port in {None, 80, 443}
        )
    except ValueError:
        return False


def _unique_response_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate Firecrawl response key")
        result[key] = value
    return result


def fallback_needed(result: FetchResult) -> bool:
    return result.outcome != "ok" and (result.outcome == "unreachable" or result.status == 403)


class FirecrawlFetcher:
    """One request per URL, with no retries and an independent hard per-run cap.

    Only FIRECRAWL_API_KEY supplies credentials. An injected transport lets tests
    exercise the actual HTTP boundary without any network or vendor spend.
    """

    def __init__(self, *, allowance: int, transport: httpx.BaseTransport | None = None) -> None:
        if type(allowance) is not int or allowance < 0:
            raise ValueError("Firecrawl allowance must be a nonnegative integer")
        self.allowance = min(allowance, FIRECRAWL_MAX_CREDITS_PER_RUN)
        self.credits_spent = 0
        self._key = os.environ.get("FIRECRAWL_API_KEY", "")
        self._transport = transport

    @property
    def can_fetch(self) -> bool:
        return bool(self._key) and self.credits_spent + FIRECRAWL_CREDITS_PER_CALL <= self.allowance

    def fetch(self, url: str) -> FetchResult:
        if not firecrawl_allowed(url):
            return FetchResult("unreachable", error="Firecrawl host is not allowed")
        if not self._key:
            return FetchResult("unreachable", error="FIRECRAWL_API_KEY is not configured")
        if not self.can_fetch:
            return FetchResult("unreachable", error="Firecrawl credit allowance exhausted")
        self.credits_spent += FIRECRAWL_CREDITS_PER_CALL
        try:
            with httpx.Client(
                transport=self._transport,
                follow_redirects=False,
                timeout=httpx.Timeout(65, connect=10),
                trust_env=False,
            ) as client:
                with client.stream(
                    "POST",
                    FIRECRAWL_ENDPOINT,
                    headers={"Authorization": f"Bearer {self._key}"},
                    json={
                        "url": canonical_url(url),
                        "formats": ["rawHtml"],
                        "onlyMainContent": False,
                        "maxAge": 0,
                        "parsers": [],
                        "timeout": 60000,
                        "skipTlsVerification": False,
                    },
                ) as response:
                    if not 200 <= response.status_code < 300:
                        return FetchResult(
                            "unreachable",
                            response.status_code,
                            error=f"Firecrawl HTTP {response.status_code}",
                        )
                    content = bytearray()
                    chunk_size = min(64 * 1024, MAX_FIRECRAWL_RESPONSE_BYTES + 1)
                    for chunk in response.iter_bytes(chunk_size=chunk_size):
                        if len(content) + len(chunk) > MAX_FIRECRAWL_RESPONSE_BYTES:
                            return FetchResult(
                                "unreachable", error="Firecrawl response exceeds 20 MiB"
                            )
                        content.extend(chunk)
            payload = json.loads(content, object_pairs_hook=_unique_response_object)
            if (
                not isinstance(payload, dict)
                or payload.get("success") is not True
                or payload.get("error")
            ):
                return FetchResult(
                    "unreachable", error="Firecrawl scrape failed or invalid response"
                )
            data = payload.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("rawHtml"), str):
                return FetchResult("unreachable", error="Firecrawl response has no raw HTML")
            metadata = data.get("metadata")
            if not isinstance(metadata, dict) or type(metadata.get("statusCode")) is not int:
                return FetchResult("unreachable", error="Firecrawl response has invalid metadata")
            status = metadata["statusCode"]
            if not 200 <= status < 300 or metadata.get("error"):
                return FetchResult(
                    "unreachable", status, error=f"Firecrawl target HTTP {status} or error"
                )
            body = data["rawHtml"].encode("utf-8")
            if not body.strip():
                return FetchResult("unreachable", error="Firecrawl returned empty raw HTML")
            if self._key in data["rawHtml"] or self._key.encode("utf-8") in content:
                return FetchResult("unreachable", error="Firecrawl response contains a credential")
            return FetchResult("ok", status, body=body, content_type="text/html", charset="utf-8")
        except (httpx.HTTPError, ValueError, UnicodeError, RecursionError):
            # Neither response error strings nor exception messages are safe to log.
            return FetchResult("unreachable", error="Firecrawl request failed or invalid JSON")
