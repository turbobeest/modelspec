import type { AdapterDecision, Cond } from "../adapter";
export function Field({
  decision,
  onAdd,
  onDismiss,
}: {
  decision: AdapterDecision;
  onAdd: (c: Cond) => void;
  onDismiss: (id: string) => void;
}) {
  const e = decision.explanation,
    steps = [
      ...e.funnel,
      { label: "Ranked on evidence", n: e.feasible.length, may: e.may.length },
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
            <li key={i} className={i === steps.length - 1 ? "ranked" : ""}>
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
              <span>{f.label}</span>
              <small>
                {i === 0
                  ? `${f.n} candidates`
                  : i === steps.length - 1
                    ? `+ ${f.may} may qualify`
                    : `${steps[i - 1].n - f.n ? "−" + (steps[i - 1].n - f.n) : "no change"}${f.may ? " · " + f.may + " may" : ""}`}
              </small>
            </li>
          ))}
        </ol>
      </div>
      <div className="panel questions">
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
                    {o.n === undefined ? (
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
      </div>
    </section>
  );
}
