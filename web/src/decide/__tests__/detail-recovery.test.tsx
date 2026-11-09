import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { decisionSpecSchema } from "../adapter/contract";
import vocabulary from "../__fixtures__/live-vocabulary.json";
import summary from "../__fixtures__/live-assistant-balanced-summary.json";
import full from "../__fixtures__/live-assistant-balanced-full.json";

const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status });
async function settle() {
  for (let i = 0; i < 6; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
}

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  delete window.turnstile;
});

it.each(["automatic", "manual", "visit"])("announces unavailable tied details and recovers through %s authorization", async (mode) => {
  vi.resetModules();
  vi.useFakeTimers();
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", String(mode === "manual"));
  vi.stubEnv("VITE_VISIT_GATE_ENABLED", String(mode === "visit"));
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "public-test-key");
  let verification = 0;
  window.turnstile = {
    render: vi.fn((_element, options) => { options.callback(`verification-${++verification}`); return `widget-${verification}`; }),
    remove: vi.fn(),
  };
  let ranking = "";
  let unavailable = true;
  const lookups: { intent: string | null; token: string | null; visit: string | null }[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.endsWith("/v1/human-status")) return json(mode === "visit"
      ? { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 }
      : { enabled: mode === "manual", remaining: 20 });
    if (url.endsWith("/v1/visit-token")) return json({ token: "visit-token", expires_at: Math.floor(Date.now() / 1000) + 1800 });
    if (url.includes("vocabulary")) return json(vocabulary);
    if (!url.endsWith("/v1/decide")) throw new Error(`Unexpected request ${url}`);
    const sent = decisionSpecSchema.parse(JSON.parse(String(init?.body)));
    const key = JSON.stringify({ ...sent, explain: undefined });
    if (sent.explain === "summary") {
      ranking = key;
      const headers = new Headers(init?.headers);
      lookups.push({ intent: headers.get("x-modelspec-intent"), token: headers.get("x-modelspec-turnstile"), visit: headers.get("x-modelspec-visit-token") });
      return json(summary);
    }
    if (key === ranking && unavailable) return json({ error: { code: "unavailable", message: "Full explanation unavailable" } }, 503);
    return json(full);
  }));
  const { DesignedApp } = await import("../App");
  render(<DesignedApp />);
  await settle();
  if (mode === "manual") {
    expect(lookups).toHaveLength(0);
    fireEvent.click(screen.getByRole("button", { name: "Look up this decision" }));
    await settle();
  }
  expect(lookups).toHaveLength(1);
  expect(screen.getByLabelText("Facet board answer")).toBeVisible();
  const why = screen.getByRole("region", { name: "Why this model" });
  expect(why).toHaveTextContent("Select a model");
  expect(within(why).queryByRole("heading")).not.toBeInTheDocument();
  expect(within(why).getByRole("alert")).toHaveTextContent("Detailed explanation unavailable");
  unavailable = false;
  if (mode === "manual") {
    expect(within(why).getByRole("alert")).toHaveTextContent("Verify again above before your next lookup");
    expect(within(why).queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Look up this decision" }));
  } else fireEvent.click(within(why).getByRole("button", { name: "Retry" }));
  await settle();
  expect(lookups).toHaveLength(2);
  expect(lookups[1].intent).not.toBe(lookups[0].intent);
  if (mode === "manual") {
    expect(lookups.map((lookup) => lookup.token)).toEqual(["verification-1", "verification-2"]);
  }
  if (mode === "visit") expect(lookups.map((lookup) => lookup.visit)).toEqual(["visit-token", "visit-token"]);
  expect(screen.getByLabelText("Facet board answer")).toBeVisible();
  expect(screen.getByRole("region", { name: "Why this model" })).toHaveTextContent("Select a model");
  expect(screen.queryByText(/Detailed explanation unavailable/)).not.toBeInTheDocument();
});
