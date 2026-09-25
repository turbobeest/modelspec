import {
  BENCH,
  buildCatalogue,
  FACETS,
  TEMPLATES,
  TYPES,
} from "../engine/catalogue";
import {
  evaluate,
  suggestions,
  condLabel,
  parseTask,
  fmtB,
  fmtCI,
  money,
  per1M,
  tok,
  num,
  daysAgo,
} from "../engine/reference";
import type { Row, FullEval, RankedRow } from "../engine/reference";
import type { BenchDef, Cond, Evidence, Spec } from "../engine/types";
import type { Decision, EvidenceItem, OfferingRef } from "./contract";
export {
  DECIDE_ENDPOINT,
  DECIDE_TIMEOUT_MS,
  DecideApiError,
  PUBLIC_DECIDE_ENDPOINT,
  decideWithFallback,
  hostedEngine,
  mayBeLimit,
} from "./hosted";
export type { HostedAnswer, SpecIssue } from "./hosted";
export { decisionSchema, decisionSpecSchema } from "./contract";
export type {
  Decision,
  DecisionSpec,
  EvidenceItem,
  OfferingRef,
  Result,
} from "./contract";
import { snapshotId, specHash } from "../state/spec";
import type { Axis } from "../state/spec";
export {
  BENCH,
  FACETS,
  TYPES,
  parseTask,
  fmtB,
  fmtCI,
  money,
  per1M,
  tok,
  num,
  daysAgo,
};
export type { Row, RankedRow, Cond, Evidence, Spec };
export const catalogue = buildCatalogue();
export const label = (c: Cond) => condLabel(c, catalogue);
export const relaxLabel = (c: Cond) =>
  "Relax to " + label(c).replace(/^.*?(≤|≥)/, "$1");
export const templates = TEMPLATES.map((t) => ({
  ...t,
  counts: evaluate(catalogue, t.spec, { lite: true }),
}));
export const candidateQuestions = (spec: Spec, dismissed: string[]) =>
  suggestions(catalogue, spec, dismissed).map((question) => ({
    ...question,
    opts: question.opts.map((option) => ({
      label: option.label,
      c: option.c,
    })),
  }));
export const status = (r: Row) =>
  r.status === 0
    ? "May qualify"
    : r.status === 1
      ? "Qualifies"
      : "Excluded";
export const reason = (r: Row) =>
  r.status === -1
    ? r.best.t[r.dropAt]?.why ||
      r.best.fails
        .map((i) => r.best.t[i].why)
        .filter(Boolean)
        .join("; ") ||
      r.unrankedWhy
    : r.unrankedWhy ||
      r.best.unks
        .map((i) => r.best.t[i].why)
        .filter(Boolean)
        .join("; ");
export const axisDefs = {
  task$: {
    label: "$ per task",
    unit: "USD per task, from your token counts",
    log: true,
    low: true,
    get: (r: Row) => r.cost,
    fmt: money,
  },
  in$: {
    label: "Input price",
    unit: "$ per 1M input tokens",
    log: true,
    low: true,
    get: (r: Row) => r.best.o.in,
    fmt: per1M,
  },
  ttft: {
    label: "Time to first token",
    unit: "ms",
    log: true,
    low: true,
    get: (r: Row) => r.best.o.ttft,
    fmt: (n: number) => num(Math.round(n)) + " ms",
  },
  tps: {
    label: "Output throughput",
    unit: "tokens/s",
    log: false,
    low: false,
    get: (r: Row) => r.tps,
    fmt: (n: number) => Math.round(n) + " tok/s",
  },
  ctx: {
    label: "Context length",
    unit: "tokens",
    log: true,
    low: false,
    get: (r: Row) => r.m.ctx,
    fmt: tok,
  },
};
function axisRecord<T>(value: (axis: Axis) => T): Record<Axis, T> {
  return {
    "task$": value("task$"),
    "in$": value("in$"),
    ttft: value("ttft"),
    tps: value("tps"),
    ctx: value("ctx"),
  };
}
export interface AdapterDecision extends Decision {
  population: { models: number; offerings: number };
  explanation: FullEval;
  nearMisses: FullEval["nearMisses"];
  questions: ReturnType<typeof suggestions>;
  frontier: Row[];
  winning_strip: { row: Row | undefined; start: number; count: number }[];
  benchmarks: Record<string, BenchDef>;
  not_plotted: Record<Axis, string[]>;
  available_axes: Record<Axis, boolean>;
}
/** Synchronous boundary for the fictional demo. The hosted contract is async. */
interface SampleDecisionEngine {
  decide(
    spec: Spec,
    options?: { axis?: Axis; dismissed?: string[] },
  ): AdapterDecision;
}
const ref = (r: Row): OfferingRef => ({
  model: r.m.lab + "/" + r.m.id,
  provider: r.best.o.provider,
  region: null,
  tier: null,
});
const ev = (e: Evidence): EvidenceItem => ({
  benchmark: e.b,
  version: null,
  sub_category: null,
  value: e.v,
  unit: BENCH[e.b].unit,
  n: null,
  measured_by: e.by === "indep" ? "independent" : "provider_self_report",
  effort: e.effort,
  harness: null,
  harness_unregistered: false,
  date: e.date,
  date_type: "published",
  source: e.src,
  source_snapshot: null,
  directness: "direct",
});
export function plotDomain(
  rows: Row[],
  spec: Spec,
  axis: Axis,
  benchmark = BENCH[spec.bench],
) {
  const ax = axisDefs[axis],
    xc = spec.conds.find((c) => c.f === axis),
    yc = spec.conds.find((c) => c.f === "bench" && c.b === spec.bench);
  const xv = xc && ("min" in xc ? xc.min : "max" in xc ? xc.max : null),
    yv = yc && "min" in yc ? yc.min : null;
  const values = rows.flatMap((r) => {
    const x = ax.get(r);
    return x === null || r.cap === null ? [] : [{ r, x, y: r.cap }];
  });
  const xs = values.map((p) => p.x).concat(xv == null ? [] : [xv]),
    ys = values
      .flatMap((p) => [p.y - (p.r.capR?.ci || 0), p.y + (p.r.capR?.ci || 0)])
      .concat(yv == null ? [] : [yv]);
  const t = (v: number) => (ax.log ? Math.log10(Math.max(v, 1e-9)) : v),
    ti = (v: number) => (ax.log ? 10 ** v : v);
  let x0 = t(xs.length ? Math.min(...xs) : 0.001),
    x1 = t(xs.length ? Math.max(...xs) : 1),
    y0 = ys.length ? Math.min(...ys) : 0,
    y1 = ys.length ? Math.max(...ys) : 100;
  const px = (x1 - x0 || 1) * 0.07,
    py = (y1 - y0 || 1) * 0.1;
  x0 -= px;
  x1 += px;
  y0 -= py;
  y1 += py;
  return {
    values,
    xv,
    yv,
    x0: ti(x0),
    x1: ti(x1),
    y0,
    y1,
    fx: (v: number) => (t(v) - x0) / (x1 - x0),
    fy: (v: number) =>
      benchmark.hi ? 1 - (v - y0) / (y1 - y0) : (v - y0) / (y1 - y0),
    xi: (v: number) => ti(x0 + v * (x1 - x0)),
    yi: (v: number) =>
      benchmark.hi ? y0 + (1 - v) * (y1 - y0) : y0 + v * (y1 - y0),
  };
}
function minimalRelaxation(spec: Spec): string[] {
  const indices = spec.conds.map((_, i) => i);
  function search(
    size: number,
    start: number,
    chosen: number[],
  ): number[] | null {
    if (chosen.length === size) {
      const alt = evaluate(
        catalogue,
        { ...spec, conds: spec.conds.filter((_, i) => !chosen.includes(i)) },
        { lite: true },
      );
      return alt.feasible.length ? chosen : null;
    }
    for (let i = start; i < indices.length; i++) {
      const result = search(size, i + 1, [...chosen, i]);
      if (result) return result;
    }
    return null;
  }
  for (let size = 1; size <= indices.length; size++) {
    const result = search(size, 0, []);
    if (result) return result.map((i) => label(spec.conds[i]));
  }
  return ["Choose a primary benchmark with evidence"];
}

export const fictionalEngine: SampleDecisionEngine = {
  decide(spec, { axis = "task$", dismissed = [] } = {}) {
    const e = evaluate(catalogue, spec),
      ax = axisDefs[axis],
      bd = BENCH[spec.bench],
      domain = spec.bench.toLowerCase().replaceAll(/[^a-z0-9]+/g, "_");
    // Primary evidence missing is a may-qualify row in all views.
    e.rows = e.rows.map((r) => e.may.find((m) => m.m.id === r.m.id) || r);
    e.inScope = e.inScope.map(
      (r) => e.rows.find((m) => m.m.id === r.m.id) || r,
    );
    const ordered = e.feasible
      .filter((r) => ax.get(r) !== null)
      .slice()
      .sort(
        (a, b) =>
          (ax.low ? 1 : -1) * ((ax.get(a) ?? 0) - (ax.get(b) ?? 0)) ||
          (bd.hi ? -1 : 1) * (a.cap - b.cap),
      );
    let best = bd.hi ? -Infinity : Infinity;
    const frontier: Row[] = [];
    for (const r of ordered)
      if (bd.hi ? r.cap > best : r.cap < best) {
        frontier.push(r);
        best = r.cap;
      }
    const pd = plotDomain(e.inScope, spec, axis),
      winning_strip: AdapterDecision["winning_strip"] = [];
    for (let i = 0; i < 60; i++) {
      const cap = pd.xi((i + 0.5) / 60),
        row = ordered
          .filter((r) =>
            ax.low
              ? (ax.get(r) ?? Infinity) <= cap
              : (ax.get(r) ?? -Infinity) >= cap,
          )
          .sort((a, b) => (bd.hi ? b.cap - a.cap : a.cap - b.cap))[0],
        last = winning_strip.at(-1);
      if (last && last.row === row) last.count++;
      else winning_strip.push({ row, start: i, count: 1 });
    }
    const tips = [e.tip?.lo, e.tip?.hi].flatMap((t) =>
      t
        ? [
            {
              description: `${t.who.m.name} takes #1 at cost weight ${t.at.toFixed(2)}`,
              dimension: "-offering.cost_per_task",
              threshold: t.at,
              new_top: ref(t.who).model,
            },
          ]
        : [],
    );
    return {
      contract_version: "1.4",
      out_of_lineup: 0,
      decision_id: "dec_fictional" + specHash(spec).slice(0, 12),
      snapshot: snapshotId(spec),
      spec_hash: "sha256:" + specHash(spec),
      explain: "full",
      status: e.feasible.length ? "answered" : "no_feasible",
      results: e.feasible.map((r) => ({
        rank: r.rank,
        offering: ref(r),
        harness: null,
        effort: r.capR.effort,
        evidence: [{ domain, items: r.m.bench.map(ev) }],
        estimates: null,
        p_best: null,
        top3_stability: null,
        soft_penalty: 0,
        contributions: (
          [
            { key: "cap", dimension: domain },
            { key: "cost", dimension: "-offering.cost_per_task" },
            { key: "speed", dimension: "output_tps" },
          ] as const
        ).map(({ key, dimension }) => ({
          dimension,
          weight: spec.w[key],
          value: r.norm[key],
          normalisation:
            key === "cost"
              ? "inverted log min-max over qualifiers"
              : "min-max over qualifiers",
          evidence: key === "cap" ? [ev(r.capR)] : [],
        })),
        warnings: [
          ...(r.labOnly ? ["lab_reported_fallback"] : []),
          ...(r.best.softs.length ? ["outside_soft_preference"] : []),
          ...(r.m.provisional ? ["provisional"] : []),
        ],
      })),
      may_qualify: e.may.map((r) => ({
        model: ref(r).model,
        offering: ref(r),
        unknown: r.unrankedWhy
          ? [domain]
          : r.best.unks.map((i) => spec.conds[i].f),
      })),
      eliminated: {
        funnel: e.funnel.slice(1).map((f, i) => ({
          condition: f.label,
          before: e.funnel[i].n,
          after: f.n,
          may_qualify: f.may,
        })),
        models: e.excluded.map((r) => ({
          values: [],
          offering: ref(r),
          unit: null,
          records: [],
          model: ref(r).model,
          condition: label(spec.conds[r.dropAt]),
          value: r.best.t[r.dropAt]?.why || null,
        })),
      },
      constraint_costs: e.costs.map((c) => ({
        units: {},
        records: [],
        condition: c.label,
        admits: Math.max(0, c.unlocks),
        gain: c.pts === null ? {} : { [domain]: c.pts },
      })),
      tipping_points: tips,
      relax: e.feasible.length ? [] : minimalRelaxation(spec),
      warnings: [
        "fictional_sample_data",
        "sample_spec_hash_not_contract_canonical",
        "sample_snapshot_not_signed",
      ],
      population: { models: catalogue.models.length, offerings: catalogue.offerings },
      explanation: e,
      near_misses: [],
      top: [],
      chart: null,
      number_origins: [],
      sources: [],
      nearMisses: e.nearMisses,
      questions: suggestions(catalogue, spec, dismissed)
        .filter((q) => (q.gain ?? 0) > 0)
        .slice(0, 3),
      frontier,
      winning_strip,
      benchmarks: BENCH,
      not_plotted: axisRecord((key) =>
        e.inScope
          .filter((row) => axisDefs[key].get(row) === null || row.cap === null)
          .map((row) => row.m.lab + "/" + row.m.id),
      ),
      available_axes: axisRecord((key) =>
        e.inScope.some((row) => axisDefs[key].get(row) !== null),
      ),
    };
  },
};
