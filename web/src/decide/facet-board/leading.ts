import type { AdapterDecision } from "../adapter";

/**
 * The models best for the board's weights: the engine's best band when it
 * sends bands, else its answer's deterministic order (one leader, or the tied
 * group). Null when the engine sent neither, so nothing is known.
 */
export function leadingModels(decision: AdapterDecision): string[] | null {
  if (decision.bands) return decision.bands.best.map((entry) => entry.model);
  if (decision.answer) return decision.answer.deterministic_order;
  return null;
}

/** Names a single leader; a tied answer has no best-now headline. */
export function bestNowLine(decision: AdapterDecision, ranked: boolean): string | null {
  if (decision.answer?.kind === "tied") return null;
  const leading = ranked ? leadingModels(decision) : null;
  if (leading === null) return null;
  if (leading.length === 0) return "Best now: none has enough evidence yet";
  const names = new Map(decision.explanation.feasible.map((row) => [`${row.m.lab}/${row.m.id}`, row.m.name]));
  return leading.length === 1 ? `Best now: ${names.get(leading[0]) ?? leading[0]}` : null;
}
