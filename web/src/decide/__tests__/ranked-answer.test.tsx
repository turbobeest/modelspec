import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { MayQualify, RankedAnswer } from "../facet-board/RankedAnswer";
import type { Row } from "../adapter";
import { realBaseSpec } from "../vocabulary";
import { vocabularySchema } from "../vocabulary";

const fixture = decisionSchema.parse(fixtureJson);
const vocabulary = vocabularySchema.parse(refinementVocabularyJson);

describe("ranked answer refinement fallbacks", () => {
  it.each([
    ["software_engineering/python", "no Python evidence — estimated from general software engineering"],
    ["maths/research_level", "no Research-level maths evidence — estimated from general maths"],
    ["writing/creative", "no Creative writing evidence — estimated from general writing"],
  ])("names the parent domain for %s", (weightKey, label) => {
    const spec = {
      ...realBaseSpec(vocabulary),
      boardWeights: { [weightKey]: 0.5 },
    };
    const decision = mapDecisionToViewModel(fixture, spec, {
      axis: "task$",
      dismissed: [],
      models: vocabulary.models,
      providers: vocabulary.providers,
    });

    render(<RankedAnswer decision={decision} spec={spec} vocabulary={vocabulary} />);

    expect(screen.getAllByText(label).length).toBeGreaterThan(0);
  });
});

describe("unranked board answer", () => {
  it("groups may-qualify models by class before their alphabetical names", () => {
    const spec = { ...realBaseSpec(vocabulary), boardWeights: {} };
    const view = mapDecisionToViewModel(fixture, spec, { axis: "task$", dismissed: [] });
    const base = view.explanation.feasible[0];
    const rows = [
      { ...base, m: { ...base.m, id: "vector", name: "A vector", type: "embed" }, status: 0, best: { ...base.best, o: { ...base.best.o, id: "vector" } } },
      { ...base, m: { ...base.m, id: "z-decision", name: "Z decision", type: "decision" }, status: 0, best: { ...base.best, o: { ...base.best.o, id: "z-decision" } } },
      { ...base, m: { ...base.m, id: "b-decision", name: "B decision", type: "decision" }, status: 0, best: { ...base.best, o: { ...base.best.o, id: "b-decision" } } },
    ] satisfies Row[];
    const decision = {
      ...view,
      may_qualify: rows.map((row) => ({ model: `${row.m.lab}/${row.m.id}`, offering: null, unknown: ["model.fits_hardware"] })),
      explanation: { ...view.explanation, feasible: [], may: rows },
    };
    render(<MayQualify decision={decision} spec={spec} vocabulary={vocabulary} />);
    expect(screen.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent))
      .toEqual(["Decision model", "Embedding model"]);
    expect([...document.querySelectorAll(".board-may-qualify > ul")].map((list) => [...list.querySelectorAll("strong")].map((name) => name.textContent)))
      .toEqual([["B decision", "Z decision"], ["A vector"]]);
  });

  it("groups by alphabetical class labels before model names, independent of capability and cost", () => {
    const spec = { ...realBaseSpec(vocabulary), boardWeights: {} };
    const view = mapDecisionToViewModel(fixture, spec, { axis: "task$", dismissed: [] });
    const base = view.explanation.feasible[0];
    const rows = [
      { ...base, m: { ...base.m, id: "vector", name: "A vector", type: "embed" }, cap: 100, cost: 0 },
      { ...base, m: { ...base.m, id: "z-decision", name: "Z decision", type: "decision" }, cap: 0, cost: 100 },
      { ...base, m: { ...base.m, id: "z-text", name: "Z text", type: "llm" } },
      { ...base, m: { ...base.m, id: "ranker", name: "Y ranker", type: "rerank" } },
      { ...base, m: { ...base.m, id: "b-decision", name: "B decision", type: "decision" } },
      { ...base, m: { ...base.m, id: "a-text", name: "A text", type: "llm" } },
    ] satisfies Row[];
    const decision = { ...view, explanation: { ...view.explanation, feasible: rows, may: [] } };
    render(<RankedAnswer decision={decision} spec={spec} vocabulary={vocabulary} />);
    expect(screen.getAllByRole("heading", { level: 2 }).map((heading) => heading.textContent))
      .toEqual(["Decision model", "Embedding model", "Reranker", "Text generator"]);
    const lists = document.querySelectorAll(".board-ranked-answer > ol");
    expect([...lists].map((list) => [...list.querySelectorAll(":scope > li strong")].map((name) => name.textContent)))
      .toEqual([["B decision", "Z decision"], ["A vector"], ["Y ranker"], ["A text", "Z text"]]);
    expect(screen.getByText("Not ranked yet: listed alphabetically")).toBeInTheDocument();
  });

  it("sorts qualifying and may-qualify models alphabetically without implying a winner", () => {
    const spec = { ...realBaseSpec(vocabulary), boardWeights: {} };
    const decision = mapDecisionToViewModel(fixture, spec, {
      axis: "task$", dismissed: [], models: vocabulary.models, providers: vocabulary.providers,
    });

    render(<RankedAnswer decision={decision} spec={spec} vocabulary={vocabulary} />);

    expect(screen.getByText("Not ranked yet: listed alphabetically")).toBeInTheDocument();
    const names = screen.getAllByRole("listitem").map((item) => item.querySelector("strong")?.textContent).filter(Boolean);
    expect(names).toEqual(names.slice().sort((left, right) => left!.localeCompare(right!)));
    expect(document.body).not.toHaveTextContent("#1");
  });
});
