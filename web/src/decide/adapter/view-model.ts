import type {
  BenchDef,
  Cond,
  Evidence,
  FacetValue,
  Model,
  Offering,
  Spec,
  TypeKey,
} from "../engine/types";
import type { FullEval, NearMiss, Question, RankedRow, Row, Test } from "../engine/reference";
import type { Axis } from "../state/spec";
import type { AdapterDecision } from "./index";
import type {
  Decision,
  DecisionSpec,
  EvidenceItem,
  OfferingRef,
} from "./contract";
import {
  renderContractCondition,
  renderUnknownFacets,
} from "./condition-label";

const CLASS_TO_TYPE: Readonly<Record<string, TypeKey>> = {
  "text-generator": "llm",
  vectoriser: "embed",
  orderer: "rerank",
  transcriber: "speech",
  analyser: "vision",
  decider: "decision",
};

const ALL_TYPES: TypeKey[] = [
  "llm",
  "embed",
  "rerank",
  "vision",
  "speech",
  "decision",
];

const slug = (value: string) =>
  value
    .toLowerCase()
    .replaceAll(/[^a-z0-9]+/g, "_")
    .replaceAll(/^_+|_+$/g, "");

const title = (value: string) =>
  value
    .split(/[._/-]+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

function classId(type: Extract<Cond, { f: "type" }>["v"]): string {
  switch (type) {
    case "llm":
      return "text-generator";
    case "embed":
      return "vectoriser";
    case "rerank":
      return "orderer";
    case "vision":
      return "analyser";
    case "speech":
      return "transcriber";
    case "decision":
      return "decider";
  }
}

const BARE = /^[A-Za-z0-9_][A-Za-z0-9_.:/+@-]*$/;
const RESERVED = new Set(["in", "not", "measured_after", "soft", "unknown", "true", "false"]);

/** A value in the compact condition syntax: bare when it would read back as itself. */
export function compactValue(value: FacetValue): string {
  if (Array.isArray(value)) return `{${value.map(compactValue).join(", ")}}`;
  if (typeof value === "boolean" || typeof value === "number") return JSON.stringify(value);
  const looksTyped = /^-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$/.test(value);
  return BARE.test(value) && !looksTyped && !RESERVED.has(value) && !value.endsWith(":")
    ? value
    : JSON.stringify(value);
}

export function contractCondition(condition: Cond): string {
  const soft = condition.soft ? " soft(0.2)" : "";
  switch (condition.f) {
    case "type":
      return `model.class = ${classId(condition.v)}`;
    case "active":
      return "model.lifecycle = active";
    case "ctx":
      return `model.context_window >= ${condition.min}${soft}`;
    case "open":
      return `model.weights_openness ${condition.v ? "=" : "!="} open_weights${soft}`;
    case "commercial":
      return `licence.commercial_use in {permitted, permitted_with_conditions}${soft}`;
    case "bench":
      return `${slug(condition.b)} >= ${condition.min}${condition.indep ? " @independent" : ""}${soft}`;
    case "task$":
      return `offering.cost_per_task <= ${condition.max}${soft}`;
    case "in$":
      return `offering.price.input <= ${condition.max}${soft}`;
    case "resid":
      return `offering.region in {${condition.v}}${soft}`;
    case "ret0":
      return `offering.data.zero_retention = true${soft}`;
    case "ttft":
      return `offering.speed.time_to_first_token <= ${condition.max}${soft}`;
    case "tps":
      return `offering.speed.throughput >= ${condition.min}${soft}`;
    case "origin":
      return `origin.lab_jurisdiction not in {${condition.ex.join(", ")}}${soft}`;
    case "rel":
      return `${slug(condition.b)} >= model(${condition.ref})${soft}`;
    case "facet":
      return `${condition.facet} ${condition.op} ${compactValue(condition.value)}${soft}`;
  }
}

function taskType(task: string | undefined): DecisionSpec["task_type"] {
  const text = (task ?? "").toLowerCase();
  if (/\bbug|fix|defect/.test(text)) return "bug_fix";
  if (/\btest/.test(text)) return "test_writing";
  if (/\bdoc|readme/.test(text)) return "docs";
  if (/\bmigrat|upgrade/.test(text)) return "migration";
  if (/\bperformance|latency|fast/.test(text)) return "performance";
  if (/\bsecurity|vulnerab/.test(text)) return "security_fix";
  if (/\breview|audit/.test(text)) return "review";
  if (/\banaly|research/.test(text)) return "analysis";
  if (/\bdata|transform|convert/.test(text)) return "data_transform";
  if (/\bconfig|infra|deploy/.test(text)) return "config_infra";
  if (/\brefactor/.test(text)) return "refactor";
  return "new_feature";
}

function capabilities(spec: Spec): DecisionSpec["capabilities"] {
  if (spec.domain) return { [spec.domain]: "required" };
  const type = spec.conds.find(
    (condition): condition is Extract<Cond, { f: "type" }> => condition.f === "type",
  )?.v;
  if (type === "llm") return { software_engineering: "required" };
  if (type === "embed" || type === "rerank") return { retrieval: "required" };
  if (type === "vision") return { vision_documents: "required" };
  if (type === "speech") return { multilingual: "preferred" };
  return undefined;
}

export function toDecisionSpec(
  spec: Spec,
  explain: "none" | "full",
): DecisionSpec {
  const weights: Record<string, number> = {};
  if (spec.w.cap > 0) weights[slug(spec.bench)] = spec.w.cap;
  if (spec.w.cost > 0) weights["-offering.cost_per_task"] = spec.w.cost;
  if (spec.w.speed > 0) weights["offering.speed.throughput"] = spec.w.speed;
  return {
    spec_version: 1,
    snapshot: "latest",
    task_type: taskType(spec.task),
    capabilities: capabilities(spec),
    task_tokens: { input: Math.round(spec.tokIn), output: Math.round(spec.tokOut) },
    where: spec.conds.map(contractCondition),
    optimize: { weights },
    unknowns: "default",
    explain,
    limit: 20,
  };
}

function sameOffering(left: OfferingRef, right: OfferingRef): boolean {
  return (
    left.model === right.model &&
    left.provider === right.provider &&
    left.region === right.region &&
    left.tier === right.tier
  );
}

function sourceRecords(decision: Decision): Map<string, string[]> {
  const byRecord = new Map<string, Set<string>>();
  for (const origin of decision.number_origins) {
    for (const record of origin.records) {
      const sources = byRecord.get(record) ?? new Set<string>();
      origin.sources.forEach((source) => sources.add(source));
      byRecord.set(record, sources);
    }
  }
  return new Map(
    [...byRecord].map(([record, sources]) => [record, [...sources].sort()]),
  );
}

function numberFact(
  facts: Decision["top"][number]["facts"],
  facet: string,
  sources: Map<string, string[]>,
): number | null {
  const fact = facts.find((item) => item.facet === facet);
  if (
    !fact ||
    typeof fact.value !== "number" ||
    !fact.record_id ||
    !sources.get(fact.record_id)?.length
  )
    return null;
  return fact.value;
}

function stringFact(
  facts: Decision["top"][number]["facts"],
  facet: string,
  sources: Map<string, string[]>,
): string | null {
  const fact = facts.find((item) => item.facet === facet);
  if (
    !fact ||
    typeof fact.value !== "string" ||
    !fact.record_id ||
    !sources.get(fact.record_id)?.length
  )
    return null;
  return fact.value;
}

function engineCost(
  facts: Decision["top"][number]["facts"],
): { cost?: number; costFormula?: string } {
  const fact = facts.find((item) => item.facet === "offering.cost_per_task");
  return fact && typeof fact.value === "number" && fact.formula
    ? { cost: fact.value, costFormula: fact.formula }
    : {};
}

function uiEvidence(item: EvidenceItem): Evidence {
  return {
    b: item.benchmark,
    v: item.value,
    ci: null,
    by: item.measured_by === "provider_self_report" ? "lab" : "indep",
    date: item.date,
    effort: item.effort ?? "not available",
    harness: item.harness ?? "not available",
    who: item.measured_by,
    src: item.source,
  };
}

function testsFor(
  spec: Spec,
  state: 1 | 0 | -1,
  unknown: string[],
  reason: string,
): Test[] {
  return spec.conds.map((condition) => {
    const rendered = contractCondition(condition);
    const facet = rendered.split(" ", 1)[0];
    if (state === -1 && reason.includes(rendered))
      return { s: -1, why: renderContractCondition(reason) };
    if (state === 0 && unknown.some((item) => item === facet || rendered.includes(item)))
      return { s: 0, why: `unknown: ${renderUnknownFacets(unknown)}` };
    return {
      s: state === 1 ? 1 : 0,
      why: state === 0 ? renderContractCondition(reason) : undefined,
    };
  });
}

function modelAndOffering(
  decision: Decision,
  offeringRef: OfferingRef,
  sources: Map<string, string[]>,
): { model: Model; offering: Offering; evidence: Evidence[] } {
  const values = decision.top.find((candidate) => sameOffering(candidate.offering, offeringRef));
  const facts = values?.facts ?? [];
  const modelId = offeringRef.model;
  const [lab, tail] = modelId.split("/", 2);
  const priceIn = numberFact(facts, "offering.price.input", sources);
  const priceOut = numberFact(facts, "offering.price.output", sources);
  const ttft = numberFact(facts, "offering.speed.time_to_first_token", sources);
  const throughput = numberFact(facts, "offering.speed.throughput", sources);
  const retention = numberFact(facts, "offering.data.retention", sources);
  const className = stringFact(facts, "model.class", sources);
  const openness = stringFact(facts, "model.weights_openness", sources);
  const lifecycle = stringFact(facts, "model.lifecycle", sources);
  const evidence = (values?.evidence ?? []).flatMap((group) => group.items.map(uiEvidence));
  const offering: Offering = {
    id: [offeringRef.provider, modelId, offeringRef.region, offeringRef.tier]
      .filter((part) => part !== null)
      .join("/"),
    provider: offeringRef.provider ?? "Provider not available",
    regions: offeringRef.region ? [offeringRef.region] : null,
    in: priceIn,
    out: priceOut,
    ttft,
    tps: throughput,
    ret: retention,
    ...engineCost(facts),
  };
  const open = openness === null ? null : openness === "open_weights";
  const model: Model = {
    id: tail ?? modelId,
    name: title(tail ?? modelId),
    lab,
    labName: title(lab),
    origin: stringFact(facts, "origin.lab_jurisdiction", sources),
    type: className ? (CLASS_TO_TYPE[className] ?? null) : null,
    status: lifecycle === "active" || lifecycle === "retired" ? lifecycle : null,
    open,
    lic: stringFact(facts, "licence.commercial_use", sources),
    commercial: null,
    ctx: numberFact(facts, "model.context_window", sources),
    rel: stringFact(facts, "model.release_date", sources),
    in: priceIn ?? 0,
    out: priceOut,
    ttft,
    tps: throughput,
    hosts: offeringRef.provider ? [offeringRef.provider] : [],
    bench: evidence,
    offerings: [offering],
  };
  return { model, offering, evidence };
}

/**
 * $ per task. The engine's `offering.cost_per_task` when the decision shows it;
 * otherwise the same formula (docs/decision-contract.md) over the engine's prices.
 */
function costPerTask(offering: Offering, spec: Spec): number | null {
  if (offering.cost !== undefined) return offering.cost;
  if (offering.in === null || offering.out === null) return null;
  return (spec.tokIn * offering.in + spec.tokOut * offering.out) / 1_000_000;
}

function benchmarkDefinition(
  decision: Decision,
  benchmark: string,
): BenchDef {
  const item = decision.top
    .flatMap((candidate) => candidate.evidence)
    .flatMap((group) => group.items)
    .find((evidence) => evidence.benchmark === benchmark);
  const dimension = decision.results
    .flatMap((result) => result.contributions)
    .find((contribution) => contribution.dimension.replace(/^-/, "") === benchmark)
    ?.dimension;
  const decimals = item && !Number.isInteger(item.value) ? 2 : 0;
  return {
    unit: item?.unit ?? "unit not recorded",
    pct: item?.unit === "percent",
    d: decimals,
    hi: dimension ? !dimension.startsWith("-") : true,
    types: ALL_TYPES,
  };
}

function axisValue(row: Row, axis: Axis): number | null {
  switch (axis) {
    case "task$":
      return row.cost;
    case "in$":
      return row.best.o.in;
    case "ttft":
      return row.best.o.ttft;
    case "tps":
      return row.tps;
    case "ctx":
      return row.m.ctx;
  }
}

function rankedRow(
  decision: Decision,
  result: Decision["results"][number],
  spec: Spec,
  sources: Map<string, string[]>,
): RankedRow {
  const { model, offering, evidence } = modelAndOffering(
    decision,
    result.offering,
    sources,
  );
  const selected = evidence.find((item) => item.b === spec.bench) ?? null;
  if (selected === null)
    throw new Error(
      `${result.offering.model} has no sourced ${spec.bench} evidence in this full decision`,
    );
  const norm = {
    cap:
      result.contributions.find((item) => item.dimension.replace(/^-/, "") === spec.bench)
        ?.value ?? 0,
    cost:
      result.contributions.find((item) =>
        ["offering.cost_per_task", "offering.price.input"].includes(
          item.dimension.replace(/^-/, ""),
        ),
      )?.value ?? 0,
    speed:
      result.contributions.find(
        (item) => item.dimension.replace(/^-/, "") === "offering.speed.throughput",
      )?.value ?? 0,
  };
  const parts = {
    cap: norm.cap * spec.w.cap,
    cost: norm.cost * spec.w.cost,
    speed: norm.speed * spec.w.speed,
  };
  const test = testsFor(spec, 1, [], "");
  return {
    m: model,
    offs: [
      {
        o: offering,
        t: test,
        fails: [],
        unks: [],
        softs: [],
        s: 1,
        cost: costPerTask(offering, spec),
      },
    ],
    status: 1,
    best: {
      o: offering,
      t: test,
      fails: [],
      unks: [],
      softs: [],
      s: 1,
      cost: costPerTask(offering, spec),
    },
    dropAt: -1,
    capR: selected,
    cap: selected.v,
    cost: costPerTask(offering, spec),
    tps: offering.tps,
    labOnly: selected.by === "lab",
    rank: result.rank,
    score: parts.cap + parts.cost + parts.speed,
    parts,
    norm,
  };
}

function unrankedRow(
  decision: Decision,
  offeringRef: OfferingRef,
  spec: Spec,
  sources: Map<string, string[]>,
  state: 0 | -1,
  unknown: string[],
  why: string,
): Row {
  const { model, offering, evidence } = modelAndOffering(
    decision,
    offeringRef,
    sources,
  );
  const selected = evidence.find((item) => item.b === spec.bench) ?? null;
  const tests = testsFor(spec, state, unknown, why);
  const failed = tests.flatMap((test, index) => (test.s === -1 ? [index] : []));
  const unresolved = tests.flatMap((test, index) => (test.s === 0 ? [index] : []));
  const off = {
    o: offering,
    t: tests,
    fails: failed,
    unks: unresolved,
    softs: [],
    s: state,
    cost: costPerTask(offering, spec),
  };
  return {
    m: model,
    offs: [off],
    status: state,
    best: off,
    dropAt: failed[0] ?? -1,
    capR: selected,
    cap: selected?.v ?? null,
    cost: off.cost,
    tps: offering.tps,
    labOnly: selected?.by === "lab",
    unrankedWhy: state === -1 ? renderContractCondition(why) : why,
  };
}

interface CandidateRow<T extends Row = Row> {
  row: T;
  hasOffering: boolean;
}

function rowModel(row: Row): string {
  return `${row.m.lab}/${row.m.id}`;
}

function consolidateRows<T extends Row>(
  base: CandidateRow<T>[],
  candidates: CandidateRow[],
  claimed: Set<string>,
): T[] {
  const seen = new Set<string>();
  const consolidated: T[] = [];
  for (const candidate of base) {
    const model = rowModel(candidate.row);
    if (claimed.has(model) || seen.has(model)) continue;
    seen.add(model);
    const variants = candidates.filter(
      (item) => rowModel(item.row) === model && item.hasOffering,
    );
    const members = variants.length > 0
      ? variants
      : candidates.filter((item) => rowModel(item.row) === model);
    const offerings = [
      ...new Map(members.map((item) => [item.row.best.o.id, item.row.best])).values(),
    ];
    consolidated.push({
      ...candidate.row,
      m: {
        ...candidate.row.m,
        offerings: offerings.map((offering) => offering.o),
      },
      offs: offerings,
    });
  }
  consolidated.forEach((row) => claimed.add(rowModel(row)));
  return consolidated;
}

function offeringKey(ref: OfferingRef): string {
  return JSON.stringify(ref);
}

function offeringId(ref: OfferingRef): string {
  return [ref.provider, ref.model, ref.region, ref.tier]
    .filter((part) => part !== null)
    .join("/");
}

function pareto(rows: RankedRow[], axis: Axis, highY: boolean): Row[] {
  const ordered = rows
    .filter((row) => axisValue(row, axis) !== null && row.cap !== null)
    .slice()
    .sort((left, right) => {
      const a = axisValue(left, axis) ?? 0;
      const b = axisValue(right, axis) ?? 0;
      const lowX = axis !== "tps" && axis !== "ctx";
      return (lowX ? a - b : b - a) || (highY ? (right.cap ?? 0) - (left.cap ?? 0) : (left.cap ?? 0) - (right.cap ?? 0));
    });
  const frontier: Row[] = [];
  let best = highY ? -Infinity : Infinity;
  for (const row of ordered) {
    const value = row.cap ?? (highY ? -Infinity : Infinity);
    if ((highY && value > best) || (!highY && value < best)) {
      frontier.push(row);
      best = value;
    }
  }
  return frontier;
}

function winningStrip(
  rows: RankedRow[],
  axis: Axis,
  highCapability: boolean,
): AdapterDecision["winning_strip"] {
  const values = rows.flatMap((row) => {
    const value = axisValue(row, axis);
    return value === null ? [] : [value];
  });
  if (!values.length) return [];
  const low = Math.min(...values);
  const high = Math.max(...values);
  const lowAxis = axis !== "tps" && axis !== "ctx";
  const out: AdapterDecision["winning_strip"] = [];
  for (let index = 0; index < 60; index += 1) {
    const threshold = low + ((high - low) * index) / 59;
    const row = rows
      .filter((candidate) => {
        const value = axisValue(candidate, axis);
        return value !== null && (lowAxis ? value <= threshold : value >= threshold);
      })
      .sort((left, right) =>
        highCapability
          ? (right.cap ?? -Infinity) - (left.cap ?? -Infinity)
          : (left.cap ?? Infinity) - (right.cap ?? Infinity),
      )[0];
    const last = out.at(-1);
    if (last && last.row === row) last.count += 1;
    else out.push({ row, start: index, count: 1 });
  }
  return out;
}

function shortlist(rows: RankedRow[], spec: Spec): FullEval["shortlist"] {
  const measured = rows.filter((row) => row.cap !== null && row.cost !== null);
  const value = measured
    .slice()
    .sort(
      (left, right) =>
        (right.cap ?? 0) / (right.cost ?? Infinity) -
        (left.cap ?? 0) / (left.cost ?? Infinity),
    )[0];
  const clears = measured
    .filter((row) => spec.bar === null || spec.bar === undefined || (row.cap ?? -Infinity) >= spec.bar)
    .sort((left, right) => (left.cost ?? Infinity) - (right.cost ?? Infinity))[0];
  return {
    top: rows[0],
    value,
    clears,
    open: rows.find((row) => row.m.open === true),
    bar: spec.bar ?? null,
  };
}

export function mapDecisionToViewModel(
  decision: Decision,
  spec: Spec,
  options: {
    axis: Axis;
    dismissed: string[];
    questions?: Question[];
    /** The benchmarks to offer, from the published vocabulary (real mode). */
    benchmarks?: Record<string, BenchDef>;
  },
): AdapterDecision {
  const sources = sourceRecords(decision);
  const rawFeasible: CandidateRow<RankedRow>[] = decision.results.map((result) => ({
    row: rankedRow(decision, result, spec, sources),
    hasOffering: result.offering.provider !== null,
  }));
  const rawMay: CandidateRow[] = decision.may_qualify.map((candidate) => {
    const ref = candidate.offering ?? {
      model: candidate.model,
      provider: null,
      region: null,
      tier: null,
    };
    return {
      row: unrankedRow(
        decision,
        ref,
        spec,
        sources,
        0,
        candidate.unknown,
        `unknown: ${renderUnknownFacets(candidate.unknown)}`,
      ),
      hasOffering: ref.provider !== null,
    };
  });
  const eliminatedByOffering = new Map<string, Decision["eliminated"]["models"][number]>();
  for (const eliminated of decision.eliminated.models) {
    const ref = eliminated.offering ?? {
      model: eliminated.model,
      provider: null,
      region: null,
      tier: null,
    };
    eliminatedByOffering.set(offeringKey(ref), eliminated);
  }
  const rawExcluded: CandidateRow[] = [...eliminatedByOffering.values()].map(
    (eliminated) => {
      const ref = eliminated.offering ?? {
        model: eliminated.model,
        provider: null,
        region: null,
        tier: null,
      };
      return {
        row: unrankedRow(
          decision,
          ref,
          spec,
          sources,
          -1,
          [],
          eliminated.condition,
        ),
        hasOffering: ref.provider !== null,
      };
    },
  );
  const rawRows: CandidateRow[] = [...rawFeasible, ...rawMay, ...rawExcluded];
  const claimed = new Set<string>();
  const feasible = consolidateRows(rawFeasible, rawRows, claimed);
  const may = consolidateRows(rawMay, rawRows, claimed);
  const excluded = consolidateRows(rawExcluded, rawRows, claimed);
  const rows = [...feasible, ...may, ...excluded];
  const benchmarks = options.benchmarks ? { ...options.benchmarks } : Object.fromEntries(
    [...new Set(decision.top.flatMap((candidate) => candidate.evidence.flatMap((group) => group.items.map((item) => item.benchmark))))].map(
      (benchmark) => [benchmark, benchmarkDefinition(decision, benchmark)],
    ),
  );
  if (!benchmarks[spec.bench]) benchmarks[spec.bench] = benchmarkDefinition(decision, spec.bench);
  const bench = benchmarks[spec.bench];
  const frontier = pareto(feasible, options.axis, bench.hi);
  const candidateRefs = new Map<string, OfferingRef>();
  decision.results.forEach((result) =>
    candidateRefs.set(offeringKey(result.offering), result.offering),
  );
  decision.may_qualify.forEach((candidate) => {
    const ref = candidate.offering ?? {
      model: candidate.model,
      provider: null,
      region: null,
      tier: null,
    };
    candidateRefs.set(offeringKey(ref), ref);
  });
  decision.eliminated.models.forEach((candidate) => {
    const ref = candidate.offering ?? {
      model: candidate.model,
      provider: null,
      region: null,
      tier: null,
    };
    candidateRefs.set(offeringKey(ref), ref);
  });
  const population = {
    models: new Set([...candidateRefs.values()].map((ref) => ref.model)).size,
    offerings: candidateRefs.size,
  };
  const eliminatedThrough = new Set<string>();
  const funnel = [
    { label: "All models", n: population.models, may: 0 },
    ...decision.eliminated.funnel.map((step) => {
      decision.eliminated.models
        .filter((candidate) => candidate.condition === step.condition)
        .forEach((candidate) => {
          const ref = candidate.offering ?? {
            model: candidate.model,
            provider: null,
            region: null,
            tier: null,
          };
          eliminatedThrough.add(offeringKey(ref));
        });
      const models = new Set(
        [...candidateRefs].flatMap(([key, ref]) =>
          eliminatedThrough.has(key) ? [] : [ref.model],
        ),
      ).size;
      const mayModels = new Set(decision.may_qualify.map((candidate) => candidate.model)).size;
      return {
        label: renderContractCondition(step.condition),
        n: models,
        may: step.may_qualify === 0 ? 0 : Math.min(models, mayModels),
      };
    }),
  ];
  while (funnel.length <= spec.conds.length)
    funnel.push({ label: "Condition not returned", n: feasible.length, may: may.length });
  const nearMisses: NearMiss[] = decision.near_misses.flatMap((miss) => {
    if (miss.offering.provider === null) return [];
    const row = excluded.find(
      (candidate) => rowModel(candidate) === miss.offering.model,
    );
    const conditionIndex = spec.conds.findIndex(
      (condition) => contractCondition(condition) === miss.condition,
    );
    if (
      !row ||
      conditionIndex < 0 ||
      row.best.o.id !== offeringId(miss.offering) ||
      row.best.fails.length !== 1 ||
      row.best.fails[0] !== conditionIndex
    ) return [];
    return [
      {
        row,
        ci: conditionIndex,
        cond: spec.conds[conditionIndex] ?? { f: "active" },
        why: `${renderContractCondition(miss.condition)}: ${miss.value ?? miss.values.join(", ")}`,
        relaxed: null,
        off: row.best,
      },
    ];
  });
  const evalView: FullEval = {
    rows,
    inScope: [...feasible, ...may],
    feasible,
    may,
    excluded,
    funnel,
    frontier: frontier.map((row) => row.m.id),
    shortlist: shortlist(feasible, spec),
    insep: (row) => {
      if (!row?.capR || row.capR.ci === null) return [];
      const interval = row.capR.ci;
      return feasible.filter(
        (other) =>
          other !== row &&
          other.capR?.ci !== null &&
          Math.abs((other.cap ?? 0) - (row.cap ?? 0)) <=
            (other.capR?.ci ?? 0) + interval,
      );
    },
    nearMisses,
    costs: decision.constraint_costs.map((cost, index) => ({
      i: index,
      c: spec.conds[index] ?? { f: "active" },
      label: renderContractCondition(cost.condition),
      pts: cost.gain[spec.bench] ?? null,
      unlocks: cost.admits,
      bestAlt: undefined,
    })),
    tip: undefined,
  };
  const notPlotted = axisRecord((axis) =>
    evalView.inScope
      .filter((row) => axisValue(row, axis) === null)
      .map((row) => row.m.lab + "/" + row.m.id),
  );
  return {
    ...decision,
    population,
    explanation: evalView,
    nearMisses,
    questions: (options.questions ?? []).filter(
      (question) => !options.dismissed.includes(question.id),
    ),
    frontier,
    winning_strip: winningStrip(feasible, options.axis, bench.hi),
    benchmarks,
    not_plotted: notPlotted,
    available_axes: axisRecord((axis) =>
      evalView.inScope.some((row) => axisValue(row, axis) !== null),
    ),
  };
}

function axisRecord<T>(value: (axis: Axis) => T): Record<Axis, T> {
  return {
    "task$": value("task$"),
    "in$": value("in$"),
    ttft: value("ttft"),
    tps: value("tps"),
    ctx: value("ctx"),
  };
}
