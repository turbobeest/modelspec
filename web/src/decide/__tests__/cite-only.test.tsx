import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import rawDecision from "../__fixtures__/live-assistant-balanced-full.json";
import { vocabularySchema, realBaseSpec } from "../vocabulary";
import { decisionSchema } from "../adapter/contract";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { SimpleAnswer } from "../simple/Answer";
import { defaultChoices, selectJob } from "../simple/model";
import { RankedAnswer } from "../facet-board/RankedAnswer";

const vocabulary = vocabularySchema.parse(rawVocabulary);
const decision = decisionSchema.parse(rawDecision);
const warning = "cite_only_not_machine_verified";
const notice = "Cited, not machine-verified";

it("shows citation assurance on the simple answer even when the cited row was trimmed", () => {
  const selection = selectJob(vocabulary, defaultChoices);
  if (!selection) throw new Error("Fixture requires an available template");
  render(<SimpleAnswer decision={{ ...decision, warnings: [warning] }} vocabulary={vocabulary}
    selection={selection} onRemoveLimit={vi.fn()} onTryAllRoutes={vi.fn()} />);
  expect(screen.getByText(new RegExp(notice))).toBeVisible();
});

it("shows citation assurance beside the detailed answer's affected model", () => {
  const changed = structuredClone(decision);
  const row = changed.results[0];
  if (!row) throw new Error("Fixture requires a ranked result");
  row.warnings.push(warning);
  changed.warnings.push(warning);
  const spec = { ...realBaseSpec(vocabulary), boardWeights: { chat_preference: 1 } };
  const view = mapDecisionToViewModel(changed, spec, {
    axis: "task$", dismissed: [], models: vocabulary.models, providers: vocabulary.providers,
  });
  render(<RankedAnswer decision={view} spec={spec} vocabulary={vocabulary} />);
  expect(screen.getAllByText(new RegExp(notice)).length).toBeGreaterThan(0);
});
