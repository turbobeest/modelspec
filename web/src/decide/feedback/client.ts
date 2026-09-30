import { z } from "zod";
import { FEEDBACK_RATINGS } from "../adapter/contract";
import type { FeedbackRating } from "../adapter/contract";

/** MODEL-221. Local development points it at a Worker from `pywrangler dev`. */
export const FEEDBACK_ENDPOINT: string =
  import.meta.env.VITE_FEEDBACK_ENDPOINT ?? "https://api.modelspec.dev/v1/feedback";
export const FEEDBACK_TIMEOUT_MS = 15_000;

export { FEEDBACK_RATINGS };
export type { FeedbackRating };

export const RATING_LABELS: Record<FeedbackRating, string> = {
  reliable: "Reliable",
  unreliable: "Unreliable",
  trustworthy: "Trustworthy",
  untrustworthy: "Untrustworthy",
  confusing: "Confusing",
};

const envelope = {
  schema_version: z.literal("1.0"),
  endpoint: z.literal("feedback"),
  service_commit: z.string(),
};
const redaction = z.enum(["card", "email", "id_number", "ip", "phone", "secret", "url_query"]);

/** What the Worker answers. Strict, so a field it starts sending is noticed. */
export const feedbackResultSchema = z.union([
  z
    .object({
      ...envelope,
      status: z.literal("recorded"),
      recorded: z.literal(true),
      receipt: z.string().regex(/^fbr_\d{8}_[0-9a-f]{32}$/),
      retention_days: z.number().int().positive(),
      redacted: z.array(redaction),
      message: z.string(),
      privacy: z.string().url(),
    })
    .strict(),
  z
    .object({
      ...envelope,
      status: z.literal("not_recorded"),
      recorded: z.literal(false),
      receipt: z.null(),
      retention_days: z.null(),
      redacted: z.array(redaction),
      message: z.string(),
      privacy: z.string().url(),
    })
    .strict(),
  z
    .object({ ...envelope, status: z.literal("deleted"), recorded: z.literal(false) })
    .strict(),
]);
export type FeedbackResult = z.infer<typeof feedbackResultSchema>;

export const feedbackErrorSchema = z
  .object({
    ...envelope,
    error: z
      .object({
        code: z.string(),
        message: z.string(),
        retry_after: z.number().int().optional(),
      })
      .strict(),
  })
  .strict();

export interface FeedbackBody {
  rating: FeedbackRating;
  client: "page";
  decision_id?: string;
  note?: string;
  trying_to_decide?: string;
  page?: string;
  template?: string;
}

export class FeedbackError extends Error {
  readonly code: string | null;
  constructor(message: string, code: string | null) {
    super(message);
    this.name = "FeedbackError";
    this.code = code;
  }
}

async function call(method: "POST" | "DELETE", body: unknown): Promise<FeedbackResult> {
  const timeout = new AbortController();
  const timer = setTimeout(() => timeout.abort(), FEEDBACK_TIMEOUT_MS);
  try {
    let response: Response;
    try {
      response = await fetch(FEEDBACK_ENDPOINT, {
        method,
        mode: "cors",
        // No credentials and no key: feedback is anonymous by construction.
        credentials: "omit",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
        signal: timeout.signal,
      });
    } catch {
      throw new FeedbackError("Feedback could not be sent. Check your connection and try again.", null);
    }
    const payload: unknown = await response.json().catch(() => null);
    if (response.ok) {
      const parsed = feedbackResultSchema.safeParse(payload);
      if (parsed.success) return parsed.data;
      throw new FeedbackError("The feedback service answered in an unexpected shape.", null);
    }
    const refused = feedbackErrorSchema.safeParse(payload);
    throw refused.success
      ? new FeedbackError(refused.data.error.message, refused.data.error.code)
      : new FeedbackError(`The feedback service answered HTTP ${response.status}.`, null);
  } finally {
    clearTimeout(timer);
  }
}

/** Only non-empty optional fields are sent. */
export function feedbackBody(input: FeedbackBody): FeedbackBody {
  const out: FeedbackBody = { rating: input.rating, client: "page" };
  for (const key of ["decision_id", "note", "trying_to_decide", "page", "template"] as const) {
    const value = input[key]?.trim();
    if (value) out[key] = value;
  }
  return out;
}

export function sendFeedback(input: FeedbackBody): Promise<FeedbackResult> {
  return call("POST", feedbackBody(input));
}

export function withdrawFeedback(receipt: string): Promise<FeedbackResult> {
  return call("DELETE", { receipt });
}
