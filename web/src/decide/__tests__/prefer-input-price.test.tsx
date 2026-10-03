// MODEL-294: Prefer on Budget → Input price blanked the whole page with
// "Cannot read properties of null (reading 'ci')". The fixture is the answer
// production gave on 2026-10-02 to exactly the spec the board sends for that
// click (snap_b40b111c5d85f459): some ranked rows carry a capability interval,
// others carry none.
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import inputPricePreferJson from "../__fixtures__/live-input-price-prefer-full.json";
import { DesignedApp } from "../App";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { Why } from "../components/Why";
import { boardToSpec, sanitizeBoardState } from "../facet-board/model";
import { realBaseSpec } from "../vocabulary";
import { VocabContext, realVocab } from "../vocabulary/context";
import { openGroup } from "./board-helpers";
import { json, realVocabulary, routeFetch, sentSpecs } from "./vocab-fixtures";

const inputPricePrefer = decisionSchema.parse(inputPricePreferJson);
const board = sanitizeBoardState(
  {
    selections: { "offering.price.input": { mode: "prefer", weight: 0.5 } },
    mustOrder: [],
    estate: { providers: [], plans: [], hardware: [] },
  },
  realVocabulary,
);
const preferInputPrice = boardToSpec(
  { ...realBaseSpec(realVocabulary), conds: [] },
  realVocabulary,
  board.selections,
  board.mustOrder,
);
const view = () =>
  mapDecisionToViewModel(inputPricePrefer, preferInputPrice, {
    axis: "task$",
    dismissed: [],
    questions: [],
    benchmarks: realVocab(realVocabulary).benchmarks,
    models: realVocabulary.models,
    providers: realVocabulary.providers,
  });

beforeEach(() => history.replaceState(null, "", "/decide/"));
afterEach(() => vi.unstubAllGlobals());

it("keeps the page and the Why panel up after Prefer on Input price", async () => {
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(inputPricePrefer),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");

  openGroup("Budget");
  const inputPrice = screen.getByText("Input price").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(inputPrice).getByLabelText("Prefer"));

  await waitFor(() =>
    // MODEL-297: lower is better, so Prefer minimises input price.
    expect(sentSpecs(fetch).some((body) => "-offering.price.input" in body.optimize.weights)).toBe(true),
  );
  const why = await screen.findByRole("region", { name: "Why this model" });
  expect(within(why).getByRole("heading", { level: 2 })).toHaveTextContent("Claude Fable 5.1");
  expect(screen.getByRole("region", { name: "Facets" })).toBeInTheDocument();
  expect(screen.queryByRole("alert", { name: "The answer could not be shown" })).not.toBeInTheDocument();
});

it("never calls a row without a capability interval inseparable", () => {
  const e = view().explanation;
  const withInterval = e.feasible.filter((row) => row.capR?.ci != null);
  const withoutInterval = e.feasible.filter((row) => row.capR?.ci == null);
  // The production answer mixes both, which is what the crash needed.
  expect(withInterval.length).toBeGreaterThan(0);
  expect(withoutInterval.length).toBeGreaterThan(0);
  for (const row of withInterval)
    for (const other of e.insep(row)) expect(other.capR?.ci).toEqual(expect.any(Number));
});

it("says 'no interval' for an inseparable row that has none, rather than throwing", () => {
  const decision = view();
  const e = decision.explanation;
  const row = e.feasible.find((candidate) => candidate.capR?.ci != null)!;
  const bare = { ...e.feasible.find((candidate) => candidate !== row)!, capR: null, cap: null };
  const withBare = { ...decision, explanation: { ...e, insep: () => [bare] } };
  render(
    <VocabContext.Provider value={realVocab(realVocabulary)}>
      <Why
        decision={withBare}
        spec={preferInputPrice}
        row={row}
        onRelax={() => undefined}
        onProvenance={() => undefined}
        boardRanked
      />
    </VocabContext.Provider>,
  );
  const note = screen.getByText("Not separable: intervals overlap.").closest<HTMLElement>(".note")!;
  expect(note).toHaveTextContent(`${bare.m.name}: — no interval`);
});
