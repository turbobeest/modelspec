import { expect, it, vi } from "vitest";
import { evaluateQuestionOptions } from "../adapter/questions";
import type { Decision, DecisionSpec } from "../adapter/contract";
import type { HostedDecisionEngine } from "../adapter/hosted";
import type { Question } from "../engine/reference";

const decision = (count: number): Decision => ({
  contract_version: "1.2",
  out_of_lineup: 0,
  decision_id: `dec_${String(count).padStart(8, "0")}`,
  snapshot: "snap_question_test",
  spec_hash: `sha256:${"a".repeat(64)}`,
  explain: "none",
  status: "answered",
  results: Array.from({ length: count }, (_, index) => ({
    rank: index + 1,
    offering: { model: `lab/model-${index}`, provider: null, region: null, tier: null },
    harness: null,
    effort: null,
    evidence: [],
    estimates: null,
    p_best: null,
    top3_stability: null,
    soft_penalty: 0,
    contributions: [],
    warnings: [],
  })),
  may_qualify: [],
  eliminated: { funnel: [], models: [], model_groups: [] },
  constraint_costs: [],
  tipping_points: [],
  relax: [],
  relax_to: [],
  warnings: [],
  near_misses: [],
  top: [],
  chart: null,
  number_origins: [],
  sources: [],
});

it("debounces next-question evaluation and caps fan-out at six requests", async () => {
  vi.useFakeTimers();
  let active = 0;
  let peak = 0;
  const engine: HostedDecisionEngine = {
    decide: vi.fn(async () => {
      active += 1;
      peak = Math.max(peak, active);
      await new Promise<void>((resolve) => window.setTimeout(resolve, 1));
      active -= 1;
      return decision(3);
    }),
  };
  const questions: Question[] = Array.from({ length: 4 }, (_, q) => ({
    id: `q-${q}`,
    q: `Question ${q}`,
    opts: Array.from({ length: 3 }, (_, o) => ({
      label: `Option ${o}`,
      c: { f: "ctx", min: 1000 * (q + o + 1) },
    })),
  }));
  const spec: DecisionSpec = {
    spec_version: 1,
    where: [],
    optimize: { min: "offering.price.input" },
    explain: "none",
  };

  const pending = evaluateQuestionOptions({ engine, spec, questions });
  await vi.advanceTimersByTimeAsync(299);
  expect(engine.decide).not.toHaveBeenCalled();
  await vi.advanceTimersByTimeAsync(1);
  expect(engine.decide).toHaveBeenCalledTimes(6);
  expect(peak).toBe(6);

  await vi.runAllTimersAsync();
  const result = await pending;
  expect(engine.decide).toHaveBeenCalledTimes(12);
  expect(result.flatMap((question) => question.opts).every((option) => option.n === 3)).toBe(true);
  vi.useRealTimers();
});

it("keeps every other question when one probe is refused", async () => {
  vi.useFakeTimers();
  const { DecideApiError } = await import("../adapter/hosted");
  const engine: HostedDecisionEngine = {
    decide: vi.fn(async (spec: DecisionSpec) => {
      if ((spec.where ?? []).some((c) => String(c).includes("context_window >= 2000")))
        throw new DecideApiError("bad spec", 400, "invalid_spec");
      return decision(4);
    }),
  };
  const questions: Question[] = [1, 2].map((q) => ({
    id: `q-${q}`,
    q: `Question ${q}`,
    opts: [{ label: "Yes", c: { f: "ctx", min: 1000 * q } }],
  }));
  const spec: DecisionSpec = { spec_version: 1, where: [], optimize: { min: "offering.price.input" }, explain: "none" };
  const pending = evaluateQuestionOptions({ engine, spec, questions });
  await vi.runAllTimersAsync();
  const result = await pending;
  expect(result.map((q) => q.id)).toEqual(["q-1", "q-2"]);
  expect(result[0].opts[0]).toMatchObject({ n: 4 });
  expect(result[1].opts[0].n).toBeUndefined();
  expect(result[1].opts[0].failed).toBe(true);
  vi.useRealTimers();
});
