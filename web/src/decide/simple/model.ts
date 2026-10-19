import type { AccessKind } from "../adapter/contract";
import { baseSpec } from "../state/spec";
import type { Spec } from "../engine/types";
import { boardToSpec, encodeBoardSpec, parseBoardCondition, sanitizeBoardState, templateToBoard } from "../facet-board/model";
import type { BoardUrlState } from "../facet-board/model";
import type { VocabTemplate, Vocabulary } from "../vocabulary";
import { sendable } from "../vocabulary";

export type Priority = "budget" | "balanced" | "best";
export type Job = "everyday" | "coding" | "writing" | "documents" | "volume" | "self-host";
export type Limit = "open" | "eu" | "no-training";
export interface Choices {
  job: Job;
  priority: Priority;
  limits: Limit[];
  route: AccessKind | "any";
  removedFacets: string[];
}
export const defaultChoices: Choices = { job: "everyday", priority: "balanced", limits: [], route: "any", removedFacets: [] };
export const priorities: { id: Priority; label: string }[] = [
  { id: "budget", label: "Spend less" }, { id: "balanced", label: "Balanced" }, { id: "best", label: "Quality counts most" },
];
export const jobs: { id: Job; label: string; subtitle: string; templates: Record<Priority, string> }[] = [
  { id: "everyday", label: "Everyday help", subtitle: "Questions and conversation", templates: { budget: "assistant-budget", balanced: "assistant-balanced", best: "assistant-best" } },
  { id: "coding", label: "Coding", subtitle: "Build, debug and review", templates: { budget: "budget-coding", balanced: "coding-balanced", best: "coding-best" } },
  { id: "writing", label: "Writing", subtitle: "Drafts and editing", templates: { budget: "writing-budget", balanced: "writing-balanced", best: "writing-best" } },
  { id: "documents", label: "Long documents", subtitle: "Read and summarise", templates: { budget: "documents-budget", balanced: "long-documents", best: "documents-best" } },
  { id: "volume", label: "High volume", subtitle: "Many short requests", templates: { budget: "high-volume", balanced: "high-volume-balanced", best: "high-volume-best" } },
  { id: "self-host", label: "Self-hosting", subtitle: "Open weights you run", templates: { budget: "assistant-budget", balanced: "assistant-balanced", best: "assistant-best" } },
];
export const limitDefinitions: { id: Limit; label: string; facet: string; template: string }[] = [
  { id: "open", label: "Open weights", facet: "model.weights_openness", template: "private-self-host" },
  { id: "eu", label: "EU residency", facet: "offering.region", template: "eu-data" },
  { id: "no-training", label: "No customer-data training", facet: "offering.data.trains_on_customer_data", template: "eu-data" },
];

export function supportedLimits(vocabulary: Vocabulary) {
  return limitDefinitions.filter((limit) => vocabulary.facets.some((facet) => facet.id === limit.facet && facet.has_data !== false && facet.known !== 0)
    && vocabulary.templates?.some((template) => template.id === limit.template && template.where.some((row) => parseBoardCondition(row.condition).facetId === limit.facet)));
}

export interface Selection {
  choices: Choices;
  jobLabel: string;
  priorityLabel: string;
  template: VocabTemplate;
  spec: Spec;
  board: BoardUrlState;
  limits: { facet: string; label: string; condition: string }[];
}

export function selectJob(vocabulary: Vocabulary, choices: Choices): Selection | null {
  const supported = supportedLimits(vocabulary);
  if (choices.limits.some((id) => !supported.some((limit) => limit.id === id))) return null;
  if (choices.job === "self-host" && choices.removedFacets.some((facet) => facet === "model.weights_openness" || facet === "licence.commercial_use")) return null;
  const job = jobs.find((item) => item.id === choices.job);
  const template = vocabulary.templates?.find((item) => item.id === job?.templates[choices.priority] && item.available);
  if (!job || !template) return null;
  const additional = supported.filter((limit) => choices.limits.includes(limit.id)).flatMap((limit) =>
    vocabulary.templates?.find((item) => item.id === limit.template)?.where.filter((row) => parseBoardCondition(row.condition).facetId === limit.facet) ?? [],
  );
  if (choices.job === "self-host") {
    const selfHost = vocabulary.templates?.find((item) => item.id === "private-self-host");
    if (!selfHost?.available) return null;
    additional.push(...selfHost.where.filter((row) => /^(model.weights_openness|licence.commercial_use) /.test(row.condition)));
  }
  const where = [...new Map([...template.where, ...additional].map((row) => [parseBoardCondition(row.condition).facetId, row])).values()]
    .filter((row) => !choices.removedFacets.includes(parseBoardCondition(row.condition).facetId));
  const converted = templateToBoard({ ...template, where }, vocabulary);
  const board = sanitizeBoardState({ ...converted, estate: { providers: [], plans: [], hardware: [] } }, vocabulary);
  // An unavailable hard requirement cannot silently become an unrestricted question.
  if (converted.mustOrder.some((facet) => !board.mustOrder.includes(facet))) return null;
  const tokens = converted.taskTokens ?? vocabulary.default_task_tokens;
  const spec = sendable(vocabulary, boardToSpec({ ...baseSpec, task: "", conds: [], tokIn: tokens.input, tokOut: tokens.output,
    ...(choices.route === "any" ? {} : { access: choices.route }),
  }, vocabulary, board.selections, board.mustOrder));
  const limits = where.flatMap((row) => {
    const { facetId, value } = parseBoardCondition(row.condition);
    if (facetId === "model.class" || facetId === "model.lifecycle") return [];
    const label = limitDefinitions.find((limit) => limit.facet === facetId)?.label
      ?? (facetId === "offering.cost_per_task" ? `At most $${value} per task`
        : facetId === "model.context_window" ? `Context at least ${Number(value).toLocaleString("en-US")} tokens`
        : facetId === "licence.commercial_use" ? "Commercial use allowed with stated conditions"
        : vocabulary.facets.find((facet) => facet.id === facetId)?.label ?? row.condition);
    return [{ facet: facetId, label, condition: row.condition }];
  });
  return { choices, jobLabel: job.label, priorityLabel: priorities.find((item) => item.id === choices.priority)?.label ?? choices.priority, template, spec, board, limits };
}

export const evidenceLink = (selection: Selection) => `/decide/details/${encodeBoardSpec(selection.spec, "task$", selection.board)}`;
export const legacyDestination = (search: string, hash: string): string | null =>
  hash.startsWith("#s=") || new URLSearchParams(search).has("template") ? `/decide/details/${search}${hash}` : null;
