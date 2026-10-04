import { useId, useState } from "react";
import type { DecisionSpec } from "../adapter/contract";
import { handoffData } from "../handoff-data";

const CURL = 'curl -X POST https://api.modelspec.dev/v1/decide -H "Authorization: Bearer $MODELSPEC_API_KEY" -H "content-type: application/json" -d @spec.json';
const CLI = "uvx --from modelspec-dev modelspec decide --spec spec.json";
const FORMATS = ["Spec", "curl", "CLI"] as const;

export function AgentHandoff({ spec }: { spec: DecisionSpec }) {
  const headingId = useId();
  const snippetId = useId();
  const keyNoteId = useId();
  const [format, setFormat] = useState<(typeof FORMATS)[number]>("Spec");
  const [confirmation, setConfirmation] = useState<{ snippet: string; message: string } | null>(null);
  const snippet = format === "Spec" ? JSON.stringify(spec, null, 2) : format === "curl" ? CURL : CLI;

  async function copy() {
    setConfirmation(null);
    try {
      await navigator.clipboard.writeText(snippet);
      setConfirmation({ snippet, message: `${format} copied for your agent.` });
    } catch {
      setConfirmation({ snippet, message: "Could not copy. Select the snippet and copy it." });
    }
  }

  return <section className="agent-handoff" aria-labelledby={headingId}>
    <h2 id={headingId}>Give this to my agent</h2>
    <p>Save the Spec as <code>spec.json</code>. Set <code>MODELSPEC_API_KEY</code> for curl or the CLI.</p>
    <div className="agent-formats" role="group" aria-label="Agent snippet format">
      {FORMATS.map((option) => <button key={option} type="button" aria-pressed={format === option}
        aria-controls={snippetId} onClick={() => { setFormat(option); setConfirmation(null); }}>
        {option}
      </button>)}
    </div>
    <pre id={snippetId} tabIndex={0} aria-label={`${format} snippet`}><code>{snippet}</code></pre>
    <div className="agent-handoff-actions">
      <button type="button" className="agent-copy" onClick={() => void copy()}>Copy for my agent</button>
      <a href={handoffData.key_link.href} aria-describedby={keyNoteId}>Get an API key</a>
    </div>
    <small id={keyNoteId}>{handoffData.key_link.note}</small>
    <p className="agent-copy-status" role="status" aria-live="polite" aria-atomic="true">
      {confirmation?.snippet === snippet ? confirmation.message : ""}
    </p>
  </section>;
}

export function AnswerAssurances() {
  return <div className="answer-assurances">
    <div className="answer-price">
      <p>Your agent gets this answer from {handoffData.summary_price_cents}¢</p>
      <small>A full explanation costs {handoffData.full_credits} credits.</small>
    </div>
    <a className="answer-trust" href={handoffData.neutrality.href}>{handoffData.neutrality.text} · sourced</a>
  </div>;
}
