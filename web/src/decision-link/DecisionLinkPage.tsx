import { useEffect, useState } from "react";
import { z } from "zod";
import { VisitGate } from "../decide/components/HumanGate";
import { prepareVisit, visitFetch, visitGateActive } from "../decide/adapter/visit";
import "./decision-link.css";

const summarySchema = z.object({
  decision_id: z.string().min(1),
  snapshot: z.object({ id: z.string().min(1), content_hash: z.string().min(1) }),
  summary_for_user: z.string().min(1),
  must_mention: z.array(z.string()),
  requirements: z.object({ applied: z.record(z.string(), z.json()), not_applied: z.array(z.string()) }),
});
type Summary = z.infer<typeof summarySchema>;
type State = { kind: "loading" } | { kind: "ready"; summary: Summary } | { kind: "error"; message: string };
const endpoint = (import.meta.env.VITE_DECIDE_ENDPOINT ?? "https://api.modelspec.dev/v1/decide").replace(/\/v1\/decide\/?$/, "/v1/decision-link");
const unavailable = "This decision link is unavailable. Ask the sender for a new link.";

function readLink(): { decision_id: string; token: string } | null {
  const match = /^\/d\/(dec_[A-Za-z0-9_-]+)\/?$/.exec(location.pathname);
  const tokens = new URLSearchParams(location.search).getAll("token");
  if (!match || tokens.length !== 1 || !tokens[0] || tokens[0].length > 32_768) return null;
  return { decision_id: match[1], token: tokens[0] };
}

const labels: Record<string, string> = {
  where: "Must meet", optimize: "Optimize for", unknowns: "Unknown measurements", task_tokens: "Task tokens",
  capabilities: "Capabilities", access: "Access", facet: "Requirement", op: "Condition", value: "Value",
  max: "Maximize", min: "Minimize", weights: "Preferences", eq: "equals", neq: "does not equal",
  gte: "at least", lte: "at most", gt: "greater than", lt: "less than",
};
function RequirementValue({ value }: { value: Summary["requirements"]["applied"][string] }) {
  if (Array.isArray(value)) return value.length
    ? <ul>{value.map((item, index) => <li key={index}><RequirementValue value={item} /></li>)}</ul>
    : <span>None</span>;
  if (value !== null && typeof value === "object") return <dl>{Object.entries(value).map(([key, item]) =>
    <div key={key}><dt>{labels[key] ?? key.replaceAll("_", " ")}</dt><dd><RequirementValue value={item} /></dd></div>)}</dl>;
  return <span>{value === null ? "Not set" : typeof value === "boolean" ? value ? "Yes" : "No" : labels[String(value)] ?? String(value)}</span>;
}

export function DecisionLinkPage() {
  const [link] = useState(readLink);
  const [state, setState] = useState<State>(() => link ? { kind: "loading" }
    : { kind: "error", message: "This decision link is incomplete. Ask the sender for the full link." });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    if (!link) return () => controller.abort();
    void (async () => {
      await prepareVisit();
      if (!visitGateActive()) throw new Error("Human verification is temporarily unavailable. Please try again later.");
      controller.signal.throwIfAborted();
      const response = await visitFetch(endpoint, {
        method: "POST", mode: "cors", cache: "no-store", referrerPolicy: "no-referrer",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(link), signal: controller.signal,
      });
      if (!response.ok) throw new Error(response.status === 410
        ? "This decision link has expired. Ask the sender for a new link."
        : unavailable);
      const value: unknown = await response.json();
      const parsed = summarySchema.safeParse(value);
      if (!parsed.success || parsed.data.decision_id !== link.decision_id) throw new Error(unavailable);
      if (!controller.signal.aborted) setState({ kind: "ready", summary: parsed.data });
    })().catch((error: unknown) => {
      if (!controller.signal.aborted) setState({ kind: "error", message: error instanceof Error && error.message.startsWith("Human verification")
        ? "Human verification is temporarily unavailable. Please try again later."
        : error instanceof Error && error.message.startsWith("This decision link") ? error.message : unavailable });
    });
    return () => controller.abort();
  }, [link, attempt]);

  return <main className="decision-link">
    <header><span className="decision-link-brand">ModelSpec</span><p>A shared decision</p><h1>Decision summary</h1></header>
    <VisitGate />
    {state.kind === "loading" && <p role="status">Checking this decision link…</p>}
    {state.kind === "error" && <div><p role="alert">{state.message}</p>{link && <button onClick={() => {
      setState({ kind: "loading" });
      setAttempt((value) => value + 1);
    }}>Try again</button>}</div>}
    {state.kind === "ready" && <>
      <p className="decision-link-summary">{state.summary.summary_for_user}</p>
      <section aria-labelledby="decision-caveats"><h2 id="decision-caveats">What to keep in mind</h2>
        {state.summary.must_mention.length ? <ul>{state.summary.must_mention.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p>No additional caveats were returned.</p>}
      </section>
      <section aria-labelledby="decision-requirements"><h2 id="decision-requirements">Applied requirements</h2>
        <RequirementValue value={state.summary.requirements.applied} />
        {state.summary.requirements.not_applied.length > 0 && <><h3>Not applied</h3><ul>{state.summary.requirements.not_applied.map((item, index) => <li key={index}>{item.replaceAll("_", " ")}</li>)}</ul></>}
      </section>
      <section aria-labelledby="decision-snapshot"><h2 id="decision-snapshot">Pinned snapshot</h2>
        <dl><div><dt>Snapshot</dt><dd><code>{state.summary.snapshot.id}</code></dd></div>
          <div><dt>Content hash</dt><dd><code>{state.summary.snapshot.content_hash}</code></dd></div></dl>
      </section>
    </>}
  </main>;
}
