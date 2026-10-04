import { z } from "zod";
import agentCopy from "./agent-copy.json";

export const vocabInput = z.object({
  section: z.enum([
    "starter", "facets", "benchmarks", "domains", "providers", "models",
    "task_types", "coverage", "templates", "refinements", "estate", "vendors",
    "template_categories", "template_tiers",
  ]).optional().describe("Defaults to starter; with search or id/ids searches every section except coverage. An explicit non-starter section scopes the lookup"),
  search: z.string().max(128).optional().describe("Search every section's ids, labels, definitions and values by case- and separator-insensitive substring or all query tokens. A miss returns suggestions; an explicit non-starter section scopes the search"),
  id: z.string().max(128).optional().describe("Full details for this exact, case-sensitive id; starter resolves across sections and intersects with search"),
  ids: z.array(z.string().max(128)).max(100).optional().describe("Full details for these exact, case-sensitive ids; starter resolves across sections and intersects with search"),
  detail: z.enum(["compact", "full"]).optional().describe("Full returns all display details; defaults to compact. Cross-section matches remain paged"),
  offset: z.number().int().min(0).optional().describe("Skip this many ranked cross-section matches or compact section rows; defaults to 0"),
  limit: z.number().int().min(1).max(20).optional().describe("Page size; defaults to 20. Cross-section lookups page even full details and ids"),
});
export type VocabInput = z.infer<typeof vocabInput>;
type Section = NonNullable<VocabInput["section"]>;
const searchSections: Section[] = ["facets", "domains", "refinements", "benchmarks", "templates", "task_types",
  "estate", "providers", "vendors", "models", "template_categories", "template_tiers"];
type EstateGroup = "providers" | "devices" | "plans";
type Entry = { id: string; row: unknown; group: EstateGroup | null };
type Match = { section: Section; id: string; label?: string } & (
  { matched: "id" | "label" | "definition" } | { matched: "value"; value: unknown }
);
type Field = { kind: Match["matched"]; text: unknown; value: unknown };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function pick(row: Record<string, unknown>, keys: string[]) {
  return Object.fromEntries(keys.filter((key) => key in row).map((key) => [key, row[key]]));
}

export function vocabularyResponse(selected: unknown, args: VocabInput,
  extra: Record<string, unknown> = {}): Record<string, unknown> {
  const section = args.section ?? "starter";
  return {
    [section]: selected,
    next: section === "starter" ? agentCopy.vocab.next.starter : agentCopy.vocab.next.lookup,
    ...(section === "starter" ? { spec: agentCopy.vocab.minimal_spec } : {}),
    ...extra,
  };
}

function starterIds(vocabulary: Record<string, unknown>) {
  const facets = Array.isArray(vocabulary.facets) ? vocabulary.facets.filter(isRecord) : [];
  const specs = Array.isArray(vocabulary.templates)
    ? vocabulary.templates.filter(isRecord).map((row) => JSON.stringify(row.spec ?? {})) : [];
  return facets.map((row) => {
    const id = String(row.id);
    const escaped = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(`(?<![\\w.])${escaped}(?![\\w.])`);
    return { id, count: specs.filter((spec) => pattern.test(spec)).length };
  }).filter(({ count }) => count > 0)
    .sort((a, b) => b.count - a.count || compareText(a.id, b.id))
    .slice(0, 15).map(({ id }) => id);
}

function compact(row: unknown, section: Section): unknown {
  if (!isRecord(row)) return row;
  if (section === "facets" || section === "starter") {
    const result = pick(row, ["id", "label", "definition", "value_type", "better", "literals"]);
    if (typeof result.definition === "string") {
      result.definition = result.definition.trim().replace(/\s+/g, " ").split(/\.\s/)[0].replace(/\.$/, "") + ".";
    }
    if (Array.isArray(row.allowed_values)) result.allowed_values = row.allowed_values;
    else if (Array.isArray(row.values)) result.allowed_values = row.values.filter(isRecord).map((value) => value.value);
    return result;
  }
  return pick(row, section === "models" ? ["display_name"] : ["id", "name", "label"]);
}

function normalize(value: unknown) {
  return String(value).toLowerCase().replace(/[_\-./\s]+/g, " ").trim();
}

function sectionRows(vocabulary: Record<string, unknown>, section: Section): Entry[] {
  const source = vocabulary[section] ?? {};
  if (section === "estate" && isRecord(source)) {
    const entries: Entry[] = [];
    for (const group of ["providers", "devices", "plans"] satisfies EstateGroup[]) {
      const rows = source[group];
      if (Array.isArray(rows)) {
        entries.push(...rows.map((row): Entry => ({ id: String(isRecord(row) ? row.id ?? "" : row), row, group })));
      }
    }
    return entries;
  }
  if (isRecord(source)) return Object.entries(source).map(([id, row]) => ({ id, row, group: null }));
  return Array.isArray(source) ? source.map((row) => ({ id: String(isRecord(row) ? row.id ?? "" : row), row, group: null })) : [];
}

function searchableFields(section: Section, { id, row }: Entry): Field[] {
  const fields: Field[] = [{ kind: "id", text: id, value: null }];
  if (section === "providers" || section === "vendors") fields.push({ kind: "label", text: row, value: null });
  if (!isRecord(row)) return fields;
  const labels = section === "facets" ? ["label"] : section === "models" ? ["display_name"] : ["name"];
  for (const label of labels) {
    if (row[label] != null) fields.push({ kind: "label", text: row[label], value: null });
  }
  if (section === "estate" && row.provider != null) fields.push({ kind: "label", text: row.provider, value: null });
  const definitions = section === "templates" ? ["purpose", "category", "tier"]
    : section === "facets" || section === "refinements" ? ["definition"] : [];
  for (const key of definitions) {
    if (row[key] != null) fields.push({ kind: "definition", text: row[key], value: null });
  }
  if (section === "facets") {
    if (Array.isArray(row.values)) {
      for (const value of row.values.filter(isRecord)) {
        fields.push({ kind: "value", text: value.value, value: value.value });
        if (value.label != null) fields.push({ kind: "value", text: value.label, value: value.value });
      }
    }
    if (Array.isArray(row.allowed_values)) {
      fields.push(...row.allowed_values.map((value): Field => ({ kind: "value", text: value, value })));
    }
  }
  return fields;
}

function matchFields(fields: Field[], needle: string): Pick<Match, "matched"> & { value: unknown } | undefined {
  const tokens = needle.split(/\s+/);
  let prior: string[] = [];
  for (const kind of ["id", "label", "definition", "value"] satisfies Match["matched"][]) {
    const current = fields.filter((field) => field.kind === kind).map(({ text, value }) => ({ text: normalize(text), value }));
    for (const { text, value } of current) {
      if (text.includes(needle)) return { matched: kind, value };
    }
    const combined = [...prior, ...current.map(({ text }) => text)];
    if (current.length > 0 && tokens.every((token) => combined.some((text) => text.includes(token)))) {
      const value = current.find(({ text }) => tokens.some((token) => text.includes(token)))?.value ?? null;
      return { matched: kind, value };
    }
    prior = combined;
  }
  return undefined;
}

function similarity(left: string, right: string) {
  if (!left || !right) return 0;
  const a = Array.from(left), b = Array.from(right);
  let previous = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (const [i, charA] of a.entries()) {
    const current = [i + 1];
    for (const [j, charB] of b.entries()) {
      current.push(Math.min(current[j] + 1, previous[j + 1] + 1, previous[j] + Number(charA !== charB)));
    }
    previous = current;
  }
  return 1 - previous[b.length] / Math.max(a.length, b.length);
}

function compareText(left: string, right: string) {
  return left < right ? -1 : left > right ? 1 : 0;
}

// A value suggestion names its facet id, so retrying with id= cannot dead-end.
type Candidate = { section: Section; id: string; name: string | null; text: string; labels: unknown[]; value: unknown };

export const SUGGESTION_CELLS = 300_000;

function suggestions(vocabulary: Record<string, unknown>, needles: string[]) {
  const candidates = new Map<string, Candidate>();
  for (const section of searchSections) {
    for (const entry of sectionRows(vocabulary, section)) {
      const fields = searchableFields(section, entry);
      candidates.set(JSON.stringify([section, entry.id, null]), { section, id: entry.id, name: null, text: entry.id,
        labels: fields.filter(({ kind }) => kind === "label").map(({ text }) => text), value: null });
      for (const { kind, text, value } of fields) {
        if (kind !== "value") continue;
        const name = typeof value === "boolean" ? JSON.stringify(value) : String(value);
        const key = JSON.stringify([section, entry.id, name]);
        const candidate = candidates.get(key) ?? { section, id: entry.id, name, text: name, labels: [], value };
        candidate.labels.push(text);
        candidates.set(key, candidate);
      }
    }
  }
  // The suggestion pass is reachable without a key, so its work has a hard ceiling:
  // two needles of at most 32 characters, and at most SUGGESTION_CELLS Levenshtein cells.
  const normalized = needles.slice(0, 2).map((needle) => Array.from(normalize(needle)).slice(0, 32).join(""));
  const scored: (Candidate & { score: number })[] = [];
  let cells = 0;
  for (const candidate of candidates.values()) {
    const { text, labels } = candidate;
    // Token scores let a typo like "pirce" suggest offering.price.input.
    // An ordered dedupe keeps the budget's stopping point the same on every run.
    const haystacks = new Set([normalize(text), normalize(text.split(/[._]/).at(-1) ?? ""),
      ...normalize(text).split(/\s+/), ...labels.map(normalize)]);
    let score = 0;
    scoring: for (const needle of normalized) {
      for (const hay of haystacks) {
        // Levenshtein similarity is at most min/max length, so skip pairs that cannot reach 0.4.
        const [n, h] = [Array.from(needle).length, Array.from(hay).length];
        if (!n || !h || Math.min(n, h) < 0.4 * Math.max(n, h)) continue;
        cells += n * h;
        if (cells > SUGGESTION_CELLS) break scoring;
        score = Math.max(score, similarity(needle, hay));
      }
    }
    if (score >= 0.4) scored.push({ ...candidate, score });
    if (cells > SUGGESTION_CELLS) break;
  }
  return scored.sort((a, b) => b.score - a.score || searchSections.indexOf(a.section) - searchSections.indexOf(b.section)
    || compareText(a.id, b.id) || compareText(a.name ?? "", b.name ?? "")).slice(0, 5)
    .map(({ section, id, name, value }) => ({ section, id, ...(name === null ? {} : { value }) }));
}

function selectRows(entries: Entry[], section: Section, full: boolean): unknown {
  if (section === "estate") {
    return Object.fromEntries((["providers", "devices", "plans"] satisfies EstateGroup[]).map((group) =>
      [group, entries.filter((entry) => entry.group === group).map(({ row }) => full ? row : compact(row, section))]));
  }
  const selected = entries.map(({ id, row }) => [id, full ? row : compact(row, section)]);
  return ["providers", "vendors", "models", "coverage"].includes(section)
    ? Object.fromEntries(selected) : selected.map(([, row]) => row);
}

function searchVocabulary(vocabulary: Record<string, unknown>, args: VocabInput, ids: string[]): Record<string, unknown> {
  const section = args.section ?? "starter", search = args.search ?? "";
  const crossSection = section === "starter";
  const searched = crossSection ? searchSections : [section];
  const full = args.detail === "full" || ids.length > 0;
  const needle = normalize(search);
  const hits: { rank: number; match: Match; entry: Entry }[] = [];
  for (const name of searched) {
    for (const entry of sectionRows(vocabulary, name)) {
      if (ids.length > 0 && !ids.includes(entry.id)) continue;
      // A search of only separators normalises to nothing: it matches nothing, not everything.
      const field = needle ? matchFields(searchableFields(name, entry), needle)
        : search ? undefined : { matched: "id", value: null } satisfies { matched: "id"; value: null };
      if (!field) continue;
      const rank = ids.includes(entry.id) || entry.id === search ? 0 : ["id", "label", "definition", "value"].indexOf(field.matched) + 1;
      const label = isRecord(entry.row) ? entry.row.label ?? entry.row.name ?? entry.row.display_name
        : name === "providers" || name === "vendors" ? entry.row : undefined;
      const base = { section: name, id: entry.id, ...(typeof label === "string" ? { label } : {}) };
      const match: Match = field.matched === "value" ? { ...base, matched: "value", value: field.value } : { ...base, matched: field.matched };
      hits.push({ rank, match, entry });
    }
  }
  const ranked = [...hits].sort((a, b) => a.rank - b.rank || searched.indexOf(a.match.section) - searched.indexOf(b.match.section));
  const offset = args.offset ?? 0, limit = args.limit ?? 20;
  const page = ranked.slice(offset, offset + limit);
  const sections = crossSection ? Object.fromEntries(searched.map((name) =>
    [name, selectRows(page.filter(({ match }) => match.section === name).map(({ entry }) => entry), name, full)]))
    : { [section]: selectRows(full ? hits.map(({ entry }) => entry) : hits.slice(offset, offset + limit).map(({ entry }) => entry), section, full) };
  if (crossSection) {
    const starters = new Set(starterIds(vocabulary));
    sections.starter = page.filter(({ match }) => match.section === "facets" && starters.has(match.id))
      .map(({ entry }) => full ? entry.row : compact(entry.row, "facets"));
  }
  const result = vocabularyResponse(sections[section], args, sections);
  result.matches = page.map(({ match }) => match);
  result.total = hits.length;
  result.searched = [...searched];
  result.next = hits.length > 0 ? agentCopy.vocab.next.lookup : agentCopy.vocab.next.empty;
  if (hits.length === 0) {
    const closest = suggestions(vocabulary, search ? [search] : [...ids].sort(compareText));
    result.suggestions = closest;
    const quoted = JSON.stringify(search || [...ids].sort(compareText).join(", "));
    const names = closest.map((item) => "value" in item ? `${item.id} (value ${typeof item.value === "boolean" ? JSON.stringify(item.value) : String(item.value)})` : item.id).join(", ") || "none";
    result.message = `No vocabulary entry matches ${quoted} in the id, label, definition or values of ${searched.join(", ")}; closest ids: ${names}.`;
  }
  return result;
}

export function lookupVocabulary(vocabulary: Record<string, unknown>, args: VocabInput): Record<string, unknown> {
  const section = args.section ?? "starter";
  const ids = [...new Set([...(args.ids ?? []), ...(args.id === undefined ? [] : [args.id])])];
  if (args.search || ids.length > 0) return searchVocabulary(vocabulary, args, ids);
  const full = args.detail === "full";
  let source = vocabulary[section] ?? [];
  if (section === "coverage" && !full) return vocabularyResponse({}, args);
  if (section === "estate" && !full) {
    source = isRecord(vocabulary.estate) ? pick(vocabulary.estate, ["providers", "devices"]) : {};
  }
  if (section === "starter") {
    const starters = starterIds(vocabulary);
    const facets = Array.isArray(vocabulary.facets) ? vocabulary.facets.filter(isRecord) : [];
    source = starters.flatMap((id) => facets.filter((row) => row.id === id));
  }
  const mapping = isRecord(source);
  let rows: [string, unknown][] = mapping ? Object.entries(source)
    : Array.isArray(source) ? source.map((row) => [String(isRecord(row) ? row.id ?? "" : row), row]) : [];
  if (!full) rows = rows.slice(args.offset ?? 0, (args.offset ?? 0) + (args.limit ?? 20));
  const selected = rows.map(([id, row]): [string, unknown] => [id, full ? row : compact(row, section)]);
  return vocabularyResponse(mapping ? Object.fromEntries(selected) : selected.map(([, row]) => row), args);
}
