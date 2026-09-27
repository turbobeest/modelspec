import type { Cond, FacetValue, Spec } from "../engine/types";
import type { VocabFacet, Vocabulary } from "../vocabulary";

export type FacetMode = "off" | "must" | "prefer" | "both";
export interface FacetSelection {
  mode: FacetMode;
  op?: "=" | "!=" | "<=" | ">=" | "in" | "not in";
  value?: FacetValue;
  weight?: number;
  reason?: string;
}
export type BoardSelections = Record<string, FacetSelection>;
export interface Estate { providers: string[]; plans: string[]; hardware: string[] }

const PREVIEW_HOSTS = new Set([
  "internal.modelspec-7np.pages.dev",
  "localhost",
  "127.0.0.1",
]);

/** Fail-safe runtime launch gate: unknown and empty hosts always get production. */
export const showsFacetBoard = (hostname: string): boolean => PREVIEW_HOSTS.has(hostname);

const GROUPS: Readonly<Record<string, string>> = {
  "model.class": "What it does",
  "model.input_modalities": "What it does",
  "model.output_modalities": "What it does",
  "offering.cost_per_task": "Budget",
  "offering.price.input": "Budget",
  "offering.price.output": "Budget",
  "offering.price.cached_input": "Budget",
  "offering.price.batch_input": "Budget",
  "offering.price.batch_output": "Budget",
  "model.context_window": "Size of work",
  "model.max_output_tokens": "Size of work",
  "model.weights_openness": "Where it runs",
  "offering.provider": "Where it runs",
  "offering.region": "Where it runs",
  "offering.private_deployment": "Where it runs",
  "model.fits_hardware": "Where it runs",
  "offering.data.trains_on_customer_data": "Your data",
  "offering.data.retention": "Your data",
  "offering.data.zero_retention": "Your data",
  "offering.attestation.baa": "Your data",
  "offering.attestation.soc2": "Your data",
  "licence.commercial_use": "Licence",
  "licence.user_cap": "Licence",
  "licence.output_training": "Licence",
  "licence.fine_tuning": "Licence",
  "feature.tool_calling": "Features",
  "feature.structured_output": "Features",
  "feature.streaming": "Features",
  "feature.effort_controls": "Features",
  "feature.batch": "Features",
  "origin.lab_jurisdiction": "Provenance",
  "model.lifecycle": "Provenance",
  "model.release_date": "Provenance",
  "offering.speed.time_to_first_token": "Speed",
  "offering.speed.throughput": "Speed",
};

export const GROUP_ORDER = [
  "What it does", "What it's good at", "Budget", "Size of work", "Where it runs",
  "Your data", "Licence", "Features", "Provenance", "Speed", "Other",
] as const;

export const facetGroup = (id: string): string =>
  id.startsWith("capability.") ? "What it's good at" : (GROUPS[id] ?? "Other");

export const supportsPreference = (id: string): boolean =>
  id.startsWith("capability.") || id === "offering.cost_per_task" ||
  id === "offering.speed.time_to_first_token" || id === "offering.speed.throughput";

export function defaultFacetValue(facet: VocabFacet): FacetValue {
  if (facet.value_type === "boolean") return true;
  if (facet.value_type === "number") {
    const min = typeof facet.range?.min === "number" ? facet.range.min : 0;
    const max = typeof facet.range?.max === "number" ? facet.range.max : min;
    return min + (max - min) / 2;
  }
  const first = facet.values?.[0]?.value ?? facet.literals?.[0] ?? "";
  return facet.value_type === "set" ? [String(first)] : first;
}

export function defaultFacetOp(facet: VocabFacet): FacetSelection["op"] {
  if (facet.value_type === "number" || facet.value_type === "date") {
    const lowerIsBetter = facet.id.includes("cost") || facet.id.includes("price") ||
      facet.id.includes("time_to_first_token") || facet.id.includes("retention");
    return lowerIsBetter && facet.operators.includes("<=") ? "<=" : ">=";
  }
  return facet.value_type === "set" && facet.operators.includes("in") ? "in" : "=";
}

function conditionFor(facet: VocabFacet, choice: FacetSelection): Cond {
  return {
    f: "facet",
    facet: facet.id.replace(/^capability\./, ""),
    op: choice.op ?? defaultFacetOp(facet) ?? "=",
    value: choice.value ?? defaultFacetValue(facet),
  };
}

/** Convert the visible board literally: gates become where conditions; weights rank only. */
export function boardToSpec(base: Spec, vocabulary: Vocabulary, selections: BoardSelections): Spec {
  const grouped = groupFacets(vocabulary);
  const synthetic = [...grouped.groups.flatMap((group) => group.facets), ...grouped.untracked];
  const boardIds = new Set(synthetic.map((facet) => facet.id));
  const preserved = base.conds.filter((condition) => condition.f !== "facet" || !boardIds.has(condition.facet));
  const gates = synthetic.flatMap((facet) => {
    const choice = selections[facet.id];
    return choice && (choice.mode === "must" || choice.mode === "both")
      ? [conditionFor(facet, choice)] : [];
  });
  const boardWeights = Object.fromEntries(synthetic.flatMap((facet) => {
    const choice = selections[facet.id];
    if (!choice || (choice.mode !== "prefer" && choice.mode !== "both") || !supportsPreference(facet.id)) return [];
    const id = facet.id.startsWith("capability.") ? facet.id.slice("capability.".length)
      : facet.id === "offering.cost_per_task" ? "-offering.cost_per_task"
      : facet.id === "offering.speed.time_to_first_token" ? "-offering.speed.time_to_first_token"
      : facet.id;
    return [[id, choice.weight ?? 0.5]];
  }));
  const selectedDomain = Object.keys(selections).find((id) =>
    id.startsWith("capability.") && selections[id].mode !== "off",
  )?.slice("capability.".length);
  const domain = selectedDomain ? vocabulary.domains.find((item) => item.id === selectedDomain) : undefined;
  return {
    ...base,
    task: "",
    conds: [...preserved, ...gates],
    boardWeights,
    ...(domain ? {
      domain: domain.id,
      basis: "estimate" as const,
      bench: domain.default_benchmark ?? domain.benchmarks[0] ?? base.bench,
    } : { domain: undefined, basis: undefined }),
  };
}

export function estateSpec(spec: Spec, providers: string[]): Spec {
  if (!providers.length) return spec;
  return {
    ...spec,
    conds: [...spec.conds, { f: "facet", facet: "offering.provider", op: "in", value: providers }],
  };
}

export function groupFacets(vocabulary: Vocabulary) {
  const capabilityFacets: VocabFacet[] = vocabulary.domains.map((domain) => ({
    id: `capability.${domain.id}`,
    label: domain.name,
    definition: `Capability estimate from ${domain.benchmarks.length} benchmarks.`,
    subject: "model",
    value_type: "number",
    unit: null,
    operators: [">=", "<=", "="],
    objective: true,
    risk: "capability",
    computed_by: "capability_estimate",
    known: domain.estimate_models,
    of: vocabulary.coverage?.models ?? Math.max(...vocabulary.facets.filter((facet) => facet.subject === "model").map((facet) => facet.of), 0),
    range: { min: 0, max: 1 },
  }));
  const all = [...capabilityFacets, ...vocabulary.facets];
  const tracked = all.filter((facet) => facet.known > 0);
  const groups = GROUP_ORDER.map((name) => ({
    name,
    facets: tracked.filter((facet) => facetGroup(facet.id) === name),
  })).filter((group) => group.facets.length);
  return { groups, untracked: all.filter((facet) => facet.known === 0) };
}

export function readEstate(): Estate {
  try {
    const encoded = new URLSearchParams(location.search).get("estate");
    const value = JSON.parse(encoded ? decodeURIComponent(atob(encoded)) : (localStorage.getItem("modelspec-estate-v1") ?? "null")) as Partial<Estate> | null;
    return { providers: value?.providers ?? [], plans: value?.plans ?? [], hardware: value?.hardware ?? [] };
  } catch { return { providers: [], plans: [], hardware: [] }; }
}

export function writeEstate(estate: Estate): void {
  try { localStorage.setItem("modelspec-estate-v1", JSON.stringify(estate)); } catch { /* storage is optional */ }
  const url = new URL(location.href);
  const empty = !estate.providers.length && !estate.plans.length && !estate.hardware.length;
  if (empty) url.searchParams.delete("estate");
  else url.searchParams.set("estate", btoa(encodeURIComponent(JSON.stringify(estate))));
  history.replaceState(null, "", url.pathname + url.search + url.hash);
}
