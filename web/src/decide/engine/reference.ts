// The reference decision engine from the Claude Design handoff (MODEL-150),
// ported to TypeScript. It is the behavioural spec for the real engine, and it
// runs only over the fictional catalogue. Keep its rules exactly as the
// handoff's modelspec-data.js has them: parity.test.ts compares the two.
//
// Nothing outside src/decide/adapter/ imports this module. The UI talks to
// the adapter, never to the engine.
import { BENCH, TODAY, TYPES } from "./catalogue";
import type {
  BenchDef,
  Catalogue,
  Cond,
  Evidence,
  Model,
  Offering,
  Spec,
  Weights,
} from "./types";

// ---------- formatting
const benchDef = (benchmark: string): BenchDef =>
  BENCH[benchmark] ?? {
    unit: "unit not recorded",
    d: 2,
    hi: true,
    types: [],
  };
export const fmtB = (b: string, v: number | null | undefined) =>
  v == null ? "—" : v.toFixed(benchDef(b).d) + (benchDef(b).pct ? "%" : "");
export const fmtCI = (b: string, r: { ci: number | null }) =>
  r.ci == null ? "no interval" : "± " + r.ci.toFixed(benchDef(b).d);
export const money = (k: number | null | undefined) =>
  k == null
    ? "unknown"
    : k < 0.01
      ? "$" + k.toFixed(4)
      : k < 1
        ? "$" + k.toFixed(3)
        : "$" + k.toFixed(2);
export const per1M = (p: number | null | undefined) =>
  p == null ? "—" : "$" + p.toFixed(2);
export const tok = (n: number | null | undefined) =>
  n == null ? "unknown" : n >= 1e6 ? n / 1e6 + "M" : Math.round(n / 1000) + "K";
export const num = (n: number | null | undefined) =>
  n == null ? "—" : n.toLocaleString("en-US");
export const daysAgo = (d: string) =>
  Math.round((new Date(TODAY).getTime() - new Date(d).getTime()) / 864e5);

// ---------- conditions
/** A condition's result on one offering: pass (1), unknown (0) or fail (−1). */
export interface Test {
  s: 1 | 0 | -1;
  why?: string;
}
const P: Test = { s: 1 };
const un = (why: string): Test => ({ s: 0, why });
const fl = (why: string): Test => ({ s: -1, why });
const regionIn = (r: string, v: string) =>
  v === "EU"
    ? /^eu-/.test(r)
    : v === "US"
      ? /^us-/.test(r)
      : v === "UK"
        ? /^uk-/.test(r)
        : false;
export const offCost = (o: Offering, spec: Pick<Spec, "tokIn" | "tokOut">) =>
  o.in == null ? null : (o.in * spec.tokIn + (o.out || 0) * spec.tokOut) / 1e6;
export function benchVal(
  m: Model,
  b: string,
  indepOnly?: boolean,
): Evidence | null {
  const rs = m.bench.filter((x) => x.b === b);
  const ind = rs.find((x) => x.by === "indep");
  if (ind) return ind;
  return indepOnly ? null : rs[0] || null;
}
export const cmpB = (b: string, v: number, floor: number) =>
  BENCH[b].hi ? v >= floor : v <= floor;

export function condLabel(c: Cond, D: Catalogue): string {
  switch (c.f) {
    case "type":
      return "Type: " + TYPES[c.v];
    case "active":
      return "Offered now";
    case "ctx":
      return "Context ≥ " + tok(c.min) + " tokens";
    case "open":
      return c.v === false ? "Open weights: exclude" : "Open weights: require";
    case "commercial":
      return "Licence allows commercial use";
    case "bench":
      return `${c.b} ${BENCH[c.b].hi ? "≥" : "≤"} ${fmtB(c.b, c.min)}${c.indep ? " · independent" : ""}`;
    case "task$":
      return "≤ " + money(c.max) + " per task";
    case "in$":
      return "Input ≤ " + per1M(c.max) + " / 1M tokens";
    case "resid":
      return "Data residency: " + c.v;
    case "ret0":
      return "Data retention: 0 days";
    case "ttft":
      return "First token ≤ " + num(c.max) + " ms";
    case "tps":
      return "Throughput ≥ " + num(c.min) + " tokens/s";
    case "origin":
      return "Origin: exclude " + c.ex.join(", ");
    case "rel":
      return `≥ ${D.byId[c.ref].name} on ${c.b}, and cheaper`;
    case "facet":
      return `${c.facet} ${c.op} ${Array.isArray(c.value) ? c.value.join(", ") : String(c.value)}`;
  }
}

export function testCond(
  c: Cond,
  m: Model,
  o: Offering,
  spec: Spec,
  D: Catalogue,
): Test {
  switch (c.f) {
    case "type":
      return m.type === c.v
        ? P
        : fl(
            `${m.type === null ? "class not available" : TYPES[m.type]}, not ${TYPES[c.v]}`,
          );
    case "active":
      return m.status === "retired"
        ? fl(`retired ${m.retiredOn}, in the live archive`)
        : P;
    case "ctx":
      return m.ctx == null
        ? un("context length not published")
        : m.ctx >= c.min
          ? P
          : fl(`context ${tok(m.ctx)}, you need ${tok(c.min)}`);
    case "open":
      return m.open === (c.v !== false)
        ? P
        : fl(m.open ? "open weights, which you excluded" : "closed weights");
    case "commercial":
      return m.commercial == null
        ? un("licence terms unclear")
        : m.commercial
          ? P
          : fl(`${m.lic} forbids commercial use`);
    case "bench": {
      const x = benchVal(m, c.b, c.indep);
      if (!x) {
        const any = benchVal(m, c.b, false);
        return any
          ? un(`no independent ${c.b} yet; lab reports ${fmtB(c.b, any.v)}`)
          : un(`no ${c.b} result`);
      }
      return cmpB(c.b, x.v, c.min)
        ? P
        : fl(`${c.b} ${fmtB(c.b, x.v)}, your floor is ${fmtB(c.b, c.min)}`);
    }
    case "task$": {
      const k = offCost(o, spec);
      return k == null
        ? un("price not published")
        : k <= c.max
          ? P
          : fl(`${money(k)} per task, your cap is ${money(c.max)}`);
    }
    case "in$":
      return o.in == null
        ? un("price not published")
        : o.in <= c.max
          ? P
          : fl(`input ${per1M(o.in)}/1M, your cap is ${per1M(c.max)}`);
    case "resid":
      return o.regions == null
        ? un(`${c.v} data residency not stated`)
        : o.regions.some((x) => regionIn(x, c.v))
          ? P
          : fl(`served from ${o.regions.join(", ")}; no ${c.v} region`);
    case "ret0":
      return o.ret == null
        ? un("retention terms not published")
        : o.ret === 0
          ? P
          : o.ret === "contract"
            ? fl("0-day retention needs an enterprise contract")
            : fl(`retains data ${o.ret} days`);
    case "ttft":
      return o.ttft == null
        ? un("time to first token not yet measured")
        : o.ttft <= c.max
          ? P
          : fl(`first token ${num(o.ttft)} ms, your cap is ${num(c.max)} ms`);
    case "tps":
      return o.tps == null
        ? un("throughput not yet measured")
        : o.tps >= c.min
          ? P
          : fl(`${o.tps} tokens/s, you need ${c.min}`);
    case "origin":
      return m.origin === null
        ? un("origin jurisdiction not published")
        : c.ex.includes(m.origin)
        ? fl(`origin ${m.origin}, which you excluded`)
        : P;
    case "rel": {
      const X = D.byId[c.ref];
      if (X.id === m.id) return fl("this is the reference model");
      const xb = benchVal(X, c.b, false)!,
        mb = benchVal(m, c.b, false);
      if (!mb) return un(`no ${c.b} result`);
      const xc = Math.min(
          ...X.offerings
            .map((q) => offCost(q, spec))
            .filter((v): v is number => v != null),
        ),
        mc = offCost(o, spec);
      if (!cmpB(c.b, mb.v, xb.v))
        return fl(
          `${c.b} ${fmtB(c.b, mb.v)}, below ${X.name}'s ${fmtB(c.b, xb.v)}`,
        );
      if (mc == null) return un("price not published");
      return mc < xc
        ? P
        : fl(
            `${money(mc)} per task, not cheaper than ${X.name} (${money(xc)})`,
          );
    }
    case "facet":
      return un(`${c.facet} is not in the fictional catalogue`);
  }
}

/** The minimal change to condition `c` that would let offering `o` of model `m` pass it. */
export function relaxValue(
  c: Cond,
  m: Model,
  o: Offering,
  spec: Spec,
): Cond | null {
  const up = (v: number, s: number) => Math.ceil(v / s) * s,
    dn = (v: number, s: number) => Math.floor(v / s) * s;
  switch (c.f) {
    case "ctx":
      return m.ctx != null ? { ...c, min: m.ctx } : null;
    case "bench": {
      const x = benchVal(m, c.b, c.indep);
      return x
        ? {
            ...c,
            min: BENCH[c.b].hi
              ? dn(x.v, BENCH[c.b].d === 3 ? 0.005 : 0.5)
              : up(x.v, 0.5),
          }
        : null;
    }
    case "task$": {
      const k = offCost(o, spec);
      return k != null ? { ...c, max: Math.ceil(k * 1000) / 1000 } : null;
    }
    case "in$":
      return { ...c, max: o.in! };
    case "ttft":
      return o.ttft != null ? { ...c, max: up(o.ttft, 50) } : null;
    case "tps":
      return o.tps != null ? { ...c, min: dn(o.tps, 5) } : null;
  }
  return null;
}

// ---------- evaluation
/** One offering tested against every condition. */
export interface OffEval {
  o: Offering;
  t: Test[];
  fails: number[];
  unks: number[];
  softs: number[];
  s: 1 | 0 | -1;
  cost: number | null;
}
/** One model: its status, its chosen offering, and where it dropped out. */
export interface Row {
  m: Model;
  offs: OffEval[];
  status: 1 | 0 | -1;
  best: OffEval;
  dropAt: number;
  capR: Evidence | null;
  cap: number | null;
  cost: number | null;
  tps: number | null;
  labOnly: boolean;
  rank?: number;
  score?: number;
  parts?: Weights;
  norm?: Weights;
  _q?: number;
  unrankedWhy?: string;
}
/** A row that is ranked: it qualifies and has a primary-benchmark result. */
export type RankedRow = Row & {
  capR: Evidence;
  cap: number;
  rank: number;
  score: number;
  parts: Weights;
  norm: Weights;
};
export interface FunnelStep {
  label: string;
  n: number;
  may: number;
  idx?: number;
}
export interface NearMiss {
  row: Row;
  ci: number;
  cond: Cond;
  why: string;
  relaxed: Cond | null;
  off: OffEval;
}
export interface CostOfCond {
  i: number;
  c: Cond;
  label: string;
  pts: number | null;
  unlocks: number;
  bestAlt: Row | undefined;
}
export interface Tip {
  lo: { at: number; who: Row } | null;
  hi: { at: number; who: Row } | null;
}
export interface Shortlist {
  top?: RankedRow;
  value?: RankedRow;
  clears?: RankedRow;
  open?: RankedRow;
  bar: number | null;
}
export interface LiteEval {
  rows: Row[];
  inScope: Row[];
  feasible: RankedRow[];
  may: Row[];
  excluded: Row[];
  funnel: FunnelStep[];
}
export interface FullEval extends LiteEval {
  frontier: string[];
  shortlist: Shortlist;
  insep: (r0: RankedRow | undefined) => RankedRow[];
  nearMisses: NearMiss[];
  costs: CostOfCond[];
  tip?: Tip;
}

export function evaluate(
  D: Catalogue,
  spec: Spec,
  opt: { lite: true },
): LiteEval;
export function evaluate(
  D: Catalogue,
  spec: Spec,
  opt?: { lite?: false },
): FullEval;
export function evaluate(
  D: Catalogue,
  spec: Spec,
  opt: { lite?: boolean } = {},
): LiteEval | FullEval {
  const conds = spec.conds;
  const w = spec.w,
    B = spec.bench;
  const speedFirst = w.speed > w.cost;
  const rows: Row[] = D.models.map((m) => {
    const offs: OffEval[] = m.offerings.map((o) => {
      const t = conds.map((c) => testCond(c, m, o, spec, D));
      const fails: number[] = [],
        unks: number[] = [],
        softs: number[] = [];
      t.forEach((x, i) => {
        if (x.s === -1) (conds[i].soft ? softs : fails).push(i);
        else if (x.s === 0) unks.push(i);
      });
      return {
        o,
        t,
        fails,
        unks,
        softs,
        s: fails.length ? -1 : unks.length ? 0 : 1,
        cost: offCost(o, spec),
      };
    });
    const status = Math.max(...offs.map((x) => x.s)) as 1 | 0 | -1;
    const pool = offs.filter((x) => x.s === status);
    pool.sort(
      (a, b) =>
        a.fails.length - b.fails.length ||
        a.softs.length - b.softs.length ||
        (speedFirst
          ? (b.o.tps || 0) - (a.o.tps || 0)
          : (a.cost ?? 1e9) - (b.cost ?? 1e9)),
    );
    const best = pool[0];
    // step at which the model drops out (prefix evaluation)
    let dropAt = -1;
    for (let i = 0; i < conds.length && dropAt < 0; i++) {
      const alive = offs.some((x) =>
        x.t.slice(0, i + 1).every((q, j) => q.s !== -1 || conds[j].soft),
      );
      if (!alive) dropAt = i;
    }
    const capR = benchVal(m, B, false);
    return {
      m,
      offs,
      status,
      best,
      dropAt,
      capR,
      cap: capR ? capR.v : null,
      cost: best.cost,
      tps: best.o.tps,
      labOnly: !!capR && capR.by === "lab",
    };
  });
  const typeCond = conds.findIndex((c) => c.f === "type");
  const inScope = rows.filter((x) => typeCond < 0 || x.dropAt !== typeCond);
  let feasible = rows.filter((x) => x.status === 1);
  const unranked = feasible.filter((x) => x.cap == null);
  feasible = feasible.filter((x) => x.cap != null);
  const may = rows
    .filter((x) => x.status === 0)
    .concat(
      unranked.map((x) => ({ ...x, unrankedWhy: `no ${B} result to rank on` })),
    );
  const excluded = rows.filter((x) => x.status === -1);
  rank(feasible, w, B);
  const ranked = feasible as RankedRow[];

  // funnel
  const funnel: FunnelStep[] = [
    { label: "Sample catalogue", n: D.models.length, may: 0 },
  ];
  conds.forEach((c, i) => {
    const alive = rows.filter((x) => x.dropAt < 0 || x.dropAt > i);
    const mayN = alive.filter(
      (x) =>
        !x.offs.some((o) =>
          o.t
            .slice(0, i + 1)
            .every((q, j) => q.s === 1 || (q.s === -1 && conds[j].soft)),
        ),
    ).length;
    funnel.push({ label: condLabel(c, D), n: alive.length, may: mayN, idx: i });
  });

  const lite: LiteEval = {
    rows,
    inScope,
    feasible: ranked,
    may,
    excluded,
    funnel,
  };
  if (opt.lite) return lite;

  // frontier (cost low, cap high)
  const hiB = BENCH[B].hi;
  const byCost = ranked
    .filter((x) => x.cost != null)
    .slice()
    .sort((a, b) => a.cost! - b.cost! || (hiB ? b.cap - a.cap : a.cap - b.cap));
  let bestCap = hiB ? -Infinity : Infinity;
  const frontier: string[] = [];
  byCost.forEach((x) => {
    if (hiB ? x.cap > bestCap : x.cap < bestCap) {
      frontier.push(x.m.id);
      bestCap = x.cap;
    }
  });

  // shortlist
  const top = ranked[0];
  const value = ranked
    .filter((x) => x.cost! > 0)
    .slice()
    .sort((a, b) => b.cap / b.cost! - a.cap / a.cost!)[0];
  const bar =
    spec.bar ??
    conds.find(
      (c): c is Extract<Cond, { f: "bench" }> => c.f === "bench" && c.b === B,
    )?.min ??
    null;
  const clears = ranked
    .filter((x) => bar == null || cmpB(B, x.cap, bar))
    .sort((a, b) => (a.cost as number) - (b.cost as number))[0];
  const open = ranked.find((x) => x.m.open);
  const shortlist: Shortlist = { top, value, clears, open, bar };
  // not separable
  const insep = (r0: RankedRow | undefined) =>
    !r0
      ? []
      : ranked.filter(
          (x) =>
            x !== r0 &&
            x.capR.ci != null &&
            r0.capR.ci != null &&
            Math.abs(x.cap - r0.cap) < Math.hypot(x.capR.ci, r0.capR.ci) &&
            x.cost! / r0.cost! < 2 &&
            r0.cost! / x.cost! < 2,
        );

  // near misses
  const nearMisses = excluded
    .filter((x) => x.dropAt !== typeCond && conds[x.dropAt]?.f !== "active")
    .map((x) => {
      const cand = x.offs
        .filter((o) => o.fails.length === 1)
        .sort((a, b) => (a.cost ?? 1e9) - (b.cost ?? 1e9))[0];
      if (!cand) return null;
      const ci = cand.fails[0],
        c = conds[ci];
      return {
        row: x,
        ci,
        cond: c,
        why: cand.t[ci].why!,
        relaxed: relaxValue(c, x.m, cand.o, spec),
        off: cand,
      };
    })
    .filter((x): x is NearMiss => !!x)
    .sort((a, b) => (hiB ? (b.row.cap ?? 0) - (a.row.cap ?? 0) : 0));

  // constraint cost
  const maxCap = (arr: RankedRow[]) =>
    arr.length
      ? hiB
        ? Math.max(...arr.map((x) => x.cap))
        : Math.min(...arr.map((x) => x.cap))
      : null;
  const nowMax = maxCap(ranked);
  const costs = conds
    .map((c, i): CostOfCond | null => {
      if (c.f === "type" || c.f === "active") return null;
      const alt = evaluate(
        D,
        { ...spec, conds: conds.filter((_, j) => j !== i) },
        { lite: true },
      );
      const altMax = maxCap(alt.feasible);
      const bestAlt = alt.feasible
        .slice()
        .sort((a, b) => (hiB ? b.cap - a.cap : a.cap - b.cap))[0];
      return {
        i,
        c,
        label: condLabel(c, D),
        pts:
          altMax == null || nowMax == null ? null : Math.abs(altMax - nowMax),
        unlocks: alt.feasible.length - ranked.length,
        bestAlt,
      };
    })
    .filter((x): x is CostOfCond => !!x);

  const out: FullEval = {
    ...lite,
    frontier,
    shortlist,
    insep,
    nearMisses,
    costs,
  };

  // tipping point on cost weight
  if (top) {
    const others = w.cap + w.speed || 1;
    const topAt = (wc: number) => {
      const ww = {
        cost: wc,
        cap: (1 - wc) * (w.cap / others),
        speed: (1 - wc) * (w.speed / others),
      };
      const f = ranked.slice();
      rank(f, ww, B, true);
      return f[0];
    };
    let lo: Tip["lo"] = null,
      hi: Tip["hi"] = null;
    for (let k = Math.round(w.cost * 100); k <= 100; k++) {
      const t = topAt(k / 100);
      if (t.m.id !== top.m.id) {
        hi = { at: k / 100, who: t };
        break;
      }
    }
    for (let k = Math.round(w.cost * 100); k >= 0; k--) {
      const t = topAt(k / 100);
      if (t.m.id !== top.m.id) {
        lo = { at: k / 100, who: t };
        break;
      }
    }
    out.tip = { lo, hi };
  }
  return out;
}

function rank(arr: Row[], w: Weights, B: string, quiet?: boolean) {
  if (!arr.length) return;
  const hiB = BENCH[B].hi;
  const caps = arr.map((x) => x.cap as number),
    lc = arr.map((x) => Math.log(Math.max(x.cost ?? 1, 1e-6))),
    sp = arr.map((x) => x.tps).filter((v): v is number => v != null);
  const n = (v: number, a: number, b: number) =>
    b - a < 1e-9 ? 1 : (v - a) / (b - a);
  const cMin = Math.min(...caps),
    cMax = Math.max(...caps),
    kMin = Math.min(...lc),
    kMax = Math.max(...lc),
    sMin = Math.min(...sp),
    sMax = Math.max(...sp);
  arr.forEach((x, i) => {
    const nc = hiB
      ? n(x.cap as number, cMin, cMax)
      : 1 - n(x.cap as number, cMin, cMax);
    const nk = 1 - n(lc[i], kMin, kMax);
    const ns = x.tps == null ? 0 : n(x.tps, sMin, sMax);
    const parts = { cap: w.cap * nc, cost: w.cost * nk, speed: w.speed * ns };
    const sc = parts.cap + parts.cost + parts.speed;
    if (quiet) x._q = sc;
    else {
      x.score = sc;
      x.parts = parts;
      x.norm = { cap: nc, cost: nk, speed: ns };
    }
  });
  arr.sort((a, b) => (quiet ? b._q! - a._q! : b.score! - a.score!));
  if (!quiet) arr.forEach((x, i) => (x.rank = i + 1));
}

// ---------- clarifying questions (ordered by how much they'd narrow)
export interface QuestionOpt {
  label: string;
  c: Cond;
  n?: number;
  may?: number;
  removes?: number;
  /** The probe for this answer failed; its count is unknown, the question stays. */
  failed?: boolean;
}
export interface Question {
  id: string;
  q: string;
  opts: QuestionOpt[];
  gain?: number;
}
export function suggestions(
  D: Catalogue,
  spec: Spec,
  dismissed: string[],
): Question[] {
  const has = (f: Cond["f"]) => spec.conds.some((c) => c.f === f);
  const type =
    spec.conds.find((c): c is Extract<Cond, { f: "type" }> => c.f === "type")
      ?.v || "llm";
  const Q: Question[] = [];
  if (!has("task$"))
    Q.push({
      id: "task$",
      q: "What can you spend per task?",
      opts: [0.02, 0.05, 0.1].map((v) => ({
        label: "≤ " + money(v),
        c: { f: "task$", max: v },
      })),
    });
  if (!has("resid"))
    Q.push({
      id: "resid",
      q: "Must data be processed in the EU?",
      opts: [{ label: "Yes, EU only", c: { f: "resid", v: "EU" } }],
    });
  if (!has("open"))
    Q.push({
      id: "open",
      q: "Do you need open weights?",
      opts: [{ label: "Yes", c: { f: "open", v: true } }],
    });
  if (!has("ret0"))
    Q.push({
      id: "ret0",
      q: "Do you need 0-day data retention?",
      opts: [{ label: "Yes", c: { f: "ret0" } }],
    });
  if (type === "llm" && !has("ttft"))
    Q.push({
      id: "ttft",
      q: "How soon must the first token arrive?",
      opts: [500, 1000].map((v) => ({
        label: "≤ " + num(v) + " ms",
        c: { f: "ttft", max: v },
      })),
    });
  if (!has("commercial"))
    Q.push({
      id: "commercial",
      q: "Is this for commercial use?",
      opts: [{ label: "Yes", c: { f: "commercial" } }],
    });
  const base = evaluate(D, spec, { lite: true });
  const baseN = base.feasible.length + base.may.length;
  return Q.filter((q) => !dismissed.includes(q.id))
    .map((q) => {
      q.opts.forEach((o) => {
        const e = evaluate(
          D,
          { ...spec, conds: spec.conds.concat(o.c) },
          { lite: true },
        );
        o.n = e.feasible.length;
        o.may = e.may.length;
        o.removes = baseN - (o.n + o.may);
      });
      q.gain = Math.max(...q.opts.map((o) => o.removes!));
      return q;
    })
    .sort((a, b) => b.gain! - a.gain!);
}

// ---------- plain-language parse (deterministic keyword classifier stand-in)
export interface ParsedTask {
  conds: Cond[];
  w: Weights;
  bench: string;
  trace: { word: string; note: string }[];
}
export function parseTask(text: string | null | undefined): ParsedTask {
  const t = (text || "").toLowerCase();
  const trace: ParsedTask["trace"] = [];
  const hit = (re: RegExp, note: string) => {
    const m = t.match(re);
    if (m) trace.push({ word: m[0], note });
    return !!m;
  };
  let type: Extract<Cond, { f: "type" }>["v"] = "llm",
    bench = "CodeBench Pro";
  if (hit(/rerank\w*/, "type: reranker")) {
    type = "rerank";
    bench = "RetrievalEval v2";
  } else if (
    hit(/embed\w*|retrieval|semantic search|\brag\b/, "type: embedding")
  ) {
    type = "embed";
    bench = "RetrievalEval v2";
  } else if (hit(/transcri\w*|speech|audio/, "type: speech")) {
    type = "speech";
    bench = "VoxWER";
  } else if (hit(/chart\w*|image\w*|vision|screenshot\w*/, "type: vision")) {
    type = "vision";
    bench = "ChartRead";
  } else if (hit(/terminal|shell|devops|cli\b/, "rank on TermTasks 4"))
    bench = "TermTasks 4";
  else if (hit(/math\w*|reason\w*|proof\w*/, "rank on ReasonHard"))
    bench = "ReasonHard";
  else
    hit(
      /refactor\w*|rust|code\w*|bug\w*|repo\w*|test\w*|typescript|python/,
      "rank on CodeBench Pro",
    );
  const conds: Cond[] = [
    { f: "type", v: type, from: true },
    { f: "active", from: true },
  ];
  const w = { cap: 0.6, cost: 0.3, speed: 0.1 };
  if (hit(/large|codebase|monorepo|long/, "context ≥ 200K"))
    conds.push({ f: "ctx", min: 200000, from: true });
  if (
    hit(
      /precision|precise|accura\w*|correct\w*|matters/,
      `${bench} floor, measured independently`,
    )
  ) {
    conds.push({
      f: "bench",
      b: bench,
      min:
        bench === "CodeBench Pro"
          ? 50
          : bench === "RetrievalEval v2"
            ? 0.6
            : 50,
      indep: true,
      from: true,
    });
    w.cap = 0.7;
    w.cost = 0.2;
    w.speed = 0.1;
  }
  if (hit(/cheap\w*|budget|low.cost/, "weight cost higher")) {
    w.cap = 0.5;
    w.cost = 0.4;
    w.speed = 0.1;
  }
  if (hit(/fast|latency|real.time|interactive/, "first token ≤ 1,000 ms")) {
    conds.push({ f: "ttft", max: 1000, from: true });
    w.speed = 0.3;
    w.cap = 0.5;
    w.cost = 0.2;
  }
  if (hit(/\beu\b|gdpr|europe\w*/, "EU data residency"))
    conds.push({ f: "resid", v: "EU", from: true });
  if (
    hit(
      /private|on.prem\w*|local|self.host\w*/,
      "open weights, 0-day retention",
    )
  ) {
    conds.push({ f: "open", v: true, from: true });
  }
  if (hit(/commercial/, "commercial licence"))
    conds.push({ f: "commercial", from: true });
  return { conds, w, bench, trace };
}
