import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { act, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import { DesignedApp } from "../App";
import { decisionSchema } from "../adapter";
import { vocabularySchema } from "../vocabulary";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";

const dir = resolve(process.env.MODELSPEC_CORPUS_DIR ?? join(__dirname, "../__corpus__"));
const read = (file: string): unknown => JSON.parse(readFileSync(join(dir, file), "utf8"));
const index = existsSync(join(dir, "index.json")) ? z.object({
  cases: z.array(z.object({ id: z.string(), snapshot: z.string(), http: z.number(), file: z.string(), generated: z.boolean().default(false) })),
  vocabularies: z.record(z.string(), z.string()),
}).parse(read("index.json")) : null;
// Match corpus.spec.ts: hand-written cases and every template's full answer.
const drawn = (index?.cases ?? []).filter((row) =>
  row.http === 200 && (!row.generated || /^template-.*-full$/.test(row.id)),
);

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe.skipIf(index === null)("corpus rendering", () => {
  it.each(drawn)("draws $id with the opening board's weights", async (row) => {
    const vocabularyFile = index?.vocabularies[row.snapshot];
    if (!vocabularyFile) throw new Error(`No vocabulary for ${row.snapshot}`);
    const vocabulary = vocabularySchema.parse(read(vocabularyFile));
    const decision = decisionSchema.parse(read(row.file));
    const fetch = routeFetch({ vocabulary: () => json(vocabulary), decide: () => json(decision) });
    vi.useFakeTimers();
    vi.stubGlobal("fetch", fetch);
    render(<DesignedApp />);
    for (let i = 0; i < 4; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
    expect(screen.getByLabelText("Facet board answer")).toBeInTheDocument();
    expect(screen.queryByRole("alert", { name: "The answer could not be shown" })).toBeNull();
    expect(screen.queryByText(/invalid_response|Decision unavailable/)).toBeNull();
    expect(sentSpecs(fetch)[0].optimize.weights).not.toEqual({});
    if (vocabulary.templates?.some((template) => template.id === "assistant-balanced" && template.available))
      expect(sentSpecs(fetch)[0].optimize.weights).toEqual({ chat_preference: 0.6, "-offering.cost_per_task": 0.4 });
  });
});
