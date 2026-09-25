import { expect, it } from "vitest";
import {
  encodeSpec,
  decodeSpec,
  snapshotId,
  setWeight,
  baseSpec,
} from "../state/spec";
it("round-trips Unicode tasks, conditions and axes through the hash", () => {
  const spec = { ...baseSpec, task: "分析 Rust 🦀" };
  expect(decodeSpec(encodeSpec(spec, "ctx"))).toEqual({ spec, x: "ctx" });
});
it("rejects corrupt hashes and unsafe numeric or catalogue values", () => {
  expect(decodeSpec("#s=broken")).toBeNull();
  expect(
    decodeSpec(encodeSpec({ ...baseSpec, tokIn: -1 }, "task$")),
  ).toBeNull();
  expect(
    decodeSpec(encodeSpec({ ...baseSpec, bench: "Unknown Bench" }, "task$")),
  ).toBeNull();
});
it("accepts a published benchmark ID, a domain and a vocabulary facet condition", () => {
  const spec = {
    ...baseSpec,
    bench: "swe_bench_verified",
    domain: "software_engineering",
    conds: [
      ...baseSpec.conds,
      { f: "facet" as const, facet: "offering.data.trains_on_customer_data", op: "=" as const, value: false },
      { f: "facet" as const, facet: "offering.region", op: "in" as const, value: ["global"] },
    ],
  };
  expect(decodeSpec(encodeSpec(spec, "task$"))).toEqual({ spec, x: "task$" });
  expect(
    decodeSpec(
      encodeSpec(
        { ...baseSpec, conds: [{ f: "facet", facet: "Not A Facet", op: "=", value: 1 }] },
        "task$",
      ),
    ),
  ).toBeNull();
});
it("identifies the whole spec deterministically without editor IDs", () => {
  expect(snapshotId(baseSpec)).toBe(snapshotId(structuredClone(baseSpec)));
  expect(snapshotId({ ...baseSpec, bench: "ReasonHard" })).not.toBe(
    snapshotId(baseSpec),
  );
  expect(snapshotId({ ...baseSpec, task: "changed" })).not.toBe(
    snapshotId(baseSpec),
  );
  expect(
    snapshotId({
      ...baseSpec,
      conds: baseSpec.conds.map((c) => ({ ...c, id: "editor" })),
    }),
  ).toBe(snapshotId(baseSpec));
});
it("renormalises the other weights preserving their ratio, including zero", () => {
  const w = setWeight({ cap: 0.6, cost: 0.3, speed: 0.1 }, "cost", 0.5);
  expect(w.cap).toBeCloseTo(3 / 7, 12);
  expect(w.cost).toBe(0.5);
  expect(w.speed).toBeCloseTo(1 / 14, 12);
  expect(setWeight({ cap: 1, cost: 0, speed: 0 }, "cap", 0.5)).toEqual({
    cap: 0.5,
    cost: 0.25,
    speed: 0.25,
  });
});
it("keeps a template snapshot ID after hash restoration and key reordering", () => {
  const spec = {
    tokIn: 40000,
    tokOut: 4000,
    bench: "CodeBench Pro",
    w: { cost: 0.3, speed: 0.1, cap: 0.6 },
    conds: baseSpec.conds,
    task: "template",
  };
  const restored = decodeSpec(encodeSpec(spec, "task$"));
  expect(restored).not.toBeNull();
  if (restored) expect(snapshotId(restored.spec)).toBe(snapshotId(spec));
});
it("rejects a relative reference with no measurement before it reaches the engine", () => {
  expect(
    decodeSpec(
      encodeSpec(
        {
          ...baseSpec,
          conds: [{ f: "rel", ref: "norrow-fjord-code", b: "VoxWER" }],
        },
        "task$",
      ),
    ),
  ).toBeNull();
});
