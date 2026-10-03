import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import { toBoardDecisionSpec } from "../facet-board/model";
import { realBaseSpec, vocabularySchema } from "../vocabulary";
import type { Vocabulary } from "../vocabulary";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { realVocabulary } from "./vocab-fixtures";
import { availableTemplates } from "../facet-board/templates";

// The fixture is the production vocabulary: 28 of 40 templates are available,
// no Fastest template is, and no EU-only data template is.
const offered = availableTemplates(realVocabulary);

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

it("starts collapsed and names the action when collapsed or expanded", () => {
  const { bar } = board();
  expect(offered).toHaveLength(28);
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(bar()).toHaveAccessibleName("Start from a template Show all 28 templates");
  const panel = document.getElementById(bar().getAttribute("aria-controls")!)!;
  expect(panel).not.toBeVisible();
  expect(screen.queryByRole("button", { name: /^Coding · Budget:/ })).not.toBeInTheDocument();

  fireEvent.click(bar());
  expect(bar()).toHaveAttribute("aria-expanded", "true");
  expect(panel).toBeVisible();
  expect(bar()).toHaveAccessibleName("Start from a template Hide templates");

  fireEvent.click(bar());
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(panel).not.toBeVisible();

  fireEvent.click(bar());
  expect(bar()).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByRole("button", { name: /^Coding · Budget:/ })).toBeVisible();
  expect(bar()).toHaveAccessibleName("Start from a template Hide templates");
});

it("names the applied template in the bar, and Reset all returns to the bar without it", () => {
  const { bar } = board();
  fireEvent.click(bar());
  const cell = screen.getByRole("button", { name: /^Coding · Budget:/ });
  cell.focus();
  fireEvent.click(cell);
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(bar()).toHaveAccessibleName("Start from a template Applied: Coding · Budget Show all 28 templates");
  // The cell unmounted; focus lands on the bar that names the result.
  expect(bar()).toHaveFocus();

  fireEvent.click(bar());
  expect(bar()).toHaveAccessibleName("Start from a template Applied: Coding · Budget Hide templates");
  fireEvent.click(bar());

  fireEvent.click(screen.getByRole("button", { name: "Reset all" }));
  expect(bar()).toBeVisible();
  expect(bar()).toHaveAttribute("aria-expanded", "false");
  expect(bar()).not.toHaveTextContent("Applied");
  expect(screen.getByText("Start from a template")).toBeVisible();

  fireEvent.click(bar());
  expect(screen.getByRole("button", { name: /^Coding · Budget:/ })).toBeVisible();
});

it("reaches every available template by its category row and tier column, from the data", () => {
  const { bar } = board();
  fireEvent.click(bar());
  const categories = realVocabulary.template_categories!;
  const tiers = realVocabulary.template_tiers!;
  const [byUse, byConstraint] = screen.getAllByRole("table");
  expect(within(byUse).getByText("By use")).toBeInTheDocument();
  expect(within(byConstraint).getByText("By constraint")).toBeInTheDocument();
  const columns = (table: HTMLElement) => within(table).getAllByRole("columnheader").slice(1).map((cell) => cell.textContent);
  // No Fastest column: no Fastest template is available. No Private column under constraints: none exists.
  expect(columns(byUse)).toEqual(["Best available", "Balanced", "Budget", "Private / self-hosted"]);
  expect(columns(byConstraint)).toEqual(["Best available", "Balanced", "Budget"]);

  for (const template of offered) {
    const category = categories.find((row) => row.id === template.category)!;
    const tier = tiers.find((row) => row.id === template.tier)!;
    const table = category.kind === "use" ? byUse : byConstraint;
    const row = within(table).getByRole("rowheader", { name: new RegExp(`^${category.name.replace(/[()]/g, "\\$&")}`) }).closest("tr")!;
    const cell = row.children[columns(table).indexOf(tier.name) + 1] as HTMLElement;
    expect(within(cell).getByRole("button")).toHaveAccessibleName(`${category.name} · ${tier.name}: ${template.tradeoff}`);
  }
  expect(screen.getAllByRole("button", { name: / · .+: / })).toHaveLength(28);
});

it("offers only what this snapshot can answer: no unavailable cells, empty columns, empty rows or counts", () => {
  const { bar } = board();
  fireEvent.click(bar());
  const panel = document.getElementById(bar().getAttribute("aria-controls")!)!;
  expect(within(panel).queryByText(/Not available/)).not.toBeInTheDocument();
  expect(within(panel).queryByText(/not available on this snapshot/)).not.toBeInTheDocument();
  expect(within(panel).queryByRole("columnheader", { name: "Fastest" })).not.toBeInTheDocument();
  expect(within(panel).queryByRole("rowheader", { name: /^EU-only data/ })).not.toBeInTheDocument();
  expect(panel).not.toHaveTextContent(/\d+ of \d+ ready|categories · \d+ templates/);
});

it("hides the card when no template is available", () => {
  board({ ...realVocabulary, templates: realVocabulary.templates!.map((template) => ({ ...template, available: false })) });
  expect(screen.queryByRole("button", { name: /Start from a template/ })).not.toBeInTheDocument();
});

it("applies a subcategory as a Prefer on that refinement beside the tier's weights", () => {
  const { onSpec, bar } = board({ ...realVocabulary, refinements });
  fireEvent.click(bar());
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
  const { onCanvasAxes, bar } = board();
  fireEvent.click(bar());
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
  const { bar } = board(legacy);
  fireEvent.click(bar());
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: /Coding agent on a budget/ })).toBeVisible();
});
