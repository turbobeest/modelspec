import { describe, expect, it } from "vitest";
import {
  parseRealTask,
  pickDrilldownBenchmark,
  realBaseSpec,
  realTemplates,
  switchBenchmark,
  switchEstimate,
  type Vocabulary,
} from "../vocabulary";
import { toDecisionSpec } from "../adapter/view-model";
import { realVocabulary } from "./vocab-fixtures";

function withDefault(v: Vocabulary, domain: string, benchmark: string | null): Vocabulary {
  return {
    ...v,
    domains: v.domains.map((d) => (d.id === domain ? { ...d, default_benchmark: benchmark } : d)),
  };
}

describe("benchmark drill-down per domain", () => {
  const offered = realVocabulary.benchmarks.filter((b) =>
    b.domains.some((t) => t.id === "software_engineering" && t.directness === "direct"),
  );

  it("preselects the published benchmark when it is offered", () => {
    const target = offered[offered.length - 1];
    const v = withDefault(realVocabulary, "software_engineering", target.id);
    expect(pickDrilldownBenchmark(v, "software_engineering")?.id).toBe(target.id);
  });

  it("falls back to the most-covered direct benchmark without a default", () => {
    const v = withDefault(realVocabulary, "software_engineering", null);
    const expected = [...offered].sort((a, b) => b.models - a.models || a.id.localeCompare(b.id))[0];
    expect(pickDrilldownBenchmark(v, "software_engineering")?.id).toBe(expected.id);
  });

  it("ignores a default that has no verified data in the vocabulary", () => {
    const v = withDefault(realVocabulary, "software_engineering", "no_such_benchmark");
    expect(pickDrilldownBenchmark(v, "software_engineering")?.id).not.toBe(
      "no_such_benchmark",
    );
  });
});

describe("domain capability is the default ranking basis", () => {
  it("uses the estimate for the default task, parsed tasks and every template", () => {
    expect(realBaseSpec(realVocabulary).basis).toBe("estimate");
    expect(parseRealTask(realVocabulary, "fix a coding bug").basis).toBe("estimate");
    expect(realTemplates(realVocabulary).every((template) => template.spec.basis === "estimate"))
      .toBe(true);
  });

  it("labels templates as estimates from every tagged benchmark", () => {
    const template = realTemplates(realVocabulary).find((item) => item.id === "budget-agent");
    const domain = realVocabulary.domains.find((item) => item.id === "software_engineering")!;
    expect(template?.ranks).toBe(
      `Software engineering capability (estimated from ${domain.estimate_benchmarks?.length ?? domain.benchmarks.length} benchmarks)`,
    );
  });

  it("does not turn the preselected coding benchmark into a default floor", () => {
    const parsed = parseRealTask(realVocabulary, "correct code matters");
    const template = realTemplates(realVocabulary).find((item) => item.id === "budget-agent");
    expect(parsed.conds.some((condition) => condition.f === "bench")).toBe(false);
    expect(template?.spec.conds.some((condition) => condition.f === "bench")).toBe(false);
  });

  it("sends the domain in weights until Measured by selects one benchmark", () => {
    const base = realBaseSpec(realVocabulary);
    expect(toDecisionSpec(base, "summary").optimize).toEqual({
      weights: {
        software_engineering: base.w.cap,
        "-offering.cost_per_task": base.w.cost,
      },
    });

    const benchmark = pickDrilldownBenchmark(realVocabulary, "software_engineering")!;
    const drilled = switchBenchmark(realVocabulary, base, benchmark.id);
    expect(drilled.basis).toBe("benchmark");
    expect(toDecisionSpec(drilled, "summary").optimize).toEqual({
      weights: {
        [benchmark.id]: drilled.w.cap,
        "-offering.cost_per_task": drilled.w.cost,
      },
    });
    expect(switchEstimate(drilled).basis).toBe("estimate");
  });

  it("uses chat preference for the self-hosted assistant estimate", () => {
    const t = realTemplates(realVocabulary).find((x) => x.id === "private");
    expect(t?.spec.domain).toBe("chat_preference");
    expect(t?.spec.basis).toBe("estimate");
    expect(t?.spec.bench).toBe("arena_elo_style_control");
  });
});
