/// <reference types="node" />
// Real mode speaks only the published vocabulary (MODEL-153). Every spec the
// page can build from vocabulary.json is checked here against the contract's
// JSON Schema and the vocabulary's own IDs, and written to a golden file that
// tests/test_decide_page_specs.py parses with the Python registry.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import Ajv from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { describe, expect, it } from "vitest";
import { toDecisionSpec } from "../adapter/view-model";
import { probeSpec } from "../adapter/questions";
import type { DecisionSpec } from "../adapter";
import type { Cond, FacetOp, Spec, TypeKey } from "../engine/types";
import {
  facetOptions,
  offeredAxes,
  offeredBenchmarks,
  offeredTypes,
  offeredWeights,
  parseRealTask,
  pickDrilldownBenchmark,
  rankChoices,
  realBaseSpec,
  realQuestions,
  realTemplates,
  sendable,
  switchBenchmark,
  vocabularySchema,
} from "../vocabulary";
import type { Vocabulary } from "../vocabulary";
import { realVocabulary as v } from "./vocab-fixtures";

const DEFAULT_TASK = "Refactor a large Rust codebase, precision matters";
const GOLDEN = "src/decide/__fixtures__/ui-specs.json";

function parsedSpec(vocabulary: Vocabulary, task: string): Spec {
  const base = realBaseSpec(vocabulary);
  const p = parseRealTask(vocabulary, task);
  return {
    ...base,
    task,
    bench: p.bench,
    basis: p.basis,
    w: p.w,
    conds: p.conds,
    domain: p.domain ?? undefined,
  };
}

const EDITABLE: FacetOp[] = ["=", "!=", "<=", ">=", "in", "not in"];

describe("published templates", () => {
  it("accepts the additive pinned refinements shape", () => {
    const parsed = vocabularySchema.parse({
      ...v,
      refinements: [
        {
          id: "python",
          parent_domain: "software_engineering",
          kind: "language",
          name: "Python",
          definition: "Software engineering tasks whose implementation language is Python.",
          evidence_state: "live",
          measured_models: 7,
          of_models: 25,
          benchmarks: [{ id: "swe_bench_verified", directness: "direct" }],
          weight_key: "software_engineering/python",
        },
      ],
    });
    expect(parsed.refinements?.[0]?.weight_key).toBe("software_engineering/python");
  });

  it("accepts vocabularies published before templates existed", () => {
    const { templates: _templates, ...withoutTemplates } = v;
    expect(_templates?.length).toBeGreaterThan(0);
    expect(vocabularySchema.parse(withoutTemplates).templates).toBeUndefined();
  });

  it("accepts the additive templates field", () => {
    const parsed = vocabularySchema.parse({
      ...v,
      templates: [
        {
          id: "maths",
          name: "Maths and proofs",
          purpose: "Find a text model for mathematical work.",
          where: [
            {
              condition: "model.class = text-generator",
              reason: "The answer must be generated as text.",
            },
          ],
          weights: { maths: { weight: 1, reason: "Rank by maths capability." } },
          needs: { classes: ["text-generator"], domains: ["maths"] },
          teaches: "Class is a Must and maths quality is a Prefer.",
          spec: {
            spec_version: 1,
            where: ["model.class = text-generator"],
            optimize: { weights: { maths: 1 } },
          },
          available: true,
          unavailable_reason: null,
        },
      ],
    });
    expect(parsed.templates?.[0]?.id).toBe("maths");
  });
});

/** Every condition the facet editor can produce on each offered facet. */
function editorConditions(vocabulary: Vocabulary): Cond[] {
  return vocabulary.facets.flatMap((row) => {
    if (row.known === 0) return [];
    const values = (row.values ?? []).map((item) => item.value);
    const sample =
      row.value_type === "number"
        ? typeof row.range?.min === "number"
          ? row.range.min
          : null
        : row.value_type === "date"
          ? typeof row.range?.min === "string"
            ? row.range.min
            : null
          : (values[0] ?? null);
    if (sample === null) return [];
    return EDITABLE.filter((op) => row.operators.includes(op)).map(
      (op): Cond => ({
        f: "facet",
        facet: row.id,
        op,
        value: op === "in" || op === "not in" ? [String(sample)] : sample,
      }),
    );
  });
}

/** Every spec the page can send: the default task, templates, options, questions, editors. */
function everySpec(vocabulary: Vocabulary): { name: string; spec: DecisionSpec }[] {
  const base = realBaseSpec(vocabulary);
  const out: { name: string; spec: Spec }[] = [
    { name: "default task", spec: parsedSpec(vocabulary, DEFAULT_TASK) },
    { name: "start from constraints", spec: base },
    ...realTemplates(vocabulary).map((t) => ({
      name: `template ${t.id}`,
      spec: { ...t.spec, task: t.task },
    })),
    ...facetOptions(vocabulary).map((option) => ({
      name: `add ${option.label}`,
      spec: { ...base, conds: [...base.conds, option.c] },
    })),
    ...realQuestions(vocabulary, base, []).flatMap((q) =>
      q.opts.map((o) => ({
        name: `question ${q.id} ${o.label}`,
        spec: { ...base, conds: [...base.conds, o.c] },
      })),
    ),
    ...editorConditions(vocabulary).map((c) => ({
      name: `edit ${c.f === "facet" ? `${c.facet} ${c.op}` : c.f}`,
      spec: { ...base, conds: [...base.conds, c] },
    })),
    ...(Object.keys(offeredTypes(vocabulary)) as TypeKey[]).map((type) => ({
      name: `type ${type}`,
      spec: {
        ...base,
        conds: [{ f: "type", v: type } as Cond, ...base.conds.filter((c) => c.f !== "type")],
      },
    })),
  ];
  // The next-question probes, built exactly as the page sends them: each
  // option appended to the spec on screen (the default task, each template).
  const onScreen = [
    { name: "default task", spec: parsedSpec(vocabulary, DEFAULT_TASK) },
    ...realTemplates(vocabulary).map((t) => ({
      name: `template ${t.id}`,
      spec: { ...t.spec, task: t.task },
    })),
  ];
  const probes = onScreen.flatMap(({ name, spec }) => {
    const sent = toDecisionSpec(sendable(vocabulary, spec), "none");
    return realQuestions(vocabulary, spec, []).flatMap((q) =>
      q.opts.map((o) => ({ name: `probe ${name} ${q.id} ${o.label}`, spec: probeSpec(sent, o) })),
    );
  });
  return [
    ...out.map(({ name, spec }) => ({
      name,
      spec: toDecisionSpec(sendable(vocabulary, spec), "full"),
    })),
    ...probes,
  ];
}

const schema = JSON.parse(readFileSync("../docs/decision-contract.schema.json", "utf8"));
const ajv = new Ajv({ strict: false, allErrors: true });
addFormats(ajv);
const validateSpec = ajv.compile({ ...schema, anyOf: undefined, $ref: "#/$defs/Spec" });

function facetsIn(spec: DecisionSpec): string[] {
  const conditions = (spec.where ?? []).map(String);
  const named = conditions.map(
    (c) => /^known\(([^)]+)\)/.exec(c)?.[1] ?? c.split(" ", 1)[0],
  );
  const weights = Object.keys(
    "weights" in spec.optimize ? spec.optimize.weights : {},
  ).map((k) => k.replace(/^-/, ""));
  return [...named, ...weights];
}

describe("the real task parser", () => {
  it.each(["Refactor this module", "coding help", "an agent that fixes bugs"])(
    "maps %j to software engineering",
    (task) => expect(parseRealTask(v, task).domain).toBe("software_engineering"),
  );

  it("ranks on the software-engineering estimate and preselects a drill-down", () => {
    const parsed = parseRealTask(v, DEFAULT_TASK);
    expect(parsed.basis).toBe("estimate");
    expect(parsed.bench).toBe("swe_bench_verified");
    expect(parsed.trace[0].note).toContain("Software engineering capability: estimated from");
    expect(parsed.trace[0].note).toContain("SWE-bench Verified is preselected for Measured by");
  });

  it("picks from the data, never a fixed name", () => {
    const more: Vocabulary = {
      ...v,
      benchmarks: [
        ...v.benchmarks,
        {
          id: "swe_bench_pro",
          name: "SWE-bench Pro",
          unit: "percent",
          higher_is_better: true,
          models: 20,
          independent_models: 20,
          range: { min: 20, max: 60 },
          domains: [{ id: "software_engineering", directness: "direct" }],
        },
      ],
    };
    expect(parseRealTask(more, DEFAULT_TASK).bench).toBe("swe_bench_pro");
    expect(pickDrilldownBenchmark(v, "maths")?.id).toBe("frontiermath_tiers_1_3_v2");
  });

  const withPro: Vocabulary = {
    ...v,
    benchmarks: [
      ...v.benchmarks,
      {
        id: "swe_bench_pro",
        name: "SWE-bench Pro",
        unit: "percent",
        higher_is_better: true,
        models: 5,
        independent_models: 5,
        range: { min: 40, max: 90 },
        domains: [{ id: "software_engineering", directness: "direct" }],
      },
    ],
  };

  it("says the estimate is the basis and explains the preselected drill-down", () => {
    const note = parseRealTask(withPro, DEFAULT_TASK).trace[0].note;
    expect(note).toContain("Software engineering capability: estimated from");
    expect(note).toContain("SWE-bench Verified is preselected for Measured by");
    expect(note).toContain("the direct benchmark with the most verified lineup models (6)");
    expect(note).toContain("also direct: SWE-bench Pro (5)");
  });

  it("lists the domain's direct benchmarks with their coverage, chosen one first", () => {
    expect(rankChoices(withPro, "software_engineering").map((b) => [b.id, b.models])).toEqual([
      ["swe_bench_verified", 6],
      ["swe_bench_pro", 5],
    ]);
    expect(rankChoices(withPro, null)).toEqual([]);
  });

  it("switches to an explicit benchmark without inventing a task floor", () => {
    const spec = parsedSpec(withPro, DEFAULT_TASK);
    const next = switchBenchmark(withPro, spec, "swe_bench_pro");
    expect(next.bench).toBe("swe_bench_pro");
    expect(next.basis).toBe("benchmark");
    const floors = next.conds.filter((c) => c.f === "bench");
    expect(floors).toEqual([]);
    expect(next.conds.length).toBe(spec.conds.length);
    const own = { ...spec, conds: [...spec.conds, { f: "bench", b: "swe_bench_verified", min: 60 } as Cond] };
    expect(switchBenchmark(withPro, own, "swe_bench_pro").conds).toContainEqual({
      f: "bench", b: "swe_bench_verified", min: 60,
    });
  });

  it("says what it could not apply instead of sending a condition without data", () => {
    const parsed = parseRealTask(v, "fast EU chatbot");
    expect(parsed.conds.some((c) => c.f === "ttft")).toBe(false);
    expect(parsed.trace.map((t) => t.note)).toContain(
      "no latency measurements in this snapshot; not applied",
    );
  });
});

it("keeps production probe bytes unchanged for an equivalent generic facet", () => {
  const condition = "model.weights_openness = open_weights";
  const spec: Spec = {
    ...realBaseSpec(v),
    conds: [
      {
        f: "facet",
        facet: "model.weights_openness",
        op: "=",
        value: "open_weights",
      },
    ],
  };
  const question = realQuestions(v, spec, []).find((candidate) => candidate.id === "open");
  const option = question?.opts.find((candidate) => candidate.label === "Yes");
  if (!option) throw new Error("production open-weights question was not offered");
  const sent = toDecisionSpec(sendable(v, spec), "none");
  const beforeBoardDeduplication = JSON.stringify({
    ...sent,
    where: [...(sent.where ?? []), condition],
    explain: "none",
    limit: 500,
  });

  expect(JSON.stringify(probeSpec(sent, option))).toBe(beforeBoardDeduplication);
  expect(probeSpec(sent, option).where).toEqual([condition, condition]);
});

describe("what is offered", () => {
  it("offers nothing the snapshot has no verified data for", () => {
    const zero = new Set(v.facets.filter((f) => f.known === 0).map((f) => f.id));
    expect(zero.has("offering.speed.throughput")).toBe(true);
    for (const option of facetOptions(v))
      if (option.c.f === "facet") expect(zero.has(option.c.facet)).toBe(false);
    expect(facetOptions(v).map((o) => o.label)).not.toContain("Output throughput");
    expect(offeredAxes(v)).not.toContain("tps");
    expect(offeredAxes(v)).not.toContain("ttft");
    expect(offeredWeights(v)).toEqual(["cap", "cost"]);
    expect(offeredBenchmarks(v).every((b) => b.models > 0)).toBe(true);
  });

  it("builds templates only on benchmarks that exist", () => {
    const ids = new Set(v.benchmarks.map((b) => b.id));
    for (const t of realTemplates(v)) expect(ids.has(t.spec.bench)).toBe(true);
    expect(realTemplates({ ...v, benchmarks: [], domains: [] })).toEqual([]);
  });
});

describe("every spec the page can generate", () => {
  const generated = everySpec(v);
  const known = new Set([
    ...v.facets.map((f) => f.id),
    ...v.benchmarks.map((b) => b.id),
    ...v.domains.map((d) => d.id),
  ]);

  it("includes a next-question probe for every option on the default task", () => {
    const probes = generated.filter((g) => g.name.startsWith("probe default task "));
    const options = realQuestions(v, parsedSpec(v, DEFAULT_TASK), []).flatMap((q) => q.opts);
    expect(probes).toHaveLength(options.length);
    expect(options.length).toBeGreaterThan(0);
    for (const probe of probes) {
      expect(probe.spec.explain).toBe("none");
      expect(probe.spec.where).toEqual(
        expect.arrayContaining(generated.find((g) => g.name === "default task")!.spec.where!),
      );
    }
  });

  it("matches the golden file the Python registry test parses", () => {
    const text = JSON.stringify(generated, null, 2) + "\n";
    if (process.env.UPDATE_GOLDEN || !existsSync(GOLDEN)) writeFileSync(GOLDEN, text);
    expect(JSON.parse(readFileSync(GOLDEN, "utf8"))).toEqual(generated);
    expect(generated.length).toBeGreaterThan(60);
  });

  it.each(generated.map((g) => [g.name, g.spec] as const))(
    "%s validates against the contract and names only vocabulary IDs",
    (_name, spec) => {
      expect(validateSpec(spec), JSON.stringify(validateSpec.errors)).toBe(true);
      for (const id of facetsIn(spec)) expect(known.has(id), id).toBe(true);
      expect(spec.task_tokens).toBeDefined();
      expect(spec.optimize).not.toHaveProperty("weights.offering.speed.throughput");
    },
  );
});
