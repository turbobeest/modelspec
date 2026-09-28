// What an empty decision was measured against (MODEL-153). Every sentence is
// built from the vocabulary's `coverage` counts and the decision's own funnel,
// eliminations and unknowns; nothing is written per question.
import type { Decision } from "../adapter/contract";
import { facetName, renderContractCondition, valueWithUnit } from "../adapter/condition-label";
import { contractCondition } from "../adapter/view-model";
import type { Cond, Spec } from "../engine/types";
import { CLASS_OF_TYPE } from "./index";
import type { Vocabulary } from "./index";

export interface LineupCoverage {
  /** One line per condition that emptied the answer or left models unknown. */
  needed: string[];
  /** What today's verified lineup holds. */
  covers: string;
  /** The engine's relaxations the page can apply: the condition's index in the spec. */
  relax: { index: number; label: string }[];
  /** The smallest change to a cap or floor that admits a model: replaces the condition at `index`. */
  relaxTo: { index: number; cond: Cond; label: string; admits: number }[];
}

/** The page condition `c` with its threshold moved to `value`, when it has one. */
function withThreshold(c: Cond, value: number): Cond | null {
  if ("max" in c && typeof c.max === "number") return { ...c, max: value } as Cond;
  if ("min" in c && typeof c.min === "number") return { ...c, min: value } as Cond;
  if (c.f === "facet" && typeof c.value === "number") return { ...c, value };
  return null;
}

const CLASS_NOUNS: Readonly<Record<string, readonly [string, string]>> = {
  "text-generator": ["text generator", "text generators"],
  vectoriser: ["embedding model", "embedding models"],
  orderer: ["reranker", "rerankers"],
  transcriber: ["speech recognition model", "speech recognition models"],
  analyser: ["vision model", "vision models"],
  decider: ["decision model", "decision models"],
};

function noun(classId: string, n: number): string {
  const [one, many] = CLASS_NOUNS[classId] ?? [
    `${classId.replaceAll("-", " ")} model`,
    `${classId.replaceAll("-", " ")} models`,
  ];
  return n === 1 ? one : many;
}

const count = (n: number, one: string, many = one + "s") => `${n} ${n === 1 ? one : many}`;

function list(items: string[]): string {
  return items.length < 2 ? items.join("") : `${items.slice(0, -1).join(", ")} and ${items.at(-1)}`;
}

const COMPARISON = /^([a-z][a-z0-9_.-]*)\s+(not in|in|!=|<=|>=|=|<|>)\s+(.+?)(\s+(?:@|soft\(|unknown\().*)?$/;

function askedClass(spec: Spec): string | null {
  for (const c of spec.conds) {
    if (c.f === "type") return CLASS_OF_TYPE[c.v];
    if (c.f === "facet" && c.facet === "model.class" && c.op === "=" && typeof c.value === "string")
      return c.value;
  }
  return null;
}

function neededLine(
  decision: Decision,
  step: Decision["eliminated"]["funnel"][number],
  v: Vocabulary,
): string {
  const coverage = v.coverage!;
  const [, facet, op, raw] = COMPARISON.exec(step.condition) ?? [];
  const label = renderContractCondition(step.condition);
  const out = decision.eliminated.models.filter((m) => m.condition === step.condition);
  const may = new Set(
    decision.may_qualify
      .filter((m) => facet && m.unknown.includes(facet))
      .map((m) => m.model),
  ).size;
  const mayText = may ? `; ${count(may, "model")} may qualify once it is recorded` : "";
  if (facet === "model.class" && op === "=") {
    const row = coverage.classes.find((c) => c.id === raw);
    if (row && row.models === 0) return `${label} — the lineup has no ${noun(row.id, 2)} yet`;
  }
  const known = v.facets.find((f) => f.id === facet);
  if (known && known.known === 0)
    return `${label} — not recorded for any of the ${count(known.of, known.subject)} yet${mayText}`;
  const remaining = new Set(out.map((m) => m.model)).size;
  let closest = "";
  const values = out.map((m) => m.value).filter((x): x is number => typeof x === "number");
  if (facet && values.length && (op === "<=" || op === "<" || op === ">=" || op === ">")) {
    const best = op.startsWith("<") ? Math.min(...values) : Math.max(...values);
    closest = `; the closest is ${valueWithUnit(facet, String(best))}`;
  }
  return `${label} — none of the ${count(remaining, "remaining model")}${closest}${mayText}`;
}

/** The coverage panel's content, or null when the decision answered or no coverage is published. */
export function lineupCoverage(
  decision: Decision,
  spec: Spec,
  v: Vocabulary,
): LineupCoverage | null {
  const coverage = v.coverage;
  if (!coverage || (decision.status !== "no_feasible" && decision.results.length)) return null;

  const funnel = decision.eliminated.funnel;
  const needed = funnel
    .filter((step) => (step.before > 0 && step.after === 0) || step.may_qualify > 0)
    .map((step) => neededLine(decision, step, v));
  const left = funnel.at(-1)?.after ?? 0;
  if (!needed.length && left > 0 && spec.w.cap > 0) {
    const name = v.benchmarks.find((b) => b.id === spec.bench)?.name ?? facetName(spec.bench);
    needed.push(`${name} — no model left after the conditions has a verified result to rank on`);
  }

  const classes = coverage.classes
    .filter((c) => c.models > 0)
    .sort((a, b) => b.models - a.models || a.id.localeCompare(b.id))
    .map((c) => `${c.models} ${noun(c.id, c.models)}`);
  const sentences = [
    `${count(coverage.models, "model")}${coverage.as_of ? ` as of ${coverage.as_of}` : ""}, ` +
      `${coverage.verified} with verified evidence.`,
  ];
  if (classes.length) sentences.push(`By class: ${list(classes)}.`);
  const asked = askedClass(spec);
  const row = coverage.classes.find((c) => c.id === asked);
  if (row && row.models === 0) {
    const plural = noun(row.id, 2);
    sentences.push(`No ${plural} yet.`);
  } else if (row && spec.domain) {
    const domain = coverage.domains.find((d) => d.id === spec.domain);
    const n = row.domains.find((d) => d.id === spec.domain)?.verified ?? 0;
    if (domain)
      sentences.push(
        `${n} ${noun(row.id, n)} with verified ${domain.name.toLowerCase()} evidence.`,
      );
  }

  const relax = decision.relax.flatMap((condition) => {
    const index = spec.conds.findIndex((c) => contractCondition(c) === condition);
    return index < 0 ? [] : [{ index, label: renderContractCondition(condition) }];
  });
  // Only what the page can apply exactly: the moved condition must be the engine's.
  const relaxTo = decision.relax_to.flatMap((r) => {
    const index = spec.conds.findIndex((c) => contractCondition(c) === r.condition);
    const cond = index < 0 ? null : withThreshold(spec.conds[index], r.value);
    return cond && contractCondition(cond) === r.relaxed
      ? [{ index, cond, label: renderContractCondition(r.relaxed), admits: r.admits }]
      : [];
  });
  return { needed, covers: sentences.join(" "), relax, relaxTo };
}
