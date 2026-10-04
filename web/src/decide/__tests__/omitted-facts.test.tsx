import { render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { DecisionTable } from "../components/DecisionTable";
import { Why } from "../components/Why";
import { baseSpec } from "../state/spec";

it.each(["summary", "full"] as const)(
  "does not claim snapshot absence when %s omits a ranked model's facts",
  (explain) => {
    const full = decisionSchema.parse(fixtureJson);
    const omitted = full.top[0];
    expect(omitted.facts.find((fact) => fact.facet === "model.context_window")?.value)
      .toBeGreaterThan(0);
    const decision = {
      ...full,
      explain,
      top: explain === "summary" ? [] : full.top.slice(1),
    };
    const spec = { ...baseSpec, bench: "quality" };
    const view = mapDecisionToViewModel(decision, spec, { axis: "task$", dismissed: [] });
    const row = view.explanation.feasible.find(
      (candidate) => `${candidate.m.lab}/${candidate.m.id}` === omitted.offering.model,
    );
    expect(row).toBeDefined();
    expect(row?.m.ctx).toBeNull();

    render(<>
      <DecisionTable decision={view} spec={spec} selected={null} onSelect={vi.fn()} />
      <Why decision={view} spec={spec} row={row ?? null} onRelax={vi.fn()}
        onProvenance={vi.fn()} boardRanked />
    </>);

    const table = screen.getByRole("region", { name: "Decision table" });
    const missing = within(table).getAllByRole("img", { name: "not yet researched or not published" });
    expect(missing.length).toBeGreaterThan(0);
    expect(missing.every((cell) => cell.textContent === "–")).toBe(true);
    expect(within(table).getAllByText("– not yet researched or not published (never zero)")).toHaveLength(1);
    expect(table).not.toHaveTextContent("not available in this response");
    expect(document.body).not.toHaveTextContent("not available in this snapshot");
    expect(document.body).toHaveTextContent("release date not available in this response");
  },
);
