import rawVocabulary from "../src/decide/__fixtures__/live-vocabulary.json";
import { vocabularySchema } from "../src/decide/vocabulary";
import type { VocabTemplate } from "../src/decide/vocabulary";
import { baseSpec } from "../src/decide/state/spec";
import type { Spec } from "../src/decide/engine/types";
import { boardToSpec, encodeBoardSpec, sanitizeBoardState, templateToBoard } from "../src/decide/facet-board/model";
import type { BoardUrlState } from "../src/decide/facet-board/model";
import { fastTrackTemplates } from "../src/decide/facet-board/templates";

export const vocabulary = vocabularySchema.parse(rawVocabulary);
export type Selection = { spec: Spec; board: BoardUrlState; template: VocabTemplate };
export type Budget = "budget" | "balanced" | "best";
export type Limit = "none" | "open" | "cost" | "eu";
const labels: Record<string, [string, string]> = {
  "assistant-balanced": ["Everyday help", "Questions & conversation"],
  "coding-balanced": ["Coding", "Build, debug & review"],
  "writing-balanced": ["Writing", "Drafts & editing"],
  "long-documents": ["Long documents", "Read & summarise"],
  "high-volume": ["High volume", "Many short requests"],
  "private-self-host": ["Self-hosting", "Open weights"],
};
export const jobs = fastTrackTemplates(vocabulary).map((template) => ({
  id: template.id,
  label: labels[template.id]?.[0] ?? template.name,
  detail: labels[template.id]?.[1] ?? template.purpose,
  template,
}));

export function selectTemplate(template: VocabTemplate): Selection {
  const converted = templateToBoard(template, vocabulary);
  const board = sanitizeBoardState({ ...converted, estate: { providers: [], plans: [], hardware: [] } }, vocabulary);
  const tokens = converted.taskTokens ?? vocabulary.default_task_tokens;
  const spec = boardToSpec({ ...baseSpec, task: "", conds: [], tokIn: tokens.input, tokOut: tokens.output }, vocabulary, board.selections, board.mustOrder);
  return { template, board, spec };
}

export function initialSelection(): Selection {
  const template = vocabulary.templates?.find((item) => item.id === "assistant-balanced");
  if (!template) throw new Error("The vocabulary has no assistant template.");
  return selectTemplate(template);
}

export function choose(jobId: string, budget: Budget, limit: Limit = "none"): Selection {
  const job = jobs.find((item) => item.id === jobId);
  if (!job) throw new Error("Unknown prototype job.");
  const tier = vocabulary.templates?.find((item) => item.category === job.template.category && item.tier === budget);
  let selection = selectTemplate(tier ?? job.template);
  // The self-host job keeps its licence and open-weight gates at every tier.
  const additional = job.id === "private-self-host" ? job.template.where : [];
  const gateTemplate = limit === "open" ? vocabulary.templates?.find((item) => item.id === "private-self-host")
    : limit === "eu" ? vocabulary.templates?.find((item) => item.id === "eu-data")
    : limit === "cost" ? vocabulary.templates?.find((item) => item.id === "assistant-budget") : undefined;
  const gates = [
    ...additional,
    ...(gateTemplate?.where.filter((item) => limit === "cost" ? item.condition.startsWith("offering.cost_per_task")
      : limit === "open" ? item.condition.startsWith("model.weights_openness") : true) ?? []),
  ];
  if (gates.length) {
    const existing = new Set(selection.template.where.map((item) => item.condition));
    selection = selectTemplate({ ...selection.template, where: [...selection.template.where, ...gates.filter((item) => !existing.has(item.condition))] });
  }
  return selection;
}

export const evidenceLink = (selection: Selection) => `/decide/${encodeBoardSpec(selection.spec, "task$", selection.board)}`;
