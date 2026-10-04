import { z } from "zod";

declare const __DECIDE_HANDOFF__: unknown;

export const handoffData = z.object({
  summary_price_cents: z.string(),
  full_credits: z.number().int().positive(),
  key_link: z.object({ href: z.string(), note: z.string() }),
  neutrality: z.object({ text: z.string(), href: z.url() }),
}).parse(__DECIDE_HANDOFF__);
