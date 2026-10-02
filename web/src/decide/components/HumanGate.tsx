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

/**
 * The manual-lookup control (MODEL-248). It sits at the top of the answer
 * column, where the answer draws (MODEL-281), and on narrow screens adds a
 * fixed "Look up (N left)" bar so the control is in reach while facets change.
 * `stale` says the facets changed since the answer shown was looked up.
 */
export function HumanGate({ onLookup, onEnabled, disabled = false, stale = false }: {
  onLookup: (token: string, onRemaining: (remaining: number) => void) => Promise<void>;
  disabled?: boolean;
  onEnabled?: (enabled: boolean) => void;
  stale?: boolean;
}) {
  const section = useRef<HTMLElement>(null);
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
  const blocked = disabled || busy || unavailable || remaining === null || remaining === 0;
  const lookUp = async () => {
    if (!token || busy) return;
    setBusy(true);
    setToken(null);
    try { await onLookup(token, setRemaining); }
    finally { setBusy(false); setUnavailable(!SITE_KEY); setChallenge((value) => value + 1); }
  };
  return <><section ref={section} className="human-gate" aria-label="Manual lookups">
    <p role="status">{unavailable
      ? "Manual decisions are temporarily unavailable. Please try again later."
      : remaining === 0
        ? "You have used today's 20 manual decisions. Come back after midnight UTC."
        : remaining === null ? "Checking today's allowance…"
        : stale ? `Facets changed. Look up again (${remaining} left).`
        : `${remaining} decisions remaining today. Resets at midnight UTC.`}</p>
    {enabled === true && <p>Manual lookups are limited to 20 per day and 3 per minute. For machine access, use the <a href="/pricing/">paid API or MCP</a>.</p>}
    {unavailable && (enabled !== true || SITE_KEY) && <button disabled={busy} onClick={() => {
      setUnavailable(false);
      setToken(null);
      setChallenge((value) => value + 1);
    }}>Retry verification</button>}
    <div ref={container} />
    {enabled === true && <button className="primary" disabled={blocked || !token} onClick={lookUp}>Look up this decision</button>}
  </section>
  {enabled === true && remaining !== null && <div className="human-gate-bar">
    <button className="primary" disabled={blocked} onClick={() => {
      // Verification lives in the answer panel; until it has passed, take the visitor there.
      if (token) void lookUp().then(() => document.getElementById("facet-board-answer")?.scrollIntoView({ block: "start" }));
      else section.current?.scrollIntoView({ block: "center" });
    }}>{stale ? "Look up again" : "Look up"} ({remaining} left)</button>
  </div>}
  </>;
}
