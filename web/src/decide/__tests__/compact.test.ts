// Contract 1.4 (MODEL-163): a `full` decision lists each source once, names it
// by ID from the origins and from each shown fact, and a page that meets a
// Worker limit on `full` falls back to `summary`. The fixtures are the
// engine's own answers (tests/test_decide_page_fixtures.py).
import { afterEach, describe, expect, it, vi } from "vitest";
import fullJson from "../__fixtures__/compact-full.json";
import summaryJson from "../__fixtures__/compact-summary.json";
import {
  DecideApiError,
  decideWithFallback,
  decisionSchema,
  hostedEngine,
  mayBeLimit,
} from "../adapter";
import type { DecisionSpec } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { baseSpec } from "../state/spec";
import { json } from "./vocab-fixtures";

const full = decisionSchema.parse(fullJson);
const summary = decisionSchema.parse(summaryJson);
const spec = { ...baseSpec, bench: "quality", tokIn: 40_000, tokOut: 4_000 };
const view = (decision = full) =>
  mapDecisionToViewModel(decision, spec, { axis: "task$", dismissed: [] });

afterEach(() => vi.unstubAllGlobals());

describe("the compact full decision", () => {
  it("parses, with sources listed once and origins naming them by ID", () => {
    expect(full.contract_version).toBe("1.4");
    expect(full.sources.map((source) => source.id)).toEqual([
      "src-board",
      "src-lab-docs",
      "src-pricing",
    ]);
    expect(full.number_origins.every((origin) => origin.sources.length === 0)).toBe(true);
    expect(full.number_origins.some((origin) => origin.source_ids.length > 0)).toBe(true);
  });

  it("shows a candidate's facts through their source IDs", () => {
    const alpha = view().explanation.feasible[0];
    expect(alpha.m.id).toBe("alpha");
    expect(alpha.best.o.in).toBe(3);
    expect(alpha.best.o.out).toBe(12);
    expect(alpha.m.ctx).toBe(200_000);
    expect(alpha.m.open).toBe(false);
    expect(alpha.m.status).toBe("active");
    expect(alpha.best.o.ttft).toBe(420);
    expect(alpha.tps).toBe(95);
    expect(alpha.cap).toBe(92);
    expect(alpha.cost).toBeCloseTo(0.168);
  });

  it("does not show a fact whose source is missing from the sources table", () => {
    const unsourced = {
      ...full,
      sources: full.sources.filter((source) => source.id !== "src-pricing"),
    };
    const alpha = view(unsourced).explanation.feasible[0];
    expect(alpha.best.o.in).toBeNull();
    expect(alpha.m.ctx).toBe(200_000);
  });
});

describe("a summary decision, when the full explanation was unavailable", () => {
  it("ranks from results, with capability from their evidence and $ per task from the formula", () => {
    const mapped = view(summary);
    expect(summary.explain).toBe("summary");
    expect(summary.top).toEqual([]);
    expect(mapped.explanation.feasible.map((row) => row.m.id)).toEqual([
      "alpha",
      "gamma",
      "beta",
    ]);
    const alpha = mapped.explanation.feasible[0];
    expect(alpha.cap).toBe(92);
    expect(alpha.capR?.src).toBe("https://board.example.org/results");
    expect(alpha.cost).toBeCloseTo(0.168);
    expect(alpha.best.o.costFormula).toContain("= 0.168 USD per task");
    // A summary shows no facts: nothing is invented for them.
    expect(alpha.best.o.in).toBeNull();
    expect(alpha.m.ctx).toBeNull();
  });
});

const fullSpec: DecisionSpec = {
  spec_version: 1,
  optimize: { max: "quality" },
  explain: "full",
};

describe("decideWithFallback", () => {
  it("retries a full decision once with summary after a Worker limit", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValueOnce(new Response("error code: 1102", { status: 503 }))
      .mockResolvedValueOnce(json(summaryJson));
    vi.stubGlobal("fetch", fetch);
    const answer = await decideWithFallback(hostedEngine, fullSpec);
    expect(answer.limited).toBe(true);
    expect(answer.decision.explain).toBe("summary");
    const sent = fetch.mock.calls.map(([, init]) => JSON.parse(String(init.body)).explain);
    expect(sent).toEqual(["full", "summary"]);
  });

  it("retries after a network failure too: a limit page carries no CORS header", async () => {
    const fetch = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(json(summaryJson));
    vi.stubGlobal("fetch", fetch);
    expect((await decideWithFallback(hostedEngine, fullSpec)).limited).toBe(true);
  });

  it("does not retry a spec error, a missing snapshot, or a summary request", async () => {
    expect(mayBeLimit(new DecideApiError("bad spec", 400, "invalid_spec"))).toBe(false);
    expect(mayBeLimit(new DecideApiError("none yet", 503, "no_snapshot"))).toBe(false);
    expect(mayBeLimit(new DecideApiError("slow", null, "timeout"))).toBe(false);
    const fetch = vi.fn().mockResolvedValue(new Response("error code: 1102", { status: 503 }));
    vi.stubGlobal("fetch", fetch);
    await expect(
      decideWithFallback(hostedEngine, { ...fullSpec, explain: "summary" }),
    ).rejects.toBeInstanceOf(DecideApiError);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("reports the limit, not the retry, when a limited request's retry fails too", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(new Response("error code: 1102", { status: 503 }))
        .mockRejectedValueOnce(new TypeError("Failed to fetch")),
    );
    const error = await decideWithFallback(hostedEngine, fullSpec).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(DecideApiError);
    expect((error as DecideApiError).code).toBe("limit");
  });

  it("reports a network failure as one when the summary retry cannot connect either", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const error = await decideWithFallback(hostedEngine, fullSpec).catch((e: unknown) => e);
    expect((error as DecideApiError).status).toBeNull();
    expect((error as DecideApiError).code).toBeNull();
  });
});
