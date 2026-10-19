import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import type { Spec } from "../adapter";
import { decisionSpecSchema } from "../adapter/contract";
import full from "../__fixtures__/live-assistant-balanced-full.json";
import vocabularyJson from "../__fixtures__/live-vocabulary.json";
import { vocabularySchema, realBaseSpec, type Vocabulary } from "../vocabulary";

const vocabulary = vocabularySchema.parse(vocabularyJson);
const spec = (value: Vocabulary): Spec => ({
  ...realBaseSpec(value), conds: [], boardWeights: { chat_preference: 0.6, "-offering.cost_per_task": 0.4 },
});
const json = (value: unknown, status = 200, headers?: HeadersInit) => new Response(JSON.stringify(value), { status, headers });
const pending = <T,>() => {
  let resolve: (value: T) => void = () => { throw new Error("Promise not initialized"); };
  const promise = new Promise<T>((done) => { resolve = done; });
  return { promise, resolve };
};

function mockNetwork(decide: (init: RequestInit | undefined) => Response | Promise<Response>, load = () => json(vocabulary)) {
  const fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/vocabulary.json")) return load();
    if (String(input).endsWith("/v1/decide")) return decide(init);
    throw new Error(`Unexpected request: ${input}`);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
const requests = (fetch: ReturnType<typeof mockNetwork>) => fetch.mock.calls.filter(([url]) => String(url).endsWith("/v1/decide"));
const body = (init?: RequestInit) => decisionSpecSchema.parse(JSON.parse(String(init?.body)));
const advance = async (milliseconds = 300) => {
  await act(async () => {});
  await act(async () => { await vi.advanceTimersByTimeAsync(milliseconds); });
};

beforeEach(() => { vi.resetModules(); vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

it("loads vocabulary, then sends summary and full with the same action and snapshot", async () => {
  const fetch = mockNetwork(() => json(full));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result, rerender } = renderHook(() => useSimpleDecision(spec));
  await advance();
  expect(requests(fetch).map(([, init]) => body(init).explain)).toEqual(["summary", "full"]);
  const calls = requests(fetch).map(([, init]) => new Headers(init?.headers));
  expect(calls[0].get("x-modelspec-intent")).toMatch(/^[A-Za-z0-9_-]{22}$/);
  expect(calls[1].get("x-modelspec-intent")).toBe(calls[0].get("x-modelspec-intent"));
  expect(calls.every((headers) => headers.get("X-ModelSpec-Snapshot") === vocabulary.snapshot)).toBe(true);
  expect(calls.every((headers) => !headers.has("X-ModelSpec-Turnstile"))).toBe(true);
  expect(result.current.decision?.decision_id).toBe(full.decision_id);
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  rerender();
  await advance();
  expect(requests(fetch)).toHaveLength(2);
});

it("keeps the summary visible when the full explanation fails", async () => {
  const details = pending<Response>();
  mockNetwork((init) => body(init).explain === "summary" ? json(full) : details.promise);
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  expect(result.current.decision?.decision_id).toBe(full.decision_id);
  expect(result.current.requestState).toEqual({ kind: "success", details: "loading" });
  await act(async () => { details.resolve(json({ error: "unavailable" }, 503)); });
  expect(result.current.decision?.decision_id).toBe(full.decision_id);
  expect(result.current.requestState).toEqual({ kind: "success", details: "unavailable" });
});

it("aborts a changed question and cannot display its delayed answer", async () => {
  const stale = pending<Response>();
  let firstSignal: AbortSignal | null | undefined;
  const fetch = mockNetwork((init) => {
    if (body(init).task_tokens?.input === vocabulary.default_task_tokens.input) {
      firstSignal = init?.signal;
      return stale.promise;
    }
    return json({ ...full, decision_id: "dec_1234567890abcdef12345678" });
  });
  const { useSimpleDecision, SIMPLE_DECISION_WATCHDOG_MS } = await import("../simple/useSimpleDecision");
  const { result, rerender } = renderHook(({ input }) => useSimpleDecision((value) => ({ ...spec(value), tokIn: input })), {
    initialProps: { input: vocabulary.default_task_tokens.input },
  });
  await advance();
  expect(requests(fetch)).toHaveLength(1);
  rerender({ input: 1234 });
  expect(firstSignal?.aborted).toBe(true);
  expect(result.current.decision).toBeNull();
  await advance();
  expect(result.current.decision?.decision_id).toBe("dec_1234567890abcdef12345678");
  await advance(SIMPLE_DECISION_WATCHDOG_MS);
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  await act(async () => { stale.resolve(json(full)); });
  expect(result.current.decision?.decision_id).toBe("dec_1234567890abcdef12345678");
});

it("refreshes human status when an open automatic tab requires verification", async () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  const fetch = mockNetwork(() => json({ error: { code: "human_challenge_required", message: "Verify this lookup." } }, 403));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  act(() => result.current.setGateStatus(false));
  await advance();
  expect(result.current.gateRefresh).toBe(1);
  expect(result.current.gateStatus).toBeNull();
  expect(result.current.decision).toBeNull();
  await advance();
  expect(requests(fetch)).toHaveLength(1);
});

it("fails closed while human status is unresolved and requires a new token after each edit", async () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  const fetch = mockNetwork(() => json(full, 200, { "x-modelspec-decisions-remaining": "19" }));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result, rerender } = renderHook(({ input }) => useSimpleDecision((value) => ({ ...spec(value), tokIn: input })), {
    initialProps: { input: 1000 },
  });
  await advance();
  await act(async () => { await result.current.lookup(); });
  expect(requests(fetch)).toHaveLength(0);
  act(() => result.current.setGateStatus(true));
  await advance();
  expect(requests(fetch)).toHaveLength(0);
  const remaining = vi.fn();
  let lookup: Promise<void>;
  act(() => { lookup = result.current.lookup("verified-token", remaining); });
  await advance();
  await act(async () => { await lookup; });
  expect(requests(fetch)).toHaveLength(2);
  expect(remaining).toHaveBeenCalledWith(19);
  const headers = requests(fetch).map(([, init]) => new Headers(init?.headers));
  expect(headers.every((value) => value.get("x-modelspec-turnstile") === "verified-token")).toBe(true);
  expect(headers[0].get("x-modelspec-intent")).toBe(headers[1].get("x-modelspec-intent"));
  rerender({ input: 2000 });
  await advance();
  expect(result.current.decision).toBeNull();
  expect(requests(fetch)).toHaveLength(2);
});

it("asks the latest edited question after status resolves to automatic lookups", async () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  const fetch = mockNetwork(() => json(full));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result, rerender } = renderHook(({ input }) => useSimpleDecision((value) => ({ ...spec(value), tokIn: input })), {
    initialProps: { input: 1000 },
  });
  await advance();
  rerender({ input: 2345 });
  act(() => result.current.setGateStatus(false));
  await advance();
  expect(requests(fetch).map(([, init]) => body(init).task_tokens?.input)).toEqual([2345, 2345]);
});

it("reloads a changed snapshot once and preserves its summary if full changes again", async () => {
  let loads = 0;
  const fetch = mockNetwork((init) => {
    const snapshot = new Headers(init?.headers).get("X-ModelSpec-Snapshot");
    return snapshot === vocabulary.snapshot || body(init).explain === "full"
      ? json({ error: { code: "snapshot_changed", message: "Reload vocabulary" } }, 409)
      : json(full);
  }, () => json({ ...vocabulary, snapshot: loads++ === 0 ? vocabulary.snapshot : "snap_reloaded" }));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  expect(loads).toBe(2);
  expect(requests(fetch)).toHaveLength(3);
  expect(result.current.vocabulary?.snapshot).toBe("snap_reloaded");
  expect(result.current.decision?.decision_id).toBe(full.decision_id);
  expect(result.current.requestState).toEqual({ kind: "success", details: "unavailable" });
});

it("reports the watchdog timeout and Retry starts a fresh action", async () => {
  let stalled = true;
  const fetch = mockNetwork(() => stalled ? new Promise<Response>(() => {}) : json(full));
  const { useSimpleDecision, SIMPLE_DECISION_WATCHDOG_MS } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  await advance(SIMPLE_DECISION_WATCHDOG_MS);
  expect(result.current.requestState).toMatchObject({ kind: "error", code: "timeout" });
  stalled = false;
  await act(async () => { await result.current.retry(); });
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  const intents = requests(fetch).map(([, init]) => new Headers(init?.headers).get("x-modelspec-intent"));
  expect(intents[0]).not.toBe(intents[1]);
  expect(intents[1]).toBe(intents[2]);
});

it("retries a failed vocabulary load and does not ask an unavailable template", async () => {
  let fail = true;
  const fetch = mockNetwork(() => json(full), () => fail ? json({}, 503) : json(vocabulary));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(() => null));
  await advance();
  expect(result.current.vocabularyState.kind).toBe("error");
  fail = false;
  act(() => result.current.retryVocabulary());
  await advance();
  expect(result.current.vocabularyState.kind).toBe("ready");
  expect(result.current.spec).toBeNull();
  expect(requests(fetch)).toHaveLength(0);
});

it("requires a new verified lookup when a snapshot changes the question instead of spending another admission", async () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  let loads = 0;
  const fetch = mockNetwork((init) => new Headers(init?.headers).get("X-ModelSpec-Snapshot") === vocabulary.snapshot
    ? json({ error: { code: "snapshot_changed", message: "Reload vocabulary" } }, 409)
    : json(full), () => json(loads++ === 0 ? vocabulary : {
      ...vocabulary, snapshot: "snap_reloaded", default_task_tokens: { input: 12345, output: 321 },
    }));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  act(() => result.current.setGateStatus(true));
  let lookup: Promise<void>;
  act(() => { lookup = result.current.lookup("verified-token"); });
  await advance(1000);
  await act(async () => { await lookup; });
  expect(requests(fetch)).toHaveLength(1);
  expect(result.current.requestState).toMatchObject({ kind: "error", code: "question_changed" });
  expect(result.current.decision).toBeNull();
  expect(result.current.spec?.tokIn).toBe(12345);
  await act(async () => { await result.current.retry(); });
  await advance();
  expect(requests(fetch)).toHaveLength(1);
  act(() => { lookup = result.current.lookup("new-verified-token"); });
  await advance();
  await act(async () => { await lookup; });
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  expect(requests(fetch).slice(1).map(([, init]) => body(init).task_tokens)).toEqual([
    { input: 12345, output: 321 }, { input: 12345, output: 321 },
  ]);
  expect(new Set(requests(fetch).map(([, init]) => new Headers(init?.headers).get("x-modelspec-intent"))).size).toBe(2);
});

it("clears a summary after a material full-response reload and lets automatic Retry ask the updated question", async () => {
  let loads = 0;
  const fetch = mockNetwork((init) => body(init).explain === "full"
    && new Headers(init?.headers).get("X-ModelSpec-Snapshot") === vocabulary.snapshot
    ? json({ error: { code: "snapshot_changed", message: "Reload vocabulary" } }, 409)
    : json(full), () => json(loads++ === 0 ? vocabulary : {
      ...vocabulary, snapshot: "snap_reloaded", default_task_tokens: { input: 4321, output: 123 },
    }));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision(spec));
  await advance();
  expect(result.current.requestState).toMatchObject({ kind: "error", code: "question_changed" });
  expect(result.current.decision).toBeNull();
  expect(requests(fetch)).toHaveLength(2);
  await act(async () => { await result.current.retry(); });
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  expect(result.current.answeredSpec?.tokIn).toBe(4321);
  expect(requests(fetch).map(([, init]) => body(init).explain)).toEqual(["summary", "full", "summary", "full"]);
  const intents = requests(fetch).map(([, init]) => new Headers(init?.headers).get("x-modelspec-intent"));
  expect(intents[0]).toBe(intents[1]);
  expect(intents[2]).toBe(intents[3]);
  expect(intents[0]).not.toBe(intents[2]);
});

it("keeps a verified action when refreshed UI metadata changes but its request stays identical", async () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  let loads = 0;
  const fetch = mockNetwork((init) => new Headers(init?.headers).get("X-ModelSpec-Snapshot") === vocabulary.snapshot
    ? json({ error: { code: "snapshot_changed", message: "Reload vocabulary" } }, 409)
    : json(full), () => json({ ...vocabulary, snapshot: loads++ === 0 ? vocabulary.snapshot : "snap_reloaded" }));
  const { useSimpleDecision } = await import("../simple/useSimpleDecision");
  const { result } = renderHook(() => useSimpleDecision((value) => ({
    ...spec(value), bench: value.snapshot === vocabulary.snapshot ? "old_benchmark" : "new_benchmark",
  })));
  await advance();
  act(() => result.current.setGateStatus(true));
  let lookup: Promise<void>;
  act(() => { lookup = result.current.lookup("verified-token"); });
  await advance(1000);
  await act(async () => { await lookup; });
  expect(result.current.requestState).toEqual({ kind: "success", details: "ready" });
  expect(result.current.answeredSpec?.bench).toBe("new_benchmark");
  const calls = requests(fetch);
  expect(calls.map(([, init]) => body(init).explain)).toEqual(["summary", "summary", "full"]);
  expect(new Set(calls.map(([, init]) => new Headers(init?.headers).get("x-modelspec-intent"))).size).toBe(1);
  expect(body(calls[0][1])).toEqual(body(calls[1][1]));
});
