import { z } from "zod";
import { sha256 } from "@noble/hashes/sha2.js";
import { BENCH, buildCatalogue } from "../engine/catalogue";
import type { Spec, Weights } from "../engine/types";
export type Axis = "task$" | "in$" | "ttft" | "tps" | "ctx";
const positive = z.number().finite().nonnegative();
/** A fictional benchmark name (demo), or a published benchmark ID (real mode). */
const bench = z
  .string()
  .refine((v) => Object.hasOwn(BENCH, v) || /^[a-z][a-z0-9_]*$/.test(v));
const facetId = z.string().regex(/^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/);
const facetValue = z.union([
  z.string().min(1).max(200),
  z.number().finite(),
  z.boolean(),
  z.array(z.string().min(1).max(200)).min(1),
]);
const metadata = {
  id: z.string().optional(),
  soft: z.boolean().optional(),
  from: z.boolean().optional(),
};
const condition = z.discriminatedUnion("f", [
  z.object({
    ...metadata,
    f: z.literal("type"),
    v: z.enum(["llm", "embed", "rerank", "vision", "speech", "decision"]),
  }),
  z.object({ ...metadata, f: z.literal("active") }),
  z.object({ ...metadata, f: z.literal("ctx"), min: positive }),
  z.object({ ...metadata, f: z.literal("open"), v: z.boolean() }),
  z.object({ ...metadata, f: z.literal("commercial") }),
  z.object({
    ...metadata,
    f: z.literal("bench"),
    b: bench,
    min: positive,
    indep: z.boolean().optional(),
  }),
  z.object({ ...metadata, f: z.literal("task$"), max: positive }),
  z.object({ ...metadata, f: z.literal("in$"), max: positive }),
  z.object({
    ...metadata,
    f: z.literal("resid"),
    v: z.enum(["EU", "US", "UK"]),
  }),
  z.object({ ...metadata, f: z.literal("ret0") }),
  z.object({ ...metadata, f: z.literal("ttft"), max: positive }),
  z.object({ ...metadata, f: z.literal("tps"), min: positive }),
  z.object({ ...metadata, f: z.literal("origin"), ex: z.array(z.string()) }),
  z.object({
    ...metadata,
    f: z.literal("facet"),
    facet: facetId,
    op: z.enum(["=", "!=", "<=", ">=", "in", "not in"]),
    value: facetValue,
  }),
  z.object({
    ...metadata,
    f: z.literal("rel"),
    ref: z.string().refine((v) => Object.hasOwn(buildCatalogue().byId, v)),
    b: bench,
  }),
]);
const schema = z.object({
  task: z.string().optional(),
  tokIn: positive,
  tokOut: positive,
  bench,
  w: z
    .object({
      cap: positive.max(1),
      cost: positive.max(1),
      speed: positive.max(1),
    })
    .refine((w) => Math.abs(w.cap + w.cost + w.speed - 1) < 0.00001),
  conds: z
    .array(condition)
    .refine(
      (conds) =>
        conds.every(
          (c) =>
            c.f !== "rel" ||
            buildCatalogue().byId[c.ref]?.bench.some((b) => b.b === c.b),
        ),
      "Relative reference has no evidence on this benchmark",
    ),
  bar: positive.nullable().optional(),
  domain: z.string().regex(/^[a-z][a-z0-9_]*$/).optional(),
});
export const baseSpec: Spec = {
  task: "",
  tokIn: 40000,
  tokOut: 4000,
  bench: "CodeBench Pro",
  w: { cap: 0.6, cost: 0.3, speed: 0.1 },
  conds: [{ f: "type", v: "llm" }, { f: "active" }],
};
export function encodeSpec(spec: Spec, x: Axis) {
  return "#s=" + btoa(encodeURIComponent(JSON.stringify({ ...spec, x })));
}
export function decodeSpec(hash: string): { spec: Spec; x: Axis } | null {
  try {
    const raw: unknown = JSON.parse(
      decodeURIComponent(atob(hash.replace(/^#s=/, ""))),
    );
    const spec = schema.parse(raw);
    const axis = z
      .object({
        x: z.enum(["task$", "in$", "ttft", "tps", "ctx"]).default("task$"),
      })
      .parse(raw);
    return { spec, x: axis.x };
  } catch {
    return null;
  }
}
export function specHash(spec: Spec) {
  const clean = {
    ...spec,
    conds: spec.conds.map((c) => ({ ...c, id: undefined })),
  };
  return Array.from(
    sha256(
      new TextEncoder().encode(
        JSON.stringify(clean, (_key, value: unknown) => {
          if (value && typeof value === "object" && !Array.isArray(value))
            return Object.fromEntries(
              Object.entries(value).sort(([a], [b]) => a.localeCompare(b)),
            );
          return value;
        }),
      ),
    ),
    (b) => b.toString(16).padStart(2, "0"),
  ).join("");
}
export const snapshotId = (spec: Spec) =>
  "snap_2026-09-24_" + specHash(spec).slice(0, 12);
/** Set one weight and renormalise the others among `keys` (the sliders offered). */
export function setWeight(
  w: Weights,
  key: keyof Weights,
  value: number,
  keys: readonly (keyof Weights)[] = ["cap", "cost", "speed"],
): Weights {
  const rest = 1 - value,
    others = keys.filter((k) => k !== key),
    sum = others.reduce((a, k) => a + w[k], 0);
  const next = { ...w, [key]: value };
  for (const k of others) next[k] = sum ? rest * (w[k] / sum) : rest / 2;
  return next;
}
