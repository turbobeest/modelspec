"""Bounded, opt-in raw HTML fallback for the weekly price re-read."""

from __future__ import annotations

import json
import math
import os
from html import escape
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
FIRECRAWL_MIN_TEAM_BALANCE = 100
MAX_FIRECRAWL_RESPONSE_BYTES = 20 * 1024 * 1024
MAX_BALANCE_RESPONSE_BYTES = 64 * 1024

# https://docs.firecrawl.dev/api-reference/endpoint/scrape documents POST /v2/scrape,
# formats: ["rawHtml"], data.rawHtml, metadata.statusCode, maxAge and parsers: [].
# https://docs.firecrawl.dev/features/scrape and
# https://docs.firecrawl.dev/features/enhanced-mode price this
# request at 1 credit, including automatic proxy escalation. Disable file parsers
# to prevent per-page PDF charges. No actions or LLM formats are requested.
# https://docs.firecrawl.dev/api-reference/endpoint/credit-usage reports
# team-wide remainingCredits, shared with other work. This account read does not
# scrape a page or reserve a credit. Check it before every paid request, fail
# closed on an unreadable balance, and stop below FIRECRAWL_MIN_TEAM_BALANCE.
# The billing table at https://docs.firecrawl.dev/billing lists workload charges.
# Confirmed against the account route and balance-only controller, which do not
# debit credits: https://github.com/firecrawl/firecrawl/blob/main/apps/api/src/
# controllers/v2/credit-usage.ts and routes/v2.ts (read 2026-10-10).
# Scrape has no documented
# total creditsUsed field. Reserve the documented
# maximum before every request, including timeouts/errors, and never refund it.
FIRECRAWL_CREDITS_PER_CALL = 1
FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"
FIRECRAWL_BALANCE_ENDPOINT = "https://api.firecrawl.dev/v2/team/credit-usage"


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

    fake = False
    credits_per_call = FIRECRAWL_CREDITS_PER_CALL

    def __init__(self, *, allowance: int, transport: httpx.BaseTransport | None = None) -> None:
        if type(allowance) is not int or allowance < 0:
            raise ValueError("Firecrawl allowance must be a nonnegative integer")
        self.allowance = min(allowance, FIRECRAWL_MAX_CREDITS_PER_RUN)
        self.credits_spent = 0
        self.team_balance: int | float | None = None
        self._balance_error: str | None = None
        self._prepared = False
        self._key = os.environ.get("FIRECRAWL_API_KEY", "")
        self._transport = transport

    @property
    def can_fetch(self) -> bool:
        return self.stop_reason is None

    @property
    def stop_reason(self) -> str | None:
        if not self._key:
            return "FIRECRAWL_API_KEY is not configured"
        if self._balance_error:
            return self._balance_error
        if self.credits_spent + self.credits_per_call > self.allowance:
            return "Firecrawl credit allowance exhausted"
        return None

    def prepare(self) -> bool:
        """Read the shared balance before reservation; one check per scrape.

        Artifact writers call this before checkpointing the reservation. Direct
        fetch callers pass through the same check. A failed check stops the run.
        """
        if not self.can_fetch:
            return False
        if self._prepared:
            return True
        self.team_balance = None
        try:
            with httpx.Client(
                transport=self._transport,
                follow_redirects=False,
                timeout=httpx.Timeout(10),
                trust_env=False,
            ) as client:
                with client.stream(
                    "GET",
                    FIRECRAWL_BALANCE_ENDPOINT,
                    headers={"Authorization": f"Bearer {self._key}"},
                ) as response:
                    if not 200 <= response.status_code < 300:
                        self._balance_error = f"Firecrawl team balance HTTP {response.status_code}"
                        return False
                    content = bytearray()
                    for chunk in response.iter_bytes(chunk_size=4096):
                        if len(content) + len(chunk) > MAX_BALANCE_RESPONSE_BYTES:
                            raise ValueError("oversize balance response")
                        content.extend(chunk)
            payload = json.loads(content, object_pairs_hook=_unique_response_object)
            if (
                self._key.encode("utf-8") in content
                or not isinstance(payload, dict)
                or payload.get("success") is not True
                or payload.get("error")
                or not isinstance(payload.get("data"), dict)
            ):
                raise ValueError("invalid balance response")
            remaining = payload["data"].get("remainingCredits")
            if (
                type(remaining) not in {int, float}
                or remaining < 0
                or isinstance(remaining, float)
                and not math.isfinite(remaining)
            ):
                raise ValueError("invalid remainingCredits")
            self.team_balance = remaining
            if remaining < FIRECRAWL_MIN_TEAM_BALANCE:
                self._balance_error = "Firecrawl team balance below minimum of 100 credits"
                return False
        except httpx.TimeoutException:
            self._balance_error = "Firecrawl team balance read timed out"
            return False
        except httpx.HTTPError:
            self._balance_error = "Firecrawl team balance request failed"
            return False
        except (ValueError, UnicodeError, RecursionError):
            self._balance_error = "Firecrawl team balance response is invalid"
            return False
        self._prepared = True
        return True

    def fetch(self, url: str) -> FetchResult:
        if not firecrawl_allowed(url):
            return FetchResult("unreachable", error="Firecrawl host is not allowed")
        if not self.prepare():
            return FetchResult("unreachable", error=self.stop_reason)
        self._prepared = False
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


class FakeFirecrawlFetcher:
    """Deterministic demo HTML, without reading a key or constructing a client."""

    fake = True
    allowance = 0
    credits_spent = 0
    credits_per_call = 0
    team_balance = None
    stop_reason = None
    can_fetch = True

    def prepare(self) -> bool:
        return True

    def fetch(self, url: str) -> FetchResult:
        if not firecrawl_allowed(url):
            return FetchResult("unreachable", error="Firecrawl host is not allowed")
        html = (
            '<!doctype html><html><head><meta name="modelspec-fallback" content="fake">'
            "</head><body><h1>FAKE price fallback demo, not evidence</h1><p>"
            + escape(canonical_url(url))
            + "</p></body></html>"
        )
        return FetchResult(
            "ok", 200, body=html.encode("utf-8"), content_type="text/html", charset="utf-8"
        )
