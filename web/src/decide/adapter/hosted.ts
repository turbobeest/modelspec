import { decisionSchema } from "./contract";
import type { Decision, DecisionSpec } from "./contract";

export const DECIDE_ENDPOINT = "https://api.modelspec.dev/v1/decide";

function apiError(payload: unknown): { code: string | null; message: string | null } {
  if (!payload || typeof payload !== "object" || !("error" in payload))
    return { code: null, message: null };
  const error = payload.error;
  if (typeof error === "string") return { code: null, message: error };
  if (!error || typeof error !== "object") return { code: null, message: null };
  return {
    code: "code" in error && typeof error.code === "string" ? error.code : null,
    message:
      "message" in error && typeof error.message === "string"
        ? error.message
        : null,
  };
}

export class DecideApiError extends Error {
  readonly status: number | null;
  readonly code: string | null;

  constructor(
    message: string,
    status: number | null,
    code: string | null,
  ) {
    super(message);
    this.name = "DecideApiError";
    this.status = status;
    this.code = code;
  }
}

export interface HostedDecisionEngine {
  decide(spec: DecisionSpec, options?: { signal?: AbortSignal }): Promise<Decision>;
}

export const hostedEngine: HostedDecisionEngine = {
  async decide(spec, options = {}) {
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
        signal: options.signal,
      });
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") throw error;
      throw new DecideApiError("The decision service could not be reached.", null, null);
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
