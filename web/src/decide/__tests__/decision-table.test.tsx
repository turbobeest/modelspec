import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import type { Row } from "../adapter";
import { DecisionTable } from "../components/DecisionTable";
import { baseSpec } from "../state/spec";

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
