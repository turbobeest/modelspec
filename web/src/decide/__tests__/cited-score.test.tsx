import { render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import rawDecision from "../__fixtures__/full-decision.json";
import { decisionSchema, evidenceItemSchema } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { Why } from "../components/Why";
import { baseSpec } from "../state/spec";

const citation = {
  status: "cited",
  sources: [{ source_id: "src-board", url: "https://board.example.org/results",
    snapshot_ref: `sha256:${"0".repeat(64)}`, retrieved_at: null }],
};

function citedDecision() {
  return decisionSchema.parse({
    ...rawDecision,
    results: rawDecision.results.map((result) => ({ ...result,
      evidence: result.evidence.map((group) => ({ ...group,
        items: group.items.map((item) => ({ ...item, citation })),
      })),
    })),
    top: rawDecision.top.map((row) => ({ ...row,
      evidence: row.evidence.map((group) => ({ ...group,
        items: group.items.map((item) => ({ ...item, citation })),
      })),
    })),
  });
}

it("accepts cited benchmark provenance without changing existing evidence fields", () => {
  const item = rawDecision.results[0]?.evidence[0]?.items[0];
  if (!item) throw new Error("Fixture requires benchmark evidence");
  expect(evidenceItemSchema.parse({ ...item, citation })).toHaveProperty("citation", citation);
  expect(evidenceItemSchema.parse(item)).not.toHaveProperty("citation");
});

it("labels cited benchmark evidence in the model explanation", () => {
  const decision = citedDecision();
  const spec = { ...baseSpec, bench: "quality" };
  const view = mapDecisionToViewModel(decision, spec, { axis: "task$", dismissed: [] });
  const model = decision.results[0]?.offering.model;
  const row = view.explanation.feasible.find((candidate) => `${candidate.m.lab}/${candidate.m.id}` === model);
  if (!row) throw new Error("Fixture requires a ranked model");
  render(<Why decision={view} spec={spec} row={row} onRelax={vi.fn()}
    onProvenance={vi.fn()} boardRanked />);
  const explanation = screen.getByRole("region", { name: "Why this model" });
  expect(within(explanation).getByText("Cited, not machine-verified")).toBeVisible();
});
