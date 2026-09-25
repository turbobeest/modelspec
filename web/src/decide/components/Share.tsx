import { useEffect, useRef, useState } from "react";
import { BENCH, fmtB, label } from "../adapter";
import type { Row, Spec } from "../adapter";
import { encodeSpec } from "../state/spec";
import type { Axis } from "../state/spec";
const tabs = [
  "Permalink",
  "API call",
  "CLI",
  "Spec YAML",
  "Save and alert",
  "Procurement review",
];
export function Share({
  spec,
  snapshot,
  axis,
  row,
  onClose,
}: {
  spec: Spec;
  snapshot: string;
  axis: Axis;
  row: Row | null;
  onClose: () => void;
}) {
  const [tab, setTab] = useState("Permalink"),
    [copied, setCopied] = useState(""),
    [saved, setSaved] = useState(false),
    [alerts, setAlerts] = useState([true, true, false]),
    dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = dialog.current;
    const previous = document.activeElement;
    node?.showModal();
    return () => {
      node?.close();
      if (previous instanceof HTMLElement) previous.focus();
    };
  }, []);
  const sample = {
    fictional_sample: true,
    task: spec.task,
    tokens_per_task: { input: spec.tokIn, output: spec.tokOut },
    conditions: spec.conds,
    objective: { benchmark: spec.bench, weights: spec.w },
    snapshot,
  };
  const yaml = [
    "# ModelSpec fictional sample spec, not a live API request",
    `snapshot: ${snapshot}`,
    `task: ${JSON.stringify(spec.task || "")}`,
    "tokens_per_task:",
    `  input: ${spec.tokIn}`,
    `  output: ${spec.tokOut}`,
    "conditions:",
    ...spec.conds.map(
      (c) => "  - " + JSON.stringify(label(c)) + (c.soft ? " # soft" : ""),
    ),
    "objective:",
    `  benchmark: ${JSON.stringify(spec.bench)}`,
    "  weights:",
    `    capability: ${spec.w.cap}`,
    `    cost: ${spec.w.cost}`,
    `    speed: ${spec.w.speed}`,
  ].join("\n");
  const code =
    tab === "Permalink"
      ? location.origin +
        location.pathname +
        location.search +
        encodeSpec(spec, axis)
      : tab === "API call"
        ? `# Fictional sample preview. MODEL-151 will connect the decision contract.\n# This payload documents the sample; it is not accepted by the real API.\ncurl https://api.modelspec.example/v1/decide \\\n  -H 'Content-Type: application/json' \\\n  -d '${JSON.stringify(sample, null, 2).replaceAll("'", "'\\''")}'`
        : tab === "CLI"
          ? `# Fictional sample preview; real CLI requires a contract spec.\n# Save the sample YAML for reference, then translate to the decision contract.\nmodelspec decide spec.yaml --explain full --json`
          : yaml;
  const clauses = row
    ? spec.conds.map((c, i) => {
        const t = row.best.t[i],
          b =
            c.f === "bench"
              ? row.m.bench.find(
                  (b) => b.b === c.b && (!c.indep || b.by === "indep"),
                )
              : null;
        return {
          clause: label(c),
          result: t.s === 1 ? "Yes" : t.s === 0 ? "Unknown" : "No",
          evidence: b
            ? `${fmtB(b.b, b.v)} ${BENCH[b.b].unit} · ${b.who} · ${b.date} · ${b.src}`
            : t.why ||
              `Fictional ${row.best.o.provider} catalogue entry · read 2026-09-24 · ${snapshot}`,
        };
      })
    : [];
  function download() {
    const csv =
      "clause,result,evidence\n" +
      clauses
        .map((c) =>
          [c.clause, c.result, c.evidence]
            .map((v) => '"' + v.replaceAll('"', '""') + '"')
            .join(","),
        )
        .join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `modelspec-${snapshot}.csv`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }
  return (
    <dialog
      ref={dialog}
      className="share-modal"
      aria-modal="true"
      aria-labelledby="share-title"
      onCancel={onClose}
      onClick={(ev) => {
        if (ev.target === ev.currentTarget) {
          const r = ev.currentTarget.getBoundingClientRect();
          if (
            ev.clientX < r.left ||
            ev.clientX > r.right ||
            ev.clientY < r.top ||
            ev.clientY > r.bottom
          )
            onClose();
        }
      }}
    >
      <div className="panel-heading">
        <div>
          <h2 id="share-title">Share or act on this decision</h2>
          <span className="snapshot">{snapshot}</span>
        </div>
        <button aria-label="Close Share or act" onClick={onClose}>
          ×
        </button>
      </div>
      <div className="share-tabs" role="tablist" aria-label="Share formats">
        {tabs.map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => {
              setTab(t);
              setCopied("");
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <div role="tabpanel" aria-label={tab}>
        <p className="muted">
          {tab === "Permalink"
            ? "The whole spec is encoded in the link. Anyone who opens it can change it."
            : tab === "Save and alert"
              ? "Try alert preferences for this fictional spec. This preview saves them in this browser; no monitoring service is connected."
              : tab === "Procurement review"
                ? `Yes, no or unknown per clause for ${row?.m.name || "the selected model"}, with fictional evidence. Unknowns are listed, not assumed.`
                : "Fictional sample format. The real backend follows the decision contract and will be connected in MODEL-151."}
        </p>
        {tabs.indexOf(tab) < 4 && (
          <>
            <pre>{code}</pre>
            <button
              className="primary"
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(code);
                  setCopied("Copied");
                } catch {
                  setCopied("Could not copy. Select the text above.");
                }
              }}
            >
              {copied || "Copy"}
            </button>
          </>
        )}
        {tab === "Save and alert" && (
          <div className="alert-options">
            {[
              "A new model beats this pick",
              "This pick’s terms change",
              "This pick is scheduled for retirement",
            ].map((t, i) => (
              <label key={t}>
                <input
                  type="checkbox"
                  checked={alerts[i]}
                  onChange={() => {
                    setAlerts((a) => a.map((v, j) => (i === j ? !v : v)));
                    setSaved(false);
                  }}
                />
                {t}
              </label>
            ))}
            <button
              className="primary"
              onClick={() => {
                localStorage.setItem(
                  "modelspec-sample-alerts",
                  JSON.stringify({ spec, alerts }),
                );
                setSaved(true);
              }}
            >
              {saved ? "Saved locally · preview only" : "Save and watch"}
            </button>
          </div>
        )}
        {tab === "Procurement review" && (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Clause</th>
                    <th>Result</th>
                    <th>Evidence and sources</th>
                  </tr>
                </thead>
                <tbody>
                  {clauses.map((c, i) => (
                    <tr key={i}>
                      <td>{c.clause}</td>
                      <td>{c.result}</td>
                      <td>{c.evidence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button onClick={download}>Download CSV</button>
          </>
        )}
      </div>
    </dialog>
  );
}
