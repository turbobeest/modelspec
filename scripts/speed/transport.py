"""How a request reaches a provider, or a recorded stream stands in for one.

``LiveTransport`` opens a fresh TLS connection per request and times the
handshake separately, so time to first token starts when the request is
written, not when the socket opens. ``FixtureTransport`` replays a recorded
stream in the provider's own wire format on a synthetic timeline; it opens no
socket, so a dry run cannot spend.
"""

from __future__ import annotations

import http.client
import json
import math
import random
import ssl
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from scripts.speed.providers import APIS, Request

FIXTURES = Path(__file__).with_name("fixtures")


@dataclass
class Exchange:
    status: int
    connect_s: float
    #: ``(seconds after the request was written, SSE data payload)``.
    events: Iterator[tuple[float, str]]
    error_body: str | None = None


class Transport(Protocol):
    provenance: str

    def send(self, request: Request) -> Exchange: ...


def _sse_payloads(lines: Iterator[bytes], sent: float) -> Iterator[tuple[float, str]]:
    for raw in lines:
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if line.startswith("data:"):
            yield time.perf_counter() - sent, line[5:].strip()


class LiveTransport:
    provenance = "live"

    def __init__(self, timeout_s: float = 180.0, port: int | None = None,
                 context: ssl.SSLContext | None = None, tls: bool = True):
        self.timeout_s = timeout_s
        self.port = port
        self.context = context
        self.tls = tls

    def _connection(self, host: str) -> http.client.HTTPConnection:
        if self.tls:
            return http.client.HTTPSConnection(host, self.port, timeout=self.timeout_s,
                                               context=self.context)
        return http.client.HTTPConnection(host, self.port, timeout=self.timeout_s)

    def send(self, request: Request) -> Exchange:
        connection = self._connection(request.host)
        opened = time.perf_counter()
        connection.connect()
        connect_s = time.perf_counter() - opened
        body = json.dumps(request.body).encode("utf-8")
        sent = time.perf_counter()
        connection.request("POST", request.path, body=body, headers=dict(request.headers))
        response = connection.getresponse()
        if response.status != 200:
            detail = response.read(4096).decode("utf-8", "replace")
            connection.close()
            return Exchange(response.status, connect_s, iter(()), detail)

        def events() -> Iterator[tuple[float, str]]:
            try:
                yield from _sse_payloads(iter(response.readline, b""), sent)
            finally:
                connection.close()

        return Exchange(200, connect_s, events())

    def get_json(self, host: str, path: str, headers: Mapping[str, str]) -> tuple[int, object]:
        """A free GET (a model list), for preflight."""
        connection = self._connection(host)
        try:
            connection.request("GET", path, headers=dict(headers))
            response = connection.getresponse()
            raw = response.read()
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw.decode("utf-8", "replace")[:500]
        finally:
            connection.close()


@dataclass(frozen=True)
class Profile:
    """A fixture offering's simulated median speed."""

    ttft_ms: float
    tokens_per_s: float


class FixtureTransport:
    """Replays ``fixtures/<api>.jsonl`` with each offering's profiled timing.

    Each call's timing is jittered by a seed drawn from its offering, workload
    and nonce, so a dry run produces a spread for the statistics to summarise
    and, with a deterministic nonce, is identical on every run.
    """

    provenance = "fixture"

    def __init__(self, profiles: Mapping[str, Profile], *, seed: int = 212,
                 fixtures: Path = FIXTURES):
        self.profiles = dict(profiles)
        self.seed = seed
        self.fixtures = fixtures
        self.calls = 0

    def _payloads(self, api: str) -> list[str]:
        wire = api if api in ("anthropic", "gemini") else "chat"
        path = self.fixtures / f"{wire}.jsonl"
        return [json.loads(line)["data"] for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def send(self, request: Request) -> Exchange:
        self.calls += 1
        profile = self.profiles[request.offering]
        rng = random.Random(f"{self.seed}|{request.offering}|{request.workload}|{request.tag}")
        ttft = profile.ttft_ms / 1000 * math.exp(rng.gauss(0, 0.2))
        rate = profile.tokens_per_s * math.exp(rng.gauss(0, 0.1))
        payloads = self._payloads(request.api)
        api = APIS[request.api]
        visible = [api.parse([(0.0, p)]).content_events > 0 for p in payloads]
        tokens = api.parse((0.0, p) for p in payloads).visible_tokens or 2
        events = max(2, sum(visible))
        # Each event carries tokens / events tokens, arriving at ``rate``.
        span = (events - 1) * tokens / events / rate
        last = events - 1
        timed: list[tuple[float, str]] = []
        k = 0
        for payload, is_content in zip(payloads, visible):
            if is_content:
                timed.append((ttft + span * k / last, payload))
                k += 1
            else:
                timed.append((ttft * 0.9 if k == 0 else ttft + span, payload))
        return Exchange(200, 0.05, iter(timed))
