import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import type { Row, Spec } from "../adapter";
import { DecisionTable } from "../components/DecisionTable";
import { baseSpec } from "../state/spec";
import { VocabContext, realVocab } from "../vocabulary/context";
import { realVocabulary } from "./vocab-fixtures";

it("keeps classes in label order and names alphabetical within each class after Clear", () => {
  const rankedSpec = { ...baseSpec, bench: "quality", boardWeights: { quality: 1 } };
  const view = mapDecisionToViewModel(decisionSchema.parse(fixtureJson), rankedSpec, { axis: "task$", dismissed: [] });
  const base = view.explanation.feasible[0];
  const rows = [
    { ...base, m: { ...base.m, id: "z-text", name: "Z text", type: "llm" }, cap: 100, cost: 0 },
    { ...base, m: { ...base.m, id: "vector", name: "A vector", type: "embed" } },
    { ...base, m: { ...base.m, id: "z-decision", name: "Z decision", type: "decision" }, cap: 0, cost: 100 },
    { ...base, m: { ...base.m, id: "a-text", name: "A text", type: "llm" } },
    { ...base, m: { ...base.m, id: "b-decision", name: "B decision", type: "decision" }, status: 0,
      best: { ...base.best, o: { ...base.best.o, provider: "Provider not available" } } },
  ] satisfies Row[];
  const decision = { ...view, explanation: { ...view.explanation, rows } };
  const props = { decision, selected: null, onSelect: vi.fn() };
  const table = (spec: Spec) =>
    <VocabContext.Provider value={realVocab(realVocabulary)}><DecisionTable {...props} spec={spec} /></VocabContext.Provider>;
  const { rerender } = render(table(rankedSpec));
  fireEvent.click(screen.getByRole("button", { name: "$ per task" }));
  rerender(table({ ...rankedSpec, boardWeights: {} }));
  fireEvent.click(screen.getByRole("button", { name: "Show 1 without a provider" }));
  expect([...document.querySelectorAll(".table-class-heading")].map((row) => row.textContent))
    .toEqual(["Decision model", "Embedding model", "Text generator"]);
  expect([...document.querySelectorAll("tbody")].map((group) => [...group.querySelectorAll(".table-model")].map((button) => button.textContent)))
    .toEqual([["B decision", "Z decision"], ["A vector"], ["A text", "Z text"]]);
  expect(screen.getByRole("button", { name: "$ per task" })).toBeDisabled();
});

it("keeps an unranked table alphabetical, including rows without a provider", () => {
  const spec = { ...baseSpec, bench: "quality", boardWeights: {} };
  const view = mapDecisionToViewModel(decisionSchema.parse(fixtureJson), spec, { axis: "task$", dismissed: [] });
  const base = view.explanation.feasible[0];
  const zulu = { ...base, m: { ...base.m, id: "zulu", name: "Zulu" } } satisfies Row;
  const alpha = {
    ...base, m: { ...base.m, id: "alpha", name: "Alpha" }, status: 0,
    best: { ...base.best, o: { ...base.best.o, provider: "Provider not available" } },
  } satisfies Row;
  const decision = {
    ...view, explanation: { ...view.explanation, rows: [zulu, alpha], feasible: [zulu], may: [alpha], excluded: [] },
  };
  render(<DecisionTable decision={decision} spec={spec} selected={null} onSelect={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Show 1 without a provider" }));
  expect(screen.getByText("Not ranked yet: listed alphabetically")).toBeInTheDocument();
  expect(Array.from(document.querySelectorAll(".table-model"), (button) => button.textContent)).toEqual(["Alpha", "Zulu"]);
  expect(screen.getByRole("button", { name: "$ per task" })).toBeDisabled();
});

it("counts collapsed providerless rows as excluded rows and answers change, and keeps zero distinct from missing", () => {
  const spec = { ...baseSpec, bench: "quality" };
  const view = mapDecisionToViewModel(decisionSchema.parse(fixtureJson), spec, { axis: "task$", dismissed: [] });
  const base = view.explanation.feasible[0];
  const published = {
    ...base,
    m: { ...base.m, id: "published", name: "Published" },
    cost: 0,
    best: { ...base.best, o: { ...base.best.o, provider: "Published provider", in: 0, out: null } },
  } satisfies Row;
  const unknown: Row = {
    ...base,
    m: { ...base.m, id: "unknown", name: "Unknown provider" },
    status: 0,
    best: { ...base.best, o: { ...base.best.o, provider: "Provider not available" } },
  };
  const excluded: Row = {
    ...unknown,
    m: { ...unknown.m, id: "excluded", name: "Excluded provider" },
    status: -1,
  };
  const decision = {
    ...view,
    explanation: { ...view.explanation, rows: [published, unknown, excluded], feasible: [published], may: [unknown], excluded: [excluded] },
  };
  const props = { spec, selected: null, onSelect: vi.fn() };
  const table = render(<DecisionTable {...props} decision={decision} />);
  expect(screen.getByRole("button", { name: "Show 2 without a provider" })).toHaveAttribute("aria-expanded", "false");
  expect(screen.queryByRole("button", { name: "Unknown provider" })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Excluded provider" })).not.toBeInTheDocument();
  const publishedRow = screen.getByRole("button", { name: "Published" }).closest("tr");
  if (!publishedRow) throw new Error("Published row missing");
  expect(within(publishedRow).getByRole("cell", { name: "$0.0000" })).toBeInTheDocument();
  expect(within(publishedRow).getByRole("cell", { name: "$0.00" })).toBeInTheDocument();
  expect(within(publishedRow).getAllByRole("img", { name: "not yet researched or not published" }).every((cell) => cell.textContent === "–")).toBe(true);
  expect(screen.getAllByText("– not yet researched or not published (never zero)")).toHaveLength(1);

  fireEvent.click(screen.getByRole("checkbox", { name: "Show 1 excluded" }));
  fireEvent.click(screen.getByRole("button", { name: "Show 1 without a provider" }));
  expect(screen.getByRole("button", { name: "Unknown provider" })).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Excluded provider" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("checkbox", { name: "Show 1 excluded" }));
  expect(screen.getByRole("button", { name: "Hide 2 without a provider" })).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByRole("button", { name: "Excluded provider" })).toBeInTheDocument();

  table.rerender(<DecisionTable {...props} decision={{ ...decision, explanation: { ...decision.explanation, rows: [published, unknown], excluded: [] } }} />);
  fireEvent.click(screen.getByRole("button", { name: "Hide 1 without a provider" }));
  expect(screen.getByRole("button", { name: "Show 1 without a provider" })).toHaveAttribute("aria-expanded", "false");
  expect(screen.queryByRole("button", { name: "Unknown provider" })).not.toBeInTheDocument();
});
