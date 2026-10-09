import { describe, expect, it } from "vitest";
import { execFileSync } from "node:child_process";
import { lookupVocabulary, takeSearchWork, vocabInput, vocabularyResponse } from "../src/vocabulary";
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
      estate: { providers: [], devices: expect.arrayContaining(["nvidia_rtx_4090"]), plans: [] },
    });
    if (search === "4090") expect(result.estate).toMatchObject({ devices: ["nvidia_rtx_4090"] });
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

  it("names the facet on a value suggestion, and a separator-only search matches nothing", () => {
    const source = { facets: [{ id: "facet", allowed_values: ["violet"] }], domains: [{ id: "domain", name: "Lilac" }] };
    const miss = lookupVocabulary(source, { section: "domains", search: "violett" });
    expect((miss.suggestions as unknown[])[0]).toEqual({ section: "facets", id: "facet", value: "violet" });
    expect(miss.message).toContain("facet (value violet)");
    expect(lookupVocabulary(source, { search: "." })).toMatchObject({ matches: [], total: 0 });
    const flag = lookupVocabulary({ facets: [{ id: "flag", allowed_values: [true, false] }] }, { search: "ture" });
    expect((flag.suggestions as unknown[])[0]).toEqual({ section: "facets", id: "flag", value: true });
    expect(flag.message).toContain("flag (value true)");
    expect(vocabInput.safeParse({ search: "x".repeat(129) }).success).toBe(false);
    expect(vocabInput.safeParse({ ids: ["x".repeat(129)] }).success).toBe(false);
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
      { search: "nvidia rtx 4091" }, { search: "flase" }, { search: "ture" }, { section: "domains", search: "ture" }, { search: "." }, { search: "_./", section: "facets" },
      { search: "eu residency training commercial use azure vertex" }, { search: "rtx 5090" },
      { search: "fits_hardware", detail: "full" },
      { section: "estate", search: "m4 macbook 24", detail: "full", limit: 20 },
      { search: "macbook m4" }, { search: "code review defect" }, { search: "price.input" },
      { section: "domains", search: "software" }, { search: "quantization" }, { search: "quantisation" },
      { search: "4-bit" }, { search: "memory" }, { section: "facets", search: "residency" },
      { section: "estate", search: "mac" }, { section: "benchmarks", search: "quantization" },
      { search: "software engineering coding" },
    ] satisfies VocabInput[];
    expect(cases.map((args) => lookupVocabulary(display, args))).toEqual(python(display, cases));
    const emojiSource = { facets: [{ id: "mood", label: "😀 smile" }] };
    const emoji = lookupVocabulary(emojiSource, { search: "😀 zzz" });
    expect(emoji.total).toBe(0);
    expect(emoji.suggestions).toEqual(expect.any(Array));
    expect(emoji).toEqual(python(emojiSource, [{ search: "😀 zzz" }])[0]);
  }, 20_000);

  it("does no more match work for a repeated token than for that token once", () => {
    const pad = (i: number) => String(i).padStart(4, "0");
    const source = {
      facets: Array.from({ length: 60 }, (_, i) => ({ id: `offering.synthetic.metric_${pad(i)}`,
        label: `Synthetic metric number ${pad(i)}`, allowed_values: [0, 1, 2].map((j) => `value_${pad(i)}_${j}`) })),
      models: Object.fromEntries(Array.from({ length: 2000 }, (_, i) => [`lab${String(i % 40).padStart(2, "0")}/model-family-${pad(i)}-instruct`,
        { display_name: `Model Family ${pad(i)} Instruct` }])),
      estate: { providers: [], devices: Array.from({ length: 200 }, (_, i) => `vendor_accelerator_${pad(i)}_96gb`), plans: [] },
    };
    const measure = (search: string) => {
      takeSearchWork();
      const result = lookupVocabulary(source, { search });
      return { total: result.total, ...takeSearchWork() };
    };
    const one = measure("ab");
    const many = measure("ab ".repeat(42));
    expect(many.total).toBe(one.total);
    expect(one.matchCalls).toBeGreaterThan(0);
    expect(many.matchCalls).toBeLessThanOrEqual(one.matchCalls);
    expect(many.foldCalls).toBeLessThanOrEqual(one.foldCalls);
    const eight = Array.from({ length: 8 }, (_, i) => `q${i}`).join(" ");
    const capped = measure(eight);
    const extra = measure(`${eight} q8`);
    expect(capped.matchCalls).toBeGreaterThan(0);
    expect(extra.matchCalls).toBeLessThanOrEqual(capped.matchCalls);
  });

  it("puts a needed id on the first page of each turn-capped vocab call (MODEL-355)", () => {
    const ids = (result: Record<string, unknown>) => {
      const found = new Set<string>();
      const lists = [result.matches, result.suggestions, result.facets, result.domains];
      for (const rows of lists) {
        if (!Array.isArray(rows)) continue;
        for (const row of rows) {
          if (typeof row === "string") found.add(row);
          else if (row && typeof row === "object" && "id" in row && typeof row.id === "string") {
            found.add(row.id);
            if ("value" in row && typeof row.value === "string") found.add(row.value);
            if ("allowed_values" in row && Array.isArray(row.allowed_values)) {
              for (const value of row.allowed_values) if (typeof value === "string") found.add(value);
            }
            if ("values" in row && Array.isArray(row.values)) {
              for (const value of row.values) {
                if (typeof value === "string") found.add(value);
                else if (value && typeof value === "object" && "value" in value && typeof value.value === "string") found.add(value.value);
              }
            }
          }
        }
      }
      const estate = result.estate;
      if (estate && typeof estate === "object") {
        for (const group of Object.values(estate)) {
          if (!Array.isArray(group)) continue;
          for (const row of group) {
            if (typeof row === "string") found.add(row);
            else if (row && typeof row === "object" && "id" in row && typeof row.id === "string") found.add(row.id);
          }
        }
      }
      return found;
    };
    expect(lookupVocabulary(display, { section: "starter" }).matches).toBeUndefined();
    const rtx = ids(lookupVocabulary(display, { search: "rtx 5090" }));
    expect(rtx.has("nvidia_rtx_5090")).toBe(true);
    expect(rtx.has("model.fits_hardware")).toBe(true);
    const dual = ids(lookupVocabulary(display, { search: "fits_hardware", detail: "full" }));
    expect(dual.has("model.fits_hardware")).toBe(true);
    expect(dual.has("nvidia_rtx_4090")).toBe(true);
    const budget = ids(lookupVocabulary(display, { search: "eu residency training commercial use azure vertex", limit: 20 }));
    for (const id of ["offering.region", "offering.data.trains_on_customer_data", "licence.commercial_use"]) {
      expect(budget.has(id)).toBe(true);
    }
    expect(budget.has("azure-ai-foundry") || budget.has("google-vertex-ai")).toBe(true);
    const estate = ids(lookupVocabulary(display, { section: "estate", search: "m4 macbook 24", detail: "full", limit: 20 }));
    expect([...estate].some((id) => id.startsWith("apple_m4"))).toBe(true);
    expect(ids(lookupVocabulary(display, { search: "macbook m4" })).has("model.fits_hardware")).toBe(true);
    expect(ids(lookupVocabulary(display, { search: "code review defect" })).has("software_engineering")).toBe(true);
    expect(ids(lookupVocabulary(display, { search: "price.input" })).has("offering.price.input")).toBe(true);
    const software = lookupVocabulary(display, { section: "domains", search: "software" });
    expect(software.total).toBe(1);
    expect(ids(software).has("software_engineering")).toBe(true);
    expect(ids(lookupVocabulary(display, { search: "software engineering coding" })).has("software_engineering")).toBe(true);
  });

  it("stops suggestion scoring at the same cell budget as Python on a catalogue-sized vocabulary", () => {
    const pad = (i: number) => String(i).padStart(4, "0");
    const source = {
      facets: Array.from({ length: 60 }, (_, i) => ({ id: `offering.synthetic.metric_${pad(i)}`,
        label: `Synthetic metric number ${pad(i)}`, allowed_values: [0, 1, 2].map((j) => `value_${pad(i)}_${j}`) })),
      models: Object.fromEntries(Array.from({ length: 1500 }, (_, i) => [`lab${String(i % 40).padStart(2, "0")}/model-family-${pad(i)}-instruct`,
        { display_name: `Model Family ${pad(i)} Instruct` }])),
      estate: { providers: [], devices: Array.from({ length: 200 }, (_, i) => `vendor_accelerator_${pad(i)}_96gb`), plans: [] },
    };
    const needles = Array.from({ length: 100 }, (_, i) => `zz${i}-qqqqvvvv-xyzwabcd`);
    const cases = [{ search: needles[0] }, { ids: needles }, { search: "q".repeat(128) }, { search: "instrct" }] satisfies VocabInput[];
    expect(cases.map((args) => lookupVocabulary(source, args))).toEqual(python(source, cases));
  }, 20_000);
});

function python(vocabulary: unknown, cases: VocabInput[]) {
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
`], { cwd: root, env: { ...process.env, PYTHONPATH: root }, input: JSON.stringify({ vocabulary, cases }), encoding: "utf8" });
  return JSON.parse(output);
}

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
