// Types for the reference engine port. The shapes follow the handoff's
// modelspec-data.js; the decision contract shapes live in ../adapter/contract.ts.

export type TypeKey =
  "llm" | "embed" | "rerank" | "vision" | "speech" | "decision";
export type Region = "EU" | "US" | "UK";

export interface BenchDef {
  unit: string;
  pct?: boolean;
  d: number;
  hi: boolean;
  types: TypeKey[];
}
export interface LabDef {
  name: string;
  origin: string;
  cloud: string;
  regions: string[];
}
export interface HostDef {
  name: string;
  regions: string[];
  pm: number;
  ttft?: number;
  ttftm?: number;
  tpsm: number;
  ret: number | "contract";
}

/** One measured result. `by` is who measured it: the lab, or an independent evaluator. */
export interface Evidence {
  b: string;
  v: number;
  ci: number | null;
  by: "lab" | "indep";
  date: string;
  effort: string;
  harness: string;
  who: string;
  src: string;
}

export type Retention = number | "contract" | null;

export interface Offering {
  id: string;
  provider: string;
  first?: boolean;
  regions: string[] | null;
  in: number | null;
  out: number | null;
  ttft: number | null;
  tps: number | null;
  ret: Retention;
}

export interface RawModel<E> {
  open: boolean;
  lic: string;
  commercial: boolean | null;
  ctx: number | null;
  rel: string;
  status?: "retired";
  retiredOn?: string;
  provisional?: boolean;
  in: number;
  out: number | null;
  ttft: number | null;
  tps: number | null;
  hosts: string[];
  fpRegions?: string[] | null;
  hostRegions?: string[];
  fpRet?: Retention;
  bench: E[];
}

export interface Model extends Omit<RawModel<Evidence>, "status"> {
  id: string;
  name: string;
  lab: string;
  labName: string;
  origin: string;
  type: TypeKey;
  status: "active" | "retired";
  offerings: Offering[];
}

export interface Catalogue {
  models: Model[];
  byId: Record<string, Model>;
  offerings: number;
  labs: number;
}

type CondBase = { soft?: boolean; from?: boolean; id?: string };
export type Cond = CondBase &
  (
    | { f: "type"; v: TypeKey }
    | { f: "active" }
    | { f: "ctx"; min: number }
    | { f: "open"; v: boolean }
    | { f: "commercial" }
    | { f: "bench"; b: string; min: number; indep?: boolean }
    | { f: "task$"; max: number }
    | { f: "in$"; max: number }
    | { f: "resid"; v: Region }
    | { f: "ret0" }
    | { f: "ttft"; max: number }
    | { f: "tps"; min: number }
    | { f: "origin"; ex: string[] }
    | { f: "rel"; ref: string; b: string }
  );
export type CondField = Cond["f"];

export interface Weights {
  cap: number;
  cost: number;
  speed: number;
}

/** The handoff's spec: task, tokens per task, primary benchmark, weights, conditions. */
export interface Spec {
  task?: string;
  tokIn: number;
  tokOut: number;
  bench: string;
  w: Weights;
  conds: Cond[];
  bar?: number | null;
}

export interface Template {
  id: string;
  name: string;
  task: string;
  spec: Omit<Spec, "task">;
}
export interface Facet {
  k: string;
  label: string;
  hint: string;
  c: Cond;
}
