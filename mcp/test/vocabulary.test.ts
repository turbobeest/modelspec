import { describe, expect, it } from "vitest";
import { lookupVocabulary } from "../src/vocabulary";
import vocabulary from "../../web/src/decide/__fixtures__/vocabulary.json";

const facets = [
  { id: "x", label: "Long Context", definition: "First sentence. More details.", value_type: "number", operators: [">="] },
  { id: "model.context", label: "Window", value_type: "number" },
  { id: "cost", label: "Price", value_type: "number" },
];

describe("compact vocabulary", () => {
  it("searches ids and labels, intersects ids and returns details on demand", () => {
    expect(lookupVocabulary({ facets }, { section: "facets", search: "CONTEXT" })).toEqual([
      { id: "x", label: "Long Context", definition: "First sentence.", value_type: "number" }, facets[1],
    ]);
    expect(lookupVocabulary({ facets }, { section: "facets", search: "CONTEXT", id: "x", ids: ["cost"] })).toEqual([facets[0]]);
    expect(lookupVocabulary({ facets }, { section: "facets", ids: ["missing"] })).toEqual([]);
    expect(lookupVocabulary({ facets }, { section: "facets", detail: "full", limit: 1 })).toEqual(facets);
    expect(lookupVocabulary({ facets }, { section: "facets", limit: 1, offset: 1 })).toEqual([facets[1]]);
    expect(lookupVocabulary({ facets }, { section: "facets", offset: 3 })).toEqual([]);
  });

  it("returns only id and display name for models and providers", () => {
    expect(lookupVocabulary({ models: { "lab/id": { display_name: "Friendly Model", lab: "lab" } } }, { section: "models", search: "FRIENDLY" })).toEqual({ "lab/id": { display_name: "Friendly Model" } });
    expect(lookupVocabulary({ providers: { id: "Provider Name" } }, { section: "providers", search: "NAME" })).toEqual({ id: "Provider Name" });
  });

  it("derives starter from spec usage rather than a fixed list", () => {
    expect(lookupVocabulary({ facets, templates: [{ spec: { where: ["model.context >= 4000"] } }] }, {})).toEqual([facets[1]]);
    expect(lookupVocabulary({ facets, templates: [{ spec: { where: ["model.context_extra >= 4000"] } }] }, {})).toEqual([]);
  });

  it("publishes allowed values even with no observed values", () => {
    expect(lookupVocabulary({ facets: [{ id: "e", value_type: "enum", values: [], allowed_values: ["a", "b"] }] }, { section: "facets" })).toEqual([{ id: "e", value_type: "enum", allowed_values: ["a", "b"] }]);
  });

  it("keeps which way is better on a compact number facet (MODEL-297)", () => {
    expect(lookupVocabulary({ facets: [{ id: "offering.price.input", label: "Input price", value_type: "number", better: "lower", known: 3 }] }, { section: "facets" }))
      .toEqual([{ id: "offering.price.input", label: "Input price", value_type: "number", better: "lower" }]);
  });

  it("keeps every default section under the chars/4 proxy budget", () => {
    for (const section of ["starter", "facets", "benchmarks", "domains", "providers", "models", "task_types", "coverage", "templates", "refinements", "estate", "vendors", "template_categories", "template_tiers"] as const) {
      const body = lookupVocabulary(vocabulary, { section });
      expect(JSON.stringify({ origin: "https://modelspec.dev/api/decision/vocabulary.json", status: 200, body }).length / 4).toBeLessThanOrEqual(4000);
    }
  });
});
