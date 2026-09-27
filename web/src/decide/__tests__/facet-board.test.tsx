import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import {
  boardToSpec, decodeBoardState, encodeBoardSpec, estateSpec, groupFacets,
  showsFacetBoard, supportsPreference, toBoardDecisionSpec,
} from "../facet-board/model";
import type { BoardSelections } from "../facet-board/model";
import { realBaseSpec } from "../vocabulary";
import { smallVocabulary } from "./vocab-fixtures";
import { toDecisionSpec } from "../adapter/view-model";

describe("facet board launch gate", () => {
  it.each(["internal.modelspec-7np.pages.dev", "localhost", "127.0.0.1"])("allows %s", (host) => expect(showsFacetBoard(host)).toBe(true));
  it.each(["modelspec.dev", "www.modelspec.dev", "abc123.modelspec-7np.pages.dev", "modelspec-7np.pages.dev", "example.com", ""])("keeps the current page on %s", (host) => expect(showsFacetBoard(host)).toBe(false));
});

describe("facet state mapping", () => {
  const base = realBaseSpec(smallVocabulary);
  const contract = (selections: BoardSelections) => toBoardDecisionSpec(boardToSpec(base, smallVocabulary, selections), "full");
  const weights = (selections: BoardSelections) => {
    const objective = contract(selections).optimize;
    if (!("weights" in objective)) throw new Error("board objective must use weights");
    return objective.weights;
  };
  it("maps numeric, boolean, enum, domain preference and Must+Prefer cost literally", () => {
    expect(contract({
      "model.context_window": { mode: "must", op: ">=", value: 200000 },
      "offering.data.zero_retention": { mode: "must", op: "=", value: true },
      "model.class": { mode: "must", op: "in", value: ["text-generator"] },
      "capability.software_engineering": { mode: "prefer", weight: 0.6 },
      "offering.cost_per_task": { mode: "both", op: "<=", value: 0.25, weight: 0.4 },
    })).toEqual({
      spec_version: 1, snapshot: "latest", task_type: "new_feature",
      capabilities: { software_engineering: "required" },
      task_tokens: { input: 40000, output: 4000 },
      where: [
        "model.class = text-generator", "model.lifecycle = active",
        "model.class in {text-generator}", "offering.cost_per_task <= 0.25",
        "model.context_window >= 200000", "offering.data.zero_retention = true",
      ],
      optimize: { weights: { software_engineering: 0.6, "-offering.cost_per_task": 0.4 } },
      unknowns: "default", explain: "full", limit: 500,
    });
  });
  it("starts with no hidden conditions and adds only visible board gates", () => {
    const emptyBase = { ...base, conds: [] };
    expect(toDecisionSpec(boardToSpec(emptyBase, smallVocabulary, {}), "full").where).toEqual([]);
    expect(toDecisionSpec(boardToSpec(emptyBase, smallVocabulary, {
      "offering.cost_per_task": { mode: "must", op: "<=", value: 0.25 },
    }), "full").where).toEqual(["offering.cost_per_task <= 0.25"]);
  });
  it("uses a membership-neutral objective when no Prefer is set", () => {
    expect(weights({})).toEqual({ "-offering.cost_per_task": 1 });
    expect(weights({
      "model.context_window": { mode: "must", op: ">=", value: 200000 },
    })).toEqual({ "-offering.cost_per_task": 1 });
    expect(weights({
      "capability.software_engineering": { mode: "prefer", weight: 0.6 },
    })).toEqual({ software_engineering: 0.6 });
  });
  it("never sends empty weights for any state produced from the vocabulary fixture", () => {
    const states: BoardSelections[] = [{}];
    for (const facet of groupFacets(smallVocabulary).groups.flatMap((group) => group.facets)) {
      states.push({ [facet.id]: { mode: "must" } });
      if (supportsPreference(facet.id)) {
        states.push({ [facet.id]: { mode: "prefer" } });
        states.push({ [facet.id]: { mode: "both" } });
      }
    }
    for (const template of smallVocabulary.templates ?? []) {
      states.push(Object.fromEntries(template.facets.map(({ id, ...selection }) => [id, selection])));
    }
    for (const state of states) {
      expect(Object.keys(weights(state)).length).toBeGreaterThan(0);
    }
  });
  it("adds the provider estate as a second-spec gate", () => {
    expect(toDecisionSpec(estateSpec(base, ["anthropic", "google"]), "summary").where?.at(-1)).toBe("offering.provider in {anthropic, google}");
  });
  it("only enables weights the engine supports", () => {
    expect(supportsPreference("offering.cost_per_task")).toBe(true);
    expect(supportsPreference("model.context_window")).toBe(false);
  });
});

it("separates not-yet-tracked facets", () => {
  const vocabulary = { ...smallVocabulary, facets: smallVocabulary.facets.map((facet, index) => index === 0 ? { ...facet, known: 0 } : facet) };
  expect(groupFacets(vocabulary).untracked.map((facet) => facet.id)).toContain(vocabulary.facets[0].id);
});

it("hides absent templates and expands groups with active template facets", () => {
  const base = realBaseSpec(smallVocabulary);
  const first = render(<FacetBoard vocabulary={smallVocabulary} spec={base} onSpec={vi.fn()} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  expect(screen.queryByText("Start from a template")).not.toBeInTheDocument();
  first.unmount();
  const onSpec = vi.fn();
  const vocabulary = { ...smallVocabulary, templates: [{ id: "budget", name: "Budget coding", description: "A practical start", facets: [{ id: "offering.cost_per_task", mode: "both" as const, op: "<=" as const, value: 0.25, weight: 0.4, reason: "Keep each run affordable" }] }] };
  render(<FacetBoard vocabulary={vocabulary} spec={base} onSpec={onSpec} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  expect(screen.getByRole("button", { name: /Budgetall Doesn't matter/ })).toHaveAttribute("aria-expanded", "false");
  fireEvent.click(screen.getByRole("button", { name: /Budget coding/ }));
  expect(screen.getByRole("button", { name: /Budget1 set/ })).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByText("Why: Keep each run affordable")).toBeInTheDocument();
  expect(onSpec).toHaveBeenCalledOnce();
  const cost = screen.getByText("Cost per task").closest<HTMLElement>(".facet-row")!;
  expect(within(cost).queryByText(/coming \(MODEL-172\)/)).not.toBeInTheDocument();
  expect(screen.getAllByText("Prefer on these facets: coming (MODEL-172)").length).toBeGreaterThan(0);
});

it("reopens Must, Prefer and Must+Prefer selections and keeps them after another edit", () => {
  const selections: BoardSelections = {
    "model.context_window": { mode: "must", op: ">=", value: 200000 },
    "capability.software_engineering": { mode: "prefer", weight: 0.6 },
    "offering.cost_per_task": { mode: "both", op: "<=", value: 0.25, weight: 0.4 },
  };
  const restored = decodeBoardState(encodeBoardSpec(realBaseSpec(smallVocabulary), "task$", {
    selections,
    estate: { providers: [], plans: [], hardware: [] },
  }));
  const onSpec = vi.fn();
  render(<FacetBoard
    vocabulary={smallVocabulary}
    spec={realBaseSpec(smallVocabulary)}
    selections={restored!.selections}
    onSelections={vi.fn()}
    onSpec={onSpec}
    estate={restored!.estate}
    onEstate={vi.fn()}
  />);
  const context = screen.getByText("Context window").closest<HTMLElement>(".facet-row")!;
  const capability = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  const cost = screen.getByText("Cost per task").closest<HTMLElement>(".facet-row")!;
  expect(within(context).getByLabelText("Must")).toBeChecked();
  expect(within(capability).getByLabelText("Prefer")).toBeChecked();
  expect(within(cost).getByLabelText("Prefer")).toBeChecked();
  expect(within(cost).getByLabelText("and never worse than…")).toBeChecked();

  fireEvent.change(within(context).getByLabelText("Threshold"), { target: { value: "250000" } });
  const next = onSpec.mock.calls.at(-1)![0];
  expect(next.conds).toEqual(expect.arrayContaining([
    expect.objectContaining({ facet: "model.context_window", value: 250000 }),
    expect.objectContaining({ facet: "offering.cost_per_task", value: 0.25 }),
  ]));
  expect(next.boardWeights).toEqual({ software_engineering: 0.6, "-offering.cost_per_task": 0.4 });
});
