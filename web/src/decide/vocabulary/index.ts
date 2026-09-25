// The published decision vocabulary (MODEL-153): which facets and benchmarks
// the current snapshot can answer. Real mode draws every template, parsed
// condition, question, facet option, axis and weight from it, and offers
// nothing the snapshot has no verified data for. `?demo=1` never loads it.
import { z } from "zod";
import type { ParsedTask, Question } from "../engine/reference";
import type {
  Cond,
  Facet,
  FacetOp,
  FacetValue,
  Spec,
  Template,
  TypeKey,
  Weights,
} from "../engine/types";
import type { Axis } from "../state/spec";

export const VOCABULARY_URL: string =
  import.meta.env.VITE_VOCABULARY_URL ?? "/api/decision/vocabulary.json";

const scalar = z.union([z.string(), z.number(), z.boolean()]);
const facetSchema = z.object({
  id: z.string(),
  label: z.string(),
  definition: z.string(),
  subject: z.enum(["model", "offering"]),
  value_type: z.enum(["number", "enum", "boolean", "date", "set"]),
  unit: z.string().nullable(),
  unit_definition: z.string().nullable().optional(),
  operators: z.array(z.string()),
  objective: z.boolean(),
  risk: z.string(),
  computed_by: z.string().nullable(),
  known: z.number().int().nonnegative(),
  of: z.number().int().nonnegative(),
  range: z
    .object({ min: z.union([z.number(), z.string()]), max: z.union([z.number(), z.string()]) })
    .nullable()
    .optional(),
  literals: z.array(z.string()).optional(),
  // `label`: the registry's plain name for an enum value (MODEL-153).
  values: z
    .array(z.object({ value: scalar, count: z.number().int(), label: z.string().optional() }))
    .optional(),
});
const benchmarkSchema = z.object({
  id: z.string().regex(/^[a-z][a-z0-9_]*$/),
  name: z.string(),
  unit: z.string().nullable(),
  higher_is_better: z.boolean(),
  models: z.number().int().nonnegative(),
  independent_models: z.number().int().nonnegative(),
  range: z.object({ min: z.number(), max: z.number() }),
  domains: z.array(
    z.object({ id: z.string(), directness: z.enum(["direct", "proxy"]) }),
  ),
});
export const vocabularySchema = z.object({
  vocabulary_version: z.literal(1),
  contract_version: z.string(),
  snapshot: z.string(),
  default_task_tokens: z.object({
    input: z.number().int().nonnegative(),
    output: z.number().int().nonnegative(),
  }),
  task_types: z.array(z.string()),
  facets: z.array(facetSchema),
  benchmarks: z.array(benchmarkSchema),
  domains: z.array(
    z.object({
      id: z.string(),
      name: z.string(),
      proxy_only: z.boolean(),
      /** The registry's default benchmark for the domain, when it has verified data. */
      default_benchmark: z.string().nullable().optional(),
      benchmarks: z.array(z.string()),
    }),
  ),
  /** Card names by model ID. A vocabulary published before MODEL-153 has none. */
  models: z
    .record(
      z.string(),
      z.object({
        display_name: z.string().nullable(),
        lab: z.string(),
        lab_name: z.string().nullable(),
      }),
    )
    .default({}),
  /** Provider display names by ID. */
  providers: z.record(z.string(), z.string()).default({}),
  /** What the lineup holds, for an empty answer. Absent before MODEL-153's coverage. */
  coverage: z
    .object({
      as_of: z.string().nullable(),
      models: z.number().int().nonnegative(),
      verified: z.number().int().nonnegative(),
      classes: z.array(
        z.object({
          id: z.string(),
          models: z.number().int().nonnegative(),
          verified: z.number().int().nonnegative(),
          domains: z.array(z.object({ id: z.string(), verified: z.number().int().nonnegative() })),
        }),
      ),
      domains: z.array(
        z.object({
          id: z.string(),
          name: z.string(),
          verified: z.number().int().nonnegative(),
          direct: z.number().int().nonnegative(),
        }),
      ),
    })
    .nullable()
    .default(null),
});
export type Vocabulary = z.infer<typeof vocabularySchema>;
export type VocabFacet = Vocabulary["facets"][number];
export type VocabBenchmark = Vocabulary["benchmarks"][number];
export type Coverage = NonNullable<Vocabulary["coverage"]>;

/** Why the vocabulary could not be used. `missing` means no snapshot is published yet. */
export class VocabularyError extends Error {
  readonly kind: "missing" | "network" | "invalid";
  constructor(message: string, kind: "missing" | "network" | "invalid") {
    super(message);
    this.name = "VocabularyError";
    this.kind = kind;
  }
}

export async function loadVocabulary(signal?: AbortSignal): Promise<Vocabulary> {
  let response: Response;
  try {
    response = await fetch(VOCABULARY_URL, {
      headers: { Accept: "application/json" },
      // The site serves this with max-age=14400; after a deploy (or a 409
      // snapshot_changed) a cached copy would describe the old snapshot.
      // no-cache revalidates with the ETag, so an unchanged file is a 304.
      cache: "no-cache",
      signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new VocabularyError("The catalogue vocabulary could not be reached.", "network");
  }
  if (response.status === 404)
    throw new VocabularyError(
      "No decision snapshot has been published yet, so there is nothing to decide from.",
      "missing",
    );
  if (!response.ok)
    throw new VocabularyError(
      `The catalogue vocabulary returned HTTP ${response.status}.`,
      "network",
    );
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new VocabularyError("The catalogue vocabulary is not JSON.", "invalid");
  }
  const parsed = vocabularySchema.safeParse(payload);
  if (!parsed.success)
    throw new VocabularyError("The catalogue vocabulary has an unexpected shape.", "invalid");
  return parsed.data;
}

// ---------- what is offered

/** A facet the page may offer: registered and known for at least one candidate. */
export function offeredFacet(v: Vocabulary, id: string): VocabFacet | null {
  const row = v.facets.find((facet) => facet.id === id);
  return row && row.known > 0 ? row : null;
}

/** Benchmarks with verified evidence, most covered first. */
export function offeredBenchmarks(v: Vocabulary): VocabBenchmark[] {
  return v.benchmarks
    .filter((b) => b.models > 0)
    .slice()
    .sort((a, b) => b.models - a.models || a.id.localeCompare(b.id));
}

export function benchmark(v: Vocabulary, id: string): VocabBenchmark | null {
  return v.benchmarks.find((b) => b.id === id && b.models > 0) ?? null;
}

const hasValue = (row: VocabFacet | null, value: FacetValue) =>
  !!row?.values?.some((item) => item.value === value);

/**
 * Whether a benchmark measures a domain directly (not as a proxy).
 */
const directFor = (b: VocabBenchmark, domain: string) =>
  b.domains.some((tag) => tag.id === domain && tag.directness === "direct");

/**
 * The benchmark a domain ranks on: the registry's default for the domain when it
 * has verified data (published as `default_benchmark`), otherwise direct first,
 * then the most verified lineup models.
 */
export function pickBenchmark(v: Vocabulary, domain: string): VocabBenchmark | null {
  const preferred = v.domains.find((d) => d.id === domain)?.default_benchmark;
  const chosen = preferred ? offeredBenchmarks(v).find((b) => b.id === preferred) : undefined;
  if (chosen) return chosen;
  return (
    offeredBenchmarks(v)
      .filter((b) => b.domains.some((tag) => tag.id === domain))
      .sort(
        (a, b) =>
          Number(directFor(b, domain)) - Number(directFor(a, domain)) ||
          b.models - a.models ||
          a.id.localeCompare(b.id),
      )[0] ?? null
  );
}

/** What the rank-by control offers: the domain's direct benchmarks, most covered first. */
export function rankChoices(v: Vocabulary, domain: string | null | undefined): VocabBenchmark[] {
  if (!domain) return [];
  return offeredBenchmarks(v).filter((b) => directFor(b, domain));
}

/** Rank on another benchmark; a floor the task parse set moves with it. */
export function switchBenchmark(v: Vocabulary, spec: Spec, id: string): Spec {
  const next = v.benchmarks.find((b) => b.id === id);
  if (!next) return spec;
  return {
    ...spec,
    bench: id,
    conds: spec.conds.map((c) =>
      c.f === "bench" && c.from && c.b === spec.bench ? benchCond(next, true) : c,
    ),
  };
}

export const CLASS_OF_TYPE: Readonly<Record<TypeKey, string>> = {
  llm: "text-generator",
  embed: "vectoriser",
  rerank: "orderer",
  vision: "analyser",
  speech: "transcriber",
  decision: "decider",
};

/** Model classes the snapshot has, as the page's type keys, with their names. */
export function offeredTypes(v: Vocabulary): Partial<Record<TypeKey, string>> {
  const classes = offeredFacet(v, "model.class");
  const out: Partial<Record<TypeKey, string>> = {};
  for (const [key, id] of Object.entries(CLASS_OF_TYPE) as [TypeKey, string][])
    if (hasValue(classes, id)) out[key] = id.replaceAll("-", " ");
  return out;
}

const AXIS_FACET: Readonly<Record<Axis, string>> = {
  task$: "offering.cost_per_task",
  in$: "offering.price.input",
  ttft: "offering.speed.time_to_first_token",
  tps: "offering.speed.throughput",
  ctx: "model.context_window",
};

export function offeredAxes(v: Vocabulary): Axis[] {
  return (Object.keys(AXIS_FACET) as Axis[]).filter((axis) =>
    offeredFacet(v, AXIS_FACET[axis]),
  );
}

export function offeredWeights(v: Vocabulary): (keyof Weights)[] {
  return (["cap", "cost", "speed"] as const).filter((key) =>
    key === "cap"
      ? offeredBenchmarks(v).length > 0
      : key === "cost"
        ? !!offeredFacet(v, "offering.cost_per_task")
        : !!offeredFacet(v, "offering.speed.throughput"),
  );
}

/** Weights over the offered sliders only, summing to 1. */
export function normaliseWeights(w: Weights, keys: readonly (keyof Weights)[]): Weights {
  const kept = { cap: 0, cost: 0, speed: 0 };
  for (const key of keys) kept[key] = w[key];
  const sum = kept.cap + kept.cost + kept.speed;
  if (sum <= 0) return { cap: keys.includes("cap") ? 1 : 0, cost: keys.includes("cap") ? 0 : 1, speed: 0 };
  return { cap: kept.cap / sum, cost: kept.cost / sum, speed: kept.speed / sum };
}

/** The spec as the engine will be asked: weights only on the offered sliders. */
export function sendable(v: Vocabulary, spec: Spec): Spec {
  return { ...spec, w: normaliseWeights(spec.w, offeredWeights(v)) };
}

// ---------- values

const nice = (value: number) => Number(value.toPrecision(2));

/** A floor that keeps the stronger three quarters of the measured range. */
export function floorFor(b: VocabBenchmark): number {
  const { min, max } = b.range;
  return nice(b.higher_is_better ? min + 0.25 * (max - min) : max - 0.25 * (max - min));
}

function benchCond(b: VocabBenchmark, from?: boolean): Cond {
  return {
    f: "bench",
    b: b.id,
    min: floorFor(b),
    ...(b.independent_models > 0 ? { indep: true } : {}),
    ...(from ? { from } : {}),
  };
}

function numberRange(row: VocabFacet | null): { min: number; max: number } | null {
  const range = row?.range;
  return range && typeof range.min === "number" && typeof range.max === "number"
    ? { min: range.min, max: range.max }
    : null;
}

/** A middle value on a log scale, for a default threshold. */
function middle(row: VocabFacet | null, fallback: number): number {
  const range = numberRange(row);
  if (!range) return fallback;
  if (range.min > 0) return nice(Math.sqrt(range.min * range.max));
  return nice((range.min + range.max) / 2);
}

const LOWER_IS_BETTER_UNITS = new Set([
  "usd_per_1m_tokens",
  "usd_per_task",
  "milliseconds",
  "days",
]);

/** The condition "+ add condition" starts from for a facet. */
export function defaultCondition(v: Vocabulary, row: VocabFacet): Cond | null {
  switch (row.id) {
    case "offering.cost_per_task":
      return { f: "task$", max: middle(row, 0.1) };
    case "offering.price.input":
      return { f: "in$", max: middle(row, 1) };
    case "offering.speed.time_to_first_token":
      return { f: "ttft", max: middle(row, 1000) };
    case "offering.speed.throughput":
      return { f: "tps", min: middle(row, 50) };
    case "model.context_window":
      return { f: "ctx", min: 128000 };
    case "model.weights_openness":
      return hasValue(row, "open_weights") ? { f: "open", v: true } : null;
    case "licence.commercial_use":
      return { f: "commercial" };
    case "offering.data.zero_retention":
      return hasValue(row, true) ? { f: "ret0" } : null;
    case "model.class": {
      const [type] = Object.keys(offeredTypes(v)) as TypeKey[];
      return type ? { f: "type", v: type } : null;
    }
  }
  const values = (row.values ?? [])
    .slice()
    .sort((a, b) => b.count - a.count)
    .map((item) => item.value);
  const facet = (op: FacetOp, value: FacetValue): Cond => ({
    f: "facet",
    facet: row.id,
    op,
    value,
  });
  switch (row.value_type) {
    case "number": {
      const range = numberRange(row);
      if (!range) return null;
      const lower = LOWER_IS_BETTER_UNITS.has(row.unit ?? "");
      return facet(lower ? "<=" : ">=", middle(row, range.min));
    }
    case "date":
      return typeof row.range?.min === "string" ? facet(">=", row.range.min) : null;
    case "boolean":
      return values.length ? facet("=", values.includes(true) ? true : Boolean(values[0])) : null;
    case "enum":
      return values.length ? facet("=", String(values[0])) : null;
    case "set":
      return values.length ? facet("in", [String(values[0])]) : null;
  }
}

/** Every option "+ add condition" offers: facets and benchmarks with verified data. */
export function facetOptions(v: Vocabulary): Facet[] {
  const facets = v.facets.flatMap((row): Facet[] => {
    if (row.known === 0 || row.id === "model.lifecycle") return [];
    const c = defaultCondition(v, row);
    if (!c) return [];
    const unit = row.unit ? row.unit.replaceAll("_", " ") : row.value_type;
    return [
      {
        k: [row.id, row.label, row.definition].join(" ").toLowerCase(),
        label: row.label,
        hint: `${unit} · known for ${row.known} of ${row.of} ${row.subject === "model" ? "models" : "offerings"}`,
        c,
      },
    ];
  });
  const benchmarks = offeredBenchmarks(v).map(
    (b): Facet => ({
      k: ["benchmark", b.id, b.name, ...b.domains.map((d) => d.id)].join(" ").toLowerCase(),
      label: `${b.name} floor`,
      hint: `${b.unit ?? "unit not recorded"} · verified for ${b.models} models`,
      c: benchCond(b),
    }),
  );
  return [...facets, ...benchmarks];
}

/** The domain and benchmark a model class ranks on, when its class changes. */
export function domainForType(
  v: Vocabulary,
  type: TypeKey,
): { domain: string; bench: string } | null {
  const domain = CLASS_OF_DOMAIN_REVERSE[type] ?? defaultDomain(v);
  const ranked = domain ? pickBenchmark(v, domain) : null;
  return domain && ranked ? { domain, bench: ranked.id } : null;
}

const CLASS_OF_DOMAIN_REVERSE: Partial<Record<TypeKey, string>> = {
  embed: "retrieval",
  rerank: "retrieval",
};

// ---------- the task parser

/** Words that name a capability domain, most specific first. */
const DOMAIN_CUES: readonly [RegExp, string][] = [
  [/\brerank\w*|\bretriev\w*|\bembed\w*|semantic search|\brag\b/, "retrieval"],
  [
    /\brefactor\w*|\bcod(?:e|es|ing)\b|\bcodebase\w*|\bprogram\w*|\bbugs?\b|\brepo\w*|\brust\b|\bpython\b|\btypescript\b|\bjavascript\b|\bsoftware\b|\bagent\w*|\bterminal\b|\bshell\b|\bdevops\b|\btests?\b/,
    "software_engineering",
  ],
  [/\bmath\w*|\bproofs?\b|\btheorem\w*|\balgebra\b|\bcalculus\b/, "maths"],
  [/\bphysics\b|\bchemistry\b|\bbiology\b|\bscien\w*|\bstem\b/, "engineering_stem"],
  [/\breason\w*|\bpuzzle\w*|\blogic\b/, "reasoning"],
  [/\blegal\b|\blaw\b|\bstatute\w*/, "legal"],
  [/\bmedic\w*|\bclinic\w*|\bhealth\w*|\bpatient\w*|\bdiagnos\w*/, "medical"],
  [/\bfinanc\w*|\baccounting\b|\bfilings?\b|\bbank\w*/, "finance"],
  [/\bmarketing\b|\bseo\b/, "marketing_seo"],
  [/\bwrit\w*|\bessay\w*|\bprose\b|\bsummar\w*/, "writing"],
  [/\btool\w*|\bbrows\w*|\bautomat\w*/, "agentic_tool_use"],
  [/\bimages?\b|\bvision\b|\bcharts?\b|\bscreenshot\w*|\bpdfs?\b|\bdocuments?\b|\bocr\b/, "vision_documents"],
  [/\btranslat\w*|\bmultilingual\b/, "multilingual"],
  [/\bchat\w*|\bassistant\w*|\bconversation\w*/, "chat_preference"],
];

const CLASS_OF_DOMAIN: Readonly<Record<string, TypeKey>> = { retrieval: "embed" };

export interface RealParsedTask extends ParsedTask {
  domain: string | null;
}

/** The domain ranked on when the task names none: software engineering, else the best-covered. */
function defaultDomain(v: Vocabulary): string | null {
  if (pickBenchmark(v, "software_engineering")) return "software_engineering";
  const top = offeredBenchmarks(v)[0];
  return top?.domains.find((d) => d.directness === "direct")?.id ?? top?.domains[0]?.id ?? null;
}

export function parseRealTask(v: Vocabulary, text: string | null | undefined): RealParsedTask {
  const t = (text || "").toLowerCase();
  const trace: ParsedTask["trace"] = [];
  const match = (re: RegExp) => t.match(re)?.[0] ?? null;
  let domain: string | null = null;
  let word: string | null = null;
  for (const [re, id] of DOMAIN_CUES) {
    const found = match(re);
    if (found && pickBenchmark(v, id)) {
      domain = id;
      word = found;
      break;
    }
  }
  domain ??= defaultDomain(v);
  const ranked = domain ? pickBenchmark(v, domain) : offeredBenchmarks(v)[0] ?? null;
  const domainName = v.domains.find((d) => d.id === domain)?.name ?? domain ?? "no domain";
  if (ranked) {
    const direct = domain !== null && directFor(ranked, domain);
    const others = rankChoices(v, domain)
      .filter((b) => b.id !== ranked.id)
      .map((b) => `${b.name} (${b.models})`);
    trace.push({
      word: word ?? "(no domain named)",
      note:
        `${domainName}: rank on ${ranked.name}, ` +
        (v.domains.find((d) => d.id === domain)?.default_benchmark === ranked.id
          ? `the default benchmark for this domain (${ranked.models} verified lineup models)`
          : direct
            ? `the direct benchmark with the most verified lineup models (${ranked.models})`
            : `a proxy with ${ranked.models} verified lineup models; no direct benchmark has data`) +
        (others.length ? `; also direct: ${others.join(", ")}` : ""),
    });
  }
  const conds: Cond[] = [];
  const types = offeredTypes(v);
  const type = (domain && CLASS_OF_DOMAIN[domain]) || "llm";
  if (types[type]) conds.push({ f: "type", v: type, from: true });
  if (hasValue(offeredFacet(v, "model.lifecycle"), "active"))
    conds.push({ f: "active", from: true });
  const keys = offeredWeights(v);
  let w: Weights = { cap: 0.6, cost: 0.3, speed: 0.1 };
  const note = (found: string | null, applied: boolean, yes: string, no: string) => {
    if (found) trace.push({ word: found, note: applied ? yes : no });
    return !!found && applied;
  };
  if (
    note(
      match(/\blarge\b|\bcodebase\w*|\bmonorepo\w*|\blong\b/),
      !!offeredFacet(v, "model.context_window"),
      "context ≥ 200K",
      "no context-window data in this snapshot; not applied",
    )
  )
    conds.push({ f: "ctx", min: 200000, from: true });
  if (
    note(
      match(/\bprecis\w*|\baccura\w*|\bcorrect\w*|\bmatters\b/),
      !!ranked,
      `${ranked?.name} floor${ranked && ranked.independent_models > 0 ? ", measured independently" : ""}`,
      "no benchmark with verified evidence; not applied",
    ) &&
    ranked
  ) {
    conds.push(benchCond(ranked, true));
    w = { cap: 0.7, cost: 0.2, speed: 0.1 };
  }
  if (
    note(
      match(/\bcheap\w*|\bbudget\w*|\blow.cost\b/),
      keys.includes("cost"),
      "weight cost per task higher",
      "no price data in this snapshot; not applied",
    )
  )
    w = { cap: 0.5, cost: 0.4, speed: 0.1 };
  if (
    note(
      match(/\bfast\b|\blatency\b|\breal.time\b|\binteractive\b/),
      !!offeredFacet(v, "offering.speed.time_to_first_token"),
      "first token ≤ 1,000 ms",
      "no latency measurements in this snapshot; not applied",
    )
  )
    conds.push({ f: "ttft", max: 1000, from: true });
  if (
    note(
      match(/\bprivate\b|\bon.prem\w*|\bself.host\w*|\blocal\b/),
      hasValue(offeredFacet(v, "model.weights_openness"), "open_weights"),
      "open weights",
      "no open-weights models in this snapshot; not applied",
    )
  )
    conds.push({ f: "open", v: true, from: true });
  if (
    note(
      match(/\bcommercial\w*/),
      !!offeredFacet(v, "licence.commercial_use"),
      "commercial licence",
      "no licence data in this snapshot; not applied",
    )
  )
    conds.push({ f: "commercial", from: true });
  const eu = match(/\beu\b|\bgdpr\b|\beurope\w*/);
  if (eu) trace.push({ word: eu, note: "no EU region data in this snapshot; not applied" });
  return {
    conds,
    w: normaliseWeights(w, keys),
    bench: ranked?.id ?? "",
    domain,
    trace,
  };
}

// ---------- templates and questions

export function realBaseSpec(v: Vocabulary): Spec {
  const parsed = parseRealTask(v, "");
  return {
    task: "",
    tokIn: v.default_task_tokens.input,
    tokOut: v.default_task_tokens.output,
    bench: parsed.bench,
    domain: parsed.domain ?? undefined,
    w: parsed.w,
    conds: parsed.conds.map((c) => ({ ...c, from: undefined })),
  };
}

export interface RealTemplate extends Template {
  spec: Omit<Spec, "task">;
  /** What the template ranks on, from the vocabulary. */
  ranks: string;
}

export function realTemplates(v: Vocabulary): RealTemplate[] {
  const keys = offeredWeights(v);
  const types = offeredTypes(v);
  const has = (id: string) => !!offeredFacet(v, id);
  const base = (type: TypeKey): Cond[] => [
    ...(types[type] ? [{ f: "type", v: type } as Cond] : []),
    ...(hasValue(offeredFacet(v, "model.lifecycle"), "active") ? [{ f: "active" } as Cond] : []),
  ];
  const make = (
    id: string,
    name: string,
    task: string,
    domain: string,
    type: TypeKey,
    tokens: [number, number],
    w: Weights,
    extra: (b: VocabBenchmark) => Cond[],
  ): RealTemplate[] => {
    const b = pickBenchmark(v, domain);
    if (!b || !types[type]) return [];
    return [
      {
        id,
        name,
        task,
        ranks: `Ranks on ${b.name} · ${b.models} models verified`,
        spec: {
          tokIn: tokens[0],
          tokOut: tokens[1],
          bench: b.id,
          domain,
          w: normaliseWeights(w, keys),
          conds: [...base(type), ...extra(b)],
        },
      },
    ];
  };
  return [
    ...make(
      "budget-agent",
      "Coding agent on a budget",
      "Coding agent that fixes failing tests in a TypeScript monorepo",
      "software_engineering",
      "llm",
      [60000, 6000],
      { cap: 0.5, cost: 0.4, speed: 0.1 },
      (b) => [
        ...(has("model.context_window") ? [{ f: "ctx", min: 128000 } as Cond] : []),
        ...(has("offering.cost_per_task") ? [{ f: "task$", max: 0.25 } as Cond] : []),
        benchCond(b),
      ],
    ),
    ...make(
      "private",
      "Open weights you can host",
      "Internal assistant we run on our own servers",
      // A general assistant, not a coding task: rank on chat preference.
      "chat_preference",
      "llm",
      [20000, 2000],
      { cap: 0.7, cost: 0.3, speed: 0 },
      () => [
        ...(hasValue(offeredFacet(v, "model.weights_openness"), "open_weights")
          ? [{ f: "open", v: true } as Cond]
          : []),
        ...(has("licence.commercial_use") ? [{ f: "commercial" } as Cond] : []),
      ],
    ),
    ...make(
      "maths",
      "Maths and proofs",
      "Check competition maths solutions step by step",
      "maths",
      "llm",
      [20000, 8000],
      { cap: 0.8, cost: 0.2, speed: 0 },
      () => [],
    ),
    ...make(
      "embed",
      "Retrieval embeddings",
      "Embed 10,000 documents of about 800 tokens for retrieval",
      "retrieval",
      "embed",
      [8000000, 0],
      // Embedding models are mostly self-hosted, with no list price to weigh.
      { cap: 1, cost: 0, speed: 0 },
      () => [],
    ),
  ];
}

/** Next questions, each only when the snapshot knows the facet it asks about. */
export function realQuestions(v: Vocabulary, spec: Spec, dismissed: string[]): Question[] {
  const has = (f: Cond["f"]) => spec.conds.some((c) => c.f === f);
  const hasFacet = (id: string) =>
    spec.conds.some((c) => c.f === "facet" && c.facet === id);
  const out: Question[] = [];
  const cost = offeredFacet(v, "offering.cost_per_task");
  if (cost && !has("task$")) {
    const range = numberRange(cost);
    const scale =
      (spec.tokIn + spec.tokOut) /
      Math.max(1, v.default_task_tokens.input + v.default_task_tokens.output);
    const low = Math.max((range?.min ?? 0.01) * scale, 0.0001);
    const high = Math.max((range?.max ?? 1) * scale, low * 10);
    const steps = [0.25, 0.5, 0.75].map((f) =>
      nice(Math.exp(Math.log(low) + f * (Math.log(high) - Math.log(low)))),
    );
    out.push({
      id: "task$",
      q: "What can you spend per task?",
      opts: [...new Set(steps)].map((max) => ({
        label: "≤ $" + max,
        c: { f: "task$", max },
      })),
    });
  }
  if (hasValue(offeredFacet(v, "model.weights_openness"), "open_weights") && !has("open"))
    out.push({
      id: "open",
      q: "Do you need open weights?",
      opts: [{ label: "Yes", c: { f: "open", v: true } }],
    });
  if (offeredFacet(v, "licence.commercial_use") && !has("commercial"))
    out.push({
      id: "commercial",
      q: "Is this for commercial use?",
      opts: [{ label: "Yes", c: { f: "commercial" } }],
    });
  if (hasValue(offeredFacet(v, "offering.data.zero_retention"), true) && !has("ret0"))
    out.push({
      id: "ret0",
      q: "Must prompts and outputs not be stored?",
      opts: [{ label: "Yes, zero retention", c: { f: "ret0" } }],
    });
  const trains = offeredFacet(v, "offering.data.trains_on_customer_data");
  if (hasValue(trains, false) && !hasFacet(trains!.id))
    out.push({
      id: trains!.id,
      q: "Must the provider not train on your data?",
      opts: [
        {
          label: "Yes",
          c: { f: "facet", facet: trains!.id, op: "=", value: false },
        },
      ],
    });
  const baa = offeredFacet(v, "offering.attestation.baa");
  if (hasValue(baa, true) && !hasFacet(baa!.id))
    out.push({
      id: baa!.id,
      q: "Do you need a HIPAA business associate agreement?",
      opts: [{ label: "Yes", c: { f: "facet", facet: baa!.id, op: "=", value: true } }],
    });
  const tools = offeredFacet(v, "feature.tool_calling");
  if (hasValue(tools, true) && !hasFacet(tools!.id))
    out.push({
      id: tools!.id,
      q: "Does the model need to call tools?",
      opts: [{ label: "Yes", c: { f: "facet", facet: tools!.id, op: "=", value: true } }],
    });
  if (offeredFacet(v, "offering.speed.time_to_first_token") && !has("ttft"))
    out.push({
      id: "ttft",
      q: "How soon must the first token arrive?",
      opts: [500, 1000].map((max) => ({ label: `≤ ${max} ms`, c: { f: "ttft", max } })),
    });
  return out.filter((q) => !dismissed.includes(q.id));
}
