import { z } from "zod";
import type { DecisionSpec } from "./adapter/contract";

declare const __DECIDE_HANDOFF__: unknown;

export const handoffData = z.object({
  summary_price_cents: z.string(),
  full_credits: z.number().int().positive(),
  key_link: z.object({ href: z.string(), label: z.string(), note: z.string() }),
  mcp_clients: z.array(z.string()).nonempty(),
  neutrality: z.object({ text: z.string(), href: z.url() }),
}).parse(__DECIDE_HANDOFF__);

export const RUN = "uvx --from modelspec-dev modelspec";
export const ORIENT = `${RUN} help agent`;

/** One pasteable message: orientation first, then the exact Spec the page POSTs. */
export function handoffMessage(spec: DecisionSpec): string {
  return `Run \`${ORIENT}\`, then decide with this spec:\n\n${JSON.stringify(spec, null, 2)}`;
}
