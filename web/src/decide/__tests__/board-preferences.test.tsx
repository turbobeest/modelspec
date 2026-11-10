import { render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { FacetBoard } from "../facet-board/FacetBoard";
import { boardToSpec, decodeBoardState, encodeBoardSpec, facetGroup, sanitizeBoardState } from "../facet-board/model";
import { prepareDecisionRequest } from "../adapter/request-spec";
import { baseSpec, decodeSpec } from "../state/spec";
import { vocabularySchema } from "../vocabulary";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import { openGroup } from "./board-helpers";

const vocabulary = vocabularySchema.parse(rawVocabulary);

it.each([
  { facet: "capability.software_engineering", saved: "chat_preference", canonical: "software_engineering" },
  { facet: "model.context_window", saved: "model.max_output_tokens", canonical: "model.context_window" },
  { facet: "capability.software_engineering", saved: "-software_engineering", canonical: "software_engineering" },
  { facet: "offering.cost_per_task", saved: "offering.cost_per_task", canonical: "-offering.cost_per_task" },
  { facet: "model.context_window", saved: "-model.context_window", canonical: "model.context_window" },
  { facet: "model.weights_openness", saved: "-model.weights_openness", canonical: "model.weights_openness", value: "open_weights" },
])("restores the displayed preference and direction for $facet from $saved", ({ facet, saved, canonical, value }) => {
  const hash = encodeBoardSpec({ ...baseSpec, conds: [] }, "task$", {
    selections: { [facet]: { mode: "prefer", weight: 1, weightKey: saved, ...(value ? { value } : {}) } },
    mustOrder: [], estate: { providers: [], plans: [], hardware: [] },
  });
  const decoded = decodeSpec(hash);
  const board = decodeBoardState(hash);
  if (!decoded || !board) throw new Error("Preference fixture must decode");
  const restored = sanitizeBoardState(board, vocabulary);
  const spec = boardToSpec(decoded.spec, vocabulary, restored.selections, restored.mustOrder);
  const request = prepareDecisionRequest(vocabulary, spec, "summary").decisionSpec;
  render(<FacetBoard vocabulary={vocabulary} spec={spec} selections={restored.selections}
    mustOrder={restored.mustOrder} estate={restored.estate} notes={restored.notes}
    onSpec={() => undefined} onEstate={() => undefined} />);
  openGroup(facetGroup(facet));
  const label = facet.startsWith("capability.")
    ? vocabulary.domains.find((domain) => `capability.${domain.id}` === facet)?.name
    : vocabulary.facets.find((row) => row.id === facet)?.label;
  expect(within(screen.getByRole("radiogroup", { name: `State for ${label}` })).getByLabelText("Prefer")).toBeChecked();
  expect.soft(request.optimize).toEqual({ weights: { [canonical]: value ? { prefer: value, weight: 1 } : 1 } });
  expect(restored.selections[facet].weightKey).toBe(canonical);
  expect(screen.getByRole("note", { name: "Notes from your old decision link" })).toHaveTextContent("preference");
});
