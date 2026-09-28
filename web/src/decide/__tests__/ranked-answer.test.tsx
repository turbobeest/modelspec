import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { RankedAnswer } from "../facet-board/RankedAnswer";
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
