import { useEffect, useState } from "react";
import type { AdapterDecision, Cond, Spec } from "../adapter";
import { contractCondition } from "../adapter/view-model";
import type { Vocabulary } from "../vocabulary";
import { boardHasPreference } from "../facet-board/model";
import { bestNowLine, leadingModels } from "../facet-board/leading";

function objectiveLabel(id: string, vocabulary?: Vocabulary): string {
  const facetId = id.startsWith("-") ? id.slice(1) : id;
  const domain = vocabulary?.domains.find((item) => item.id === facetId);
  const facet = vocabulary?.facets.find((item) => item.id === facetId);
  const label = domain?.name ?? facet?.label ?? facetId.replaceAll("_", " ").replaceAll(".", " ");
  return label.charAt(0).toUpperCase() + label.slice(1);
}

type FieldProps = {
  decision: AdapterDecision | null;
  spec?: Spec;
  onAdd: (c: Cond) => void;
  onDismiss: (id: string) => void;
  showQuestions?: boolean;
  vocabulary?: Vocabulary;
  boardOnly?: boolean;
  settled?: boolean;
};

/** The board ranks only once some Prefer carries weight. */
function boardRanked({ boardOnly, spec }: Pick<FieldProps, "boardOnly" | "spec">): boolean {
  return boardOnly === true && spec !== undefined && boardHasPreference(spec);
}

export function Field({ settled = true, ...props }: FieldProps) {
  const e = props.decision?.explanation;
  const qualify = e?.feasible.length, may = e?.may.length, out = e?.excluded.length;
  const best = props.decision && boardRanked(props) ? leadingModels(props.decision)?.length : undefined;
  const [announcement, setAnnouncement] = useState("");
  useEffect(() => {
    if (settled && qualify !== undefined && may !== undefined && out !== undefined)
      setAnnouncement(`${qualify} qualify · ${may} may qualify · ${out} out${best === undefined ? "" : ` · ${best} best for your weights`}`);
  }, [settled, qualify, may, out, best]);
  return <section className="narrowing" aria-label="Narrowing">
    <p className="template-sr" role="status" aria-live="polite" aria-atomic="true">{announcement}</p>
    {props.decision && <NarrowingDetails {...props} decision={props.decision} />}
  </section>;
}

function NarrowingDetails({
  decision,
  spec,
  onAdd,
  onDismiss,
  showQuestions = true,
  vocabulary,
  boardOnly = false,
}: Omit<FieldProps, "decision"> & { decision: AdapterDecision }) {
  const e = decision.explanation,
    requested = new Set(spec?.conds.map(contractCondition) ?? []),
    steps = [
      ...e.funnel.map((step, index) => ({
        ...step,
        engineAdded: boardOnly && index > 0 && !requested.has(
          decision.eliminated.funnel[index - 1]?.condition ?? "",
        ),
      })),
      {
        label: boardOnly && spec && !boardHasPreference(spec)
          ? "Qualifying models"
          : spec?.boardWeights && Object.keys(spec.boardWeights).length
          ? `Ranking on ${Object.entries(spec.boardWeights).map(([id, term]) => `${objectiveLabel(id, vocabulary)} ${typeof term === "number" ? term.toFixed(2) : term.weight.toFixed(2)}`).join(" · ")}`
          : "Ranked on evidence",
        n: e.feasible.length,
        may: e.may.length,
        engineAdded: false,
      },
    ],
    total = Math.max(1, steps[0]?.n ?? 1),
    ranked = boardRanked({ boardOnly, spec }),
    best = ranked ? leadingModels(decision)?.length : undefined,
    bestNow = bestNowLine(decision, ranked);
  return (
    <>
      <div className="panel">
        <div className="narrowing-counts" aria-hidden="true">
          {[
            { state: "qualifies", n: e.feasible.length, label: "qualify", icon: "✓" },
            { state: "may", n: e.may.length, label: "may qualify", icon: "?" },
            { state: "out", n: e.excluded.length, label: "out", icon: "×" },
            ...(boardOnly ? [{ state: "best", n: best ?? "—", label: "best for your weights", icon: "★" }] : []),
          ].map(({ state, n, label, icon }) => <div className={`narrowing-total status-${state}`} key={state}>
            <strong className="narrowing-number" key={n}>{n}</strong><span>{icon} {label}</span>
          </div>)}
        </div>
        {bestNow && <p className="narrowing-best">{bestNow}</p>}
        {(decision.truncated.models > 0 || decision.truncated.offerings > 0) && <small className="narrowing-truncated">
            {decision.truncated.models > 0
              ? `${decision.truncated.models} more ${decision.truncated.models === 1 ? "model" : "models"} not shown`
              : decision.truncated.offerings > 0
                ? ` · ${decision.truncated.offerings} more ${decision.truncated.offerings === 1 ? "offering" : "offerings"} not shown`
                : null}
          </small>}
        <details className="narrowing-details"><summary>Narrowing, in the order you set conditions</summary>
        <ol className="funnel">
          {steps.map((f, i) => (
            <li key={i} className={`${i === steps.length - 1 ? "ranked" : ""}${f.engineAdded ? " engine-added" : ""}`}>
              <span className="count">{f.n}</span>
              <span className="funnel-track">
                <span
                  style={{
                    width:
                      (100 * (i === steps.length - 1 ? f.n : f.n - f.may)) /
                        total +
                      "%",
                  }}
                />
                <i
                  style={{
                    left:
                      (100 * (i === steps.length - 1 ? f.n : f.n - f.may)) /
                        total +
                      "%",
                    width: (100 * f.may) / total + "%",
                  }}
                />
              </span>
              <span
                className="funnel-label"
                title={f.engineAdded ? "This condition was added by the decision engine." : undefined}
              >
                {f.engineAdded ? `Added by the engine: ${f.label}` : f.label}
              </span>
              <small>
                {i === 0
                  ? `${decision.population.models} models · ${decision.population.offerings} offerings`
                  : i === steps.length - 1
                    ? `+ ${f.may} may qualify`
                    : `${steps[i - 1].n - f.n ? "−" + (steps[i - 1].n - f.n) : "no change"}${f.may ? " · " + f.may + " may" : ""}`}
              </small>
            </li>
          ))}
        </ol>
        </details>
      </div>
      {showQuestions && <div className="panel questions">
        <div className="eyebrow">Next questions, most narrowing first</div>
        {decision.questions.map((q) => (
          <div className="question" key={q.id}>
            <div>
              <strong>{q.q}</strong>
              <button className="text-button" onClick={() => onDismiss(q.id)}>
                Doesn't matter
              </button>
            </div>
            <div className="inline">
              {q.opts.map((o) => (
                <button key={o.label} onClick={() => onAdd(o.c)}>
                  {o.label}{" "}
                  <small>
                    {o.failed ? (
                      "count unavailable"
                    ) : o.n === undefined ? (
                      "checking…"
                    ) : (
                      <>
                        → {o.n}
                        {o.may ? " + " + o.may + " may" : ""}
                      </>
                    )}
                  </small>
                </button>
              ))}
            </div>
          </div>
        ))}
        {!decision.questions.length && (
          <p>No further question would narrow the field.</p>
        )}
      </div>}
    </>
  );
}
