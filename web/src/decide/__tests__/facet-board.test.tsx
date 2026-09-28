import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import {
  boardToSpec, decodeBoardState, encodeBoardSpec, estateSpec, groupFacets,
  formatBoardCondition, nextMustOrder, parseBoardCondition, showsFacetBoard, supportsPreference,
  templateToBoard, toBoardDecisionSpec,
} from "../facet-board/model";
import type { BoardSelections } from "../facet-board/model";
import { realBaseSpec } from "../vocabulary";
import { realVocabulary, smallVocabulary } from "./vocab-fixtures";
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
        "model.context_window >= 200000", "offering.data.zero_retention = true",
        "model.class in {text-generator}", "offering.cost_per_task <= 0.25",
      ],
      optimize: { weights: { software_engineering: 0.6, "-offering.cost_per_task": 0.4 } },
      unknowns: "default", explain: "full", limit: 20,
    });
  });
  it("starts with no hidden conditions and adds only visible board gates", () => {
    const emptyBase = { ...base, conds: [] };
    expect(toDecisionSpec(boardToSpec(emptyBase, smallVocabulary, {}), "full").where).toEqual([]);
    expect(toDecisionSpec(boardToSpec(emptyBase, smallVocabulary, {
      "offering.cost_per_task": { mode: "must", op: "<=", value: 0.25 },
    }), "full").where).toEqual(["offering.cost_per_task <= 0.25"]);
  });
  it("waits for an enum value before adding a Must condition", () => {
    const emptyBase = { ...realBaseSpec(realVocabulary), conds: [] };
    const where = (selections: BoardSelections) => toDecisionSpec(
      boardToSpec(emptyBase, realVocabulary, selections), "full",
    ).where;
    expect(where({
      "model.weights_openness": { mode: "must" },
      "offering.data.zero_retention": { mode: "must" },
    })).toEqual([]);
    expect(where({
      "model.weights_openness": { mode: "must", op: "=", value: "open_weights" },
    })).toEqual(["model.weights_openness = open_weights"]);
    expect(where({
      "offering.data.zero_retention": { mode: "must", op: "=", value: false },
    })).toEqual(["offering.data.zero_retention = false"]);
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
      states.push(templateToBoard(template, smallVocabulary).selections);
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

it("starts enum Must controls unselected and shows vocabulary counts", () => {
  const onSpec = vi.fn();
  render(<FacetBoard vocabulary={realVocabulary} spec={{ ...realBaseSpec(realVocabulary), conds: [] }} onSpec={onSpec} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: /Where it runsall Doesn't matter/ }));
  const weights = screen.getByText("Open weights").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(weights).getByLabelText("Must"));
  expect(within(weights).getByText("Choose value(s)")).toBeInTheDocument();
  expect(onSpec.mock.calls.at(-1)![0].conds).toEqual([]);
  const openWeights = within(weights).getByLabelText(/Open weights \(\d+\)/);
  fireEvent.click(openWeights);
  expect(onSpec.mock.calls.at(-1)![0].conds).toEqual([
    expect.objectContaining({ facet: "model.weights_openness", op: "=", value: "open_weights" }),
  ]);
});

it("hides absent templates and expands groups with active canonical template facets", () => {
  const base = realBaseSpec(smallVocabulary);
  const { templates: _templates, ...withoutTemplates } = smallVocabulary;
  const first = render(<FacetBoard vocabulary={withoutTemplates} spec={base} onSpec={vi.fn()} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  expect(screen.queryByText("Start from a template")).not.toBeInTheDocument();
  first.unmount();
  const onSpec = vi.fn();
  const vocabulary = { ...smallVocabulary, templates: realVocabulary.templates };
  render(<FacetBoard vocabulary={vocabulary} spec={base} onSpec={onSpec} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  expect(screen.getByRole("button", { name: /Budgetall Doesn't matter/ })).toHaveAttribute("aria-expanded", "false");
  expect(screen.queryByRole("button", { name: /EU-only data handling/ })).not.toBeInTheDocument();
  expect(screen.getByText("Not available on today's data: EU-only data handling — No offering passes: Inference region in the EU — 0 of 4 offerings")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /Coding agent on a budget/ }));
  expect(screen.getByRole("button", { name: /Budget1 set/ })).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByText(/Why: The offering must stay within the per-task budget.*prefer the cheaper task/)).toBeInTheDocument();
  expect(onSpec).toHaveBeenCalledOnce();
  const cost = screen.getByText("Cost per task").closest<HTMLElement>(".facet-row")!;
  expect(within(cost).queryByText(/coming \(MODEL-172\)/)).not.toBeInTheDocument();
  expect(screen.getAllByText("Prefer on these facets: coming (MODEL-172)").length).toBeGreaterThan(0);
});

it("restores default task tokens when a template has no token override", () => {
  const onSpec = vi.fn();
  const base = realBaseSpec(realVocabulary);
  const view = render(<FacetBoard vocabulary={realVocabulary} spec={base} onSpec={onSpec} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);

  fireEvent.click(screen.getByRole("button", { name: /High volume, good enough/ }));
  const highVolume = onSpec.mock.calls.at(-1)![0];
  expect([highVolume.tokIn, highVolume.tokOut]).toEqual([2000, 500]);

  view.rerender(<FacetBoard vocabulary={realVocabulary} spec={highVolume} onSpec={onSpec} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: /Templates/ }));
  fireEvent.click(screen.getByRole("button", { name: /Maths and proofs/ }));
  const maths = onSpec.mock.calls.at(-1)![0];
  expect([maths.tokIn, maths.tokOut]).toEqual([
    realVocabulary.default_task_tokens.input,
    realVocabulary.default_task_tokens.output,
  ]);
});

describe("canonical template mapping", () => {
  it.each(realVocabulary.templates ?? [])("round-trips $id through board serialization", (template) => {
    const converted = templateToBoard(template, realVocabulary);
    for (const row of template.where) {
      const parsed = parseBoardCondition(row.condition);
      expect(formatBoardCondition(parsed.facetId, { mode: "must", ...parsed })).toBe(row.condition);
    }
    const base = { ...realBaseSpec(realVocabulary), conds: [] };
    const withTokens = converted.taskTokens
      ? { ...base, tokIn: converted.taskTokens.input, tokOut: converted.taskTokens.output }
      : base;
    const serialized = toBoardDecisionSpec(
      boardToSpec(withTokens, realVocabulary, converted.selections, converted.mustOrder),
      "full",
    );
    expect(serialized.where).toEqual(template.spec.where);
    expect(serialized.optimize).toEqual(template.spec.optimize);
    if (template.spec.task_tokens) expect(serialized.task_tokens).toEqual(template.spec.task_tokens);
  });

  it("maps a shared gate and signed preference to Must+Prefer", () => {
    const budget = realVocabulary.templates?.find((template) => template.id === "budget-coding");
    if (!budget) throw new Error("budget-coding fixture is missing");
    const cost = templateToBoard(budget, realVocabulary).selections["offering.cost_per_task"];
    expect(cost).toMatchObject({
      mode: "both", op: "<=", value: 0.25, weight: 0.4,
      weightKey: "-offering.cost_per_task",
    });
  });

  it("appends a new Must after existing Musts", () => {
    const selections: BoardSelections = {
      "model.context_window": { mode: "must", op: ">=", value: 200000 },
    };
    const nextSelections = {
      ...selections,
      "offering.cost_per_task": { mode: "must" as const, op: "<=" as const, value: 0.25 },
    };
    const order = nextMustOrder(
      ["model.context_window"],
      selections,
      "offering.cost_per_task",
      nextSelections["offering.cost_per_task"],
    );
    expect(order).toEqual(["model.context_window", "offering.cost_per_task"]);
    expect(toDecisionSpec(boardToSpec(
      { ...realBaseSpec(smallVocabulary), conds: [] }, smallVocabulary, nextSelections, order,
    ), "full").where).toEqual([
      "model.context_window >= 200000",
      "offering.cost_per_task <= 0.25",
    ]);
  });

  it("seeds a legacy URL's Must order before appending a new Must", () => {
    const selections: BoardSelections = {
      "model.context_window": { mode: "must", op: ">=", value: 200000 },
      "model.class": { mode: "must", op: "in", value: ["text-generator"] },
    };
    const legacyHash = "#s=" + btoa(encodeURIComponent(JSON.stringify({
      board: { selections, estate: { providers: [], plans: [], hardware: [] } },
    })));
    const restored = decodeBoardState(legacyHash);
    expect(restored?.mustOrder).toEqual([]);

    const order = nextMustOrder(
      restored!.mustOrder,
      restored!.selections,
      "offering.region",
      { mode: "must", op: "in", value: ["us"] },
    );
    expect(order).toEqual([
      "model.class",
      "model.context_window",
      "offering.region",
    ]);
  });

  it("keeps a Must in position when its threshold changes", () => {
    const selections: BoardSelections = {
      "model.context_window": { mode: "must", op: ">=", value: 200000 },
      "offering.cost_per_task": { mode: "must", op: "<=", value: 0.25 },
    };
    const nextSelections = {
      ...selections,
      "model.context_window": { mode: "must" as const, op: ">=" as const, value: 250000 },
    };
    const order = nextMustOrder(
      ["model.context_window", "offering.cost_per_task"],
      selections,
      "model.context_window",
      nextSelections["model.context_window"],
    );
    expect(order).toEqual(["model.context_window", "offering.cost_per_task"]);
    expect(toDecisionSpec(boardToSpec(
      { ...realBaseSpec(smallVocabulary), conds: [] }, smallVocabulary, nextSelections, order,
    ), "full").where).toEqual([
      "model.context_window >= 250000",
      "offering.cost_per_task <= 0.25",
    ]);
  });
});

it("reopens Must, Prefer and Must+Prefer selections and keeps them after another edit", () => {
  const selections: BoardSelections = {
    "model.context_window": { mode: "must", op: ">=", value: 200000 },
    "capability.software_engineering": { mode: "prefer", weight: 0.6 },
    "offering.cost_per_task": { mode: "both", op: "<=", value: 0.25, weight: 0.4 },
  };
  const restored = decodeBoardState(encodeBoardSpec(realBaseSpec(smallVocabulary), "task$", {
    selections,
    mustOrder: ["model.context_window", "offering.cost_per_task"],
    estate: { providers: [], plans: [], hardware: [] },
  }));
  expect(restored?.mustOrder).toEqual(["model.context_window", "offering.cost_per_task"]);
  const onSpec = vi.fn();
  render(<FacetBoard
    vocabulary={smallVocabulary}
    spec={realBaseSpec(smallVocabulary)}
    selections={restored!.selections}
    onSelections={vi.fn()}
    mustOrder={restored!.mustOrder}
    onMustOrder={vi.fn()}
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
