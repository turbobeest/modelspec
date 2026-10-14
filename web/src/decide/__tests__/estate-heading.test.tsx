import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import codingJson from "../__fixtures__/plans-coding-full.json";
import ownSoftwareJson from "../__fixtures__/plans-own-software-full.json";
import vendorCodingJson from "../__fixtures__/plans-vendor-coding-full.json";
import { decisionSchema } from "../adapter/contract";
import type { Decision } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { RankedAnswer } from "../facet-board/RankedAnswer";
import { estateAsDecision } from "../facet-board/routes";
import type { EstateMark } from "../adapter/contract";
import { realBaseSpec } from "../vocabulary";
import { planVocabulary } from "./plan-vocabulary";

// MODEL-389. The estate answer ranks its own leader or tie. The heading must
// name that answer, including when the unrestricted band names someone else.
const spec = {
  ...realBaseSpec(planVocabulary),
  boardWeights: { software_engineering: 1 },
};
const UNRESTRICTED = "other/huge";
const OPUS = "anthropic/claude-opus-5-5";
const SONNET = "anthropic/claude-sonnet-5";

function show(decision: Decision, marks?: Map<string, EstateMark>) {
  const view = mapDecisionToViewModel(decision, spec, {
    axis: "task$",
    dismissed: [],
    models: planVocabulary.models,
    providers: planVocabulary.providers,
  });
  render(<RankedAnswer decision={view} spec={spec} vocabulary={planVocabulary} marks={marks} />);
}

function bestHeading(): HTMLElement {
  return screen.getByRole("heading", { name: /^Best for your weights/ });
}

it("keeps the unrestricted heading on the unrestricted band leader", () => {
  show(decisionSchema.parse(codingJson));
  expect(bestHeading()).toHaveTextContent(`Best for your weights: ${UNRESTRICTED}`);
});

it("names the estate tie, not the unrestricted band leader", () => {
  const decision = decisionSchema.parse(codingJson);
  expect(decision.bands?.leader).toBe(UNRESTRICTED);
  expect(decision.with_estate?.answer?.deterministic_order).toEqual([OPUS, SONNET]);
  const held = estateAsDecision(decision);
  if (!held) throw new Error("expected an estate answer");
  show(held.decision, held.marks);

  const heading = bestHeading();
  expect(heading).toHaveTextContent(
    "Best for your weights: these 2. The evidence can't separate them.",
  );
  expect(heading).not.toHaveTextContent(UNRESTRICTED);
  const block = heading.closest("section");
  if (!block) throw new Error("expected the answer section");
  const group = block.querySelector(".board-tie-group");
  if (!(group instanceof HTMLElement)) throw new Error("expected the tied members");
  expect(within(group).getAllByRole("listitem").map((item) => item.querySelector("strong")?.textContent))
    .toEqual(["Claude Opus 5.5", "Claude Sonnet 5"]);
});

it("names a separated estate leader when that leader is not the unrestricted one", () => {
  const decision = decisionSchema.parse(codingJson);
  const estate = decision.with_estate;
  if (!estate?.answer) throw new Error("fixture has no estate answer");
  const separated = decisionSchema.parse({
    ...decision,
    with_estate: {
      ...estate,
      answer: {
        kind: "separated",
        members: [SONNET],
        leader: SONNET,
        basis: estate.answer.basis,
        tie_breakers: estate.answer.tie_breakers,
        deterministic_order: [SONNET],
      },
    },
  });
  const held = estateAsDecision(separated);
  if (!held) throw new Error("expected an estate answer");
  show(held.decision, held.marks);

  const heading = bestHeading();
  expect(heading).toHaveTextContent("Best for your weights: Claude Sonnet 5");
  expect(heading).not.toHaveTextContent(UNRESTRICTED);
});

it("keeps the estate heading when the estate leader is the unrestricted leader", () => {
  const decision = decisionSchema.parse(vendorCodingJson);
  expect(decision.with_estate?.answer?.kind).toBe("separated");
  const held = estateAsDecision(decision);
  if (!held) throw new Error("expected an estate answer");
  show(held.decision, held.marks);
  expect(bestHeading()).toHaveTextContent(`Best for your weights: ${UNRESTRICTED}`);
});

it("does not give an estate answer with no leader the unrestricted heading", () => {
  const decision = decisionSchema.parse(ownSoftwareJson);
  expect(decision.with_estate?.answer ?? null).toBeNull();
  expect(decision.bands?.leader).toBe(UNRESTRICTED);
  const held = estateAsDecision(decision);
  if (!held) throw new Error("expected an estate answer");
  show(held.decision, held.marks);
  expect(screen.queryByRole("heading", { name: /^Best for your weights/ })).not.toBeInTheDocument();
});
