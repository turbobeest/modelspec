"""Plain HTTP tool calling for the vendors' public APIs. Explicit, budgeted Gemini retries."""

from __future__ import annotations

import json
import os
import re
from random import uniform
from time import sleep
from dataclasses import dataclass, field
from typing import Any

import httpx

from qa.schemas import provider_schema

GEMINI_MAX_ATTEMPTS = 3

KEY_ENV = {"claude": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}


class SpendLimitError(Exception):
    """The next paid call cannot fit in the remaining reservation."""


class ProviderError(Exception):
    """A vendor failed, refused, or omitted billable usage."""

    def __init__(self, summary: str, details: dict | None = None):
        super().__init__(summary)
        # Only the private run record may consume these details. str(exc) stays safe.
        self.details = details


def redact(text: str) -> str:
    for name in (*KEY_ENV.values(), "MODELSPEC_API_KEY"):
        secret = os.environ.get(name)
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return re.sub(
        r"\b(?:(?:sk|rk|ghp|gho|ghs|ghu|github_pat|xox[abpr]|hf|glpat|msk)[-_]"
        r"[A-Za-z0-9_-]{8,}|AIza[A-Za-z0-9_-]{8,}|ya29\.[A-Za-z0-9_.-]{10,}"
        r"|(?:live|test)_[A-Za-z0-9]{16,}|(?:AKIA|ASIA)[0-9A-Z]{12,}|Bearer\s+\S+)",
        "[REDACTED]",
        text,
        flags=re.I,
    )


MAX_RETRY_DELAY_S = 65.0


def _retry_delay(response: httpx.Response) -> float | None:
    """The wait a 429/503 asks for: Retry-After, or Gemini's RetryInfo.retryDelay ("37s")."""
    header = response.headers.get("retry-after", "")
    if header.replace(".", "", 1).isdigit():
        return min(float(header), MAX_RETRY_DELAY_S)
    try:
        data = response.json()
    except ValueError:
        return None
    error = data.get("error") if isinstance(data, dict) else None
    details = error.get("details") if isinstance(error, dict) else None
    for detail in details if isinstance(details, list) else ():
        delay = detail.get("retryDelay") if isinstance(detail, dict) else None
        if isinstance(delay, str) and delay.endswith("s"):
            try:
                return min(float(delay[:-1]), MAX_RETRY_DELAY_S)
            except ValueError:
                return None
    return None


def _error_details(response: httpx.Response) -> tuple[dict, bool]:
    """Extract only the error fields, never headers, URLs or the full body."""
    try:
        data = response.json()
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    error = data.get("error", {})
    if not isinstance(error, dict):
        error = {}
    details = {"http_status": response.status_code}
    for key, value in (
        ("type", error.get("type", error.get("status"))),
        ("message", error.get("message")),
    ):
        if isinstance(value, str):
            details[key] = redact(value)[:300]
    # A rejected request is free unless the response indicates possible usage.
    # Unexpected usage shapes and request timeouts retain the reservation.
    usage = data.get("usage", data.get("usageMetadata"))
    zero_usage = usage is None or (
        isinstance(usage, dict)
        and bool(usage)
        and all(type(v) is int and v == 0 for v in usage.values())
    )
    return details, zero_usage


@dataclass
class Budget:
    limit_usd: float
    spent_usd: float = 0.0
    calls: list[dict] = field(default_factory=list)
    halted: bool = False

    def reserve(self, payload: dict, model: str, price: dict, max_output: int) -> float:
        # UTF-8 bytes bound text tokens more conservatively than chars/4. Include
        # protocol/tool framing, and charge all input at the uncached ceiling rate.
        input_bound = len(json.dumps(payload, ensure_ascii=False).encode()) + 8192
        amount = (input_bound * price["input"] + max_output * price["output"]) / 1_000_000
        if self.halted or self.spent_usd + amount > self.limit_usd:
            raise SpendLimitError("Next call would exceed the configured spend cap")
        self.spent_usd += amount
        self.calls.append(
            {"model": model, "reserved_usd": amount, "cost_usd": amount, "usage_known": False}
        )
        return amount

    def settle(self, reserved: float, tokens_in: int, tokens_out: int, price: dict) -> float:
        cost = (tokens_in * price["input"] + tokens_out * price["output"]) / 1_000_000
        self.spent_usd += cost - reserved
        self.calls[-1].update(
            cost_usd=cost, usage_known=True, tokens_in=tokens_in, tokens_out=tokens_out
        )
        if cost > reserved:
            self.halted = True
            raise ProviderError("Vendor usage exceeded its reservation; refusing further calls")
        return cost

    def release(self, reserved: float) -> None:
        self.spent_usd -= reserved
        self.calls[-1].update(cost_usd=0.0, usage_known=True, tokens_in=0, tokens_out=0)


@dataclass
class Reply:
    text: str
    calls: list[dict]
    tokens_in: int
    tokens_out: int
    cost_usd: float = 0.0
    model: str | None = None


def _arguments(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value  # Return malformed arguments to the agent as a validation error.
    return value


def prepare_tools(tools: list[dict], family: str) -> list[dict]:
    return [t | {"input_schema": provider_schema(t["input_schema"], family)} for t in tools]


def initial_history(family: str, request: str) -> list[dict]:
    if family == "gemini":
        return [{"role": "user", "parts": [{"text": request}]}]
    return [{"role": "user", "content": request}]


def request_payload(family: str, model: str, system: str, history: list[dict],
                    tools: list[dict], max_output: int) -> dict:
    """The exact wire body, shared by live calls and credential-free offline accounting."""
    if family == "claude":
        return {"model": model, "system": system, "messages": history,
                "tools": tools, "max_tokens": max_output}
    if family == "openai":
        functions = [{"type": "function", "name": t["name"], "description": t["description"],
                      "parameters": t["input_schema"], "strict": False} for t in tools]
        return {"model": model, "instructions": system, "input": history, "tools": functions,
                "max_output_tokens": max_output, "store": False, "reasoning": {"effort": "low"},
                "include": ["reasoning.encrypted_content"]}
    if family != "gemini":
        raise ValueError("Unsupported provider family")
    functions = [{"name": t["name"], "description": t["description"],
                  "parametersJsonSchema": t["input_schema"]} for t in tools]
    payload = {"systemInstruction": {"parts": [{"text": system}]}, "contents": history,
               "generationConfig": {"maxOutputTokens": max_output}}
    if functions:
        payload["tools"] = [{"functionDeclarations": functions}]
    return payload


def first_request(family: str, model: str, system: str, request: str,
                  tools: list[dict], max_output: int) -> dict:
    return request_payload(family, model, system, initial_history(family, request),
                           prepare_tools(tools, family), max_output)


class HttpAgent:
    """Retain native assistant blocks, including reasoning and thought signatures."""

    def __init__(
        self,
        family: str,
        model: str,
        system: str,
        request: str,
        tools: list[dict],
        budget: Budget,
        price: dict,
        max_output: int,
        client: httpx.Client,
        ceiling_price: dict | None = None,
        fallback: dict | None = None,
    ):
        self.family, self.model, self.system = family, model, system
        if any(not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", t["name"]) for t in tools):
            raise ValueError(
                "Tool names must contain 1 to 64 letters, digits, underscores or hyphens"
            )
        if type(max_output) is not int or max_output < (16 if family == "openai" else 1):
            raise ValueError("Output token limit is below the provider minimum")
        if not model.strip() or not request.strip():
            raise ValueError("Model and initial user message must be nonempty")
        self.tools = prepare_tools(tools, family)
        self.budget, self.price = budget, price
        self.max_output, self.client = max_output, client
        self.ceiling_price = ceiling_price or price
        self.fallback = fallback if family == "gemini" else None
        self.key = os.environ.get(KEY_ENV[family])
        if not self.key:
            raise ValueError(f"Missing {KEY_ENV[family]}")
        self.history = initial_history(family, request)

    def payload(self) -> dict:
        return request_payload(self.family, self.model, self.system, self.history,
                               self.tools, self.max_output)

    def _before_retry(self, attempt: int, attempts: int, hinted: float | None = None) -> None:
        # The final attempt may use a different model only before any reply:
        # thought signatures belong to their model.
        if attempt + 1 == attempts - 1 and self.fallback and len(self.history) == 1:
            self.model = self.fallback["model"]
            self.price = self.fallback["price"]
            self.ceiling_price = self.fallback["ceiling_price"]
        # A per-minute quota needs the wait the provider names, not a 1-3 s backoff.
        sleep(max(2**attempt + uniform(0, 1), hinted or 0))

    def step(self) -> Reply:
        attempts = GEMINI_MAX_ATTEMPTS if self.family == "gemini" else 1
        for attempt in range(attempts):
            # Reserve separately for every wire request, including the fallback.
            # Unknown usage on an earlier attempt remains charged to the cap.
            payload = self.payload()
            reserved = self.budget.reserve(payload, self.model, self.ceiling_price, self.max_output)
            if self.family == "claude":
                url = "https://api.anthropic.com/v1/messages"
                headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
            elif self.family == "openai":
                url = "https://api.openai.com/v1/responses"
                headers = {"Authorization": f"Bearer {self.key}"}
            else:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.model}:generateContent"
                )
                headers = {"x-goog-api-key": self.key}
            self.last_model = self.model
            try:
                response = self.client.post(url, json=payload, headers=headers)
                if response.status_code >= 400:
                    details, zero_usage = _error_details(response)
                    if (
                        400 <= response.status_code < 500
                        and response.status_code != 408
                        and zero_usage
                    ):
                        self.budget.release(reserved)
                    if response.status_code in (429, 503) and attempt + 1 < attempts:
                        self._before_retry(attempt, attempts, _retry_delay(response))
                        continue
                    raise ProviderError(f"{self.family} HTTP {response.status_code}", details)
                data = response.json()
                reply = self.decode(data)
                reply.model = self.model
                reply.cost_usd = self.budget.settle(
                    reserved,
                    reply.tokens_in,
                    reply.tokens_out,
                    self.ceiling_price if reply.tokens_in > 200_000 else self.price,
                )
                return reply
            except httpx.TimeoutException as exc:
                # A timeout keeps its reservation charged, so retrying stays inside the cap.
                if attempt + 1 < attempts:
                    self._before_retry(attempt, attempts)
                    continue
                raise ProviderError(
                    f"{self.family} response or transport failed",
                    {"type": type(exc).__name__},
                ) from None
            except httpx.HTTPError as exc:
                raise ProviderError(
                    f"{self.family} response or transport failed",
                    {"type": type(exc).__name__},
                ) from None
            except (ValueError, KeyError, IndexError, TypeError):
                raise ProviderError(f"{self.family} response or transport failed") from None

    def decode(self, data: dict) -> Reply:
        if self.family == "claude":
            usage = data["usage"]
            tokens_in = (
                usage["input_tokens"]
                + usage.get("cache_read_input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
            )
            tokens_out = usage["output_tokens"]
            blocks = data["content"]
            self.history.append({"role": "assistant", "content": blocks})
            text = "".join(b.get("text", "") for b in blocks if b["type"] == "text")
            calls = [
                {"id": b["id"], "name": b["name"], "arguments": _arguments(b["input"])}
                for b in blocks
                if b["type"] == "tool_use"
            ]
        elif self.family == "openai":
            usage = data["usage"]
            tokens_in, tokens_out = usage["input_tokens"], usage["output_tokens"]
            blocks = data["output"]
            self.history.extend(blocks)
            text = "".join(
                c.get("text", "")
                for b in blocks
                if b["type"] == "message"
                for c in b.get("content", [])
                if c["type"] == "output_text"
            )
            calls = [
                {"id": b["call_id"], "name": b["name"], "arguments": _arguments(b["arguments"])}
                for b in blocks
                if b["type"] == "function_call"
            ]
        else:
            usage = data["usageMetadata"]
            tokens_in = usage["promptTokenCount"]
            tokens_out = usage.get("candidatesTokenCount", 0) + usage.get("thoughtsTokenCount", 0)
            content = data["candidates"][0]["content"]
            self.history.append(content)
            text = "".join(p.get("text", "") for p in content["parts"] if not p.get("thought"))
            calls = [
                {
                    "id": p["functionCall"].get("id", f"call-{i}"),
                    "name": p["functionCall"]["name"],
                    "arguments": _arguments(p["functionCall"].get("args", {})),
                }
                for i, p in enumerate(content["parts"])
                if "functionCall" in p
            ]
        if (
            not isinstance(tokens_in, int)
            or not isinstance(tokens_out, int)
            or tokens_in < 0
            or tokens_out < 0
        ):
            raise ProviderError("Invalid vendor token usage")
        return Reply(text, calls, tokens_in, tokens_out)

    def add_results(self, results: list[tuple[dict, dict]]) -> None:
        if self.family == "claude":
            self.history.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": c["id"],
                            "content": json.dumps(r),
                            "is_error": r["isError"],
                        }
                        for c, r in results
                    ],
                }
            )
        elif self.family == "openai":
            self.history.extend(
                {"type": "function_call_output", "call_id": c["id"], "output": json.dumps(r)}
                for c, r in results
            )
        else:
            self.history.append(
                {
                    "role": "user",
                    "parts": [
                        {"functionResponse": {"name": c["name"], "id": c["id"], "response": r}}
                        for c, r in results
                    ],
                }
            )
