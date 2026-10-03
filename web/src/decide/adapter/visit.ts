import { z } from "zod";

export const VISIT_GATE_ENABLED = import.meta.env.VITE_VISIT_GATE_ENABLED === "true";
const endpoint = (path: string) => (import.meta.env.VITE_DECIDE_ENDPOINT ?? "https://api.modelspec.dev/v1/decide").replace(/\/v1\/decide\/?$/, path);
const credentialSchema = z.object({ token: z.string().min(1), expires_at: z.number().int().positive() });
const statusSchema = z.union([
  z.object({ enabled: z.literal(false) }),
  z.object({ enabled: z.literal(true), mode: z.literal("visit"), day_limit: z.number().int().positive(), burst_limit: z.number().int().positive() }),
  z.object({ enabled: z.literal(true), remaining: z.number().int().nonnegative() }),
]);
export type Challenge = { resolve: (token: string) => void; reject: (error: Error) => void };
let listener: ((challenge: Challenge | null) => void) | null = null;
let challenge: Challenge | null = null;
let credential: z.infer<typeof credentialSchema> | null = null;
let checking: Promise<void> | null = null;
let status: Promise<boolean> | null = null;
let modeEnabled = false;

export function visitGateActive(): boolean { return modeEnabled; }

export function registerChallenge(next: NonNullable<typeof listener>): () => void {
  listener = next;
  next(challenge);
  return () => { if (listener === next) listener = null; };
}

async function active(): Promise<boolean> {
  if (!VISIT_GATE_ENABLED) return false;
  if (!status) status = fetch(endpoint("/v1/human-status"), { mode: "cors", signal: AbortSignal.timeout(15_000) }).then(async (response) => {
    if (!response.ok) throw new Error("Human verification is temporarily unavailable.");
    const value = statusSchema.parse(await response.json());
    modeEnabled = value.enabled && "mode" in value && value.mode === "visit";
    return modeEnabled;
  }).catch((error: unknown) => { status = null; throw error; });
  return status;
}

export async function prepareVisit(): Promise<void> {
  if (!await active()) return;
  if (credential && credential.expires_at * 1000 > Date.now()) return;
  if (!checking) checking = (async () => {
    const token = await new Promise<string>((resolve, reject) => {
      challenge = { resolve, reject };
      listener?.(challenge);
    });
    const response = await fetch(endpoint("/v1/visit-token"), {
      method: "POST", mode: "cors", headers: { "X-ModelSpec-Turnstile": token },
      signal: AbortSignal.timeout(15_000),
    });
    if (!response.ok) throw new Error("Human verification failed. Please try again.");
    credential = credentialSchema.parse(await response.json());
  })().finally(() => { checking = null; challenge = null; listener?.(null); });
  return checking;
}

export async function visitFetch(url: string, options: RequestInit): Promise<Response> {
  if (!VISIT_GATE_ENABLED) return fetch(url, options);
  const send = (headers: HeadersInit | undefined) => {
    const deadline = AbortSignal.timeout(30_000);
    const signal = options.signal ? AbortSignal.any([options.signal, deadline]) : deadline;
    return fetch(url, { ...options, headers, signal });
  };
  // Static vocabulary has a deadline but never receives a visit credential.
  if (!/\/v1\/(?:decide|vocabulary)\/?(?:\?|$)/.test(url)) return send(options.headers);
  for (let attempt = 0; attempt < 2; attempt++) {
    const gated = await active();
    if (gated) await prepareVisit();
    options.signal?.throwIfAborted();
    const sent = gated ? credential : null;
    const headers = new Headers(options.headers);
    if (sent) headers.set("X-ModelSpec-Visit-Token", sent.token);
    // Each exchange has a deadline; a person completing the widget does not.
    const response = await send(headers);
    if (attempt === 0 && response.status === 401) {
      const error: unknown = await response.clone().json().catch(() => null);
      const refresh = z.object({ error: z.object({ code: z.enum(["visit_token_expired", "visit_token_invalid", "missing_api_key"]) }) }).safeParse(error);
      if (refresh.success && refresh.data.error.code === "missing_api_key" && !gated) {
        status = null;
        if (await active()) continue;
      } else if (refresh.success && gated && refresh.data.error.code !== "missing_api_key") {
        // A concurrent renewal may already have replaced the refused token.
        if (credential === sent) credential = null;
        continue;
      }
    }
    const token = response.headers.get("x-modelspec-visit-token");
    const expires = Number(response.headers.get("x-modelspec-visit-expires"));
    if (token && Number.isInteger(expires) && expires > (credential?.expires_at ?? 0))
      credential = { token, expires_at: expires };
    return response;
  }
  throw new Error("Human verification failed. Please try again.");
}
