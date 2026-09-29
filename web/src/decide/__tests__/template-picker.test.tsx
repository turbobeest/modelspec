import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import { toBoardDecisionSpec } from "../facet-board/model";
import { realBaseSpec, vocabularySchema } from "../vocabulary";
import type { Vocabulary } from "../vocabulary";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { realVocabulary } from "./vocab-fixtures";

const emptyEstate = { providers: [], plans: [], hardware: [] };
const refinements = vocabularySchema.parse(refinementVocabularyJson).refinements;

function board(vocabulary: Vocabulary = realVocabulary) {
  const onSpec = vi.fn();
  const onCanvasAxes = vi.fn();
  render(
    <FacetBoard
      vocabulary={vocabulary}
      spec={realBaseSpec(vocabulary)}
      onSpec={onSpec}
      estate={emptyEstate}
      onEstate={vi.fn()}
      onCanvasAxes={onCanvasAxes}
    />,
  );
  return { onSpec, onCanvasAxes, bar: () => screen.getByRole("button", { name: /Start from a template/ }) };
}

it("collapses to a one-line bar and expands again", () => {
  const { bar } = board();
  expect(bar()).toHaveAttribute("aria-expanded", "true");
  const panel = document.getElementById(bar().getAttribute("aria-controls")!)!;
  expect(panel).toBeVisible();

  fireEvent.click(bar());
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(panel).not.toBeVisible();
  expect(screen.queryByRole("button", { name: /^Coding · Budget:/ })).not.toBeInTheDocument();
  expect(bar()).toHaveTextContent("Start from a template40 templates");

  fireEvent.click(bar());
  expect(bar()).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByRole("button", { name: /^Coding · Budget:/ })).toBeVisible();
});

it("names the applied template in the bar, and Reset all returns to the bar without it", () => {
  const { bar } = board();
  const cell = screen.getByRole("button", { name: /^Coding · Budget:/ });
  cell.focus();
  fireEvent.click(cell);
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(bar()).toHaveTextContent("Applied: Coding · Budget");
  // The cell unmounted; focus lands on the bar that names the result.
  expect(bar()).toHaveFocus();

  fireEvent.click(screen.getByRole("button", { name: "Reset all" }));
  expect(bar()).toBeVisible();
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(bar()).not.toHaveTextContent("Applied");
  expect(screen.getByText("Start from a template")).toBeVisible();

  fireEvent.click(bar());
  expect(screen.getByRole("button", { name: /^Coding · Budget:/ })).toBeVisible();
});

it("reaches every template by its category row and tier column, from the data", () => {
  board();
  const categories = realVocabulary.template_categories!;
  const tiers = realVocabulary.template_tiers!;
  const [byUse, byConstraint] = screen.getAllByRole("table");
  expect(within(byUse).getByText("By use")).toBeInTheDocument();
  expect(within(byConstraint).getByText("By constraint")).toBeInTheDocument();
  expect(within(byUse).getAllByRole("columnheader").slice(1).map((cell) => cell.textContent)).toEqual(
    tiers.map((tier) => tier.name),
  );

  for (const template of realVocabulary.templates!) {
    const category = categories.find((row) => row.id === template.category)!;
    const tier = tiers.find((row) => row.id === template.tier)!;
    const table = category.kind === "use" ? byUse : byConstraint;
    const row = within(table).getByRole("rowheader", { name: new RegExp(`^${category.name.replace(/[()]/g, "\\$&")}`) }).closest("tr")!;
    const column = tiers.indexOf(tier) + 1;
    const cell = row.children[column] as HTMLElement;
    const subject = `${category.name} · ${tier.name}`;
    if (template.available) {
      expect(within(cell).getByRole("button")).toHaveAccessibleName(`${subject}: ${template.tradeoff}`);
    } else {
      expect(within(cell).getByRole("group")).toHaveAccessibleName(`${subject}: not available on this snapshot`);
    }
  }
  // Counts come from the same rows: "4 of 5 ready" for Coding, whose Fastest tier has no speed data.
  expect(screen.getByRole("rowheader", { name: /^Coding/ })).toHaveTextContent("4 of 5 ready");
  expect(byUse).toHaveTextContent("6 categories · 30 templates");
  expect(byConstraint).toHaveTextContent("3 categories · 10 templates");
});

it("keeps an unavailable template on the grid with its reason instead of a button", () => {
  board();
  const fastest = screen.getByRole("group", { name: "Coding · Fastest: not available on this snapshot" });
  expect(fastest).toHaveTextContent("No offering has a known Output throughput yet");
  expect(within(fastest).queryByRole("button")).not.toBeInTheDocument();
  expect(screen.getByRole("group", { name: "EU-only data · Best available: not available on this snapshot" }))
    .toHaveTextContent("No offering passes: Inference region in the EU");
});

it("applies a subcategory as a Prefer on that refinement beside the tier's weights", () => {
  const { onSpec, bar } = board({ ...realVocabulary, refinements });
  const select = screen.getByRole("combobox", { name: "Coding subcategory" });
  // Only refinements with measured evidence are offered; Rust is not measured in this fixture.
  expect(within(select).queryByRole("option", { name: /Rust/ })).not.toBeInTheDocument();
  fireEvent.change(select, { target: { value: "python" } });
  fireEvent.click(screen.getByRole("button", { name: /^Coding › Python · Budget:/ }));

  const sent = toBoardDecisionSpec(onSpec.mock.calls.at(-1)![0], "full");
  expect(sent.optimize).toEqual({
    weights: {
      software_engineering: 0.3,
      "software_engineering/python": 0.3,
      "-offering.cost_per_task": 0.4,
    },
  });
  expect(bar()).toHaveTextContent("Applied: Coding › Python · Budget");
});

it("sets both canvas axes from the template it applies", () => {
  const { onCanvasAxes } = board();
  fireEvent.click(screen.getByRole("button", { name: /^Long documents · Balanced:/ }));
  expect(onCanvasAxes).toHaveBeenLastCalledWith({ x: "facet:model.context_window", y: "capability:writing" });
  for (const template of realVocabulary.templates!) {
    expect(template.canvas, template.id).toEqual({ x: expect.any(String), y: expect.any(String) });
  }
});

it("lists templates flat when the vocabulary predates categories", () => {
  const legacy = {
    ...realVocabulary,
    template_categories: undefined,
    template_tiers: undefined,
    templates: realVocabulary.templates!.map((template) => ({
      ...template, category: undefined, tier: undefined, tradeoff: undefined, canvas: undefined,
    })),
  };
  board(legacy);
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Coding agent on a budget/ })).toBeVisible();
});
