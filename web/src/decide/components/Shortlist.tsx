import { fmtB, fmtCI, money, reason } from "../adapter";
import { useVocab } from "../vocabulary/context";
import type { AdapterDecision, Spec } from "../adapter";
export function Shortlist({
  decision,
  spec,
  selected,
  onSelect,
}: {
  decision: AdapterDecision;
  spec: Spec;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const { label, benchName, weightKeys } = useVocab(),
    bench = benchName(spec.bench),
    speed = weightKeys.includes("speed");
  const e = decision.explanation,
    s = e.shortlist,
    seen = new Map<string, string>();
  return (
    <aside className="shortlist">
      <section className="panel">
        <div className="eyebrow">Shortlist</div>
        <small>
          {bench} {spec.w.cap.toFixed(2)} · $ {spec.w.cost.toFixed(2)}
          {speed && ` · speed ${spec.w.speed.toFixed(2)}`}
        </small>
        <div className="cards">
          {[
            { role: "Best overall for your weights", row: s.top },
            { role: "Best value", row: s.value },
            { role: "Cheapest that clears your bar", row: s.clears },
            { role: "Best open weights", row: s.open },
          ].map(({ role, row }) => {
            const dup = row && seen.get(row.m.id);
            if (row) seen.set(row.m.id, role);
            return (
              <button
                key={role}
                className={
                  "result-card " + (row?.m.id === selected ? "selected" : "")
                }
                onClick={() => row && onSelect(row.m.id)}
              >
                {row ? (
                  <>
                    <span className="role-row">
                      <span className="role">{role}</span>
                      <small>
                        {dup
                          ? "same as " + dup.toLowerCase()
                          : role === "Best value"
                            ? "most " + bench + " per $"
                            : role === "Best overall for your weights"
                              ? "#1 of " + e.feasible.length
                              : role === "Best open weights"
                                ? row.m.lic
                                : s.bar === null
                                  ? "no bar set; any score"
                                  : "bar: " + fmtB(spec.bench, s.bar)}
                      </small>
                    </span>
                    <span className="name-row">
                      <strong className="model-name">{row.m.name}</strong>
                      <small>
                        {row.m.labName} · via {row.best.o.provider}
                      </small>
                    </span>
                    <div className="metrics">
                      <span>
                        <small>{bench}</small>
                        {fmtB(spec.bench, row.cap)}{" "}
                        <small>{fmtCI(spec.bench, row.capR)}</small>
                        <small>
                          {row.labOnly ? "Lab-reported" : "Independent"}
                        </small>
                      </span>
                      <span>
                        <small>$ per task</small>
                        {money(row.cost)}
                      </span>
                      {speed && (
                        <span>
                          <small>Output</small>
                          {row.tps ?? "unknown"} {row.tps === null ? "" : "tok/s"}
                        </span>
                      )}
                    </div>
                    {(e.insep(row).length > 0 ||
                      row.labOnly ||
                      row.best.softs.length > 0) && (
                      <span className="note">
                        {[
                          e.insep(row).length
                            ? "Not separable from " +
                              e
                                .insep(row)
                                .map((r) => r.m.name)
                                .join(", ") +
                              " on " +
                              bench
                            : "",
                          row.labOnly ? "Ranked on a lab-reported score" : "",
                          row.best.softs.length
                            ? "Outside your preference: " +
                              row.best.softs
                                .map((i) => label(spec.conds[i]))
                                .join(", ")
                            : "",
                        ]
                          .filter(Boolean)
                          .join(" · ")}
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    <span className="role">{role}</span>
                    <span>
                      {role === "Best open weights"
                        ? "No open-weights model qualifies."
                        : "Nothing qualifies yet."}
                    </span>
                  </>
                )}
              </button>
            );
          })}
        </div>
      </section>
      <section className="may-panel">
        <div className="eyebrow">May qualify · {e.may.length}</div>
        {e.may.map((r) => (
          <button key={r.m.id} onClick={() => onSelect(r.m.id)}>
            <strong>{r.m.name}</strong>
            {r.m.provisional && <span className="badge warn">Provisional</span>}
            <small>{r.m.labName}</small>
            <span>Unknown: {reason(r)}</span>
          </button>
        ))}
        {!e.may.length && <small>No unresolved conditions.</small>}
      </section>
    </aside>
  );
}
