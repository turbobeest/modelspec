"""Answer-engine adapters for the visibility runs (MODEL-256).

Each adapter sends one prompt to an engine's own web-search API and reduces the
reply to an ``Answer``: the text, the URLs it cited, the searches it ran, and
what it cost. These are API surfaces, not the consumer apps: every run is
labelled ``surface=api`` and a report never presents it as what a buyer saw.

Keys are read per call with ``op read`` from the reference in the private
engine config, passed straight into a request header, and dropped. Nothing here
writes a key anywhere, and no key or vault reference lives in this repository.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import httpx

TIMEOUT = httpx.Timeout(120.0, connect=15.0)


class EngineUnavailable(RuntimeError):
    """The engine refused for a reason a retry won't fix today (quota, auth)."""


@dataclass(frozen=True)
class Citation:
    url: str
    domain: str
    title: str = ""


@dataclass
class Answer:
    text: str
    model_version: str
    citations: list[Citation] = field(default_factory=list)
    fanout_queries: list[str] = field(default_factory=list)
    searched: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    searches: int = 0
    reported_cost_usd: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


def domain_of(url: str, title: str = "") -> str:
    host = urlparse(url).hostname or ""
    # Gemini grounds through a Google redirect; its title carries the real domain.
    if host.endswith("vertexaisearch.cloud.google.com") and title:
        host = title
    return host.removeprefix("www.").lower()


def _citations(pairs: list[tuple[str, str]]) -> list[Citation]:
    seen: dict[str, Citation] = {}
    for url, title in pairs:
        if url and url not in seen:
            seen[url] = Citation(url=url, domain=domain_of(url, title), title=title)
    return list(seen.values())


def op_read(reference: str) -> str:
    """A secret from 1Password, never echoed."""
    out = subprocess.run(["op", "read", reference], capture_output=True, text=True, check=False)
    if out.returncode != 0 or not out.stdout.strip():
        raise EngineUnavailable(f"op read failed for the configured reference ({out.returncode})")
    return out.stdout.strip()


def _raise_for(response: httpx.Response, engine: str) -> None:
    if response.status_code in (401, 403, 429):
        detail = response.text[:200].replace("\n", " ")
        raise EngineUnavailable(f"{engine}: HTTP {response.status_code}: {detail}")
    response.raise_for_status()


# ── OpenAI Responses API with web_search ─────────────────────────────────────

def openai_request(model: str, prompt: str, max_output_tokens: int) -> dict[str, Any]:
    return {"model": model, "input": prompt, "tools": [{"type": "web_search"}],
            "max_output_tokens": max_output_tokens}


def openai_parse(body: Mapping[str, Any]) -> Answer:
    texts, pairs, queries, searches = [], [], [], 0
    for item in body.get("output", []):
        if item.get("type") == "web_search_call":
            searches += 1
            action = item.get("action") or {}
            queries += action.get("queries") or ([action["query"]] if action.get("query") else [])
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    texts.append(part.get("text", ""))
                    pairs += [(a.get("url", ""), a.get("title", "")) for a in part.get("annotations", [])
                              if a.get("type") == "url_citation"]
    usage = body.get("usage") or {}
    return Answer(text="\n".join(texts), model_version=body.get("model", ""),
                  citations=_citations(pairs), fanout_queries=queries, searched=searches > 0,
                  input_tokens=usage.get("input_tokens", 0), output_tokens=usage.get("output_tokens", 0),
                  searches=searches, raw=dict(body))


def openai_call(model: str, key: str, prompt: str, max_output_tokens: int) -> Answer:
    r = httpx.post("https://api.openai.com/v1/responses", timeout=TIMEOUT,
                   headers={"Authorization": f"Bearer {key}"},
                   json=openai_request(model, prompt, max_output_tokens))
    _raise_for(r, "openai")
    return openai_parse(r.json())


# ── Anthropic Messages API with the web search tool ──────────────────────────

ANTHROPIC_WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}


def anthropic_request(model: str, prompt: str, max_output_tokens: int) -> dict[str, Any]:
    return {"model": model, "max_tokens": max_output_tokens, "tools": [ANTHROPIC_WEB_SEARCH],
            "messages": [{"role": "user", "content": prompt}]}


def anthropic_parse(body: Mapping[str, Any]) -> Answer:
    texts, pairs, queries = [], [], []
    for block in body.get("content", []):
        kind = block.get("type")
        if kind == "server_tool_use" and block.get("name") == "web_search":
            if (block.get("input") or {}).get("query"):
                queries.append(block["input"]["query"])
        elif kind == "text":
            texts.append(block.get("text", ""))
            pairs += [(c.get("url", ""), c.get("title", "")) for c in block.get("citations") or []
                      if c.get("type") == "web_search_result_location"]
        elif kind == "web_search_tool_result" and isinstance(block.get("content"), list):
            pairs += [(r.get("url", ""), r.get("title", "")) for r in block["content"]
                      if r.get("type") == "web_search_result"]
    usage = body.get("usage") or {}
    searches = (usage.get("server_tool_use") or {}).get("web_search_requests", len(queries))
    return Answer(text="".join(texts), model_version=body.get("model", ""),
                  citations=_citations(pairs), fanout_queries=queries, searched=searches > 0,
                  input_tokens=usage.get("input_tokens", 0), output_tokens=usage.get("output_tokens", 0),
                  searches=searches, raw=dict(body))


def anthropic_call(model: str, key: str, prompt: str, max_output_tokens: int) -> Answer:
    r = httpx.post("https://api.anthropic.com/v1/messages", timeout=TIMEOUT,
                   headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                   json=anthropic_request(model, prompt, max_output_tokens))
    _raise_for(r, "anthropic")
    return anthropic_parse(r.json())


# ── Perplexity Sonar ─────────────────────────────────────────────────────────

def perplexity_request(model: str, prompt: str, max_output_tokens: int) -> dict[str, Any]:
    return {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max(16, max_output_tokens)}


def perplexity_parse(body: Mapping[str, Any]) -> Answer:
    choice = (body.get("choices") or [{}])[0]
    results = body.get("search_results") or []
    pairs = [(r.get("url", ""), r.get("title", "")) for r in results] or \
            [(url, "") for url in body.get("citations") or []]
    usage = body.get("usage") or {}
    cost = (usage.get("cost") or {}).get("total_cost")
    return Answer(text=(choice.get("message") or {}).get("content", ""), model_version=body.get("model", ""),
                  citations=_citations(pairs), searched=bool(pairs),
                  input_tokens=usage.get("prompt_tokens", 0), output_tokens=usage.get("completion_tokens", 0),
                  searches=1 if pairs else 0, reported_cost_usd=cost, raw=dict(body))


def perplexity_call(model: str, key: str, prompt: str, max_output_tokens: int) -> Answer:
    r = httpx.post("https://api.perplexity.ai/chat/completions", timeout=TIMEOUT,
                   headers={"Authorization": f"Bearer {key}"},
                   json=perplexity_request(model, prompt, max_output_tokens))
    _raise_for(r, "perplexity")
    return perplexity_parse(r.json())


# ── Gemini with Google Search grounding ──────────────────────────────────────

def gemini_request(model: str, prompt: str, max_output_tokens: int) -> dict[str, Any]:
    return {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}],
            "generationConfig": {"maxOutputTokens": max_output_tokens}}


def gemini_parse(body: Mapping[str, Any]) -> Answer:
    candidate = (body.get("candidates") or [{}])[0]
    parts = (candidate.get("content") or {}).get("parts") or []
    grounding = candidate.get("groundingMetadata") or {}
    pairs = [((c.get("web") or {}).get("uri", ""), (c.get("web") or {}).get("title", ""))
             for c in grounding.get("groundingChunks") or []]
    queries = list(grounding.get("webSearchQueries") or [])
    usage = body.get("usageMetadata") or {}
    return Answer(text="".join(p.get("text", "") for p in parts), model_version=body.get("modelVersion", ""),
                  citations=_citations(pairs), fanout_queries=queries, searched=bool(queries),
                  input_tokens=usage.get("promptTokenCount", 0), output_tokens=usage.get("candidatesTokenCount", 0),
                  searches=1 if queries else 0, raw=dict(body))


def gemini_call(model: str, key: str, prompt: str, max_output_tokens: int) -> Answer:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r = httpx.post(url, timeout=TIMEOUT, headers={"x-goog-api-key": key},
                   json=gemini_request(model, prompt, max_output_tokens))
    _raise_for(r, "gemini")
    return gemini_parse(r.json())


CALLS: dict[str, Callable[[str, str, str, int], Answer]] = {
    "openai": openai_call,
    "anthropic": anthropic_call,
    "perplexity": perplexity_call,
    "gemini": gemini_call,
}
