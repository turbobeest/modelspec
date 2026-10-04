import { useEffect, useId, useRef, useState } from "react";
import type { DecisionSpec } from "../adapter/contract";
import { handoffData, handoffMessage, ORIENT, RUN } from "../handoff-data";

const CLI = `${ORIENT}\n${RUN} decide --spec spec.json`;
const CURL = 'curl -X POST https://api.modelspec.dev/v1/decide -H "Authorization: Bearer $MODELSPEC_API_KEY" -H "content-type: application/json" -d @spec.json';
const FORMATS = ["CLI", "MCP", "Spec", "curl"] as const;
const DEFAULT_CLIENT = "claude-code";
const COPIED = "Hand-off copied for your agent.";
const HANDOFF_FAILED = "Could not copy. Select the CLI and Spec snippets and copy them.";

const CONFIRM_MS = 2000;

/** Copies text and reports it, but only while the copied text is still current. */
function useCopy() {
  const [copied, setCopied] = useState<{ text: string; message: string; ok: boolean } | null>(null);
  const [confirmed, setConfirmed] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  async function copy(text: string, message: string, failed: string) {
    setCopied(null);
    try {
      await navigator.clipboard.writeText(text);
      setCopied({ text, message, ok: true });
      setConfirmed(text);
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setConfirmed(null), CONFIRM_MS);
    } catch {
      setCopied({ text, message: failed, ok: false });
    }
  }
  const current = (texts: string[]) => copied && texts.includes(copied.text) ? copied : null;
  const status = (...texts: string[]) => current(texts)?.message ?? "";
  // A success is confirmed on the button itself; only a failure needs visible words.
  const quiet = (...texts: string[]) => current(texts)?.ok === true;
  const clear = () => { setCopied(null); setConfirmed(null); };
  return { copy, status, quiet, confirmed: (text: string) => confirmed === text, clear };
}

function CopyStatus({ className, quiet, children }: { className: string; quiet: boolean; children: string }) {
  // Always in the tree, so the live region exists before it speaks; seen only when a copy fails.
  return <p className={quiet || !children ? `${className} template-sr` : className} role="status" aria-live="polite" aria-atomic="true">{children}</p>;
}

const copyLabel = (confirmed: boolean) => confirmed ? "Copied ✓" : "Copy for my agent";

export function AgentHandoff({ spec }: { spec: DecisionSpec }) {
  const headingId = useId();
  const snippetId = useId();
  const keyNoteId = useId();
  const clientNoteId = useId();
  const [format, setFormat] = useState<(typeof FORMATS)[number]>("CLI");
  const [client, setClient] = useState(DEFAULT_CLIENT);
  const { copy, status, quiet, confirmed, clear } = useCopy();
  const message = handoffMessage(spec);
  const snippet = format === "CLI" ? CLI
    : format === "MCP" ? `${RUN} setup mcp --client ${client}`
    : format === "Spec" ? JSON.stringify(spec, null, 2)
    : CURL;

  return <section className="panel agent-handoff" aria-labelledby={headingId}>
    <h2 id={headingId}>Give this to my agent</h2>
    <p>Paste it into your agent; <code>modelspec help agent</code> covers keys, MCP and curl.</p>
    <div className="agent-formats" role="group" aria-label="Agent snippet format">
      {FORMATS.map((option) => <button key={option} type="button" aria-pressed={format === option}
        aria-controls={snippetId} onClick={() => { setFormat(option); clear(); }}>
        {option}
      </button>)}
    </div>
    {format === "MCP" && <div className="agent-client">
      <label>
        MCP client{" "}
        <select value={client} aria-describedby={clientNoteId} onChange={(event) => { setClient(event.target.value); clear(); }}>
          {handoffData.mcp_clients.map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
      </label>
      <small id={clientNoteId}>Prints the config for that client.</small>
    </div>}
    <pre id={snippetId} tabIndex={0} aria-label={`${format} snippet`}><code>{snippet}</code></pre>
    <div className="agent-handoff-actions">
      <button type="button" className="agent-copy" onClick={() => void copy(message, COPIED, HANDOFF_FAILED)}>{copyLabel(confirmed(message))}</button>
      <button type="button" className="text-button agent-copy-snippet" onClick={() => void copy(snippet, `${format} copied.`, "Could not copy. Select the snippet and copy it.")}>Copy {format}</button>
      <a href={handoffData.key_link.href} aria-describedby={keyNoteId}>{handoffData.key_link.label}</a>
    </div>
    <small id={keyNoteId}>{handoffData.key_link.note}</small>
    <CopyStatus className="agent-copy-status" quiet={quiet(message)}>{status(message, snippet)}</CopyStatus>
  </section>;
}

export function AnswerAssurances({ spec }: { spec: DecisionSpec }) {
  const { copy, status, quiet, confirmed } = useCopy();
  const message = handoffMessage(spec);
  return <div className="answer-assurances">
    <div className="answer-price">
      <div className="answer-price-line">
        <p>Your agent gets this answer from {handoffData.summary_price_cents}¢</p>
        <button type="button" className="answer-copy" onClick={() => void copy(message, COPIED, "Could not copy. Use the hand-off panel below the answer.")}>{copyLabel(confirmed(message))}</button>
      </div>
      <small>A full explanation costs {handoffData.full_credits} credits.</small>
      <CopyStatus className="answer-copy-status" quiet={quiet(message)}>{status(message)}</CopyStatus>
    </div>
    <a className="answer-trust" href={handoffData.neutrality.href}>{handoffData.neutrality.text} · sourced</a>
  </div>;
}
