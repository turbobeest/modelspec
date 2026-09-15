"""Stream parsers: timestamped CLI events -> model time and tool time.

Input is a list of `(t, event)` where `t` is the harness's monotonic receipt
time in seconds relative to process start, and `event` is one parsed JSON line.
Neither CLI puts timestamps on its events, so every interval here is
*harness-observed line-receipt time*. It includes CLI-internal overhead and
stdout buffering, and it is not a per-request server timing.

State machine shared by the parsers:
- `startup`: process start to the first event.
- `model`: from the first event (or from the receipt of the last pending tool
  result) until the model's output requests a tool.
- `tool`: from the tool request until every pending tool call has a result.
- anything after the final result event is `shutdown`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Timing:
    startup_s: float = 0.0
    model_s: float | None = 0.0
    tool_s: float | None = 0.0
    shutdown_s: float = 0.0
    turns: int = 0
    tool_calls: int = 0
    tokens_in: int | None = None
    tokens_out: int | None = None
    cli_reported: dict = field(default_factory=dict)
    final_ok: bool | None = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        d = asdict(self)
        for k in ("startup_s", "model_s", "tool_s", "shutdown_s"):
            d[k] = None if d[k] is None else round(d[k], 3)
        return d


class _Clock:
    def __init__(self, timing: Timing):
        self.t = timing
        self.state = "startup"
        self.since = 0.0

    def switch(self, new: str, now: float) -> None:
        span = max(0.0, now - self.since)
        attr = f"{self.state}_s"
        setattr(self.t, attr, getattr(self.t, attr) + span)
        self.state, self.since = new, now


def parse_claude(events: list[tuple[float, dict]], end: float) -> Timing:
    """`claude -p --output-format stream-json --verbose`.

    assistant events carry one content block each; a `tool_use` block opens a
    tool call, a user event with `tool_result` closes it. The result event
    carries CLI-reported `duration_ms`, `duration_api_ms`, `num_turns`, usage.
    """
    timing, clock, pending = Timing(), None, set()
    for now, ev in events:
        if clock is None:
            clock = _Clock(timing)
            clock.switch("model", now)
        kind = ev.get("type")
        if kind == "assistant":
            blocks = ev.get("message", {}).get("content", [])
            ids = [b.get("id") for b in blocks if b.get("type") == "tool_use"]
            if ids:
                if not pending:
                    timing.turns += 1
                    clock.switch("tool", now)
                pending.update(ids)
                timing.tool_calls += len(ids)
        elif kind == "user":
            blocks = ev.get("message", {}).get("content", [])
            if isinstance(blocks, list):
                for b in blocks:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        pending.discard(b.get("tool_use_id"))
                if not pending and clock.state == "tool":
                    clock.switch("model", now)
        elif kind == "result":
            timing.turns += 1  # the final model turn that produced the answer
            clock.switch("shutdown", now)
            usage = ev.get("usage") or {}
            timing.tokens_in = sum(usage.get(k) or 0 for k in (
                "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")) or None
            timing.tokens_out = usage.get("output_tokens")
            timing.final_ok = not ev.get("is_error", False)
            timing.cli_reported = {k: ev.get(k) for k in (
                "duration_ms", "duration_api_ms", "num_turns", "subtype", "total_cost_usd") if k in ev}
    if clock is None:
        timing.startup_s = end
        timing.notes.append("no events")
    else:
        clock.switch("shutdown" if clock.state == "shutdown" else clock.state, end)
        if clock.state != "shutdown":
            timing.notes.append(f"stream ended in state {clock.state} without a result event")
    return timing


def parse_unverified(events: list[tuple[float, dict]], end: float) -> Timing:
    """For harnesses with no recorded, verified event stream (Grok, Codex, Gemini
    as of the MODEL-60 smoke). Total time only; the model/tool split is
    left null rather than guessed."""
    timing = Timing()
    timing.model_s = timing.tool_s = None
    timing.startup_s = events[0][0] if events else end
    timing.notes.append("model/tool split not derived: no verified parser for this event stream")
    return timing


def parse_opencode(events: list[tuple[float, dict]], end: float) -> Timing:
    """`opencode run --format json`.

    Every event carries an epoch-ms `timestamp`; each tool part carries
    `state.time.start/end` in epoch ms, written by opencode itself. A step is
    `step_start` .. `step_finish` (one model request plus the tools it called).
    tool_s = sum of tool `state.time` spans (CLI-reported, not receipt time).
    model_s = sum of step spans (by event timestamp) minus the tool spans inside them.
    startup_s = process start to the first step_start receipt; on a cold Ollama
    model this includes loading the model on the inference host.
    """
    timing = Timing()
    step_open, step_tool_ms, first = None, 0, None
    model_ms = tool_ms = 0
    last_t = None
    for now, ev in events:
        kind, part = ev.get("type"), ev.get("part") or {}
        if kind == "step_start":
            first = now if first is None else first
            step_open, step_tool_ms = ev.get("timestamp"), 0
        elif kind == "tool_use":
            span = (part.get("state") or {}).get("time") or {}
            if "start" in span and "end" in span:
                step_tool_ms += span["end"] - span["start"]
            timing.tool_calls += 1
        elif kind == "step_finish" and step_open is not None:
            timing.turns += 1
            model_ms += max(0, ev.get("timestamp", step_open) - step_open - step_tool_ms)
            tool_ms += step_tool_ms
            tokens = part.get("tokens") or {}
            timing.tokens_in = (timing.tokens_in or 0) + (tokens.get("input") or 0)
            timing.tokens_out = (timing.tokens_out or 0) + (tokens.get("output") or 0) + (tokens.get("reasoning") or 0)
            step_open, last_t = None, now
            timing.final_ok = part.get("reason") == "stop" if part.get("reason") else timing.final_ok
        elif kind == "error":
            timing.notes.append("error event in stream")
            timing.final_ok = False
    if first is None:
        timing.model_s = timing.tool_s = None
        timing.startup_s = end
        timing.notes.append("no steps in stream")
        return timing
    timing.startup_s = first
    timing.model_s = model_ms / 1000
    timing.tool_s = tool_ms / 1000
    timing.shutdown_s = max(0.0, end - (last_t or end))
    if step_open is not None:
        timing.notes.append("stream ended inside an open step")
    return timing


PARSERS = {"claude": parse_claude, "opencode": parse_opencode, "unverified": parse_unverified}
