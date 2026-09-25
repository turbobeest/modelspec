// No raw enum token reaches the page (MODEL-153). On 2026-09-25 the
// open-weights shortlist card read `permitted_with_conditions`. Every enum
// value the page shows comes from the vocabulary's `label`, which the
// registry's `value_labels` supply.
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { decisionSchema } from "../adapter/contract";
import { registerValueLabels, renderContractCondition } from "../adapter/condition-label";
import { encodeSpec } from "../state/spec";
import type { Spec } from "../engine/types";
import { EMPTY_DECISIONS, EMPTY_SPECS } from "./empty-specs";
import { json, realVocabulary, routeFetch, smallVocabulary } from "./vocab-fixtures";

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

/** Every token-shaped enum value the vocabulary publishes: snake_case or kebab-case. */
const TOKENS = [
  ...new Set(
    realVocabulary.facets.flatMap((row) =>
      (row.values ?? [])
        .map((item) => item.value)
        .filter((value): value is string => typeof value === "string" && /[_-]/.test(value)),
    ),
  ),
];

/** Tokens shown as text, node by node: `textContent` would run adjacent elements together. */
function rawTokensShown(): string[] {
  const texts: string[] = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) texts.push(node.nodeValue ?? "");
  return TOKENS.filter((token) => {
    const shown = new RegExp(
      `(^|[^A-Za-z0-9_/.-])${token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}([^A-Za-z0-9_/.-]|$)`,
    );
    return texts.some((text) => shown.test(text));
  });
}

/** The fixture decision, with the licence facts the live open-weights card showed raw. */
function withLicences() {
  const raw = structuredClone(fixtureJson) as typeof fixtureJson;
  for (const candidate of raw.top) {
    const openness = candidate.facts.find((fact) => fact.facet === "model.weights_openness");
    if (openness)
      candidate.facts.push({
        ...openness,
        facet: "licence.commercial_use",
        value: "permitted_with_conditions",
      } as (typeof candidate.facts)[number]);
  }
  return decisionSchema.parse(raw);
}

it("publishes the tokens this test looks for", () => {
  expect(TOKENS).toEqual(
    expect.arrayContaining(["permitted_with_conditions", "open_weights", "text-generator"]),
  );
});

it("labels enum values in conditions from the vocabulary", () => {
  registerValueLabels(realVocabulary.facets);
  expect(
    renderContractCondition("licence.commercial_use in {permitted, permitted_with_conditions}"),
  ).toBe("Commercial use: Permitted or Permitted with conditions");
  expect(renderContractCondition("model.weights_openness = open_weights")).toBe(
    "Weights: Open weights",
  );
});

/** An open-weights question on the fixture's `quality` benchmark. */
const OPEN: Spec = {
  task: "Open weights you can host",
  tokIn: 40000,
  tokOut: 4000,
  bench: "quality",
  w: { cap: 1, cost: 0, speed: 0 },
  conds: [
    { f: "type", v: "llm" },
    { f: "active" },
    { f: "open", v: true },
    { f: "commercial" },
  ],
};

it.each([
  ["an open-weights shortlist", smallVocabulary, () => withLicences(), OPEN, "Best open weights"],
  ["an empty open-weights answer (Q17)", realVocabulary, () => EMPTY_DECISIONS.q17, EMPTY_SPECS.q17,
    "What this question needed"],
])("renders no raw enum token for %s", async (_name, vocabulary, decision, shared, landmark) => {
  vi.stubGlobal(
    "fetch",
    routeFetch({ vocabulary: () => json(vocabulary), decide: () => json(decision()) }),
  );
  history.replaceState(null, "", "/" + encodeSpec(shared, "task$"));
  render(<App />);
  await screen.findByText(landmark);
  // Every row selected in turn, so the Why panel shows each model's facts too.
  for (const card of document.querySelectorAll<HTMLElement>(".result-card")) {
    fireEvent.click(card);
    expect(rawTokensShown()).toEqual([]);
  }
  expect(rawTokensShown()).toEqual([]);
});

it("shows the licence label on the open-weights card", async () => {
  vi.stubGlobal(
    "fetch",
    routeFetch({ vocabulary: () => json(smallVocabulary), decide: () => json(withLicences()) }),
  );
  history.replaceState(null, "", "/" + encodeSpec(OPEN, "task$"));
  render(<App />);
  const card = (await screen.findByText("Best open weights")).closest(".result-card")!;
  expect(card).toHaveTextContent("Permitted with conditions");
});

it("labels the value a near miss had (Q10: a decider, not `decider`)", async () => {
  const { mapDecisionToViewModel } = await import("../adapter/view-model");
  registerValueLabels(realVocabulary.facets.map((row) =>
    row.id === "model.class"
      ? { ...row, values: [...(row.values ?? []), { value: "decider", count: 1, label: "Decision model" }] }
      : row,
  ));
  const view = mapDecisionToViewModel(EMPTY_DECISIONS.q10, EMPTY_SPECS.q10, {
    axis: "task$",
    dismissed: [],
    providers: realVocabulary.providers,
  });
  const whys = view.nearMisses.map((miss) => miss.why);
  expect(whys.length).toBeGreaterThan(0);
  for (const why of whys) expect(why).not.toMatch(/: decider$|_/);
  expect(whys.some((why) => why.includes("/ 1M tokens"))).toBe(true);
});
