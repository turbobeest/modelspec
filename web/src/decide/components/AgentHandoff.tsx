import { useId, useState } from "react";
import type { DecisionSpec } from "../adapter/contract";
import { handoffData, handoffMessage, ORIENT, RUN } from "../handoff-data";

const CLI = `${ORIENT}\n${RUN} decide --spec spec.json`;
const CURL = 'curl -X POST https://api.modelspec.dev/v1/decide -H "Authorization: Bearer $MODELSPEC_API_KEY" -H "content-type: application/json" -d @spec.json';
const FORMATS = ["CLI", "MCP", "Spec", "curl"] as const;
const DEFAULT_CLIENT = "claude-code";
const COPIED = "Hand-off copied for your agent.";
const HANDOFF_FAILED = "Could not copy. Select the CLI and Spec snippets and copy them.";

/** Copies text and reports it, but only while the copied text is still current. */
function useCopy() {
  const [copied, setCopied] = useState<{ text: string; message: string } | null>(null);
  async function copy(text: string, message: string, failed: string) {
    setCopied(null);
    try {
      await navigator.clipboard.writeText(text);
      setCopied({ text, message });
    } catch {
      setCopied({ text, message: failed });
    }
  }
  const status = (...current: string[]) => copied && current.includes(copied.text) ? copied.message : "";
  return { copy, status, clear: () => setCopied(null) };
}

function CopyStatus({ className, children }: { className: string; children: string }) {
  return <p className={className} role="status" aria-live="polite" aria-atomic="true">{children}</p>;
}

export function AgentHandoff({ spec }: { spec: DecisionSpec }) {
  const headingId = useId();
  const snippetId = useId();
  const keyNoteId = useId();
  const clientNoteId = useId();
  const [format, setFormat] = useState<(typeof FORMATS)[number]>("CLI");
  const [client, setClient] = useState(DEFAULT_CLIENT);
  const { copy, status, clear } = useCopy();
  const message = handoffMessage(spec);
  const snippet = format === "CLI" ? CLI
    : format === "MCP" ? `${RUN} setup mcp --client ${client}`
    : format === "Spec" ? JSON.stringify(spec, null, 2)
    : CURL;

  return <section className="agent-handoff" aria-labelledby={headingId}>
    <h2 id={headingId}>Give this to my agent</h2>
    <p>Get a key with <code>modelspec key</code>, then store it for the CLI with <code>modelspec auth set</code>. MCP and curl read <code>MODELSPEC_API_KEY</code>. Save the Spec as <code>spec.json</code>.</p>
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
      <button type="button" className="agent-copy" onClick={() => void copy(message, COPIED, HANDOFF_FAILED)}>Copy for my agent</button>
      <button type="button" onClick={() => void copy(snippet, `${format} copied.`, "Could not copy. Select the snippet and copy it.")}>Copy {format}</button>
      <a href={handoffData.key_link.href} aria-describedby={keyNoteId}>Get an API key</a>
    </div>
    <small id={keyNoteId}>{handoffData.key_link.note}</small>
    <CopyStatus className="agent-copy-status">{status(message, snippet)}</CopyStatus>
  </section>;
}

export function AnswerAssurances({ spec }: { spec: DecisionSpec }) {
  const { copy, status } = useCopy();
  const message = handoffMessage(spec);
  return <div className="answer-assurances">
    <div className="answer-price">
      <div className="answer-price-line">
        <p>Your agent gets this answer from {handoffData.summary_price_cents}¢</p>
        <button type="button" className="answer-copy" onClick={() => void copy(message, COPIED, "Could not copy. Use the hand-off panel below the answer.")}>Copy for my agent</button>
      </div>
      <small>A full explanation costs {handoffData.full_credits} credits.</small>
      <CopyStatus className="answer-copy-status">{status(message)}</CopyStatus>
    </div>
    <a className="answer-trust" href={handoffData.neutrality.href}>{handoffData.neutrality.text} · sourced</a>
  </div>;
}
