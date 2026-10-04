import { describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import { lookupVocabulary, vocabularyResponse } from "../src/vocabulary";
import type { VocabInput } from "../src/vocabulary";
import vocabulary from "../../web/src/decide/__fixtures__/vocabulary.json";

const display = {
  ...vocabulary,
  facets: vocabulary.facets.map((row) => row.id === "model.fits_hardware"
    ? { ...row, values: vocabulary.estate.devices.map((value) => ({ value, label: value })) } : row),
};

const searched = ["facets", "domains", "refinements", "benchmarks", "templates", "task_types",
  "estate", "providers", "vendors", "models", "template_categories", "template_tiers"];

describe("vocabulary discovery", () => {
  it("finds prices outside starter", () => {
    const result = lookupVocabulary(display, { search: "price" });
    expect(result).toMatchObject({
      matches: expect.arrayContaining([{ section: "facets", id: "offering.price.input", label: "Input price", matched: "id" }]),
      facets: expect.arrayContaining([expect.objectContaining({ id: "offering.price.input" })]),
      searched,
      next: "next: call decide using these ids; refine from reading",
    });
  });

  it.each(["4090", "RTX 4090", "rtx_4090"])("finds hardware values and estate devices for %s", (search) => {
    const result = lookupVocabulary(display, { search });
    expect(result).toMatchObject({
      matches: expect.arrayContaining([
        { section: "facets", id: "model.fits_hardware", label: "Fits hardware", matched: "value", value: "nvidia_rtx_4090" },
        { section: "estate", id: "nvidia_rtx_4090", matched: "id" },
      ]),
      facets: expect.arrayContaining([expect.objectContaining({
        id: "model.fits_hardware", allowed_values: expect.arrayContaining(["nvidia_rtx_4090", "nvidia_rtx_3090"]),
      })]),
      estate: { providers: [], devices: ["nvidia_rtx_4090"], plans: [] },
    });
  });

  it("finds the chat domain without matching nested Arena domains", () => {
    expect(lookupVocabulary(display, { search: "chat" })).toMatchObject({
      matches: expect.arrayContaining([{ section: "domains", id: "chat_preference", label: "Chat and preference", matched: "id" }]),
      domains: expect.arrayContaining([expect.objectContaining({ id: "chat_preference" })]),
    });
    expect(JSON.stringify(lookupVocabulary(display, { search: "chat" }))).not.toContain('"section":"benchmarks"');
  });

  it("resolves an exact facet id in full detail and normalizes search separators", () => {
    expect(lookupVocabulary(display, { id: "offering.price.input" })).toMatchObject({
      matches: [{ section: "facets", id: "offering.price.input", label: "Input price", matched: "id" }],
      facets: [expect.objectContaining({ id: "offering.price.input", operators: ["=", "!=", "<", "<=", ">", ">=", "between", "known"] })],
    });
    expect(lookupVocabulary(display, { search: "Offering.Price.Input" })).toMatchObject({
      matches: expect.arrayContaining([{ section: "facets", id: "offering.price.input", label: "Input price", matched: "id" }]),
    });
    expect(lookupVocabulary(display, { id: "Offering.Price.Input" })).toMatchObject({ matches: [], total: 0 });
  });

  it("explains misses and suggests ids across sections", () => {
    expect(lookupVocabulary(display, { search: "zzzqqq" })).toMatchObject({
      starter: [], matches: [], total: 0, searched,
      message: expect.stringContaining("id, label, definition or values"),
      suggestions: expect.any(Array), next: expect.stringContaining("retry"),
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
    });
    expect(lookupVocabulary(display, { search: "pirce" })).toMatchObject({
      suggestions: expect.arrayContaining([expect.objectContaining({ section: "facets", id: "offering.price.input" })]),
    });
    expect(lookupVocabulary(display, { id: "offering.price.inptu" })).toMatchObject({
      suggestions: expect.arrayContaining([{ section: "facets", id: "offering.price.input" }]),
    });
    expect(lookupVocabulary(display, { section: "domains", search: "price" })).toMatchObject({
      domains: [], matches: [], searched: ["domains"],
      suggestions: expect.arrayContaining([{ section: "facets", id: "offering.price.input" }]),
    });
  });

  it("ranks fields, pages full cross-section results and intersects exact ids", () => {
    const source = {
      facets: [
        { id: "value_hit", values: [{ value: "rtx", label: "RTX 4090" }] },
        { id: "definition_hit", definition: "Uses rtx" },
        { id: "label_hit", label: "RTX" },
        { id: "id.rtx" },
        { id: "rtx" },
      ],
      domains: [{ id: "domain_rtx" }], templates: [{ id: "template", purpose: "rtx" }],
      estate: { plans: [{ id: "plus", provider: "openai", name: "ChatGPT Plus" }] },
    };
    const result = lookupVocabulary(source, { search: "rtx" });
    expect(result).toMatchObject({ matches: [
      { section: "facets", id: "rtx", matched: "id" },
      { section: "facets", id: "id.rtx", matched: "id" },
      { section: "domains", id: "domain_rtx", matched: "id" },
      { section: "facets", id: "label_hit", label: "RTX", matched: "label" },
      { section: "facets", id: "definition_hit", matched: "definition" },
      { section: "templates", id: "template", matched: "definition" },
      { section: "facets", id: "value_hit", matched: "value", value: "rtx" },
    ] });
    expect(lookupVocabulary(source, { search: "rtx", detail: "full", offset: 1, limit: 2 })).toMatchObject({
      matches: [{ id: "id.rtx" }, { id: "domain_rtx" }], total: 7,
      facets: [source.facets[3]], domains: source.domains,
    });
    expect(lookupVocabulary(source, { search: "rtx", ids: ["label_hit", "plus"] })).toMatchObject({ matches: [{ id: "label_hit" }] });
    expect(lookupVocabulary(source, { search: "plus openai" })).toMatchObject({ estate: { plans: [{ id: "plus", name: "ChatGPT Plus" }] } });
    expect(lookupVocabulary(source, { section: "estate", search: "chat" })).toMatchObject({ estate: { plans: [{ id: "plus", name: "ChatGPT Plus" }] } });
  });

  it("keeps a cross-section page under the envelope token budget", () => {
    const selected = lookupVocabulary(display, { search: "a" });
    const body = vocabularyResponse(selected.starter, { search: "a" }, selected);
    expect(body).toMatchObject({ matches: expect.any(Array), total: expect.any(Number) });
    expect(JSON.stringify({ origin: "https://api.modelspec.dev/v1/vocabulary?search=a", status: 200, body }).length / 4)
      .toBeLessThanOrEqual(4000);
  });

  it("returns the same lookup bodies as Python for the shared vocabulary", () => {
    const cases = [
      {}, { section: "starter" }, { search: "price" }, { section: "starter", search: "4090" },
      { search: "chat" }, { id: "offering.price.input" }, { search: "RTX 4090" },
      { search: "Offering.Price.Input" }, { search: "zzzqqq" }, { search: "pirce" },
      { id: "offering.price.inptu" }, { section: "domains", search: "price" },
      { section: "facets", search: "CONTEXT" }, { section: "estate", search: "4090" },
      { search: "price", ids: ["offering.price.input", "chat_preference"] },
      { search: "a", offset: 20, limit: 7 }, { search: "a", detail: "full", offset: 20, limit: 2 },
      { ids: display.facets.map(({ id }) => id), offset: 20, limit: 3 },
      { ids: ["not_a_facet", "offering.price.inptu"] },
    ] satisfies VocabInput[];
    const root = new URL("../../", import.meta.url).pathname;
    const output = execFileSync("python3", ["-c", `
import json, sys
from api.worker.src.display_vocabulary import lookup
request = json.load(sys.stdin)
results = []
for args in request["cases"]:
    if "id" in args:
        args["ids"] = [*args.get("ids", []), args.pop("id")]
    results.append(lookup(request["vocabulary"], **args))
json.dump(results, sys.stdout, ensure_ascii=False)
`], { cwd: root, env: { ...process.env, PYTHONPATH: root }, input: JSON.stringify({ vocabulary: display, cases }), encoding: "utf8" });
    expect(cases.map((args) => lookupVocabulary(display, args))).toEqual(JSON.parse(output));
  }, 20_000);
});

const facets = [
  { id: "x", label: "Long Context", definition: "First sentence. More details.", value_type: "number", operators: [">="] },
  { id: "model.context", label: "Window", value_type: "number" },
  { id: "cost", label: "Price", value_type: "number" },
];

function lookupSection(source: Record<string, unknown>, args: VocabInput) {
  return lookupVocabulary(source, args)[args.section ?? "starter"];
}

describe("compact vocabulary", () => {
  it("keeps a mapping id equal to its section name inside the section", () => {
    expect(lookupVocabulary({ providers: { providers: "Provider Name" } }, { section: "providers" })).toEqual({
      providers: { providers: "Provider Name" }, next: "next: call decide using these ids; refine from reading",
    });
  });

  it("searches ids and labels, intersects ids and returns details on demand", () => {
    expect(lookupSection({ facets }, { section: "facets", search: "CONTEXT" })).toEqual([
      { id: "x", label: "Long Context", definition: "First sentence.", value_type: "number" }, facets[1],
    ]);
    expect(lookupSection({ facets }, { section: "facets", search: "CONTEXT", id: "x", ids: ["cost"] })).toEqual([facets[0]]);
    expect(lookupSection({ facets }, { section: "facets", ids: ["missing"] })).toEqual([]);
    expect(lookupSection({ facets }, { section: "facets", detail: "full", limit: 1 })).toEqual(facets);
    expect(lookupSection({ facets }, { section: "facets", limit: 1, offset: 1 })).toEqual([facets[1]]);
    expect(lookupSection({ facets }, { section: "facets", offset: 3 })).toEqual([]);
  });

  it("returns only id and display name for models and providers", () => {
    expect(lookupSection({ models: { "lab/id": { display_name: "Friendly Model", lab: "lab" } } }, { section: "models", search: "FRIENDLY" })).toEqual({ "lab/id": { display_name: "Friendly Model" } });
    expect(lookupSection({ providers: { id: "Provider Name" } }, { section: "providers", search: "NAME" })).toEqual({ id: "Provider Name" });
  });

  it("derives starter from spec usage rather than a fixed list", () => {
    expect(lookupSection({ facets, templates: [{ spec: { where: ["model.context >= 4000"] } }] }, {})).toEqual([facets[1]]);
    expect(lookupSection({ facets, templates: [{ spec: { where: ["model.context_extra >= 4000"] } }] }, {})).toEqual([]);
  });

  it("publishes allowed values even with no observed values", () => {
    expect(lookupSection({ facets: [{ id: "e", value_type: "enum", values: [], allowed_values: ["a", "b"] }] }, { section: "facets" })).toEqual([{ id: "e", value_type: "enum", allowed_values: ["a", "b"] }]);
  });

  it("keeps which way is better on a compact number facet (MODEL-297)", () => {
    expect(lookupSection({ facets: [{ id: "offering.price.input", label: "Input price", value_type: "number", better: "lower", known: 3 }] }, { section: "facets" }))
      .toEqual([{ id: "offering.price.input", label: "Input price", value_type: "number", better: "lower" }]);
  });

  it("keeps every default section under the chars/4 proxy budget", () => {
    for (const section of ["starter", "facets", "benchmarks", "domains", "providers", "models", "task_types", "coverage", "templates", "refinements", "estate", "vendors", "template_categories", "template_tiers"] as const) {
      const body = lookupSection(vocabulary, { section });
      const response = vocabularyResponse(body, { section });
      expect(response.next).toMatch(/^next: call decide/);
      expect(JSON.stringify({ origin: "https://modelspec.dev/api/decision/vocabulary.json", status: 200, body: response }).length / 4).toBeLessThanOrEqual(4000);
    }
  });

  it("gives an empty starter lookup a ready-to-send Spec and the next call", () => {
    expect(vocabularyResponse([], {})).toEqual({ starter: [],
      spec: { spec_version: 1, optimize: { min: "offering.cost_per_task" } },
      next: "next: call decide with this; refine from reading" });
  });
});
