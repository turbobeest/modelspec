import { useEffect, useRef, useState } from "react";
import { fmtB } from "../adapter";
import { useVocab } from "../vocabulary/context";
import { SnapshotId } from "./SnapshotId";
import type { Row, Spec } from "../adapter";
import { encodeSpec } from "../state/spec";
import type { Axis } from "../state/spec";
import { toDecisionSpec } from "../adapter/view-model";
import { boardHasPreference, encodeBoardSpec, toBoardDecisionSpec } from "../facet-board/model";
import type { BoardUrlState } from "../facet-board/model";
const tabs = [
  "Permalink",
  "API call",
  "Spec YAML",
  "Save and alert",
  "Procurement review",
];
export function Share({
  spec,
  snapshot,
  axis,
  row,
  demo,
  refinementsFolded = false,
  humanGateEnabled = false,
  boardPermalink,
  onClose,
}: {
  spec: Spec;
  snapshot: string;
  axis: Axis;
  row: Row | null;
  demo: boolean;
  refinementsFolded?: boolean;
  humanGateEnabled?: boolean;
  boardPermalink?: { spec: Spec; state: BoardUrlState };
  onClose: () => void;
}) {
  const { label } = useVocab();
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
  const unrankedBoard = spec.boardWeights !== undefined && !boardHasPreference(spec);
  const contractSpec = spec.boardWeights === undefined
    ? toDecisionSpec(spec, "full")
    : toBoardDecisionSpec(spec, "full");
  // An unranked board still sends a membership-neutral objective: the contract
  // requires one, and weights never exclude. Share it so the spec runs as-is.
  const sharedContractSpec = contractSpec;
  const sample = demo
    ? {
        fictional_sample: true,
        task: spec.task,
        tokens_per_task: { input: spec.tokIn, output: spec.tokOut },
        conditions: spec.conds,
        objective: { benchmark: spec.bench, weights: spec.w },
        snapshot,
      }
    : sharedContractSpec;
  const yaml = demo
    ? [
        "# ModelSpec fictional sample spec, not a live API request",
        `snapshot: ${snapshot}`,
        `task: ${JSON.stringify(spec.task || "")}`,
        "conditions:",
        ...spec.conds.map(
          (condition) =>
            "  - " +
            JSON.stringify(label(condition)) +
            (condition.soft ? " # soft" : ""),
        ),
      ].join("\n")
    : [
        "# ModelSpec decision contract 1.3",
        ...(boardPermalink?.state.canvas
          ? [
              `# canvas x: ${boardPermalink.state.canvas.x}`,
              `# canvas y: ${boardPermalink.state.canvas.y}`,
            ]
          : []),
        `spec_version: ${contractSpec.spec_version}`,
        `snapshot: ${contractSpec.snapshot ?? "latest"}`,
        ...(contractSpec.task_type
          ? [`task_type: ${contractSpec.task_type}`]
          : []),
        ...(contractSpec.capabilities
          ? [`capabilities: ${JSON.stringify(contractSpec.capabilities)}`]
          : []),
        // An empty list must print as [] — a bare "where:" parses as null.
        (contractSpec.where ?? []).length ? "where:" : "where: []",
        ...(contractSpec.where ?? []).map(
          (condition) => `  - ${JSON.stringify(condition)}`,
        ),
        ...(unrankedBoard
          ? ["# unranked: no Prefer set; this objective only lets the spec run, it does not rank"]
          : []),
        ...(refinementsFolded
          ? ["# refinement weights folded into their parent domains until nested ranking is available"]
          : []),
        `optimize: ${JSON.stringify(contractSpec.optimize)}`,
        `unknowns: ${contractSpec.unknowns ?? "default"}`,
        `explain: ${contractSpec.explain ?? "full"}`,
        `limit: ${contractSpec.limit ?? 500}`,
      ].join("\n");
  const code =
    tab === "Permalink"
      ? location.origin +
        location.pathname +
        location.search +
        (boardPermalink
          ? encodeBoardSpec(boardPermalink.spec, axis, boardPermalink.state)
          : encodeSpec(spec, axis))
      : tab === "API call"
        ? demo
          ? `# Fictional sample preview; this payload is not sent.\ncurl https://api.modelspec.example/v1/decide \\\n  -H 'Authorization: Bearer <API_KEY>' \\\n  -H 'Content-Type: application/json' \\\n  -d '${JSON.stringify(sample, null, 2).replaceAll("'", "'\\''")}'`
          : `${unrankedBoard ? "# unranked: no Prefer set; the objective below only lets the spec run, it does not rank\n" : ""}curl https://api.modelspec.dev/v1/decide \\\n  -H 'Authorization: Bearer <API_KEY>' \\\n  -H 'Content-Type: application/json' \\\n  -d '${JSON.stringify(sharedContractSpec, null, 2).replaceAll("'", "'\\''")}'`
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
            ? `${fmtB(b.b, b.v)} · ${b.who} · ${b.date} · ${b.src}`
            : t.why ||
              (demo
                ? `Fictional ${row.best.o.provider} catalogue entry · read 2026-09-24 · ${snapshot}`
                : "No sourced value returned for this clause."),
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
          <h2 id="share-title">Share</h2>
          <SnapshotId snapshot={snapshot} />
        </div>
        <button aria-label="Close Share" onClick={onClose}>
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
              ? demo
                ? "Try alert preferences for this fictional spec. This preview saves them in this browser; no monitoring service is connected."
                : "Alert preferences are saved in this browser. Server monitoring is not enabled."
              : tab === "Procurement review"
                ? `Yes, no or unknown per clause for ${row?.m.name || "the selected model"}, with returned evidence. Unknowns are listed, not assumed.`
                : demo
                  ? "Fictional sample format."
                  : "This is the contract sent to the hosted decision backend."}
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
                  demo ? "modelspec-sample-alerts" : "modelspec-alerts",
                  JSON.stringify({ spec, alerts }),
                );
                setSaved(true);
              }}
            >
              {saved
                ? demo
                  ? "Saved locally · preview only"
                  : "Saved in this browser"
                : "Save and watch"}
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
            {!humanGateEnabled && <button onClick={download}>Download CSV</button>}
          </>
        )}
      </div>
    </dialog>
  );
}
