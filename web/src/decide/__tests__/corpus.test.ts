import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { decisionSchema } from "../adapter/contract";
import { vocabularySchema } from "../vocabulary";

// MODEL-203: every decision in the spec corpus (tests/corpus) parses with the
// page's schema. `python -m tests.corpus decisions --out DIR` writes them from
// the engine; the site build does that before this suite, and the post-deploy
// smoke points MODELSPEC_CORPUS_DIR at what api.modelspec.dev answered. This is
// the guard for #361: a field the page parses strictly and the engine sends as
// null fails here, on the pull request, not on the live page.
const dir = resolve(process.env.MODELSPEC_CORPUS_DIR ?? join(__dirname, "../__corpus__"));
const required = process.env.MODELSPEC_CORPUS_REQUIRED === "1";

interface IndexRow {
  id: string;
  intent: string;
  snapshot: string;
  http: number;
  file: string;
}
interface CorpusIndex {
  cases: IndexRow[];
  vocabularies: Record<string, string>;
}

const read = (file: string): unknown => JSON.parse(readFileSync(join(dir, file), "utf8"));
const index: CorpusIndex | null = existsSync(join(dir, "index.json"))
  ? (read("index.json") as CorpusIndex)
  : null;

it("has the corpus decisions to check", () => {
  if (!required && index === null) return;
  expect(index, `no corpus at ${dir}; run python -m tests.corpus decisions --out ${dir}`).not.toBeNull();
  expect(index!.cases.length).toBeGreaterThan(0);
});

const answered = index?.cases.filter((row) => row.http === 200) ?? [];
const refused = index?.cases.filter((row) => row.http !== 200) ?? [];

describe.skipIf(answered.length === 0)("every answered corpus spec", () => {
  it.each(answered.map((row) => [row.id, row] as const))("%s parses as a decision", (_id, row) => {
    const parsed = decisionSchema.safeParse(read(row.file));
    const issues = parsed.success ? [] : parsed.error.issues.slice(0, 5);
    expect(issues, `${row.intent}\n${JSON.stringify(issues, null, 1)}`).toEqual([]);
  });
});

describe.skipIf(refused.length === 0)("every refused corpus spec", () => {
  // hosted.ts reads `error.code` (or the 503's bare string) to say why.
  it.each(refused.map((row) => [row.id, row] as const))("%s carries an error code", (_id, row) => {
    const body = read(row.file) as { error?: unknown };
    const code = typeof body.error === "string" ? body.error : (body.error as { code?: unknown })?.code;
    expect(typeof code, row.intent).toBe("string");
  });
});

const vocabularies = Object.entries(index?.vocabularies ?? {});

describe.skipIf(vocabularies.length === 0)("every corpus snapshot's vocabulary", () => {
  it.each(vocabularies)("%s parses as the page's vocabulary", (_snapshot, file) => {
    const parsed = vocabularySchema.safeParse(read(file));
    const issues = parsed.success ? [] : parsed.error.issues.slice(0, 5);
    expect(issues, JSON.stringify(issues, null, 1)).toEqual([]);
  });
});
