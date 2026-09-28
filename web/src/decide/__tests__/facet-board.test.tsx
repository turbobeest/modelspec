import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import {
  allocateBoardWeights, boardToSpec, decodeBoardState, encodeBoardSpec, estateSpec, foldRefinementWeights, groupFacets,
  formatBoardCondition, nextMustOrder, parseBoardCondition, showsFacetBoard, supportsPreference,
  templateToBoard, toBoardDecisionSpec,
} from "../facet-board/model";
import type { BoardSelections } from "../facet-board/model";
import { realBaseSpec } from "../vocabulary";
import { realVocabulary, smallVocabulary } from "./vocab-fixtures";
import { toDecisionSpec } from "../adapter/view-model";
import { decisionSpecSchema } from "../adapter/contract";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { vocabularySchema } from "../vocabulary";

const refinementVocabulary = vocabularySchema.parse(refinementVocabularyJson);

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
      "offering.data.zero_retention": { mode: "both", op: "=", value: true, weight: 0.2 },
      "model.class": { mode: "must", op: "in", value: ["text-generator"] },
      "model.weights_openness": { mode: "prefer", value: "open_weights", weight: 0.3 },
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
      optimize: { weights: {
        software_engineering: 0.6,
        "-offering.cost_per_task": 0.4,
        "model.weights_openness": { prefer: "open_weights", weight: 0.3 },
        "offering.data.zero_retention": { prefer: true, weight: 0.2 },
      } },
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
      if (supportsPreference(facet)) {
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
    expect(supportsPreference(smallVocabulary.facets.find((facet) => facet.id === "offering.cost_per_task")!)).toBe(true);
    expect(supportsPreference(smallVocabulary.facets.find((facet) => facet.id === "model.input_modalities")!)).toBe(false);
  });
});

describe("refinements", () => {
  it("carves refinement weights from the parent and folds them back exactly", () => {
    const selections: BoardSelections = {
      "capability.software_engineering": { mode: "prefer", weight: 0.6 },
      "refinement.python": { mode: "prefer", weight: 0.3 },
    };
    const carved = boardToSpec(realBaseSpec(refinementVocabulary), refinementVocabulary, selections);
    expect(toBoardDecisionSpec(carved, "summary").optimize).toEqual({
      weights: { software_engineering: 0.3, "software_engineering/python": 0.3 },
    });
    expect(toBoardDecisionSpec(foldRefinementWeights(carved, refinementVocabulary), "summary").optimize).toEqual({
      weights: { software_engineering: 0.6 },
    });
  });

  it("adds a refinement preference when its parent is Must-only", () => {
    const spec = boardToSpec(realBaseSpec(refinementVocabulary), refinementVocabulary, {
      "capability.software_engineering": { mode: "must", value: 0.5 },
      "refinement.python": { mode: "prefer", weight: 0.25 },
    });
    expect(toBoardDecisionSpec(spec, "summary").optimize).toEqual({
      weights: { "software_engineering/python": 0.25 },
    });
  });

  it.each(["prefer", "must"] as const)("keeps a saved refinement dormant while its %s parent is off", (parentMode) => {
    const active: BoardSelections = {
      "capability.software_engineering": { mode: parentMode, weight: 0.6 },
      "refinement.python": { mode: "prefer", weight: 0.25 },
    };
    expect(allocateBoardWeights(refinementVocabulary, active).weights)
      .toHaveProperty("software_engineering/python", 0.25);

    const dormant = {
      ...active,
      "capability.software_engineering": { ...active["capability.software_engineering"], mode: "off" as const },
    };
    const dormantAllocation = allocateBoardWeights(refinementVocabulary, dormant);
    expect(dormantAllocation.weights).not.toHaveProperty("software_engineering/python");
    expect(dormantAllocation.refinements).not.toHaveProperty("refinement.python");
    expect(dormantAllocation.selections["refinement.python"]).toEqual({ mode: "prefer", weight: 0.25 });

    const restored = {
      ...dormantAllocation.selections,
      "capability.software_engineering": active["capability.software_engineering"],
    };
    expect(allocateBoardWeights(refinementVocabulary, restored).weights)
      .toHaveProperty("software_engineering/python", 0.25);
  });

  it.each([
    { refinements: [["python", 0.4], ["bug_fix", 0.4]] },
    { refinements: [["python", 0.3], ["bug_fix", 0.3], ["new_feature", 0.3]] },
  ] as const)("scales $refinements proportionally when the parent is lowered", ({ refinements }) => {
    const selections: BoardSelections = {
      "capability.software_engineering": { mode: "prefer", weight: 0.3 },
      ...Object.fromEntries(refinements.map(([id, weight]) => [
        `refinement.${id}`, { mode: "prefer", weight },
      ])),
    };
    const allocation = allocateBoardWeights(refinementVocabulary, selections);
    const expected = 0.3 / refinements.length;
    for (const [id] of refinements) {
      expect(allocation.selections[`refinement.${id}`].weight).toBeCloseTo(expected);
      expect(allocation.refinements[`refinement.${id}`].max).toBeCloseTo(expected);
    }
    expect(allocation.general.software_engineering).toBeCloseTo(0);
    expect(Object.values(allocation.weights).reduce<number>(
      (sum, term) => sum + (typeof term === "number" ? term : term.weight), 0,
    )).toBeCloseTo(0.3);
    expect(allocateBoardWeights(refinementVocabulary, allocation.selections).weights)
      .toEqual(allocation.weights);
    const request = toBoardDecisionSpec(
      boardToSpec(realBaseSpec(refinementVocabulary), refinementVocabulary, selections),
      "summary",
    );
    expect("weights" in request.optimize && request.optimize.weights)
      .not.toHaveProperty("software_engineering");
    expect(decisionSpecSchema.safeParse(request).success).toBe(true);
  });

  it("omits a fully carved parent from the request and keeps positive refinements", () => {
    const spec = boardToSpec(realBaseSpec(refinementVocabulary), refinementVocabulary, {
      "capability.software_engineering": { mode: "prefer", weight: 0.3 },
      "refinement.python": { mode: "prefer", weight: 0.3 },
    });
    const request = toBoardDecisionSpec(spec, "summary");
    expect(request.optimize).toEqual({ weights: { "software_engineering/python": 0.3 } });
    expect(decisionSpecSchema.safeParse(request).success).toBe(true);
  });

  it("uses the same allocation for slider limits, the equation and normalized state", () => {
    const onSelections = vi.fn();
    const selections: BoardSelections = {
      "capability.software_engineering": { mode: "prefer", weight: 0.6 },
      "refinement.python": { mode: "prefer", weight: 0.3 },
      "refinement.bug_fix": { mode: "prefer", weight: 0.3 },
    };
    render(<FacetBoard
      vocabulary={refinementVocabulary}
      spec={realBaseSpec(refinementVocabulary)}
      selections={selections}
      onSelections={onSelections}
      onSpec={vi.fn()}
      estate={{ providers: [], plans: [], hardware: [] }}
      onEstate={vi.fn()}
    />);
    const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
    expect(software).toHaveTextContent("general 0.0 · Bug fix 0.3 · Python 0.3");
    fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
    expect(within(software).getByLabelText("Weight for Python")).toHaveAttribute("max", "0.3");
    fireEvent.change(within(software).getByLabelText("Weight for Software engineering"), {
      target: { value: "0.3" },
    });
    const normalized = onSelections.mock.calls.at(-1)![0] as BoardSelections;
    expect(normalized["refinement.python"].weight).toBe(0.15);
    expect(normalized["refinement.bug_fix"].weight).toBe(0.15);
  });

  it("shows Refine only for an active domain and orders evidence within each kind", () => {
    const base = realBaseSpec(refinementVocabulary);
    const view = render(<FacetBoard vocabulary={refinementVocabulary} spec={base} onSpec={vi.fn()} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Refine" })).not.toBeInTheDocument();
    view.rerender(<FacetBoard vocabulary={refinementVocabulary} spec={base} selections={{ "capability.software_engineering": { mode: "prefer", weight: 0.6 } }} onSpec={vi.fn()} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Refine" }));
    const language = screen.getByRole("heading", { name: "Language" }).closest("section")!;
    expect(within(language).getAllByText(/Python|Go|Java|Rust|TypeScript/).map((node) => node.textContent)).toEqual(["Python", "Go", "Java", "Rust", "TypeScript"]);
    const rust = screen.getByText("Rust").closest<HTMLElement>(".refinement-row")!;
    expect(within(rust).getByLabelText("Prefer")).toBeDisabled();
    expect(within(rust).getByLabelText("Prefer")).toHaveAccessibleDescription("Benchmarks exist; no scores for these models yet");
    expect(within(rust).getByLabelText("Must")).toHaveAccessibleDescription("Must for refinements is coming");
    expect(within(rust).getByText("Benchmarks exist; no scores for these models yet")).toBeInTheDocument();
    const terminal = screen.getByText("Terminal agent").closest<HTMLElement>(".refinement-row")!;
    expect(within(terminal).getByLabelText("Prefer")).toBeEnabled();
    expect(within(terminal).getByText("proxy evidence only")).toBeInTheDocument();
  });

  it("excludes a saved refinement from counts while its parent is off", () => {
    render(<FacetBoard
      vocabulary={refinementVocabulary}
      spec={realBaseSpec(refinementVocabulary)}
      onSpec={vi.fn()}
      estate={{ providers: [], plans: [], hardware: [] }}
      onEstate={vi.fn()}
    />);

    const facets = screen.getByRole("region", { name: "Facets" });
    const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
    fireEvent.click(within(software).getByLabelText("Prefer"));
    fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
    const python = within(software).getByText("Python").closest<HTMLElement>(".refinement-row")!;
    fireEvent.click(within(python).getByLabelText("Prefer"));

    expect(within(facets).getByText("2 set")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /What it's good at2 set/ })).toBeInTheDocument();

    const softwareState = within(software).getByRole("radiogroup", { name: "State for Software engineering" });
    fireEvent.click(within(softwareState).getByLabelText("Doesn't matter"));

    expect(within(facets).getByText("0 set")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /What it's good atall Doesn't matter/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /What it's good at1 set/ })).not.toBeInTheDocument();
  });

  it("restores refinement selection and weight from the board URL", () => {
    const restored = decodeBoardState(encodeBoardSpec(realBaseSpec(refinementVocabulary), "task$", {
      selections: { "refinement.python": { mode: "prefer", weight: 0.3 } },
      mustOrder: [], estate: { providers: [], plans: [], hardware: [] },
    }));
    expect(restored?.selections["refinement.python"]).toEqual({ mode: "prefer", weight: 0.3 });
  });

  it("renders no Refine control when the optional field is absent", () => {
    render(<FacetBoard vocabulary={realVocabulary} spec={realBaseSpec(realVocabulary)} selections={{ "capability.software_engineering": { mode: "prefer" } }} onSpec={vi.fn()} estate={{ providers: [], plans: [], hardware: [] }} onEstate={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Refine" })).not.toBeInTheDocument();
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
  const withoutTemplates = { ...smallVocabulary, templates: undefined };
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
  expect(screen.queryByText("Prefer on these facets: coming (MODEL-172)")).not.toBeInTheDocument();
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
