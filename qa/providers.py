"""Plain HTTP tool calling for the vendors' public APIs. No implicit retries."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

KEY_ENV = {"claude": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}


class SpendLimitError(Exception):
    """The next paid call cannot fit in the remaining reservation."""


class ProviderError(Exception):
    """A vendor failed, refused, or omitted billable usage."""


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


@dataclass
class Reply:
    text: str
    calls: list[dict]
    tokens_in: int
    tokens_out: int
    cost_usd: float = 0.0


def _arguments(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value  # Return malformed arguments to the agent as a validation error.
    return value


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
    ):
        self.family, self.model, self.system = family, model, system
        self.tools, self.budget, self.price = tools, budget, price
        self.max_output, self.client = max_output, client
        self.ceiling_price = ceiling_price or price
        self.key = os.environ.get(KEY_ENV[family])
        if not self.key:
            raise ValueError(f"Missing {KEY_ENV[family]}")
        if family == "gemini":
            self.history = [{"role": "user", "parts": [{"text": request}]}]
        else:
            self.history = [{"role": "user", "content": request}]

    def payload(self) -> dict:
        if self.family == "claude":
            return {
                "model": self.model,
                "system": self.system,
                "messages": self.history,
                "tools": self.tools,
                "max_tokens": self.max_output,
            }
        if self.family == "openai":
            functions = [
                {
                    "type": "function",
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                    "strict": False,
                }
                for t in self.tools
            ]
            return {
                "model": self.model,
                "instructions": self.system,
                "input": self.history,
                "tools": functions,
                "max_output_tokens": self.max_output,
                "store": False,
                "reasoning": {"effort": "low"},
                "include": ["reasoning.encrypted_content"],
            }
        functions = [
            {
                "name": t["name"],
                "description": t["description"],
                "parametersJsonSchema": t["input_schema"],
            }
            for t in self.tools
        ]
        payload = {
            "systemInstruction": {"parts": [{"text": self.system}]},
            "contents": self.history,
            "generationConfig": {"maxOutputTokens": self.max_output},
        }
        if functions:
            payload["tools"] = [{"functionDeclarations": functions}]
        return payload

    def step(self) -> Reply:
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
        try:
            response = self.client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                # Never include a URL/query/header or vendor body in exceptions.
                raise ProviderError(f"{self.family} HTTP {response.status_code}")
            data = response.json()
            reply = self.decode(data)
            reply.cost_usd = self.budget.settle(
                reserved,
                reply.tokens_in,
                reply.tokens_out,
                self.ceiling_price if reply.tokens_in > 200_000 else self.price,
            )
            return reply
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
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
