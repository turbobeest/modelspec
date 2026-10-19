import { render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import tiedJson from "../__fixtures__/compact-tied-full.json";
import separatedJson from "../__fixtures__/compact-full.json";
import bandsJson from "../__fixtures__/compact-bands-full.json";
import vocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import type { Spec } from "../engine/types";
import { Field } from "../components/Field";
import { bestNowLine, leadingModels } from "../facet-board/leading";
import { realBaseSpec, vocabularySchema } from "../vocabulary";

// MODEL-325: the counter names what is best for the board's weights, so a
// template that only changes Prefers still visibly changes the first screen.
const vocabulary = vocabularySchema.parse(vocabularyJson);
const ranked: Spec = { ...realBaseSpec(vocabulary), bench: "quality", domain: undefined, basis: undefined, boardWeights: { software_engineering: 0.78 } };
const unranked: Spec = { ...realBaseSpec(vocabulary), boardWeights: {} };
const models = Object.fromEntries(["alpha", "beta", "gamma", "delta", "strong", "steady", "cheap", "weak", "unproven"].map((id) => [
  `lab/${id}`,
  { display_name: id.charAt(0).toUpperCase() + id.slice(1), lab: "lab", lab_name: "Lab" },
]));
const view = (json: unknown, spec = ranked) =>
  mapDecisionToViewModel(decisionSchema.parse(json), spec, { axis: "task$", dismissed: [], models });
const counter = (json: unknown, spec = ranked) => {
  render(<Field decision={view(json, spec)} spec={spec} onAdd={vi.fn()} onDismiss={vi.fn()} showQuestions={false} boardOnly vocabulary={vocabulary} />);
  return screen.getByRole("region", { name: "Narrowing" });
};

it("reads the leading models from the bands, else from the answer", () => {
  expect(leadingModels(view(bandsJson))).toEqual(["lab/steady", "lab/cheap"]);
  expect(leadingModels(view(tiedJson))).toEqual(["lab/alpha", "lab/gamma"]);
  expect(leadingModels(view(separatedJson))).toEqual(["lab/alpha"]);
  expect(leadingModels({ ...view(separatedJson), answer: null, bands: null })).toBeNull();
});

it("names a separated leader or no leader, and omits tied groups", () => {
  expect(bestNowLine(view(separatedJson), true)).toBe("Best now: Alpha");
  expect(bestNowLine(view(tiedJson), true)).toBeNull();
  const decision = view(bandsJson);
  const bands = decision.bands;
  if (!bands?.best[0]) throw new Error("Expected a best band in the fixture");
  const five = { ...decision, bands: { ...bands, best: ["steady", "cheap", "strong", "weak", "unproven"].map((id) => ({ ...bands.best[0], model: `lab/${id}` })) } };
  expect(bestNowLine(five, true)).toBeNull();
  expect(bestNowLine({ ...decision, answer: null, bands: { ...bands, best: [] } }, true)).toBe("Best now: none has enough evidence yet");
  expect(bestNowLine(decision, false)).toBeNull();
});

it("counts the whole tied group without a star or best-now headline", () => {
  const narrowing = counter(tiedJson);
  expect([...narrowing.querySelectorAll(".narrowing-number")].map((node) => node.textContent)).toEqual(["3", "0", "1", "2"]);
  expect(within(narrowing).getByText("best for your weights")).toBeInTheDocument();
  expect(narrowing).not.toHaveTextContent("★");
  expect(narrowing.querySelector(".narrowing-best")).toBeNull();
  expect(within(narrowing).getByRole("status")).toHaveTextContent("3 qualify · 0 may qualify · 1 out · 2 best for your weights");
});

it("keeps the star and best-now headline for a separated leader", () => {
  const narrowing = counter(separatedJson);
  expect(within(narrowing).getByText("★ best for your weights")).toBeInTheDocument();
  expect(narrowing.querySelector(".narrowing-best")).toHaveTextContent("Best now: Alpha");
});

it("shows a dash and no best-now line while nothing is ranked", () => {
  const narrowing = counter(tiedJson, unranked);
  expect([...narrowing.querySelectorAll(".narrowing-number")].map((node) => node.textContent)).toEqual(["3", "0", "1", "—"]);
  expect(narrowing.querySelector(".narrowing-best")).toBeNull();
  expect(within(narrowing).getByRole("status")).toHaveTextContent(/^3 qualify · 0 may qualify · 1 out$/);
});
