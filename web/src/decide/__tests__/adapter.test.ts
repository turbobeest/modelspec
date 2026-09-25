import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DECIDE_ENDPOINT,
  fictionalEngine,
  hostedEngine,
  templates,
  catalogue,
} from "../adapter";
import { baseSpec } from "../state/spec";
import type { Spec } from "../adapter";
const budget = templates[0].spec;
const decide = (s: Spec = budget) => fictionalEngine.decide(s);
const contractSpec = {
  spec_version: 1 as const,
  snapshot: "latest" as const,
  task_type: "refactor" as const,
  where: ["model.class = text-generator"],
  optimize: { min: "offering.price.input" },
  explain: "full" as const,
};
const answer = {
  contract_version: "1.0",
  decision_id: "dec_12345678",
  snapshot: "snap_12345678",
  spec_hash: `sha256:${"a".repeat(64)}`,
  explain: "full",
  status: "answered",
  results: [],
  may_qualify: [],
  eliminated: { funnel: [], models: [] },
  constraint_costs: [],
  tipping_points: [],
  relax: [],
  warnings: [],
};
afterEach(() => vi.unstubAllGlobals());
describe("the fictional decision adapter", () => {
  it("maps ranked results, missing independent evidence and eliminations into the contract envelope", () => {
    const d = decide();
    expect(d.results[0].offering.model).toBe("norrow/norrow-fjord-code");
    expect(d.results[0].offering.provider).toBe("Arcgrid");
    expect(d.results).toHaveLength(7);
    expect(d.may_qualify.map((r) => r.model)).toEqual(["oban/oban-cairn-1"]);
    expect(d.results[0].p_best).toBeNull();
    expect(d.warnings).toContain("fictional_sample_data");
  });
  it("selects the fastest offering when speed outweighs cost", () => {
    const d = decide({ ...baseSpec, w: { cap: 0.4, cost: 0.1, speed: 0.5 } });
    const r = d.explanation.rows.find((r) => r.m.name === "Fjord Code");
    expect(r?.best.o.provider).toBe("Norrow Platform");
    expect(r?.best.o.tps).toBe(140);
  });
  it("keeps soft misses without adding a score or a penalty", () => {
    const plain = decide(baseSpec),
      soft = decide({
        ...baseSpec,
        conds: [...baseSpec.conds, { f: "open", v: true, soft: true }],
      });
    expect(soft.results.map((r) => r.offering.model)).toEqual(
      plain.results.map((r) => r.offering.model),
    );
    expect(soft.results[0].warnings).toContain("outside_soft_preference");
    expect(soft.results[0].soft_penalty).toBe(0);
  });
  it("flags lab fallback and computes the not-separable interval rule", () => {
    expect(decide(baseSpec).results[0].warnings).toContain(
      "lab_reported_fallback",
    );
    const d = decide();
    expect(
      d.explanation.insep(d.explanation.shortlist.top).map((r) => r.m.name),
    ).toEqual(["Talon 2", "Tide 4 Reason", "Fjord L"]);
  });
  it("assigns the first eliminating condition, even if another offering fails a different condition", () => {
    const d = decide();
    const r = d.explanation.rows.find((r) => r.m.name === "Q-Prime");
    expect(r?.dropAt).toBe(3);
    expect(
      d.eliminated.models.find((m) => m.model === "quillon/quillon-q-prime")
        ?.condition,
    ).toBe("≤ $0.100 per task");
  });
  it("computes constraint costs in the benchmark unit and a minimal near-miss relaxation", () => {
    const d = decide();
    expect(
      d.constraint_costs.find((c) => c.condition === "≤ $0.100 per task")?.gain
        .codebench_pro,
    ).toBeCloseTo(7.9);
    expect(d.near_misses[0].relaxed).toEqual({ f: "task$", max: 1.35 });
    const n = d.near_misses[0],
      s = {
        ...budget,
        conds: budget.conds.map((c, i) => (i === n.ci ? n.relaxed || c : c)),
      };
    expect(decide(s).results.map((r) => r.offering.model)).toContain(
      "quillon/quillon-q-prime",
    );
  });
  it("reports the .01 cost-weight tipping sweep and orders next questions by removals", () => {
    const d = decide();
    expect(d.tipping_points).toEqual([
      {
        description: "Tide 4 takes #1 at cost weight 0.57",
        dimension: "-cost_per_task",
        threshold: 0.57,
        new_top: "meridian/meridian-tide-4",
      },
    ]);
    expect(decide(baseSpec).questions.map((q) => q.id)).toEqual([
      "task$",
      "open",
      "resid",
    ]);
  });
  it("only puts qualifying measured models on the frontier, and changes it with the axis", () => {
    const d = decide(baseSpec);
    expect(d.frontier.map((r) => r.m.name)).toEqual([
      "Wren 7B",
      "Tide 4 Mini",
      "Fjord S",
      "Talon 2 Flash",
      "Tide 4",
      "Fjord Code",
      "Cairn 1",
      "Q-Prime",
    ]);
    expect(
      fictionalEngine
        .decide(baseSpec, { axis: "tps" })
        .frontier.map((r) => r.m.name),
    ).not.toEqual(d.frontier.map((r) => r.m.name));
    expect(d.winning_strip.at(-1)?.row?.m.name).toBe("Q-Prime");
  });
  it("keeps a qualifier without primary evidence in may-qualify and never assigns it a rank", () => {
    const d = decide({ ...baseSpec, bench: "ChartRead" });
    expect(d.results).toHaveLength(0);
    expect(d.may_qualify).toHaveLength(17);
    expect(
      d.explanation.rows.find((r) => r.m.name === "Fjord Code")?.unrankedWhy,
    ).toBe("no ChartRead result to rank on");
  });
  it("returns a minimal relaxation even when no single-condition near miss exists", () => {
    const d = decide({
      ...baseSpec,
      conds: [
        ...baseSpec.conds,
        { f: "ctx", min: 9000000 },
        { f: "task$", max: 0 },
      ],
    });
    expect(d.results).toHaveLength(0);
    expect(d.relax).toHaveLength(2);
  });
  it("posts a contract spec to the hosted decision endpoint and validates the decision", async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(answer), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetch);
    await expect(hostedEngine.decide(contractSpec)).resolves.toEqual(answer);
    expect(fetch).toHaveBeenCalledWith(
      DECIDE_ENDPOINT,
      expect.objectContaining({
        method: "POST",
        mode: "cors",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(contractSpec),
      }),
    );
    expect(catalogue.offerings).toBe(60);
  });
  it("preserves the API error code and never accepts an invalid success body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            contract_version: "1.0",
            error: { code: "invalid_spec", message: "Unknown facet" },
          }),
          { status: 422, headers: { "content-type": "application/json" } },
        ),
      ),
    );
    await expect(hostedEngine.decide(contractSpec)).rejects.toMatchObject({
      status: 422,
      code: "invalid_spec",
      message: "Unknown facet",
    });

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(
        new Response(JSON.stringify({ ...answer, snapshot: "latest" }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    await expect(hostedEngine.decide(contractSpec)).rejects.toThrow(
      "invalid decision response",
    );
  });
});
it("tests all offerings in three values and selects a passing one before price", () => {
  const spec = {
      ...baseSpec,
      conds: [...baseSpec.conds, { f: "ret0" as const }],
    },
    d = fictionalEngine.decide(spec);
  const r = d.explanation.rows.find((r) => r.m.name === "Fjord Code");
  expect(r?.offs.map((o) => o.s)).toEqual([-1, 1, 1, -1]);
  expect(r?.best.o.provider).toBe("Stratus");
  const eu = fictionalEngine.decide({
    ...baseSpec,
    conds: [...baseSpec.conds, { f: "resid", v: "EU" }],
  });
  expect(eu.explanation.rows.find((r) => r.m.name === "Q-Swift")?.status).toBe(
    0,
  );
});
