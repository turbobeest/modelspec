import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import { VISIT_GATE_ENABLED, registerChallenge, type Challenge } from "../adapter/visit";
import { DECIDE_ENDPOINT } from "../adapter/hosted";

export const HUMAN_GATE_ENABLED = import.meta.env.VITE_HUMAN_GATE_ENABLED === "true";
const SITE_KEY: string = import.meta.env.VITE_TURNSTILE_SITE_KEY ?? "";
const statusSchema = z.union([
  z.object({ enabled: z.literal(false) }),
  z.object({ enabled: z.literal(true), remaining: z.number().int().min(0).max(20) }),
  z.object({ enabled: z.literal(true), mode: z.literal("visit"), day_limit: z.number().int().positive(), burst_limit: z.number().int().positive() }),
]);

interface Turnstile {
  render(container: HTMLElement, options: {
    sitekey: string;
    action: string;
    appearance?: "interaction-only";
    size?: "compact";
    callback: (token: string) => void;
    "expired-callback": () => void;
    "error-callback": () => void;
  }): string;
  remove(id: string): void;
}

declare global {
  interface Window { turnstile?: Turnstile }
}

let scriptReady: Promise<void> | null = null;
export function loadWidget(): Promise<void> {
  if (window.turnstile) return Promise.resolve();
  if (!scriptReady) scriptReady = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => { scriptReady = null; reject(new Error("Verification unavailable")); };
    document.head.append(script);
  });
  return scriptReady;
}

export function HumanGate({ onLookup, onEnabled, disabled = false }: {
  onLookup: (token: string, onRemaining: (remaining: number) => void) => Promise<void>;
  disabled?: boolean;
  onEnabled?: (enabled: boolean) => void;
}) {
  const container = useRef<HTMLDivElement>(null);
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [challenge, setChallenge] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch(DECIDE_ENDPOINT.replace(/\/v1\/decide\/?$/, "/v1/human-status"), {
      mode: "cors", signal: controller.signal,
    }).then(async (response) => {
      if (!response.ok) throw new Error("Unavailable");
      const status = statusSchema.parse(await response.json());
      if (controller.signal.aborted) return;
      if (status.enabled && "mode" in status) {
        if (!VISIT_GATE_ENABLED) throw new Error("Visit verification requires a new page build");
        setEnabled(false);
        setUnavailable(false);
        onEnabled?.(false);
        return;
      }
      setEnabled(status.enabled);
      onEnabled?.(status.enabled);
      if (status.enabled) {
        setRemaining(status.remaining);
        setUnavailable(!SITE_KEY);
      }
      else setUnavailable(false);
    }).catch(() => { if (!controller.signal.aborted) setUnavailable(true); });
    return () => controller.abort();
  }, [challenge, onEnabled]);
  const canVerify = enabled === true && !!SITE_KEY && !unavailable && remaining !== null && remaining > 0;
  useEffect(() => {
    if (!canVerify) return;
    let active = true;
    let widget: string | null = null;
    void loadWidget().then(() => {
      if (!active || !container.current || !window.turnstile) return;
      widget = window.turnstile.render(container.current, {
        sitekey: SITE_KEY, action: "decide", callback: (value) => {
          setToken(value);
          setUnavailable(false);
        },
        "expired-callback": () => setToken(null),
        "error-callback": () => { setToken(null); setUnavailable(true); },
      });
    }).catch(() => { if (active) setUnavailable(true); });
    return () => { active = false; if (widget !== null) window.turnstile?.remove(widget); };
  }, [challenge, canVerify]);
  if (enabled === false || (enabled === null && !unavailable)) return null;
  return <section className="human-gate" aria-label="Manual lookups">
    <p role="status">{unavailable
      ? "Manual decisions are temporarily unavailable. Please try again later."
      : remaining === 0
        ? "You have used today's 20 manual decisions. Come back after midnight UTC."
        : remaining === null ? "Checking today's allowance…" : `${remaining} decisions remaining today. Resets at midnight UTC.`}</p>
    {enabled === true && <p>Manual lookups are limited to 20 per day and 3 per minute. For machine access, use the <a href="/pricing/">paid API or MCP</a>.</p>}
    {unavailable && (enabled !== true || SITE_KEY) && <button disabled={busy} onClick={() => {
      setUnavailable(false);
      setToken(null);
      setChallenge((value) => value + 1);
    }}>Retry verification</button>}
    <div ref={container} />
    {enabled === true && <button className="primary" disabled={disabled || busy || unavailable || remaining === null || remaining === 0 || !token}
      onClick={async () => {
        if (!token || busy) return;
        setBusy(true);
        setToken(null);
        try { await onLookup(token, setRemaining); }
        finally { setBusy(false); setUnavailable(!SITE_KEY); setChallenge((value) => value + 1); }
      }}>Look up this decision</button>}
  </section>;
}


export function VisitGate() {
  const container = useRef<HTMLDivElement>(null);
  const [pending, setPending] = useState<Challenge | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => registerChallenge(setPending), []);
  useEffect(() => {
    if (!pending) return;
    let active = true;
    let widget: string | null = null;
    const fail = () => {
      if (!active) return;
      setError("Verification is temporarily unavailable. Retry your lookup.");
      pending.reject(new Error("Human verification unavailable"));
    };
    setError(null);
    if (!SITE_KEY) { fail(); return; }
    void loadWidget().then(() => {
      if (!active || !container.current || !window.turnstile) return;
      widget = window.turnstile.render(container.current, {
        sitekey: SITE_KEY, action: "decide", appearance: "interaction-only", size: "compact",
        callback: (token) => { if (active) pending.resolve(token); },
        "expired-callback": fail, "error-callback": fail,
      });
    }).catch(fail);
    return () => { active = false; if (widget !== null) window.turnstile?.remove(widget); };
  }, [pending]);
  return <section className="visit-gate" aria-label="Visit verification">
    {pending && <>
      <p className="visit-gate-prompt">One quick check keeps this free</p>
      <p className="visit-gate-preview">For example: require open weights, prefer lower cost, and see which models fit.</p>
    </>}
    {error && <p role="alert">{error}</p>}
    <div ref={container} />
  </section>;
}
