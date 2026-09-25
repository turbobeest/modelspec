import facetsYaml from "../../../../registry/facets.yaml?raw";

interface FacetPresentation {
  name: string;
  unit: string | null;
  unitId?: string;
}

const NAME_OVERRIDES: Readonly<Record<string, string>> = {
  "model.class": "Type",
  "model.context_window": "Context",
  "model.weights_openness": "Weights",
  "licence.commercial_use": "Commercial use",
  "origin.lab_jurisdiction": "Lab jurisdiction",
  "offering.provider": "Provider",
  "offering.region": "Region",
  "offering.price.input": "Input price",
  "offering.price.output": "Output price",
  "offering.speed.time_to_first_token": "Time to first token",
  "offering.speed.throughput": "Output throughput",
  "offering.data.retention": "Data retention",
  "offering.data.zero_retention": "Zero retention",
};

const UNIT_NAMES: Readonly<Record<string, string>> = {
  usd_per_1m_tokens: "$ / 1M tokens",
  tokens: "tokens",
  tokens_per_second: "tokens/s",
  milliseconds: "ms",
  parameters: "parameters",
  days: "days",
  requests_per_minute: "requests/min",
  tokens_per_minute: "tokens/min",
  percent: "%",
  monthly_active_users: "monthly active users",
  benchmark_metric: "benchmark units",
  usd_per_task: "per task",
  capability_scale: "capability scale",
};

function sentenceCase(value: string): string {
  const words = value.replaceAll(/[._-]+/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function registryPresentation(source: string): Readonly<Record<string, FacetPresentation>> {
  const facets = source.split("\nfacets:\n", 2)[1] ?? "";
  const entries: Record<string, FacetPresentation> = {};
  let id: string | null = null;
  for (const line of facets.split("\n")) {
    const nextId = /^ {2}- id: ([a-z][a-z0-9_.-]*)$/.exec(line)?.[1];
    if (nextId) {
      id = nextId;
      entries[id] = {
        name: NAME_OVERRIDES[id] ?? sentenceCase(id.split(".").at(-1) ?? id),
        unit: null,
      };
      continue;
    }
    const unit = /^ {4}unit: ([a-z0-9_]+)$/.exec(line)?.[1];
    if (id && unit) {
      entries[id] = {
        ...entries[id],
        unit: UNIT_NAMES[unit] ?? sentenceCase(unit),
        unitId: unit,
      };
    }
    const label = /^ {4}label: (.+)$/.exec(line)?.[1];
    if (id && label && !NAME_OVERRIDES[id]) entries[id] = { ...entries[id], name: label };
  }
  return entries;
}

const FACETS = registryPresentation(facetsYaml);
const BENCHMARKS = new Map<string, { name: string; percent: boolean }>();

/** Benchmark names and units from the published vocabulary (real mode). */
export function registerBenchmarks(
  rows: readonly { id: string; name: string; unit: string | null }[],
): void {
  BENCHMARKS.clear();
  for (const row of rows)
    BENCHMARKS.set(row.id, { name: row.name, percent: row.unit === "percent" });
}

const PROVIDERS = new Map<string, string>();

/** Provider display names from the published vocabulary (real mode). */
export function registerProviders(names: Readonly<Record<string, string>>): void {
  PROVIDERS.clear();
  for (const [id, name] of Object.entries(names)) PROVIDERS.set(id, name);
}

export function providerName(id: string): string {
  return PROVIDERS.get(id) ?? id;
}

export function facetName(id: string): string {
  return (
    BENCHMARKS.get(id)?.name ??
    FACETS[id]?.name ??
    sentenceCase(id.split(".").at(-1) ?? id)
  );
}

function humanValue(value: string): string {
  const bare = value.replace(/^\{(.*)\}$/, "$1");
  return bare
    .split(/,\s*/)
    .map((item) => item.replaceAll(/[_-]+/g, " "))
    .join(" or ");
}

export function valueWithUnit(facet: string, value: string): string {
  if (facet === "offering.provider")
    return value
      .replace(/^\{(.*)\}$/, "$1")
      .split(/,\s*/)
      .map(providerName)
      .join(" or ");
  const numeric = /^-?\d+(\.\d+)?(e-?\d+)?$/.test(value);
  const unitId = FACETS[facet]?.unitId;
  if (numeric && unitId === "usd_per_task") return `$${Number(value)} per task`;
  if (numeric && unitId === "usd_per_1m_tokens") return `$${Number(value)} / 1M tokens`;
  if (numeric && BENCHMARKS.get(facet)?.percent) return `${Number(value)}%`;
  const unit = FACETS[facet]?.unit;
  const formatted = numeric
    ? Number(value).toLocaleString("en-US")
    : humanValue(value);
  return unit ? `${formatted} ${unit}` : formatted;
}

const MODIFIERS: readonly [RegExp, string][] = [
  [/\s+@independent\b/, "independent"],
  [/\s+@provider_self_report\b/, "lab-reported only"],
  [/\s+@direct\b/, "direct evidence"],
  [/\s+soft\([^)]*\)/, "soft"],
  [/\s+unknown\([^)]*\)/, ""],
  [/\s+@any\b/, ""],
];

/** Split trailing qualifiers and modifiers off a compact condition. */
function modifiers(condition: string): { core: string; notes: string[] } {
  let core = condition;
  const notes: string[] = [];
  for (const [re, note] of MODIFIERS)
    if (re.test(core)) {
      core = core.replace(re, "");
      if (note) notes.push(note);
    }
  return { core, notes };
}

export function renderContractCondition(condition: string): string {
  const { core, notes } = modifiers(condition);
  const text = renderCore(core);
  return notes.length ? `${text} · ${notes.join(" · ")}` : text;
}

function renderCore(condition: string): string {
  const known = /^known\(([a-z][a-z0-9_.-]*)\)$/.exec(condition);
  if (known) return `Has a ${facetName(known[1]).toLowerCase()}`;

  const comparison = /^([a-z][a-z0-9_.-]*)\s+(not in|in|!=|<=|>=|=|<|>)\s+(.+)$/.exec(
    condition,
  );
  if (comparison) {
    const [, facet, operator, rawValue] = comparison;
    const name = facetName(facet);
    const value = valueWithUnit(facet, rawValue);
    switch (operator) {
      case "=":
        return `${name}: ${value}`;
      case "!=":
        return `${name}: not ${value}`;
      case "in":
        return `${name}: ${value}`;
      case "not in":
        return `${name}: exclude ${value}`;
      case ">=":
        return `${name}: at least ${value}`;
      case ">":
        return `${name}: more than ${value}`;
      case "<=":
        return `${name}: at most ${value}`;
      case "<":
        return `${name}: less than ${value}`;
    }
  }

  return sentenceCase(
    condition
      .replaceAll(/([a-z][a-z0-9_-]*(?:\.[a-z0-9_-]+)+)/g, (facet) =>
        facetName(facet),
      )
      .replaceAll("_", " "),
  );
}

export function renderUnknownFacets(facets: string[]): string {
  return facets.map((facet) => facetName(facet)).join(", ");
}
