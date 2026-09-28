import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { Field } from "../components/Field";
import { baseSpec } from "../state/spec";

it("reports a qualifying model omitted by the result limit", () => {
  const decision = decisionSchema.parse({
    ...fixtureJson,
    contract_version: "1.9",
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

  expect(screen.getByText("Narrowing, in the order you set conditions").parentElement)
    .toHaveTextContent("1 more model not shown");
});
