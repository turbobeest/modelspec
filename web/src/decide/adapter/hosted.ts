import { decisionSchema } from "./contract";
import type { Decision, DecisionSpec } from "./contract";

/** Where the page sends specs. Local development points it at a Vite proxy. */
export const DECIDE_ENDPOINT: string =
  import.meta.env.VITE_DECIDE_ENDPOINT ?? "https://api.modelspec.dev/v1/decide";
/** The public endpoint, for the copy-and-paste API call in Share. */
export const PUBLIC_DECIDE_ENDPOINT = "https://api.modelspec.dev/v1/decide";
/** A request that has not answered by then is reported, never left spinning. */
export const DECIDE_TIMEOUT_MS = 30_000;

/** One thing the engine could not accept in a spec (a 400's `error.issues`). */
export interface SpecIssue {
  path: string;
  condition: string | null;
  field: string | null;
  reason: string;
}

function apiError(payload: unknown): {
  code: string | null;
  message: string | null;
  issues: SpecIssue[];
} {
  const none = { code: null, message: null, issues: [] };
  if (!payload || typeof payload !== "object" || !("error" in payload)) return none;
  const error = payload.error;
  // The Worker's 503 before a snapshot is published: {"error": "no_snapshot", "message": …}.
  if (typeof error === "string")
    return {
      code: error,
      message:
        "message" in payload && typeof payload.message === "string" ? payload.message : null,
      issues: [],
    };
  if (!error || typeof error !== "object") return none;
  const issues =
    "issues" in error && Array.isArray(error.issues)
      ? error.issues.flatMap((raw: unknown): SpecIssue[] => {
          if (!raw || typeof raw !== "object") return [];
          const get = (key: string) =>
            key in raw && typeof (raw as Record<string, unknown>)[key] === "string"
              ? ((raw as Record<string, unknown>)[key] as string)
              : null;
          const reason = get("reason");
          return reason === null
            ? []
            : [{ path: get("path") ?? "", condition: get("condition"), field: get("field"), reason }];
        })
      : [];
  return {
    code: "code" in error && typeof error.code === "string" ? error.code : null,
    message: "message" in error && typeof error.message === "string" ? error.message : null,
    issues,
  };
}

export class DecideApiError extends Error {
  readonly status: number | null;
  readonly code: string | null;
  readonly issues: SpecIssue[];

  constructor(
    message: string,
    status: number | null,
    code: string | null,
    issues: SpecIssue[] = [],
  ) {
    super(message);
    this.name = "DecideApiError";
    this.status = status;
    this.code = code;
    this.issues = issues;
  }
}

export interface HostedDecisionEngine {
  decide(spec: DecisionSpec, options?: { signal?: AbortSignal }): Promise<Decision>;
}

export const hostedEngine: HostedDecisionEngine = {
  async decide(spec, options = {}) {
    const timeout = new AbortController();
    const timer = setTimeout(() => timeout.abort(), DECIDE_TIMEOUT_MS);
    const abort = () => timeout.abort();
    options.signal?.addEventListener("abort", abort, { once: true });
    let response: Response;
    try {
      response = await fetch(DECIDE_ENDPOINT, {
        method: "POST",
        mode: "cors",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(spec),
        signal: timeout.signal,
      });
    } catch (error) {
      if (options.signal?.aborted) throw new DOMException("Aborted", "AbortError");
      if (timeout.signal.aborted)
        throw new DecideApiError(
          `The decision service did not answer within ${DECIDE_TIMEOUT_MS / 1000} seconds.`,
          null,
          "timeout",
        );
      if (error instanceof Error && error.name === "AbortError") throw error;
      throw new DecideApiError("The decision service could not be reached.", null, null);
    } finally {
      clearTimeout(timer);
      options.signal?.removeEventListener("abort", abort);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new DecideApiError(
        `The decision service returned a non-JSON response (${response.status}).`,
        response.status,
        null,
      );
    }
    if (!response.ok) {
      const parsed = apiError(payload);
      throw new DecideApiError(
        parsed.message ?? `The decision service returned HTTP ${response.status}.`,
        response.status,
        parsed.code,
        parsed.issues,
      );
    }

    const parsed = decisionSchema.safeParse(payload);
    if (!parsed.success) {
      throw new DecideApiError(
        "The decision service returned an invalid decision response.",
        response.status,
        "invalid_response",
      );
    }
    return parsed.data;
  },
};
