import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { execFileSync } from "node:child_process";
import { z } from "zod";
import fixture from "../__fixtures__/full-decision.json";
import { json, routeFetch, realVocabulary, sentSpecs } from "./vocab-fixtures";

beforeEach(() => {
  vi.resetModules();
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "true");
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "public-test-key");
  window.turnstile = {
    render: vi.fn((_element, options) => { options.callback("single-use-token"); return "widget"; }),
    remove: vi.fn(),
  };
});
afterEach(() => {
  vi.useRealTimers();
  delete window.turnstile;
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

it("paces verified auxiliaries and cancels queued calls before fetch", async () => {
  vi.useFakeTimers();
  const fetch = vi.fn(async () => json(fixture));
  vi.stubGlobal("fetch", fetch);
  const { hostedEngine, decisionAction } = await import("../adapter/hosted");
  const options = decisionAction("token");
  const spec = { spec_version: 1, optimize: { max: "software_engineering" } } satisfies Parameters<typeof hostedEngine.decide>[0];
  await hostedEngine.decide(spec, options);
  expect(fetch).toHaveBeenCalledTimes(1);
  const controller = new AbortController();
  const queued = hostedEngine.decide(spec, { ...options, signal: controller.signal });
  const refusal = expect(queued).rejects.toMatchObject({ name: "AbortError" });
  controller.abort();
  await refusal;
  const next = hostedEngine.decide(spec, options);
  await vi.advanceTimersByTimeAsync(299);
  expect(fetch).toHaveBeenCalledTimes(1);
  await vi.advanceTimersByTimeAsync(1);
  await next;
  expect(fetch).toHaveBeenCalledTimes(2);
  await expect(hostedEngine.decide(spec, { ...options, signal: controller.signal }))
    .rejects.toMatchObject({ name: "AbortError" });
  expect(fetch).toHaveBeenCalledTimes(2);
});

it("shows the remaining allowance and consumes one token per manual lookup", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true, remaining: 19 })));
  const onLookup = vi.fn(async (_token: string, onRemaining: (remaining: number) => void) => onRemaining(18));
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={onLookup} />);
  expect(await screen.findByText(/19 decisions remaining today/)).toBeVisible();
  const button = screen.getByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  await waitFor(() => expect(onLookup).toHaveBeenCalledWith("single-use-token", expect.any(Function)));
  await waitFor(() => expect(window.turnstile?.remove).toHaveBeenCalledWith("widget"));
  await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledTimes(2));
});

it("shows the day-cap message and paid API/MCP link", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true, remaining: 0 })));
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={vi.fn()} />);
  expect(await screen.findByText(/used today's 20 manual decisions/)).toBeVisible();
  expect(screen.getByRole("link", { name: "paid API or MCP" })).toHaveAttribute("href", "/pricing/");
  expect(screen.getByRole("button", { name: "Look up this decision" })).toBeDisabled();
  expect(window.turnstile?.render).not.toHaveBeenCalled();
});

it("fails closed with an unavailable message when secrets are missing", async () => {
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true }, 503)));
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={vi.fn()} />);
  expect(await screen.findByText(/Manual decisions are temporarily unavailable/)).toBeVisible();
  expect(screen.queryByRole("button", { name: "Look up this decision" })).not.toBeInTheDocument();
});

it("fails closed when the public site key is missing", async () => {
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "");
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true, remaining: 20 })));
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={vi.fn()} />);
  expect(await screen.findByText(/Manual decisions are temporarily unavailable/)).toBeVisible();
  expect(window.turnstile?.render).not.toHaveBeenCalled();
});

it("sends the token in a header, preserves the Spec body and reads allowance on burst refusal", async () => {
  const fetch = vi.fn(async () => new Response(JSON.stringify({ error: {
    code: "human_burst_limit", message: "Wait a minute, then verify again.",
  } }), { status: 429, headers: { "x-modelspec-decisions-remaining": "17" } }));
  vi.stubGlobal("fetch", fetch);
  const { hostedEngine } = await import("../adapter/hosted");
  const onRemaining = vi.fn();
  const spec = { spec_version: 1, optimize: { max: "swe_bench_pro" }, where: [], explain: "full", limit: 20 } satisfies Parameters<typeof hostedEngine.decide>[0];
  await expect(hostedEngine.decide(spec, { humanToken: "single-use-token", onRemaining })).rejects.toThrow("Wait a minute, then verify again.");
  expect(fetch).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({
    headers: expect.objectContaining({ "X-ModelSpec-Turnstile": "single-use-token" }),
    body: JSON.stringify(spec),
  }));
  expect(onRemaining).toHaveBeenCalledWith(17);
});

it("the real app verifies each action and preserves its background requests", async () => {
  let remaining = 20;
  const trace: { intent: string; token: string; spec: unknown; now: number }[] = [];
  const outcomeSchema = z.array(z.tuple([z.number(), z.string(), z.string(), z.record(z.string(), z.string())]));
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/v1/human-status")) return json({ enabled: true, remaining });
    if (String(input).endsWith("/v1/decide")) {
      const headers = new Headers(init?.headers);
      trace.push({ intent: headers.get("x-modelspec-intent") ?? "",
        token: headers.get("x-modelspec-turnstile") ?? "",
        spec: JSON.parse(String(init?.body)), now: Date.now() / 1000 });
      const outcomes = outcomeSchema.parse(JSON.parse(execFileSync(
        process.env.MODELSPEC_TEST_PYTHON ?? "python3", ["../tests/replay_human_gate.py"],
        { input: JSON.stringify(trace), encoding: "utf8" },
      )));
      const [status, code, message, gateHeaders] = outcomes[outcomes.length - 1];
      remaining = Number(gateHeaders["x-modelspec-decisions-remaining"]);
      if (status !== 200) return json({ error: { code, message } }, status);
      const response = await routed(input, init);
      for (const [key, value] of Object.entries(gateHeaders)) response.headers.set(key, value);
      return response;
    }
    return routed(input, init);
  }));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  const button = await screen.findByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(0);
  fireEvent.click(button);
  await waitFor(() => expect(sentSpecs(vi.mocked(fetch))).toHaveLength(3), { timeout: 10_000 });
  await waitFor(() => expect(button).toBeEnabled());
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(3);
  const firstIds = new Set(routed.mock.calls.filter(([url]) => String(url).endsWith("/v1/decide"))
    .map(([, init]) => new Headers(init.headers).get("x-modelspec-intent")));
  expect(firstIds.size).toBe(1);
  expect([...firstIds][0]).toMatch(/^[A-Za-z0-9_-]{21}[AQgw]$/);
  expect(window.turnstile?.render).toHaveBeenCalled();
  expect(await screen.findByText(/19 decisions remaining today/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /^Coding · Budget:/ }));
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(3);
  fireEvent.click(button);
  await waitFor(() => expect(sentSpecs(vi.mocked(fetch))).toHaveLength(6), { timeout: 10_000 });
  await waitFor(() => expect(button).toBeEnabled());
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(6);
  const allIds = new Set(routed.mock.calls.filter(([url]) => String(url).endsWith("/v1/decide"))
    .map(([, init]) => new Headers(init.headers).get("x-modelspec-intent")));
  expect(allIds.size).toBe(2);
  expect(trace).toHaveLength(6);
  expect(await screen.findByText(/18 decisions remaining today/)).toBeVisible();
}, 30_000);

it("shows a burst refusal in the page and asks for fresh verification", async () => {
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json({
    error: { code: "human_burst_limit", message: "Three decisions per minute is the manual lookup limit. Wait a minute, then verify again." },
  }, 429) });
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    String(input).endsWith("/v1/human-status")
      ? Promise.resolve(json({ enabled: true, remaining: 17 }))
      : routed(input, init)));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  const button = await screen.findByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  expect(await screen.findByText(/Three decisions per minute is the manual lookup limit/)).toBeVisible();
  expect(screen.getByText("Verify again above before your next lookup.")).toBeVisible();
  await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledTimes(2));
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(1);
});


it("recovers from a transient status 503 after retry without a reload", async () => {
  const fetchStatus = vi.fn()
    .mockResolvedValueOnce(json({ enabled: true }, 503))
    .mockResolvedValue(json({ enabled: true, remaining: 20 }));
  vi.stubGlobal("fetch", fetchStatus);
  const onLookup = vi.fn(async () => {});
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={onLookup} />);
  expect(await screen.findByText(/Manual decisions are temporarily unavailable/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Retry verification" }));
  expect(await screen.findByText(/20 decisions remaining today/)).toBeVisible();
  const button = screen.getByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  expect(fetchStatus).toHaveBeenCalledTimes(2);
  fireEvent.click(button);
  await waitFor(() => expect(onLookup).toHaveBeenCalledTimes(1));
});


it("a gated build uses automatic lookups when the Worker gate is disabled, even without a site key", async () => {
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "");
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    String(input).endsWith("/v1/human-status")
      ? Promise.resolve(json({ enabled: false }))
      : routed(input, init)));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  await waitFor(() => expect(sentSpecs(vi.mocked(fetch)).length).toBeGreaterThan(0));
  expect(screen.queryByRole("button", { name: "Look up this decision" })).not.toBeInTheDocument();
  expect(screen.queryByText(/Manual decisions are temporarily unavailable/)).not.toBeInTheDocument();
  expect(window.turnstile?.render).not.toHaveBeenCalled();
  const requests = vi.mocked(fetch).mock.calls.filter(([input]) => String(input).endsWith("/v1/decide"));
  for (const [, init] of requests) {
    expect(init?.headers).not.toHaveProperty("X-ModelSpec-Turnstile");
  }
});

it("recovers to ungated behavior when a retry reports the Worker gate disabled", async () => {
  vi.stubGlobal("fetch", vi.fn()
    .mockResolvedValueOnce(json({ enabled: true }, 503))
    .mockResolvedValue(json({ enabled: false })));
  const onEnabled = vi.fn();
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onEnabled={onEnabled} onLookup={vi.fn()} />);
  fireEvent.click(await screen.findByRole("button", { name: "Retry verification" }));
  await waitFor(() => expect(onEnabled).toHaveBeenCalledWith(false));
  expect(screen.queryByRole("region", { name: "Manual lookups" })).not.toBeInTheDocument();
  expect(window.turnstile?.render).not.toHaveBeenCalled();
});


it("answers edits made while status is pending without flashing gated UI", async () => {
  let resolveStatus: (response: Response) => void = () => { throw new Error("Status not initialized"); };
  const status = new Promise<Response>((resolve) => { resolveStatus = resolve; });
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    String(input).endsWith("/v1/human-status") ? status : routed(input, init)));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  const capability = (await screen.findByText("Software engineering")).closest<HTMLElement>(".facet-row");
  if (!capability) throw new Error("Software engineering facet missing");
  expect(screen.queryByText(/Checking today's allowance/)).not.toBeInTheDocument();
  expect(screen.queryByText(/limited to 20 per day/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Choose your facets, then verify/)).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Look up this decision" })).not.toBeInTheDocument();
  fireEvent.click(within(capability).getByLabelText("Prefer"));
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(0);
  await act(async () => { resolveStatus(json({ enabled: false })); });
  await waitFor(() => expect(sentSpecs(vi.mocked(fetch)).length).toBeGreaterThan(0));
  const lookups = sentSpecs(vi.mocked(fetch)).filter((body) => body.explain !== "none");
  expect(lookups[0].optimize.weights).toEqual({ software_engineering: 0.5 });
  expect(within(capability).getByLabelText("Prefer")).toBeChecked();
  expect(window.turnstile?.render).not.toHaveBeenCalled();
  expect(screen.queryByRole("region", { name: "Manual lookups" })).not.toBeInTheDocument();
});


it("an open ungated tab refreshes status after the Worker enables the gate", async () => {
  const fetchStatus = vi.fn()
    .mockResolvedValueOnce(json({ enabled: false }))
    .mockResolvedValue(json({ enabled: true, remaining: 20 }));
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json({
    error: { code: "human_challenge_required", message: "Complete human verification before each lookup." },
  }, 403) });
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    String(input).endsWith("/v1/human-status") ? fetchStatus() : routed(input, init)));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  const button = await screen.findByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  expect(fetchStatus).toHaveBeenCalledTimes(2);
  expect(window.turnstile?.render).toHaveBeenCalledTimes(1);
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(1);
});
