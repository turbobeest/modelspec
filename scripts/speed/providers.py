"""Direct provider APIs for the speed harness: request shape and stream parsing.

Only first-party provider hosts are listed. A router is never a target:
``tests/test_speed_harness.py`` fails if a host outside ``FIRST_PARTY_HOSTS``
appears. Keys come from the environment variable each API names, are sent only
in a request header, and are never written to a result.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

FIRST_PARTY_HOSTS = frozenset({
    "api.anthropic.com",
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.x.ai",
    "api.deepseek.com",
    "api.z.ai",
})


@dataclass(frozen=True)
class Request:
    """One streaming request. ``headers`` holds the key; never serialise it."""

    api: str
    host: str
    path: str
    headers: Mapping[str, str] = field(repr=False)
    body: Mapping[str, Any]
    #: Where the call sits in the plan; the fixture transport keys timing on it.
    offering: str = ""
    workload: str = ""
    tag: str = ""


@dataclass
class StreamResult:
    """What one stream says about its own timing and billing."""

    first_content_s: float | None = None
    last_content_s: float | None = None
    content_events: int = 0
    input_tokens: int | None = None
    cached_input_tokens: int = 0
    billed_output_tokens: int | None = None
    reasoning_tokens: int = 0
    #: Thinking or reasoning deltas seen in the stream. Anthropic reports its
    #: thinking only this way, inside ``output_tokens``.
    reasoning_events: int = 0
    error: str | None = None

    @property
    def visible_tokens(self) -> int | None:
        if self.billed_output_tokens is None:
            return None
        return self.billed_output_tokens - self.reasoning_tokens

    def feed(self, t: float, visible: bool) -> None:
        if visible:
            if self.first_content_s is None:
                self.first_content_s = t
            self.last_content_s = t
            self.content_events += 1


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


# ── Anthropic Messages ────────────────────────────────────────────────────


def _anthropic_body(model: str, prompt: str, max_tokens: int, params: Mapping) -> dict:
    return {"model": model, "max_tokens": max_tokens, "stream": True, "temperature": 0,
            "messages": [{"role": "user", "content": prompt}], **params}


def _anthropic_headers(key: str) -> dict[str, str]:
    return {"x-api-key": key, "anthropic-version": "2023-06-01",
            "content-type": "application/json"}


def _anthropic_event(result: StreamResult, t: float, event: Mapping[str, Any]) -> None:
    kind = event.get("type")
    if kind == "message_start":
        usage = event.get("message", {}).get("usage", {})
        result.input_tokens = _int(usage.get("input_tokens"))
        result.cached_input_tokens = _int(usage.get("cache_read_input_tokens")) or 0
    elif kind == "content_block_delta":
        delta = event.get("delta", {})
        result.feed(t, delta.get("type") == "text_delta" and bool(delta.get("text")))
        result.reasoning_events += delta.get("type") == "thinking_delta"
    elif kind == "message_delta":
        result.billed_output_tokens = _int(event.get("usage", {}).get("output_tokens"))
    elif kind == "error":
        result.error = str(event.get("error", {}).get("type") or "error")


# ── OpenAI-compatible Chat Completions (OpenAI, xAI, DeepSeek, Z.ai) ────────


def _chat_body(model: str, prompt: str, max_tokens: int, params: Mapping) -> dict:
    return {"model": model, "stream": True, "stream_options": {"include_usage": True},
            "max_completion_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}], **params}


def _chat_body_max_tokens(model: str, prompt: str, max_tokens: int, params: Mapping) -> dict:
    body = _chat_body(model, prompt, max_tokens, params)
    body["max_tokens"] = body.pop("max_completion_tokens")
    return body


def _bearer(key: str) -> dict[str, str]:
    return {"authorization": f"Bearer {key}", "content-type": "application/json"}


def _chat_event(result: StreamResult, t: float, event: Mapping[str, Any]) -> None:
    if "error" in event:
        result.error = str(event["error"].get("type") or event["error"].get("code") or "error")
        return
    for choice in event.get("choices") or []:
        delta = choice.get("delta") or {}
        result.feed(t, bool(delta.get("content")))
        result.reasoning_events += bool(delta.get("reasoning_content") or delta.get("reasoning"))
    usage = event.get("usage")
    if usage:
        result.input_tokens = _int(usage.get("prompt_tokens"))
        result.billed_output_tokens = _int(usage.get("completion_tokens"))
        details = usage.get("completion_tokens_details") or {}
        result.reasoning_tokens = _int(details.get("reasoning_tokens")) or 0
        prompt_details = usage.get("prompt_tokens_details") or {}
        result.cached_input_tokens = (_int(prompt_details.get("cached_tokens"))
                                      or _int(usage.get("prompt_cache_hit_tokens")) or 0)


# ── Gemini API ────────────────────────────────────────────────────────────


def _gemini_body(model: str, prompt: str, max_tokens: int, params: Mapping) -> dict:
    config = {"maxOutputTokens": max_tokens, "temperature": 0, **params}
    return {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": config}


def _gemini_headers(key: str) -> dict[str, str]:
    return {"x-goog-api-key": key, "content-type": "application/json"}


def _gemini_event(result: StreamResult, t: float, event: Mapping[str, Any]) -> None:
    if "error" in event:
        result.error = str(event["error"].get("status") or "error")
        return
    for candidate in event.get("candidates") or []:
        parts = (candidate.get("content") or {}).get("parts") or []
        result.feed(t, any(p.get("text") and not p.get("thought") for p in parts))
        result.reasoning_events += any(p.get("thought") for p in parts)
    usage = event.get("usageMetadata")
    if usage:
        result.input_tokens = _int(usage.get("promptTokenCount"))
        thoughts = _int(usage.get("thoughtsTokenCount")) or 0
        candidates = _int(usage.get("candidatesTokenCount"))
        result.reasoning_tokens = thoughts
        result.billed_output_tokens = None if candidates is None else candidates + thoughts
        result.cached_input_tokens = _int(usage.get("cachedContentTokenCount")) or 0


# ── the registry of APIs ──────────────────────────────────────────────────


@dataclass(frozen=True)
class Api:
    id: str
    host: str
    env: str
    stream_path: Callable[[str], str]
    #: A free endpoint listing the account's models, for ``preflight``.
    models_path: str | None
    body: Callable[[str, str, int, Mapping], dict]
    headers: Callable[[str], dict[str, str]]
    event: Callable[[StreamResult, float, Mapping[str, Any]], None]

    def request(self, key: str, model: str, prompt: str, max_tokens: int,
                params: Mapping | None = None, **where: Any) -> Request:
        return Request(self.id, self.host, self.stream_path(model), self.headers(key),
                       self.body(model, prompt, max_tokens, params or {}), **where)

    def parse(self, events: Iterable[tuple[float, str]]) -> StreamResult:
        """Read ``(seconds after send, SSE data payload)`` pairs into a result."""
        result = StreamResult()
        for t, payload in events:
            if payload == "[DONE]":
                break
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                result.error = "unparseable event"
                continue
            self.event(result, t, event)
        return result


APIS: dict[str, Api] = {
    "anthropic": Api("anthropic", "api.anthropic.com", "ANTHROPIC_API_KEY",
                     lambda m: "/v1/messages", "/v1/models",
                     _anthropic_body, _anthropic_headers, _anthropic_event),
    "openai": Api("openai", "api.openai.com", "OPENAI_API_KEY",
                  lambda m: "/v1/chat/completions", "/v1/models",
                  _chat_body, _bearer, _chat_event),
    "gemini": Api("gemini", "generativelanguage.googleapis.com", "GEMINI_API_KEY",
                  lambda m: f"/v1beta/models/{m}:streamGenerateContent?alt=sse",
                  "/v1beta/models", _gemini_body, _gemini_headers, _gemini_event),
    "xai": Api("xai", "api.x.ai", "XAI_API_KEY",
               lambda m: "/v1/chat/completions", "/v1/models",
               _chat_body_max_tokens, _bearer, _chat_event),
    "deepseek": Api("deepseek", "api.deepseek.com", "DEEPSEEK_API_KEY",
                    lambda m: "/chat/completions", "/models",
                    _chat_body_max_tokens, _bearer, _chat_event),
    "zai": Api("zai", "api.z.ai", "ZAI_API_KEY",
               lambda m: "/api/paas/v4/chat/completions", None,
               _chat_body_max_tokens, _bearer, _chat_event),
}
