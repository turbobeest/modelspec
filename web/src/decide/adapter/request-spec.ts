import type { Spec } from "./index";
import type { DecisionSpec } from "./contract";
import { sendable, type Vocabulary } from "../vocabulary";
import { toBoardDecisionSpec } from "../facet-board/model";

/** One conversion for the live request and the visitor's agent hand-off. */
export function prepareDecisionRequest(
  vocabulary: Vocabulary | null,
  source: Spec,
  explain: NonNullable<DecisionSpec["explain"]>,
) {
  const boardSpec = vocabulary ? sendable(vocabulary, source) : source;
  return { boardSpec, decisionSpec: toBoardDecisionSpec(boardSpec, explain) };
}
