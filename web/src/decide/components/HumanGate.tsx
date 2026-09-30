import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import { DECIDE_ENDPOINT } from "../adapter/hosted";

export const HUMAN_GATE_ENABLED = import.meta.env.VITE_HUMAN_GATE_ENABLED === "true";
const SITE_KEY: string = import.meta.env.VITE_TURNSTILE_SITE_KEY ?? "";
const statusSchema = z.union([
  z.object({ enabled: z.literal(false) }),
  z.object({ enabled: z.literal(true), remaining: z.number().int().min(0).max(20) }),
]);

interface Turnstile {
  render(container: HTMLElement, options: {
    sitekey: string;
    action: string;
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
function loadWidget(): Promise<void> {
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

export function HumanGate({ onLookup, disabled = false }: {
  onLookup: (token: string, onRemaining: (remaining: number) => void) => Promise<void>;
  disabled?: boolean;
}) {
  const container = useRef<HTMLDivElement>(null);
  const [token, setToken] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [unavailable, setUnavailable] = useState(!SITE_KEY);
  const [busy, setBusy] = useState(false);
  const [challenge, setChallenge] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch(DECIDE_ENDPOINT.replace(/\/v1\/decide\/?$/, "/v1/human-status"), {
      mode: "cors", signal: controller.signal,
    }).then(async (response) => {
      if (!response.ok) throw new Error("Unavailable");
      const status = statusSchema.parse(await response.json());
      if (status.enabled) setRemaining(status.remaining);
      else setUnavailable(true);
    }).catch(() => { if (!controller.signal.aborted) setUnavailable(true); });
    return () => controller.abort();
  }, [challenge]);
  const canVerify = !!SITE_KEY && !unavailable && remaining !== null && remaining > 0;
  useEffect(() => {
    if (!canVerify) return;
    let active = true;
    let widget: string | null = null;
    void loadWidget().then(() => {
      if (!active || !container.current || !window.turnstile) return;
      widget = window.turnstile.render(container.current, {
        sitekey: SITE_KEY, action: "decide", callback: setToken,
        "expired-callback": () => setToken(null),
        "error-callback": () => { setToken(null); setUnavailable(true); },
      });
    }).catch(() => { if (active) setUnavailable(true); });
    return () => { active = false; if (widget !== null) window.turnstile?.remove(widget); };
  }, [challenge, canVerify]);
  return <section className="human-gate" aria-label="Manual lookups">
    <p role="status">{unavailable
      ? "Manual decisions are temporarily unavailable. Please try again later."
      : remaining === 0
        ? "You have used today's 20 manual decisions. Come back after midnight UTC."
        : remaining === null ? "Checking today's allowance…" : `${remaining} decisions remaining today. Resets at midnight UTC.`}</p>
    <p>Manual lookups are limited to 20 per day and 3 per minute. For machine access, use the <a href="/pricing/">paid API or MCP</a>.</p>
    <div ref={container} />
    <button className="primary" disabled={disabled || busy || unavailable || remaining === null || remaining === 0 || !token}
      onClick={async () => {
        if (!token || busy) return;
        setBusy(true);
        setToken(null);
        try { await onLookup(token, setRemaining); }
        finally { setBusy(false); setChallenge((value) => value + 1); }
      }}>Look up this decision</button>
  </section>;
}
