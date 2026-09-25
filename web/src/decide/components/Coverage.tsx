import type { Decision } from "../adapter/contract";
import type { Spec } from "../engine/types";
import { lineupCoverage } from "../vocabulary/coverage";
import { useVocab } from "../vocabulary/context";

/** Shown above the results when a decision ranks nothing (MODEL-153). */
export function Coverage({
  decision,
  spec,
  onSpec,
}: {
  decision: Decision;
  spec: Spec;
  onSpec: (s: Spec) => void;
}) {
  const { vocabulary } = useVocab();
  const c = vocabulary && lineupCoverage(decision, spec, vocabulary);
  if (!c) return null;
  return (
    <section className="panel coverage-panel" aria-label="Lineup coverage">
      <div className="eyebrow">No ranked result</div>
      <div className="coverage-columns">
        <div>
          <h2>What this question needed</h2>
          <ul>
            {c.needed.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>
        <div>
          <h2>What today's verified lineup covers</h2>
          <p>{c.covers}</p>
        </div>
      </div>
      {!!c.relaxTo.length && (
        <div className="coverage-relax">
          <span>The smallest change that answers:</span>
          {c.relaxTo.map((r) => (
            <button
              key={r.index}
              className="ink-button"
              onClick={() =>
                onSpec({
                  ...spec,
                  conds: spec.conds.map((cond, i) => (i === r.index ? r.cond : cond)),
                })
              }
            >
              {r.label}{" "}
              <small>
                admits {r.admits} {r.admits === 1 ? "model" : "models"}
              </small>
            </button>
          ))}
        </div>
      )}
      {!!c.relax.length && (
        <div className="coverage-relax">
          <span>{c.relaxTo.length ? "Or drop:" : "The engine can answer if you drop:"}</span>
          {c.relax.map((r) => (
            <button
              key={r.index}
              className="ink-button"
              onClick={() =>
                onSpec({ ...spec, conds: spec.conds.filter((_, i) => i !== r.index) })
              }
            >
              {r.label}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
