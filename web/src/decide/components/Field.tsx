import type { AdapterDecision, Cond, Spec } from "../adapter";
import { contractCondition } from "../adapter/view-model";
import type { Vocabulary } from "../vocabulary";
import { boardHasPreference } from "../facet-board/model";

function objectiveLabel(id: string, vocabulary?: Vocabulary): string {
  const facetId = id.startsWith("-") ? id.slice(1) : id;
  const domain = vocabulary?.domains.find((item) => item.id === facetId);
  const facet = vocabulary?.facets.find((item) => item.id === facetId);
  const label = domain?.name ?? facet?.label ?? facetId.replaceAll("_", " ").replaceAll(".", " ");
  return label.charAt(0).toUpperCase() + label.slice(1);
}

export function Field({
  decision,
  spec,
  onAdd,
  onDismiss,
  showQuestions = true,
  vocabulary,
  boardOnly = false,
}: {
  decision: AdapterDecision;
  spec?: Spec;
  onAdd: (c: Cond) => void;
  onDismiss: (id: string) => void;
  showQuestions?: boolean;
  vocabulary?: Vocabulary;
  boardOnly?: boolean;
}) {
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
          ? `Ranking on ${Object.entries(spec.boardWeights).map(([id, weight]) => `${objectiveLabel(id, vocabulary)} ${weight.toFixed(2)}`).join(" · ")}`
          : "Ranked on evidence",
        n: e.feasible.length,
        may: e.may.length,
        engineAdded: false,
      },
    ],
    total = Math.max(1, steps[0]?.n ?? 1);
  return (
    <section className="narrowing">
      <div className="panel">
        <div className="panel-heading">
          <span className="eyebrow">
            Narrowing, in the order you set conditions
          </span>
          <small>
            {e.feasible.length} qualify · {e.may.length} may qualify ·{" "}
            {e.excluded.length} excluded
          </small>
        </div>
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
    </section>
  );
}
