import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import vocabulary from "../__fixtures__/vocabulary.json";
import answer from "../__fixtures__/full-decision.json";

const broken = vi.hoisted(() => ({ rankedAnswer: false, canvas: false }));
vi.mock("../facet-board/RankedAnswer", async (importOriginal) => {
  const real = await importOriginal<typeof import("../facet-board/RankedAnswer")>();
  return {
    ...real,
    RankedAnswer: (props: Parameters<typeof real.RankedAnswer>[0]) => {
      if (broken.rankedAnswer) throw new TypeError("RankedAnswer failed to render");
      return <real.RankedAnswer {...props} />;
    },
  };
});

vi.mock("../components/FreeAxisCanvas", async (importOriginal) => {
  const real = await importOriginal<typeof import("../components/FreeAxisCanvas")>();
  return {
    ...real,
    FreeAxisCanvas: (props: Parameters<typeof real.FreeAxisCanvas>[0]) => {
      if (broken.canvas) throw new TypeError("canvas failed to render");
      return <real.FreeAxisCanvas {...props} />;
    },
  };
});
vi.mock("../components/Canvas", async (importOriginal) => {
  const real = await importOriginal<typeof import("../components/Canvas")>();
  return {
    ...real,
    Canvas: (props: Parameters<typeof real.Canvas>[0]) => {
      if (broken.canvas) throw new TypeError("canvas failed to render");
      return <real.Canvas {...props} />;
    },
  };
});

beforeEach(() => {
  broken.rankedAnswer = false;
  broken.canvas = false;
  vi.resetModules();
  vi.stubEnv("VITE_VISIT_GATE_ENABLED", "true");
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "public-test-key");
});
afterEach(() => {
  delete window.turnstile;
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});
const json = (body: unknown, status = 200, headers: HeadersInit = {}) => new Response(JSON.stringify(body), { status, headers });

it("does not verify or add a credential while the Worker gate is off", async () => {
  const fetch = vi.fn(async (url: string) => json(url.endsWith("human-status") ? { enabled: false } : {}));
  vi.stubGlobal("fetch", fetch);
  const { visitFetch, registerChallenge } = await import("../adapter/visit");
  const challenge = vi.fn();
  registerChallenge(challenge);
  await visitFetch("/v1/decide", { method: "POST" });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(challenge.mock.calls).toEqual([[null]]);
  const { decisionAction } = await import("../adapter/hosted");
  expect(decisionAction().pace).toBeUndefined();
  expect(fetch.mock.calls[1]).toEqual(["/v1/decide", expect.objectContaining({ method: "POST", signal: expect.any(AbortSignal) })]);
});

it("an open page adopts a newly enabled Worker gate after a missing-key refusal", async () => {
  let statusReads = 0;
  let decisions = 0;
  let checks = 0;
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.endsWith("human-status")) return json(++statusReads === 1 ? { enabled: false } : { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 });
    if (url.endsWith("visit-token")) { checks++; return json({ token: "visit", expires_at: Math.floor(Date.now() / 1000) + 1800 }); }
    return ++decisions === 1 ? json({ error: { code: "missing_api_key" } }, 401) : json({ answer: "ok" });
  }));
  const { visitFetch, registerChallenge } = await import("../adapter/visit");
  registerChallenge((challenge) => challenge?.resolve("single-use"));
  expect((await visitFetch("/v1/decide", {})).status).toBe(200);
  expect(decisions).toBe(2);
  expect(checks).toBe(1);
});

it("a visit-capable page preserves the legacy manual mode when the Worker selects it", async () => {
  window.turnstile = { render: vi.fn((_container, options) => { options.callback("manual-token"); return "widget"; }), remove: vi.fn() };
  vi.stubGlobal("fetch", vi.fn(async () => json({ enabled: true, remaining: 20 })));
  const { HumanGate } = await import("../components/HumanGate");
  const lookup = vi.fn(async () => {});
  render(<HumanGate onLookup={lookup} />);
  const button = await screen.findByRole("button", { name: "Look up this decision" });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  await waitFor(() => expect(lookup).toHaveBeenCalledWith("manual-token", expect.any(Function)));
});

async function client({ refuse = 0, code = "visit_token_expired" } = {}) {
  let checks = 0;
  let now = 1_000_000;
  vi.spyOn(Date, "now").mockImplementation(() => now);
  const requests: RequestInit[] = [];
  const fetch = vi.fn(async (url: string, init?: RequestInit) => {
    if (url.endsWith("human-status")) return json({ enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 });
    if (url.endsWith("visit-token")) { checks++; return json({ token: `visit-${checks}`, expires_at: now / 1000 + 1800 }); }
    requests.push(init ?? {});
    if (refuse-- > 0) return json({ error: { code } }, 401);
    return json({ answer: "ok" });
  });
  vi.stubGlobal("fetch", fetch);
  const visit = await import("../adapter/visit");
  visit.registerChallenge((challenge) => challenge?.resolve("single-use"));
  return { ...visit, fetch, requests, checks: () => checks, advance: () => { now += 1800 * 1000; } };
}

it("shares one check across vocabulary and concurrent decisions, then rechecks local expiry", async () => {
  const visit = await client();
  await Promise.all([visit.visitFetch("/v1/vocabulary", {}), visit.visitFetch("/v1/decide", {}), visit.visitFetch("/v1/decide", {})]);
  expect(visit.checks()).toBe(1);
  expect(visit.requests.map((request) => new Headers(request.headers).get("X-ModelSpec-Visit-Token"))).toEqual(["visit-1", "visit-1", "visit-1"]);
  visit.advance();
  await visit.visitFetch("/v1/decide", {});
  expect(visit.checks()).toBe(2);
});

it("rechecks a Worker expiry and retries the same intent and body exactly once", async () => {
  const visit = await client({ refuse: 2 });
  const options = { method: "POST", headers: { "x-modelspec-intent": "one-action" }, body: '{"spec_version":1}' };
  const response = await visit.visitFetch("/v1/decide", options);
  expect(response.status).toBe(401);
  expect(visit.checks()).toBe(2);
  expect(visit.requests).toHaveLength(2);
  expect(visit.requests.map((request) => new Headers(request.headers).get("x-modelspec-intent"))).toEqual(["one-action", "one-action"]);
  expect(visit.requests.map((request) => request.body)).toEqual([options.body, options.body]);
});

it("rechecks a changed daily identity once and refuses a repeated binding failure", async () => {
  const visit = await client({ refuse: 2, code: "visit_token_invalid" });
  expect((await visit.visitFetch("/v1/decide", {})).status).toBe(401);
  expect(visit.checks()).toBe(2);
  expect(visit.requests).toHaveLength(2);
});

it("does not send an aborted request after shared verification finishes", async () => {
  const visit = await client();
  const controller = new AbortController();
  controller.abort();
  await expect(visit.visitFetch("/v1/decide", { signal: controller.signal })).rejects.toMatchObject({ name: "AbortError" });
  expect(visit.requests).toHaveLength(0);
});

it("uses a sliding renewal without another Turnstile check", async () => {
  const visit = await client();
  visit.fetch.mockImplementationOnce(async () => json({ enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 }));
  await visit.prepareVisit();
  visit.fetch.mockImplementationOnce(async () => json({}, 200, { "x-modelspec-visit-token": "renewed", "x-modelspec-visit-expires": "4600" }));
  await visit.visitFetch("/v1/decide", {});
  visit.advance();
  await visit.visitFetch("/v1/decide", {});
  expect(visit.checks()).toBe(1);
  expect(new Headers(visit.requests.at(-1)?.headers).get("X-ModelSpec-Visit-Token")).toBe("renewed");
});

it("renders managed interaction-only verification and no lookup button", async () => {
  const visit = await client();
  window.turnstile = { render: vi.fn((_container, options) => { options.callback("single-use"); return "widget"; }), remove: vi.fn() };
  const { VisitGate } = await import("../components/HumanGate");
  render(<VisitGate />);
  await visit.prepareVisit();
  await waitFor(() => expect(window.turnstile?.render).toHaveBeenCalledWith(expect.any(HTMLElement), expect.objectContaining({ action: "decide", appearance: "interaction-only" })));
  expect(screen.queryByRole("button", { name: /Look up/ })).toBeNull();
  expect(visit.checks()).toBe(1);
});

it("answers initial load and facet changes automatically with one verification and one intent per action", async () => {
  let checks = 0;
  const intents: (string | null)[] = [];
  window.turnstile = { render: vi.fn((_container, options) => { options.callback("single-use"); return "widget"; }), remove: vi.fn() };
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.endsWith("human-status")) return json({ enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 });
    if (url.endsWith("visit-token")) { checks++; return json({ token: "visit", expires_at: Math.floor(Date.now() / 1000) + 1800 }); }
    if (url.endsWith("vocabulary.json")) return json(vocabulary);
    if (url.endsWith("decide")) {
      expect(new Headers(init?.headers).get("X-ModelSpec-Visit-Token")).toBe("visit");
      intents.push(new Headers(init?.headers).get("x-modelspec-intent"));
      return json(answer);
    }
    throw new Error(`Unexpected request ${url}`);
  }));
  const { default: App } = await import("../App");
  render(<App />);
  await waitFor(() => expect(intents).toHaveLength(3), { timeout: 5000 });
  expect(new Set(intents).size).toBe(1);
  expect(screen.getByLabelText("Facet board answer")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /What it.s good at/ }));
  const row = document.querySelector('[data-facet="capability.software_engineering"]');
  expect(row).not.toBeNull();
  if (!(row instanceof HTMLElement)) throw new Error("Missing capability row");
  fireEvent.click(within(row).getByLabelText("Prefer", { exact: true }));
  await waitFor(() => expect(intents.length).toBeGreaterThanOrEqual(5), { timeout: 5000 });
  expect(new Set(intents.slice(3)).size).toBe(1);
  expect(intents[3]).not.toBe(intents[0]);
  expect(checks).toBe(1);
  expect(screen.queryByRole("button", { name: "Look up this decision" })).toBeNull();
  expect(document.querySelector("#facet-board-answer .visit-gate")).not.toBeNull();
}, 10_000);

it("names a failed visit check as the reason the vocabulary was not requested", async () => {
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "");
  const requested: string[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    requested.push(url);
    if (url.endsWith("human-status")) return json({ enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 });
    throw new Error(`Unexpected request ${url}`);
  }));
  const { default: App } = await import("../App");
  render(<App />);
  const alert = await screen.findByText(/Couldn't load what the snapshot can answer/);
  expect(alert.closest("[role=alert]")).toHaveTextContent("Human verification did not complete, so the catalogue vocabulary was not requested.");
  expect(screen.queryByText(/did not load in time/)).toBeNull();
  expect(requested.filter((url) => !url.endsWith("human-status"))).toEqual([]);
});

function answerColumn(): HTMLElement {
  const column = document.getElementById("facet-board-answer");
  if (!column) throw new Error("The answer column is not rendered");
  return column;
}

async function answeredVisitApp({ refuseAfter = Infinity } = {}) {
  let renders = 0;
  let decisions = 0;
  window.turnstile = {
    render: vi.fn((_container, options) => {
      if (++renders === 1) options.callback("single-use");
      else options["error-callback"]();
      return "widget";
    }),
    remove: vi.fn(),
  };
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.endsWith("human-status")) return json({ enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 });
    if (url.endsWith("visit-token")) return json({ token: "visit", expires_at: Math.floor(Date.now() / 1000) + 1800 });
    if (url.endsWith("vocabulary.json")) return json(vocabulary);
    if (url.endsWith("decide")) return ++decisions > refuseAfter ? json({ error: { code: "visit_token_expired" } }, 401) : json(answer);
    throw new Error(`Unexpected request ${url}`);
  }));
  const { default: App } = await import("../App");
  render(<App />);
  await screen.findByLabelText("Facet board answer", {}, { timeout: 5000 });
  const preferSoftware = () => {
    fireEvent.click(screen.getByRole("button", { name: /What it.s good at/ }));
    const row = document.querySelector('[data-facet="capability.software_engineering"]');
    if (!(row instanceof HTMLElement)) throw new Error("Missing capability row");
    fireEvent.click(within(row).getByLabelText("Prefer", { exact: true }));
  };
  return { preferSoftware };
}

it("shows a failed re-check as the gate's own alert in the answer column, never as a broken answer", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  const app = await answeredVisitApp({ refuseAfter: 3 });
  app.preferSoftware();
  // Query afresh each time: the board re-renders the answer while a request
  // settles, so a node found earlier may already have been replaced.
  await waitFor(() => {
    const gate = within(answerColumn()).getByRole("region", { name: "Visit verification" });
    expect(within(gate).getByRole("alert")).toHaveTextContent("Verification is temporarily unavailable. Retry your lookup.");
  }, { timeout: 5000 });
  expect(screen.queryAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(0);
}, 10_000);

it("keeps the visit gate in the answer column when the answer itself fails to draw", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  const app = await answeredVisitApp();
  broken.rankedAnswer = true;
  app.preferSoftware();
  await waitFor(() => {
    const column = answerColumn();
    expect(within(column).getAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(1);
    expect(within(column).getByRole("region", { name: "Visit verification" })).toBeInTheDocument();
  }, { timeout: 5000 });
  expect(screen.getAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(1);
}, 10_000);

it("keeps the visit gate in the answer column when the canvas fails to draw (MODEL-298)", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  const app = await answeredVisitApp();
  broken.canvas = true;
  app.preferSoftware();
  await waitFor(() => {
    expect(screen.getAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(1);
    expect(within(answerColumn()).getByRole("region", { name: "Visit verification" })).toBeInTheDocument();
  }, { timeout: 5000 });
  // The canvas sits under the board now: its failure notice is outside the answer column.
  expect(within(answerColumn()).queryAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(0);
  expect(within(answerColumn()).getByLabelText("Facet board answer")).toBeInTheDocument();
}, 10_000);

it("a failed re-check stays the gate's own alert while the canvas is broken (MODEL-298)", async () => {
  vi.spyOn(console, "error").mockImplementation(() => undefined);
  broken.canvas = true;
  const app = await answeredVisitApp({ refuseAfter: 3 });
  app.preferSoftware();
  await waitFor(() => {
    const gate = within(answerColumn()).getByRole("region", { name: "Visit verification" });
    expect(within(gate).getByRole("alert")).toHaveTextContent("Verification is temporarily unavailable. Retry your lookup.");
  }, { timeout: 5000 });
  // The answer column never shows the boundary alert in place of the gate's.
  expect(within(answerColumn()).queryAllByRole("alert", { name: "The answer could not be shown" })).toHaveLength(0);
}, 10_000);
