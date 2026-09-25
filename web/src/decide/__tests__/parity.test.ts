// The TypeScript engine must give the same answers as the handoff's
// modelspec-data.js on every spec here. The handoff file is the behavioural
// spec; this test is what "port it faithfully" means.
import { describe, expect, it } from "vitest";
import * as JS from "@handoff/modelspec-data";
import { buildCatalogue, FACETS, TEMPLATES } from "../engine/catalogue";
import { evaluate, parseTask, suggestions } from "../engine/reference";
import type { Cond, Spec } from "../engine/types";

/* eslint-disable @typescript-eslint/no-explicit-any */
const id = (r: any) => r?.m.id ?? null;
function project(e: any) {
  const insepTop = e.insep ? e.insep(e.shortlist.top).map(id) : null;
  return {
    rows: e.rows.map((r: any) => [
      r.m.id,
      r.status,
      r.best.o.id,
      r.dropAt,
      r.cap,
      r.cost,
      r.tps,
      !!r.labOnly,
      r.rank ?? null,
      r.score ?? null,
      r.best.t.map((t: any) => [t.s, t.why ?? null]),
    ]),
    inScope: e.inScope.map(id),
    feasible: e.feasible.map(id),
    may: e.may.map((r: any) => [id(r), r.unrankedWhy ?? null]),
    excluded: e.excluded.map(id),
    funnel: e.funnel.map((f: any) => [f.label, f.n, f.may]),
    frontier: e.frontier ?? null,
    shortlist: e.shortlist
      ? [
          id(e.shortlist.top),
          id(e.shortlist.value),
          id(e.shortlist.clears),
          id(e.shortlist.open),
          e.shortlist.bar,
        ]
      : null,
    insepTop,
    near:
      e.nearMisses?.map((n: any) => [
        id(n.row),
        n.ci,
        n.why,
        n.relaxed,
        n.off.o.id,
      ]) ?? null,
    costs:
      e.costs?.map((c: any) => [
        c.i,
        c.label,
        c.pts,
        c.unlocks,
        id(c.bestAlt),
      ]) ?? null,
    tip: e.tip
      ? [
          e.tip.lo?.at ?? null,
          id(e.tip.lo?.who),
          e.tip.hi?.at ?? null,
          id(e.tip.hi?.who),
        ]
      : null,
  };
}
const projectQ = (qs: any[]) =>
  qs.map((q) => [
    q.id,
    q.gain,
    q.opts.map((o: any) => [o.label, o.n, o.may, o.removes]),
  ]);

const TASKS = [
  "Refactor a large Rust codebase, precision matters",
  "Coding agent that fixes failing tests in a TypeScript monorepo, cheap",
  "Rerank search results for a help centre",
  "Embed documents for semantic search, EU only, GDPR",
  "Transcribe support calls in real time",
  "Read charts from screenshots",
  "Shell automation for devops, fast and interactive",
  "Math proofs, accuracy matters, commercial",
  "Private assistant we self-host on-prem",
  "Summarise meeting notes",
  "",
];

function specs(): Spec[] {
  const out: Spec[] = [];
  for (const t of TEMPLATES)
    out.push(structuredClone({ ...t.spec, task: t.task }));
  for (const text of TASKS) {
    const p = parseTask(text);
    out.push({
      task: text,
      tokIn: 40000,
      tokOut: 4000,
      bench: p.bench,
      w: p.w,
      conds: p.conds,
    });
  }
  const base: Spec = {
    tokIn: 40000,
    tokOut: 4000,
    bench: "CodeBench Pro",
    w: { cap: 0.6, cost: 0.3, speed: 0.1 },
    conds: [{ f: "type", v: "llm" }, { f: "active" }],
  };
  FACETS.forEach((f, i) => {
    out.push({ ...base, conds: [...base.conds, f.c] });
    out.push({
      ...base,
      conds: [...base.conds, { ...f.c, soft: true } as Cond],
    });
    const g = FACETS[(i + 3) % FACETS.length];
    out.push({
      ...base,
      w: { cap: 0.2, cost: 0.3, speed: 0.5 },
      conds: [...base.conds, f.c, g.c],
    });
  });
  for (const bench of ["TermTasks 4", "ReasonHard"])
    out.push({ ...base, bench });
  out.push({
    ...base,
    bench: "VoxWER",
    conds: [{ f: "type", v: "speech" }, { f: "active" }],
  });
  out.push({
    ...base,
    bench: "IntentRoute",
    conds: [{ f: "type", v: "decision" }],
  });
  out.push({
    ...base,
    conds: [
      ...base.conds,
      { f: "task$", max: 0.0001 },
      { f: "bench", b: "CodeBench Pro", min: 60, indep: true },
    ],
  });
  out.push({ ...base, conds: [] });
  out.push({
    ...base,
    tokIn: 200000,
    tokOut: 0,
    w: { cap: 1, cost: 0, speed: 0 },
  });
  return out;
}

describe("the TypeScript engine matches the handoff reference engine", () => {
  const D = buildCatalogue();
  const JD = JS.buildCatalogue();

  it("builds the same catalogue", () => {
    expect(D.models.length).toBe(25);
    expect(D.offerings).toBe(60);
    expect(JSON.parse(JSON.stringify(D))).toEqual(
      JSON.parse(JSON.stringify(JD)),
    );
  });

  it.each(specs().map((s, i) => [i, s] as const))(
    "spec %i evaluates the same",
    (_i, spec) => {
      expect(project(evaluate(D, structuredClone(spec)))).toEqual(
        project(JS.evaluate(JD, structuredClone(spec))),
      );
      expect(
        project(evaluate(D, structuredClone(spec), { lite: true })),
      ).toEqual(
        project(JS.evaluate(JD, structuredClone(spec), { lite: true })),
      );
    },
  );

  it.each(specs().map((s, i) => [i, s] as const))(
    "spec %i asks the same next questions",
    (_i, spec) => {
      expect(projectQ(suggestions(D, structuredClone(spec), []))).toEqual(
        projectQ(JS.suggestions(JD, structuredClone(spec), [])),
      );
      expect(
        projectQ(suggestions(D, structuredClone(spec), ["task$", "open"])),
      ).toEqual(
        projectQ(JS.suggestions(JD, structuredClone(spec), ["task$", "open"])),
      );
    },
  );

  it.each(TASKS)("parses %j the same", (text) => {
    expect(parseTask(text)).toEqual(JS.parseTask(text));
  });

  it("keeps the same templates and facets", () => {
    expect(TEMPLATES).toEqual(JS.TEMPLATES);
    expect(FACETS).toEqual(JS.FACETS);
  });
});
