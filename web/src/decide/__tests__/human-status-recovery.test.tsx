import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import vocabulary from "../__fixtures__/live-vocabulary.json";

const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), {
  status,
  headers: { "content-type": "application/json" },
});
function stall(signal: AbortSignal | null | undefined): Promise<Response> {
  return new Promise((_resolve, reject) => {
    signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
  });
}

beforeEach(() => {
  vi.resetModules();
  vi.useFakeTimers();
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "public-test-key");
  window.turnstile = {
    render: vi.fn((_element, options) => {
      options.callback("single-use-token");
      return "widget";
    }),
    remove: vi.fn(),
  };
});

afterEach(() => {
  vi.useRealTimers();
  delete window.turnstile;
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

it("a stalled human-status fetch shows verification recovery and a retry can finish", async () => {
  let calls = 0;
  let signal: AbortSignal | null | undefined;
  vi.stubGlobal("fetch", vi.fn(async (_url: string, init?: RequestInit) => {
    calls += 1;
    signal = init?.signal;
    if (calls === 1) return stall(init?.signal);
    return json({ enabled: true, remaining: 12 });
  }));
  const onEnabled = vi.fn();
  const { HumanGate, HUMAN_STATUS_TIMEOUT_MS } = await import("../components/HumanGate");
  expect(HUMAN_STATUS_TIMEOUT_MS).toBe(15_000);
  render(<HumanGate onLookup={vi.fn()} onEnabled={onEnabled} />);
  await act(async () => {});
  await act(async () => { await vi.advanceTimersByTimeAsync(HUMAN_STATUS_TIMEOUT_MS - 1); });
  expect(screen.queryByRole("button", { name: "Retry verification" })).toBeNull();
  await act(async () => { await vi.advanceTimersByTimeAsync(1); });
  expect(signal?.aborted).toBe(true);
  expect(onEnabled).not.toHaveBeenCalled();
  expect(screen.getByRole("status")).toHaveTextContent("Manual decisions are temporarily unavailable. Please try again later.");
  fireEvent.click(screen.getByRole("button", { name: "Retry verification" }));
  await act(async () => {});
  expect(screen.getByText(/12 decisions remaining today/)).toBeVisible();
  expect(onEnabled).toHaveBeenCalledWith(true);
});

it("a stalled human-status body shows verification recovery", async () => {
  let signal: AbortSignal | null | undefined;
  vi.stubGlobal("fetch", vi.fn(async (_url: string, init?: RequestInit) => {
    signal = init?.signal;
    return new Response(new ReadableStream({ start() {} }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  }));
  const { HumanGate, HUMAN_STATUS_TIMEOUT_MS } = await import("../components/HumanGate");
  render(<HumanGate onLookup={vi.fn()} />);
  await act(async () => {});
  await act(async () => { await vi.advanceTimersByTimeAsync(HUMAN_STATUS_TIMEOUT_MS - 1); });
  expect(screen.queryByRole("button", { name: "Retry verification" })).toBeNull();
  await act(async () => { await vi.advanceTimersByTimeAsync(1); });
  expect(signal?.aborted).toBe(true);
  expect(screen.getByRole("button", { name: "Retry verification" })).toBeVisible();
  expect(screen.getByRole("status")).toHaveTextContent("Manual decisions are temporarily unavailable. Please try again later.");
});

it("the simple decide page recovers a stalled human-status exchange without a reload", async () => {
  let signal: AbortSignal | null | undefined;
  let statusCalls = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (String(url).endsWith("/v1/human-status")) {
      statusCalls += 1;
      signal = init?.signal;
      if (statusCalls === 1) return stall(init?.signal);
      return json({ enabled: true, remaining: 12 });
    }
    if (String(url).endsWith("/vocabulary.json")) return json(vocabulary);
    throw new Error(`Unexpected request ${url}`);
  }));
  const { default: SimpleApp } = await import("../simple/SimpleApp");
  const { HUMAN_STATUS_TIMEOUT_MS } = await import("../components/HumanGate");
  render(<SimpleApp />);
  await act(async () => {});
  await act(async () => { await vi.advanceTimersByTimeAsync(HUMAN_STATUS_TIMEOUT_MS - 1); });
  expect(screen.queryByRole("button", { name: "Retry verification" })).toBeNull();
  await act(async () => { await vi.advanceTimersByTimeAsync(1); });
  expect(signal?.aborted).toBe(true);
  expect(screen.getByRole("button", { name: "Retry verification" })).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Retry verification" }));
  await act(async () => {});
  expect(screen.getByText(/12 decisions remaining today/)).toBeVisible();
});
