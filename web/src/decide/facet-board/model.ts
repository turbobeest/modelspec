import type { Cond, FacetValue, Spec } from "../engine/types";
import type { DecisionSpec } from "../adapter/contract";
import { contractCondition, toDecisionSpec } from "../adapter/view-model";
import type { Axis } from "../state/spec";
import type { VocabFacet, Vocabulary } from "../vocabulary";
import { z } from "zod";

export type FacetMode = "off" | "must" | "prefer" | "both";
export interface FacetSelection {
  mode: FacetMode;
  op?: "=" | "!=" | "<=" | ">=" | "in" | "not in";
  value?: FacetValue;
  weight?: number;
  weightKey?: string;
  reason?: string;
}
export type BoardSelections = Record<string, FacetSelection>;
export interface BoardTemplateState {
  selections: BoardSelections;
  taskTokens?: { input: number; output: number };
}
export interface Estate { providers: string[]; plans: string[]; hardware: string[] }
export interface BoardUrlState { selections: BoardSelections; estate: Estate }

const UNRANKED_OBJECTIVE = { "-offering.cost_per_task": 1 };

const facetValueSchema = z.union([
  z.string(), z.number().finite(), z.boolean(), z.array(z.string()),
]);
const selectionSchema = z.object({
  mode: z.enum(["off", "must", "prefer", "both"]),
  op: z.enum(["=", "!=", "<=", ">=", "in", "not in"]).optional(),
  value: facetValueSchema.optional(),
  weight: z.number().finite().nonnegative().max(1).optional(),
  weightKey: z.string().optional(),
  reason: z.string().optional(),
});
const boardUrlSchema = z.object({
  selections: z.record(z.string(), selectionSchema).default({}),
  estate: z.object({
    providers: z.array(z.string()), plans: z.array(z.string()), hardware: z.array(z.string()),
  }),
});

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

const BOARD_CONDITION = /^(\S+) (not in|in|!=|<=|>=|=) (.+)$/;

function parseConditionValue(text: string): FacetValue {
  if (text.startsWith("{") && text.endsWith("}")) {
    const body = text.slice(1, -1);
    return body ? body.split(", ").map(parseScalarValue).map(String) : [];
  }
  return parseScalarValue(text);
}

function parseScalarValue(text: string): string | number | boolean {
  if (text === "true") return true;
  if (text === "false") return false;
  if (/^-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(text)) return Number(text);
  if (text.startsWith('"') && text.endsWith('"')) {
    const parsed: unknown = JSON.parse(text);
    if (typeof parsed === "string") return parsed;
  }
  return text;
}

/** Parse the compact condition form that the board sends to the decision API. */
export function parseBoardCondition(condition: string): { facetId: string; op: NonNullable<FacetSelection["op"]>; value: FacetValue } {
  const match = BOARD_CONDITION.exec(condition);
  if (!match) throw new Error(`Template condition is not editable on the facet board: ${condition}`);
  const [, facetId, op, text] = match;
  return {
    facetId,
    op: z.enum(["=", "!=", "<=", ">=", "in", "not in"]).parse(op),
    value: parseConditionValue(text),
  };
}

/** Format a board condition with the same compact-value rules as API serialization. */
export function formatBoardCondition(facetId: string, choice: FacetSelection): string {
  return contractCondition({
    f: "facet",
    facet: facetId,
    op: choice.op ?? "=",
    value: choice.value ?? "",
  });
}

/** Convert one canonical vocabulary template into board selections and token counts. */
export function templateToBoard(
  template: NonNullable<Vocabulary["templates"]>[number],
  vocabulary: Vocabulary,
): BoardTemplateState {
  const selections: BoardSelections = {};
  const addReason = (facetId: string, reason: string) => {
    const current = selections[facetId]?.reason;
    return current && current !== reason ? `${current} ${reason}` : reason;
  };
  for (const row of template.where) {
    const parsed = parseBoardCondition(row.condition);
    const current = selections[parsed.facetId];
    selections[parsed.facetId] = {
      ...current,
      mode: current?.mode === "prefer" ? "both" : "must",
      op: parsed.op,
      value: parsed.value,
      reason: addReason(parsed.facetId, row.reason),
    };
  }
  for (const [weightKey, preference] of Object.entries(template.weights)) {
    const objective = weightKey.startsWith("-") ? weightKey.slice(1) : weightKey;
    const facetId = template.needs.domains.includes(objective) ||
      vocabulary.domains.some((domain) => domain.id === objective)
      ? `capability.${objective}` : objective;
    const current = selections[facetId];
    selections[facetId] = {
      ...current,
      mode: current?.mode === "must" ? "both" : "prefer",
      weight: preference.weight,
      weightKey,
      reason: addReason(facetId, preference.reason),
    };
  }
  return { selections, ...(template.task_tokens ? { taskTokens: template.task_tokens } : {}) };
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
  const selectedWeights = boardWeightsFromSelections(selections);
  const selectedDomain = Object.keys(selections).find((id) =>
    id.startsWith("capability.") && selections[id].mode !== "off",
  )?.slice("capability.".length);
  const domain = selectedDomain ? vocabulary.domains.find((item) => item.id === selectedDomain) : undefined;
  return {
    ...base,
    task: "",
    conds: [...preserved, ...gates],
    boardWeights: selectedWeights,
    ...(domain ? {
      domain: domain.id,
      basis: "estimate" as const,
      bench: domain.default_benchmark ?? domain.benchmarks[0] ?? base.bench,
    } : { domain: undefined, basis: undefined }),
  };
}

export function boardWeights(_vocabulary: Vocabulary, selections: BoardSelections): Record<string, number> {
  return boardWeightsFromSelections(selections);
}

function boardWeightsFromSelections(selections: BoardSelections): Record<string, number> {
  return Object.fromEntries(Object.entries(selections).flatMap(([facetId, choice]) => {
    if ((choice.mode !== "prefer" && choice.mode !== "both") || !supportsPreference(facetId)) return [];
    const id = choice.weightKey ?? (facetId.startsWith("capability.")
      ? facetId.slice("capability.".length)
      : facetId === "offering.cost_per_task" ? "-offering.cost_per_task"
      : facetId === "offering.speed.time_to_first_token" ? "-offering.speed.time_to_first_token"
      : facetId);
    return [[id, choice.weight ?? 0.5]];
  }));
}

export function toBoardDecisionSpec(spec: Spec, explain: "none" | "summary" | "full"): DecisionSpec {
  const contract = toDecisionSpec(spec, explain);
  return spec.boardWeights !== undefined
    ? { ...contract, optimize: { weights: boardHasPreference(spec) ? spec.boardWeights : UNRANKED_OBJECTIVE } }
    : contract;
}

export function boardHasPreference(spec: Spec): boolean {
  return spec.boardWeights !== undefined && Object.keys(spec.boardWeights).length > 0;
}

export function encodeBoardSpec(spec: Spec, axis: Axis, board: BoardUrlState): string {
  const { boardWeights: _previewWeights, ...productionSpec } = spec;
  return "#s=" + btoa(encodeURIComponent(JSON.stringify({ ...productionSpec, x: axis, board })));
}

export function decodeBoardState(hash: string): BoardUrlState | null {
  try {
    const raw: unknown = JSON.parse(decodeURIComponent(atob(hash.replace(/^#s=/, ""))));
    return z.object({ board: boardUrlSchema }).parse(raw).board;
  } catch {
    return null;
  }
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
    const value = JSON.parse(localStorage.getItem("modelspec-estate-v1") ?? "null") as Partial<Estate> | null;
    return { providers: value?.providers ?? [], plans: value?.plans ?? [], hardware: value?.hardware ?? [] };
  } catch { return { providers: [], plans: [], hardware: [] }; }
}

export function writeEstate(estate: Estate): void {
  try { localStorage.setItem("modelspec-estate-v1", JSON.stringify(estate)); } catch { /* storage is optional */ }
}
