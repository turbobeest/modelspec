import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
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
  delete window.turnstile;
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
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
  expect(screen.getByRole("button", { name: "Look up this decision" })).toBeDisabled();
});

it("fails closed when the public site key is missing", async () => {
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "");
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true, remaining: 20 })));
  const { HumanGate } = await import("../components/HumanGate");
  render(<HumanGate onLookup={vi.fn()} />);
  expect(screen.getByText(/Manual decisions are temporarily unavailable/)).toBeVisible();
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

it("the real app waits for a person and sends one full lookup without background probes", async () => {
  const routed = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) =>
    String(input).endsWith("/v1/human-status")
      ? Promise.resolve(json({ enabled: true, remaining: 20 }))
      : routed(input, init)));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  const button = await screen.findByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(0);
  fireEvent.click(button);
  await waitFor(() => expect(sentSpecs(vi.mocked(fetch))).toHaveLength(1));
  await waitFor(() => expect(button).toBeEnabled());
  expect(sentSpecs(vi.mocked(fetch))).toHaveLength(1);
});

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
