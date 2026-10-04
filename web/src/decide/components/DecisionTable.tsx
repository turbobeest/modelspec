import { useEffect, useState } from "react";
import {
  fmtB,
  fmtCI,
  money,
  per1M,
  tok,
  status,
  reason,
} from "../adapter";
import { useVocab } from "../vocabulary/context";
import type { AdapterDecision, Row, Spec } from "../adapter";
import { boardHasPreference } from "../facet-board/model";
import { groupRowsByClass } from "../facet-board/class-groups";
const unavailable = <span role="img" aria-label="not yet researched or not published">–</span>;
const columns: [string, string, (r: Row) => number | string][] = [
  ["rank", "#", (r) => r.rank ?? (r.status === 0 ? 500 : 1000 + r.dropAt)],
  ["name", "Model", (r) => r.m.name],
  ["offering", "Offering", (r) => r.best.o.provider],
  ["cap", "", (r) => r.cap ?? -1],
  ["cost", "$ per task", (r) => r.cost ?? Infinity],
  ["in", "In $/1M", (r) => r.best.o.in ?? Infinity],
  ["out", "Out $/1M", (r) => r.best.o.out ?? Infinity],
  ["ttft", "First token", (r) => r.best.o.ttft ?? Infinity],
  ["tps", "Tok/s", (r) => r.tps ?? -1],
  ["ctx", "Context", (r) => r.m.ctx ?? -1],
  ["weights", "Weights", (r) => (r.m.open ? 0 : 1)],
  ["status", "Status", (r) => -r.status],
];
export function DecisionTable({
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
  const { label, basisName, vocabulary } = useVocab();
  const ranked = spec.boardWeights === undefined || boardHasPreference(spec);
  const visibleColumns = ranked ? columns : columns.filter(([key]) => key !== "rank");
  const [sort, setSort] = useState(ranked ? "rank" : "name"),
    [dir, setDir] = useState(1),
    [show, setShow] = useState(true),
    [showWithoutProvider, setShowWithoutProvider] = useState(false),
    e = decision.explanation;
  useEffect(() => {
    setSort(ranked ? "rank" : "name");
    setDir(1);
  }, [ranked]);
  const filteredRows = e.rows.filter((r) => show || r.status !== -1);
  const withoutProvider = filteredRows.filter((r) => r.best.o.provider === "Provider not available").length;
  const sortedBy = ranked ? sort : "name";
  const direction = ranked ? dir : 1;
  const val = columns.find((c) => c[0] === sortedBy)?.[2] || columns[0][2],
    rows = filteredRows
      .filter((r) => showWithoutProvider || r.best.o.provider !== "Provider not available")
      .slice()
      .sort((a, b) => {
        if (!ranked) return 0;
        const x = val(a),
          y = val(b);
        return (x > y ? 1 : x < y ? -1 : 0) * direction;
      });
  const groups = ranked
    ? [{ id: "ranked", label: null, rows }]
    : groupRowsByClass(rows, vocabulary);
  return (
    <section className="panel decision-table" aria-label="Decision table">
      <div className="panel-heading">
        <span className="eyebrow">
          Decision table · {e.feasible.length} qualify, {e.may.length} may
        </span>
        <label>
          <input
            type="checkbox"
            checked={show}
            onChange={(ev) => setShow(ev.target.checked)}
          />{" "}
          Show {e.excluded.length} excluded
        </label>
        {withoutProvider > 0 && <button
          aria-expanded={showWithoutProvider}
          onClick={() => setShowWithoutProvider((current) => !current)}
        >
          {showWithoutProvider ? "Hide" : "Show"} {withoutProvider} without a provider
        </button>}
      </div>
      {!ranked && <p className="table-key">Not ranked yet: listed alphabetically</p>}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {visibleColumns.map(([key, title]) => (
                <th
                  key={key}
                  title={key === "rank" ? "Model rank on your weights" : undefined}
                  aria-sort={
                    sortedBy === key
                      ? direction === 1
                        ? "ascending"
                        : "descending"
                      : "none"
                  }
                >
                  <button
                    disabled={!ranked}
                    title={!ranked ? "Set a Prefer to rank or sort these models" : undefined}
                    onClick={() => {
                      setSort(key);
                      setDir(sort === key ? -dir : 1);
                    }}
                  >
                    {title || basisName(spec)}
                    {sortedBy === key ? (direction === 1 ? " ↑" : " ↓") : ""}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          {groups.map((group) => <tbody key={group.id}>
            {group.label && <tr className="table-class-heading"><th scope="rowgroup" colSpan={visibleColumns.length}>{group.label}</th></tr>}
            {group.rows.map((r, index) => (
              <tr
                key={`${r.m.lab}/${r.m.id}:${r.best.o.id}:${r.status}:${index}`}
                className={`${r.m.id === selected ? "selected" : ""} ${r.status === -1 ? "excluded-row status-out" : r.status === 0 ? "status-may" : "status-qualifies"}`}
                onClick={() => onSelect(r.m.id)}
              >
                {ranked && <td>{r.rank ?? ""}</td>}
                <td>
                  <button
                    className="table-model"
                    onClick={() => onSelect(r.m.id)}
                  >
                    {r.m.name}
                  </button>
                  <small>{r.m.labName}</small>
                </td>
                <td>{r.best.o.provider === "Provider not available" ? unavailable : r.best.o.provider}</td>
                <td>
                  {r.cap === null ? unavailable : fmtB(spec.bench, r.cap)}{" "}
                  <small>{r.capR && fmtCI(spec.bench, r.capR)}</small>
                  <small>
                    {r.capR ? (r.labOnly ? "○ lab" : "● ind.") : ""}
                  </small>
                </td>
                <td>{r.cost === null ? unavailable : money(r.cost)}</td>
                <td>{r.best.o.in === null ? unavailable : per1M(r.best.o.in)}</td>
                <td>{r.best.o.out === null ? unavailable : per1M(r.best.o.out)}</td>
                <td>
                  {r.best.o.ttft === null ? unavailable : r.best.o.ttft + " ms"}
                </td>
                <td>{r.tps ?? unavailable}</td>
                <td>{r.m.ctx === null ? unavailable : tok(r.m.ctx)}</td>
                <td>{r.m.open === null ? unavailable : r.m.open ? "Open" : "Closed"}</td>
                <td>
                  <span
                    className={`eligibility status-${r.status === -1 ? "out" : r.status === 0 ? "may" : "qualifies"}`}
                  >
                    <span aria-hidden="true">{r.status === -1 ? "×" : r.status === 0 ? "?" : "✓"}</span>{" "}{status(r)}
                  </span>
                  <small>{reason(r)}</small>
                </td>
              </tr>
            ))}
          </tbody>)}
        </table>
      </div>
      <p className="table-key">– not yet researched or not published (never zero)</p>
      <div className="eliminations">
        <div className="eyebrow">Eliminations by condition</div>
        {spec.conds.map((c, i) => {
          const group = e.excluded.filter((r) => r.dropAt === i);
          return (
            group.length > 0 && (
              <p key={i}>
                <strong>
                  Failed: {label(c)} · {group.length}
                </strong>
                <small>{group.map((r) => r.m.name).join(", ")}</small>
              </p>
            )
          );
        })}
      </div>
    </section>
  );
}
