"""Unit identifiers and scale factors shared by readers and admission."""
from __future__ import annotations

import re
from collections.abc import Mapping

#: Unit ID -> (dimension, factor to the dimension's base unit). IDs follow the
#: facet registry's ``units`` where one exists.
UNITS: Mapping[str, tuple[str, float]] = {
    "percent": ("ratio", 0.01),
    "fraction": ("ratio", 1.0),
    "tokens": ("tokens", 1.0),
    "k_tokens": ("tokens", 1e3),
    "m_tokens": ("tokens", 1e6),
    "usd_per_1m_tokens": ("usd_per_token", 1e-6),
    "usd_per_1k_tokens": ("usd_per_token", 1e-3),
    "usd_per_token": ("usd_per_token", 1.0),
    "milliseconds": ("seconds", 1e-3),
    "seconds": ("seconds", 1.0),
    "tokens_per_second": ("tokens_per_second", 1.0),
    "tokens_per_minute": ("tokens_per_minute", 1.0),
    "requests_per_minute": ("requests_per_minute", 1.0),
    "parameters": ("parameters", 1.0),
    "m_parameters": ("parameters", 1e6),
    "b_parameters": ("parameters", 1e9),
    "days": ("days", 1.0),
}

_UNIT_SPELLINGS = {
    "%": "percent", "percent": "percent", "pct": "percent", "per cent": "percent",
    "fraction": "fraction", "ratio": "fraction",
    "token": "tokens", "tokens": "tokens", "tok": "tokens",
    "ktok": "k_tokens", "mtok": "m_tokens",
    "ms": "milliseconds", "millisecond": "milliseconds", "milliseconds": "milliseconds",
    "s": "seconds", "sec": "seconds", "second": "seconds", "seconds": "seconds",
    "tokens/s": "tokens_per_second", "tok/s": "tokens_per_second",
    "tokens/sec": "tokens_per_second", "tokens/second": "tokens_per_second",
    "tokens/min": "tokens_per_minute", "tpm": "tokens_per_minute",
    "requests/min": "requests_per_minute", "rpm": "requests_per_minute",
    "parameter": "parameters", "parameters": "parameters", "params": "parameters",
    "day": "days", "days": "days",
    "usd/token": "usd_per_token",
}
_MAGNITUDE = {"k": "k", "thousand": "k", "m": "m", "million": "m", "b": "b", "billion": "b"}
_SCALED = re.compile(r"^(k|m|b|thousand|million|billion)\s*(tokens?|parameters?|params)$")
_PRICE = re.compile(r"^usd\s*/\s*(1\s*)?(k|m|thousand|million)\s*(tokens?|tok)?$")


def unit_id(text: str | None) -> str | None:
    """A unit spelling ("%", "K tokens", "$/1M tokens") as a unit ID, or ``None``.

    An unrecognised spelling is returned cleaned, so it still compares exactly.
    """
    if text is None:
        return None
    s = text.strip().casefold().replace("$", "usd ").replace(" per ", "/")
    s = re.sub(r"\s*/\s*", "/", re.sub(r"\s+", " ", s)).strip()
    if not s:
        return None
    if s in {"/1m tokens", "per 1m tokens", "per million tokens"}:
        return "usd_per_1m_tokens"
    if s in UNITS:
        return s
    if s in _UNIT_SPELLINGS:
        return _UNIT_SPELLINGS[s]
    if m := _SCALED.match(s):
        base = "tokens" if m.group(2).startswith("tok") else "parameters"
        return f"{_MAGNITUDE[m.group(1)]}_{base}"
    if m := _PRICE.match(s):
        return f"usd_per_1{_MAGNITUDE[m.group(2)]}_tokens"
    return s

