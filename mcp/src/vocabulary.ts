import { z } from "zod";

export const vocabInput = z.object({
  section: z.enum([
    "starter", "facets", "benchmarks", "domains", "providers", "models",
    "task_types", "coverage", "templates", "refinements", "estate", "vendors",
    "template_categories", "template_tiers",
  ]).optional().describe("Return only this vocabulary section; defaults to starter"),
  search: z.string().optional().describe("Case-insensitive substring over id and label or display name"),
  id: z.string().optional().describe("Return full details for this exact id"),
  ids: z.array(z.string()).max(100).optional().describe("Return full details for these exact ids"),
  detail: z.enum(["compact", "full"]).optional().describe("Full returns all display details; defaults to compact"),
  offset: z.number().int().min(0).optional().describe("Skip this many matching rows; defaults to 0"),
  limit: z.number().int().min(1).max(20).optional().describe("Compact page size; defaults to 20"),
});
export type VocabInput = z.infer<typeof vocabInput>;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function pick(row: Record<string, unknown>, keys: string[]) {
  return Object.fromEntries(keys.filter((key) => key in row).map((key) => [key, row[key]]));
}

export function lookupVocabulary(vocabulary: Record<string, unknown>, args: VocabInput) {
  const section = args.section ?? "starter";
  const ids = [...new Set([...(args.ids ?? []), ...(args.id === undefined ? [] : [args.id])])];
  const full = args.detail === "full" || ids.length > 0;
  let source = vocabulary[section] ?? [];
  if (section === "coverage" && !full) return {};
  if (section === "estate" && !full) {
    source = isRecord(vocabulary.estate) ? pick(vocabulary.estate, ["providers", "devices"]) : {};
  }
  if (section === "starter") {
    const facets = Array.isArray(vocabulary.facets) ? vocabulary.facets.filter(isRecord) : [];
    const specs = Array.isArray(vocabulary.templates)
      ? vocabulary.templates.filter(isRecord).map((row) => JSON.stringify(row.spec)) : [];
    source = facets.map((row) => {
      const id = String(row.id);
      const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const pattern = new RegExp(`(?<![\\w.])${escaped}(?![\\w.])`);
      return { row, count: specs.filter((spec) => pattern.test(spec)).length };
    }).filter(({ count }) => count > 0)
      .sort((a, b) => b.count - a.count || (String(a.row.id) < String(b.row.id) ? -1 : 1))
      .slice(0, 15).map(({ row }) => row);
  }
  const mapping = isRecord(source);
  let rows: [string, unknown][] = mapping ? Object.entries(source)
    : Array.isArray(source) ? source.map((row) => [String(isRecord(row) ? row.id ?? "" : row), row]) : [];
  const search = (args.search ?? "").toLowerCase();
  rows = rows.filter(([id, row]) => {
    const label = isRecord(row) ? row.label ?? row.name ?? row.display_name ?? "" : row;
    return (ids.length === 0 || ids.includes(id)) &&
      (!search || id.toLowerCase().includes(search) || String(label).toLowerCase().includes(search));
  });
  if (!full) rows = rows.slice(args.offset ?? 0, (args.offset ?? 0) + (args.limit ?? 20));
  function compact(row: unknown): unknown {
    if (!isRecord(row)) return row;
    if (section === "facets" || section === "starter") {
      const result = pick(row, ["id", "label", "definition", "value_type", "literals"]);
      if (typeof result.definition === "string") {
        result.definition = result.definition.trim().replace(/\s+/g, " ").split(/\.\s/)[0].replace(/\.$/, "") + ".";
      }
      if (Array.isArray(row.allowed_values)) result.allowed_values = row.allowed_values;
      else if (Array.isArray(row.values)) result.allowed_values = row.values.filter(isRecord).map((value) => value.value);
      return result;
    }
    if (section === "models") return pick(row, ["display_name"]);
    return pick(row, ["id", "name", "label"]);
  }
  const selected = rows.map(([id, row]): [string, unknown] => [id, full ? row : compact(row)]);
  return mapping ? Object.fromEntries(selected) : selected.map(([, row]) => row);
}
