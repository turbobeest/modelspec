import { z } from "zod";
import agentCopy from "./agent-copy.json";
import synonymData from "../../pipeline/vocab_synonyms.json";

export const vocabInput = z.object({
  section: z.enum([
    "starter", "facets", "benchmarks", "domains", "providers", "models",
    "task_types", "coverage", "templates", "refinements", "estate", "vendors",
    "template_categories", "template_tiers",
  ]).optional().describe("Defaults to starter; with search or id/ids searches every section except coverage. An explicit non-starter section scopes the lookup"),
  search: z.string().max(128).optional().describe("Search every section's ids, labels, definitions, values and synonyms. All tokens rank first; else content tokens match, stopwords omitted. A miss returns nearest ids. A non-starter section scopes the search"),
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
type Match = { section: Section; id: string; label?: string; via?: "synonym"; matched_tokens?: string[] } & (
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
  if (section !== "models" && row.display_name != null) fields.push({ kind: "label", text: row.display_name, value: null });
  for (const key of ["aliases", "synonyms"]) {
    const raw = row[key];
    const items = typeof raw === "string" ? [raw] : Array.isArray(raw) ? raw : [];
    for (const item of items) {
      if (typeof item === "string") fields.push({ kind: "label", text: item, value: null });
    }
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

const KINDS = ["id", "label", "definition", "value"] satisfies Match["matched"][];
const STOPWORDS = new Set(["use", "for", "the", "a", "and", "of", "with", "on", "in", "to"]);
// Suggestion scoring and subset matching both stop at the first 8 unique content tokens.
const SUGGESTION_TOKENS = 8;
const SUGGESTION_NEEDLE_CHARS = 32;

type Folded = { kind: Match["matched"]; text: string; value: unknown };
type Classified = {
  tier: 0 | 1 | 2;
  kind: Match["matched"];
  value: unknown;
  via: "synonym" | null;
  matchedTokens: string[];
  quality: Map<string, number>;
};

function words(value: string) {
  return value.length === 0 ? [] : value.split(/\s+/).filter((token) => token.length > 0);
}

let synonyms: { spelling: Map<string, string>; phrases: { tokens: string[]; ids: string[] }[] } | undefined;
function synonymTable() {
  if (synonyms) return synonyms;
  const spelling = new Map<string, string>();
  for (const [canonical, variant] of synonymData.spelling) {
    spelling.set(normalize(variant), normalize(canonical));
  }
  const phrases: { tokens: string[]; ids: string[] }[] = [];
  for (const row of synonymData.synonyms) {
    for (const phrase of row.phrases) {
      const tokens = words(normalize(phrase));
      if (tokens.length > 0 && row.ids.length > 0) phrases.push({ tokens, ids: [...row.ids] });
    }
  }
  synonyms = { spelling, phrases };
  return synonyms;
}

let matchCalls = 0;
let foldCalls = 0;

/** Counts from the last reset, so a test can bound match work without a timer. */
export function takeSearchWork() {
  const work = { matchCalls, foldCalls };
  matchCalls = 0;
  foldCalls = 0;
  return work;
}

function foldToken(token: string) {
  foldCalls += 1;
  return synonymTable().spelling.get(token) ?? token;
}

function fold(value: unknown) {
  return words(normalize(value)).map(foldToken).join(" ");
}

function foldFields(fields: Field[]): Folded[] {
  return fields.map(({ kind, text, value }) => ({ kind, text: fold(text), value }));
}

function codePointLength(value: string) {
  return Array.from(value).length;
}

function matchFolded(folded: Folded[], foldedNeedle: string, tokens: string[]) {
  // Needle is folded once per request. `tokens` are its unique folded words.
  matchCalls += 1;
  if (tokens.length === 0) return undefined;
  let prior: string[] = [];
  for (const kind of KINDS) {
    const current = folded.filter((field) => field.kind === kind);
    for (const { text, value } of current) {
      if (text && text.includes(foldedNeedle)) return { matched: kind, value };
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

type Prepared = {
  raw: string[];
  content: string[];
  foldedAll: string;
  allTokens: string[];
  contentFolded: string[];
};

function prepareQuery(needle: string): Prepared {
  // Subset matching keeps the first 8 unique content tokens. Length is code points.
  const raw = needle ? words(needle) : [];
  const foldedOf = new Map<string, string>();
  for (const token of raw) {
    if (!foldedOf.has(token)) foldedOf.set(token, foldToken(token));
  }
  const content: string[] = [];
  const seen = new Set<string>();
  for (const token of raw) {
    if (STOPWORDS.has(token) || codePointLength(token) < 2 || seen.has(token)) continue;
    seen.add(token);
    content.push(token);
    if (content.length >= SUGGESTION_TOKENS) break;
  }
  const foldedAll = raw.map((token) => foldedOf.get(token) ?? token).join(" ");
  const allTokens: string[] = [];
  const seenFolded = new Set<string>();
  for (const token of raw) {
    const folded = foldedOf.get(token) ?? token;
    if (seenFolded.has(folded)) continue;
    seenFolded.add(folded);
    allTokens.push(folded);
  }
  return { raw, content, foldedAll, allTokens, contentFolded: content.map((token) => foldedOf.get(token) ?? token) };
}

function phraseCover(raw: string[], content: string[]) {
  const cover = new Map<string, Set<string>>();
  const whole = new Set<string>();
  const contentSet = new Set(content);
  for (const phrase of synonymTable().phrases) {
    const size = phrase.tokens.length;
    if (size === 0 || size > raw.length) continue;
    for (let start = 0; start <= raw.length - size; start += 1) {
      if (!phrase.tokens.every((token, index) => raw[start + index] === token)) continue;
      const hit = phrase.tokens.filter((token) => contentSet.has(token));
      for (const key of phrase.ids) {
        const tokens = cover.get(key) ?? new Set<string>();
        for (const token of hit) tokens.add(token);
        cover.set(key, tokens);
      }
      if (size === raw.length) for (const key of phrase.ids) whole.add(key);
    }
  }
  return { cover, whole };
}

function tokenQuality(folded: Folded[], foldedToken: string, synonym: boolean) {
  if (synonym) return 0;
  let partial = false;
  for (const { text } of folded) {
    if (!foldedToken || !text) continue;
    if (words(text).includes(foldedToken)) return 1;
    partial = partial || text.includes(foldedToken);
  }
  return partial ? 2 : 9;
}

function bestKind(found: { kind: Match["matched"]; value: unknown }[]): { kind: Match["matched"]; value: unknown } {
  let kind: Match["matched"] = "value";
  for (const item of found) {
    if (KINDS.indexOf(item.kind) < KINDS.indexOf(kind)) kind = item.kind;
  }
  const value = kind === "value" ? found.find((item) => item.kind === kind)?.value ?? null : null;
  return { kind, value };
}

function viaFor(tokens: string[], textTokens: Set<string>): "synonym" | null {
  return tokens.some((token) => !textTokens.has(token)) ? "synonym" : null;
}

function pickHit(all: { kind: Match["matched"]; value: unknown } | undefined,
  found: { kind: Match["matched"]; value: unknown }[]): { kind: Match["matched"]; value: unknown } {
  if (all) return all;
  if (found.length > 0) return bestKind(found);
  return { kind: "label", value: null };
}

// total counts subset and synonym hits. Only a true miss is zero.
function classify(folded: Folded[], key: string, query: Prepared,
  cover: Map<string, Set<string>>, whole: Set<string>, exact: boolean): Classified | undefined {
  const { raw, content, foldedAll, allTokens, contentFolded } = query;
  const textAll = raw.length > 0 ? matchFolded(folded, foldedAll, allTokens) : undefined;
  const synonymTokens = cover.get(key) ?? new Set<string>();
  const textFound: { token: string; kind: Match["matched"]; value: unknown }[] = [];
  for (let i = 0; i < content.length; i += 1) {
    const token = content[i];
    const foldedToken = contentFolded[i];
    if (token === undefined || foldedToken === undefined) continue;
    const found = matchFolded(folded, foldedToken, [foldedToken]);
    if (found) textFound.push({ token, kind: found.matched, value: found.value });
  }
  const textTokens = new Set(textFound.map(({ token }) => token));
  const matchedTokens = content.filter((token) => textTokens.has(token) || synonymTokens.has(token));
  const synonymFull = content.length > 0 && content.every((token) => synonymTokens.has(token));
  const wholeQuery = whole.has(key);
  const fromAll = textAll ? { kind: textAll.matched, value: textAll.value } : undefined;
  if (exact) {
    if (!fromAll && textFound.length === 0 && matchedTokens.length === 0 && !wholeQuery && !synonymFull) return undefined;
    const picked = pickHit(fromAll, textFound);
    return { tier: 0, kind: picked.kind, value: picked.kind === "value" ? picked.value : null,
      via: null, matchedTokens: [], quality: new Map() };
  }
  if (fromAll) {
    return { tier: 1, kind: fromAll.kind, value: fromAll.kind === "value" ? fromAll.value : null,
      via: null, matchedTokens: [], quality: new Map() };
  }
  if (wholeQuery || synonymFull) {
    const picked = pickHit(undefined, textFound);
    return { tier: 1, kind: picked.kind, value: picked.kind === "value" ? picked.value : null,
      via: viaFor(content, textTokens), matchedTokens: [], quality: new Map() };
  }
  if (matchedTokens.length === 0) return undefined;
  const picked = pickHit(undefined, textFound);
  const quality = new Map<string, number>();
  for (let i = 0; i < content.length; i += 1) {
    const token = content[i];
    const foldedToken = contentFolded[i];
    if (token === undefined || foldedToken === undefined || !matchedTokens.includes(token)) continue;
    quality.set(token, tokenQuality(folded, foldedToken, synonymTokens.has(token)));
  }
  return { tier: 2, kind: picked.kind, value: picked.kind === "value" ? picked.value : null,
    via: viaFor(matchedTokens, textTokens), matchedTokens, quality };
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
type Scored = { score: number; section: Section; id: string; name: string | null; value: unknown };

export const SUGGESTION_CELLS = 300_000;

function suggestionTokens(needles: string[]) {
  const tokens: string[] = [];
  for (const needle of needles) {
    for (const token of words(normalize(needle))) {
      tokens.push(Array.from(token).slice(0, SUGGESTION_NEEDLE_CHARS).join(""));
      if (tokens.length >= SUGGESTION_TOKENS) return tokens;
    }
  }
  return tokens;
}

function foldedHaystacks(text: string, labels: unknown[]) {
  const normalized = normalize(text);
  const raw: string[] = [];
  const seenRaw = new Set<string>();
  for (const item of [normalized, normalize(text.split(/[._]/).at(-1) ?? ""), ...words(normalized), ...labels.map(normalize)]) {
    if (seenRaw.has(item)) continue;
    seenRaw.add(item);
    raw.push(item);
  }
  const folded: string[] = [];
  const seen = new Set<string>();
  for (const item of raw) {
    const hay = fold(item);
    if (seen.has(hay)) continue;
    seen.add(hay);
    folded.push(hay);
  }
  return folded;
}

function scoreSuggestions(candidates: Map<string, Candidate>, tokens: string[], cover: Map<string, Set<string>>,
  cells: { n: number }, lengthFilter: boolean, idsOnly: boolean) {
  const scored: Scored[] = [];
  let calls = 0;
  let stopped = false;
  for (const candidate of candidates.values()) {
    if (stopped) break;
    if (idsOnly && candidate.name !== null) continue;
    const haystacks = foldedHaystacks(candidate.text, candidate.labels);
    const synonymTokens = candidate.name === null ? cover.get(candidate.id) ?? new Set<string>() : new Set<string>();
    let score = 0;
    for (const token of tokens) {
      if (synonymTokens.has(token)) {
        score += 1;
        continue;
      }
      const foldedToken = fold(token);
      let best = 0;
      for (const hay of haystacks) {
        // Levenshtein similarity is at most min/max length, so skip pairs that cannot reach 0.4.
        const n = Array.from(foldedToken).length;
        const h = Array.from(hay).length;
        if (!n || !h || (lengthFilter && Math.min(n, h) < 0.4 * Math.max(n, h))) continue;
        const cost = n * h;
        if (cells.n + cost > SUGGESTION_CELLS) {
          stopped = true;
          break;
        }
        cells.n += cost;
        calls += 1;
        best = Math.max(best, similarity(foldedToken, hay));
      }
      score += best;
      if (stopped) break;
    }
    if (score > 0) scored.push({ score, section: candidate.section, id: candidate.id, name: candidate.name, value: candidate.value });
  }
  return { scored, calls };
}

function suggestions(vocabulary: Record<string, unknown>, needles: string[]) {
  // Scores each of the first 8 tokens. Synonym ids score 1. Keeps scores of at
  // least 0.4, or the best score above zero when nothing reaches 0.4. A query
  // of only separators has no tokens and suggests nothing.
  const tokens = suggestionTokens(needles);
  if (tokens.length === 0) return [];
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
  const { cover } = phraseCover(tokens, tokens);
  const cells = { n: 0 };
  let { scored, calls } = scoreSuggestions(candidates, tokens, cover, cells, true, false);
  if (scored.length === 0 && calls === 0 && cells.n < SUGGESTION_CELLS) {
    scored = scoreSuggestions(candidates, tokens, cover, cells, false, true).scored;
  }
  const strong = scored.filter((item) => item.score >= 0.4);
  const pool = strong.length > 0 ? strong : scored;
  return pool.sort((a, b) => b.score - a.score || searchSections.indexOf(a.section) - searchSections.indexOf(b.section)
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

type Hit = { match: Match; entry: Entry; tier: 0 | 1 | 2; kind: Match["matched"]; matchedTokens: string[]; quality: Map<string, number>; source: number };

function rankHits(hits: Hit[], content: string[], searched: Section[]) {
  const bySection = (hit: Hit) => searched.indexOf(hit.match.section);
  const exact = hits.filter((hit) => hit.tier === 0).sort((a, b) => bySection(a) - bySection(b) || a.source - b.source);
  const full = hits.filter((hit) => hit.tier === 1).sort((a, b) => KINDS.indexOf(a.kind) - KINDS.indexOf(b.kind) || bySection(a) - bySection(b) || a.source - b.source);
  const subset = hits.filter((hit) => hit.tier === 2);
  const buckets = content.map((token) => subset.filter((hit) => hit.matchedTokens.includes(token)).sort((a, b) =>
    (a.quality.get(token) ?? 9) - (b.quality.get(token) ?? 9) || b.matchedTokens.length - a.matchedTokens.length
    || KINDS.indexOf(a.kind) - KINDS.indexOf(b.kind) || bySection(a) - bySection(b) || a.source - b.source));
  const interleaved: Hit[] = [];
  const seen = new Set<number>();
  const indexes = buckets.map(() => 0);
  for (;;) {
    let moved = false;
    for (let i = 0; i < buckets.length; i += 1) {
      const group = buckets[i];
      if (!group) continue;
      let idx = indexes[i] ?? 0;
      while (idx < group.length && seen.has(group[idx].source)) idx += 1;
      if (idx < group.length) {
        const hit = group[idx];
        idx += 1;
        seen.add(hit.source);
        interleaved.push(hit);
        moved = true;
      }
      indexes[i] = idx;
    }
    if (!moved) break;
  }
  return [...exact, ...full, ...interleaved];
}

function searchVocabulary(vocabulary: Record<string, unknown>, args: VocabInput, ids: string[]): Record<string, unknown> {
  const section = args.section ?? "starter", search = args.search ?? "";
  const crossSection = section === "starter";
  const searched = crossSection ? searchSections : [section];
  const full = args.detail === "full" || ids.length > 0;
  const needle = normalize(search);
  const query = prepareQuery(needle);
  const { cover, whole } = needle ? phraseCover(query.raw, query.content) : { cover: new Map<string, Set<string>>(), whole: new Set<string>() };
  const hits: Hit[] = [];
  // Record exact ids before the search-text filter. A known id that misses the
  // text stays known; only an id absent from the searched sections is unknown.
  const requested = new Set(ids);
  const exactIds = new Set<string>();
  for (const name of searched) {
    for (const entry of sectionRows(vocabulary, name)) {
      if (requested.has(entry.id)) exactIds.add(entry.id);
      if (requested.size > 0 && !requested.has(entry.id)) continue;
      // A search of only separators normalises to nothing: it matches nothing, not everything.
      const classified = needle
        ? classify(foldFields(searchableFields(name, entry)), entry.id, query, cover, whole, ids.includes(entry.id) || entry.id === search)
        : search ? undefined : { tier: 0, kind: "id", value: null, via: null, matchedTokens: [], quality: new Map<string, number>() } satisfies Classified;
      if (!classified) continue;
      const label = isRecord(entry.row) ? entry.row.label ?? entry.row.name ?? entry.row.display_name
        : name === "providers" || name === "vendors" ? entry.row : undefined;
      const base = {
        section: name, id: entry.id, ...(typeof label === "string" ? { label } : {}),
        ...(classified.via ? { via: classified.via } : {}),
        ...(classified.matchedTokens.length > 0 ? { matched_tokens: classified.matchedTokens } : {}),
      };
      const match: Match = classified.kind === "value"
        ? { ...base, matched: "value", value: classified.value }
        : { ...base, matched: classified.kind };
      hits.push({ match, entry, tier: classified.tier, kind: classified.kind, matchedTokens: classified.matchedTokens,
        quality: classified.quality, source: hits.length });
    }
  }
  const ranked = rankHits(hits, query.content, searched);
  const offset = args.offset ?? 0, limit = args.limit ?? 20;
  const page = ranked.slice(offset, offset + limit);
  const sections = crossSection ? Object.fromEntries(searched.map((name) =>
    [name, selectRows(page.filter(({ match }) => match.section === name).map(({ entry }) => entry), name, full)]))
    : { [section]: selectRows((full ? hits : hits.slice(offset, offset + limit)).map(({ entry }) => entry), section, full) };
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
  if (requested.size > 0) {
    const missing = [...requested].filter((id) => !exactIds.has(id)).sort(compareText);
    if (missing.length > 0) result.unknown_ids = missing;
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
