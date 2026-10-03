import { lowerIsBetter } from "../vocabulary";
import type { Vocabulary, VocabFacet } from "../vocabulary";
import type { DecisionSpec } from "../adapter";

export type CanvasAxisId = `facet:${string}` | `capability:${string}`;

export type CanvasAxisOption =
  | {
      kind: "facet";
      id: `facet:${string}`;
      key: string;
      label: string;
      unit: string | null;
      valueType: "number" | "date";
      known?: number;
      disabled: boolean;
      disabledReason: string | null;
      mustOp: "<=" | ">=" | null;
      lowerIsBetter: boolean;
    }
  | {
      kind: "capability";
      id: `capability:${string}`;
      key: string;
      label: string;
      unit: "capability score";
      valueType: "number";
      known?: number;
      disabled: boolean;
      disabledReason: string | null;
      mustOp: ">=";
      lowerIsBetter: false;
    };

function facetMustOp(facet: VocabFacet): "<=" | ">=" | null {
  if (lowerIsBetter(facet) && facet.operators.includes("<=")) return "<=";
  if (facet.operators.includes(">=")) return ">=";
  return null;
}

/** Every scale the current snapshot describes, including unavailable choices. */
export function canvasAxisOptions(vocabulary: Vocabulary): CanvasAxisOption[] {
  const facets: CanvasAxisOption[] = vocabulary.facets
    .filter(
      (facet): facet is VocabFacet & { value_type: "number" | "date" } =>
        facet.value_type === "number" || facet.value_type === "date",
    )
    .map((facet) => ({
      kind: "facet",
      id: `facet:${facet.id}`,
      key: facet.id,
      label: facet.label,
      unit: facet.unit,
      valueType: facet.value_type,
      known: facet.known,
      disabled: facet.known === 0,
      disabledReason:
        facet.known === 0
          ? "No models have a recorded value in this snapshot"
          : null,
      mustOp: facetMustOp(facet),
      lowerIsBetter: lowerIsBetter(facet),
    }));
  const capabilities: CanvasAxisOption[] = vocabulary.domains.map((domain) => ({
    kind: "capability",
    id: `capability:${domain.id}`,
    key: domain.id,
    label: `${domain.name} capability`,
    unit: "capability score",
    valueType: "number",
    known: domain.estimate_models,
    disabled: domain.estimate_models === 0,
    disabledReason:
      domain.estimate_models === 0
        ? "No models have a capability estimate in this snapshot"
        : null,
    mustOp: ">=",
    lowerIsBetter: false,
  }));
  return [...facets, ...capabilities];
}

export function isCanvasAxisId(value: string): value is CanvasAxisId {
  return /^(?:facet|capability):[a-z][a-z0-9_.-]*$/.test(value);
}

function objectiveDimensions(objective: DecisionSpec["optimize"]): string[] {
  if ("max" in objective) return [objective.max];
  if ("min" in objective) return [objective.min];
  if ("weights" in objective) return Object.keys(objective.weights);
  if ("pareto" in objective) return objective.pareto;
  return objective.lexicographic.map((part) =>
    "max" in part ? part.max : part.min,
  );
}

/**
 * A plot request asks the engine to return another estimate but leaves the
 * decision's conditions and objective intact. `preferred` requests an
 * estimate without making that capability a requirement.
 */
export function capabilityPlotSpec(
  ranking: DecisionSpec,
  requested: string | readonly string[],
): DecisionSpec | null {
  const domains = typeof requested === "string" ? [requested] : requested;
  const ranked = new Set(
    objectiveDimensions(ranking.optimize).map(
      (dimension) => dimension.replace(/^-/, "").split("/", 1)[0],
    ),
  );
  const extra = domains.filter((domain) => !ranked.has(domain));
  if (extra.length === 0) return null;
  const additions: [string, "preferred"][] = extra.map((domain) => [
    domain,
    "preferred",
  ]);
  return {
    ...ranking,
    capabilities: Object.fromEntries([
      ...Object.entries(ranking.capabilities ?? {}),
      ...additions,
    ]),
  };
}

/** Build the membership-neutral request that supplies canvas coordinates. */
export function canvasPlotSpec(
  ranking: DecisionSpec,
  x: CanvasAxisOption,
  y: CanvasAxisOption,
  numericFallback?: CanvasAxisOption,
): DecisionSpec {
  const numericAxes = [x, y].filter((axis) => axis.valueType === "number");
  const objectiveAxes = numericAxes.length > 0
    ? numericAxes
    : numericFallback
      ? [numericFallback]
      : [];
  const dimensions = objectiveAxes.map((axis) =>
    `${axis.lowerIsBetter ? "-" : ""}${axis.key}`,
  );
  const unique = [...new Set(dimensions)];
  const optimize = unique.length > 0
    ? {
        weights: Object.fromEntries(
          unique.map((dimension) => [dimension, 1 / unique.length]),
        ),
      }
    : ranking.optimize;
  const capabilityDomains = [...new Set(
    [x, y].flatMap((axis) =>
      axis.kind === "capability" ? [axis.key] : [],
    ),
  )];
  const capabilities: [string, "preferred"][] = capabilityDomains.map(
    (domain) => [domain, "preferred"],
  );
  return {
    ...ranking,
    where: [],
    capabilities:
      capabilities.length > 0 ? Object.fromEntries(capabilities) : undefined,
    optimize,
    explain: "full",
    limit: 500,
  };
}
