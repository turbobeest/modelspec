import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { Field } from "../components/Field";
import { baseSpec } from "../state/spec";
import { readFileSync } from "node:fs";

it("reports a qualifying model omitted by the result limit", () => {
  const decision = decisionSchema.parse({
    ...fixtureJson,
    contract_version: "1.12",
    truncated: { offerings: 0, models: 1 },
  });
  const view = mapDecisionToViewModel(
    decision,
    { ...baseSpec, bench: "quality" },
    { axis: "task$", dismissed: [] },
  );

  render(
    <Field
      decision={view}
      spec={baseSpec}
      onAdd={vi.fn()}
      onDismiss={vi.fn()}
    />,
  );

  expect(screen.getByRole("region", { name: "Narrowing" }))
    .toHaveTextContent("1 more model not shown");
});

it("announces exact final counts once and keeps animated digits out of the live region", () => {
  const decision = decisionSchema.parse(fixtureJson);
  const view = mapDecisionToViewModel(decision, { ...baseSpec, bench: "quality" }, { axis: "task$", dismissed: [] });
  const { rerender } = render(<Field decision={view} onAdd={vi.fn()} onDismiss={vi.fn()} showQuestions={false} />);
  const announcement = screen.getByRole("status");
  expect(announcement).toHaveAttribute("aria-live", "polite");
  expect(announcement).toHaveAttribute("aria-atomic", "true");
  expect(announcement).toHaveTextContent("4 qualify · 0 may qualify · 0 out");
  const numbers = document.querySelector(".narrowing-counts");
  expect(numbers).toHaveAttribute("aria-hidden", "true");
  expect([...document.querySelectorAll(".narrowing-number")].map((number) => number.textContent)).toEqual(["4", "0", "0"]);

  const updated = { ...view, explanation: { ...view.explanation, feasible: view.explanation.feasible.slice(0, 2), may: view.explanation.feasible.slice(2, 3), excluded: view.explanation.feasible.slice(3) } };
  rerender(<Field decision={updated} onAdd={vi.fn()} onDismiss={vi.fn()} showQuestions={false} />);
  expect(announcement).toHaveTextContent("2 qualify · 1 may qualify · 1 out");
  expect([...document.querySelectorAll(".narrowing-number")].map((number) => number.textContent)).toEqual(["2", "1", "1"]);
});

it("disables count animation for reduced motion", () => {
  const css = readFileSync("src/decide/decide.css", "utf8");
  expect(css).toMatch(/\.narrowing-number\s*\{[^}]*animation:\s*narrowing-count/);
  expect(css).toMatch(/@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{\s*\.decide-app \*,[^}]*animation:\s*none !important/);
});
