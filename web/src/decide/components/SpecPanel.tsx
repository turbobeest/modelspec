import { useState } from "react";
import { BENCH, FACETS, TYPES, label } from "../adapter";
import type { Cond, Spec } from "../adapter";
import type { AdapterDecision } from "../adapter";
import { setWeight } from "../state/spec";
import type { ParsedTask } from "../engine/reference";
export function SpecPanel({
  spec,
  decision,
  draft,
  onDraft,
  onParse,
  onSpec,
  parsing,
  trace,
  addOpen,
  setAddOpen,
  edit,
  setEdit,
}: {
  spec: Spec;
  decision: AdapterDecision;
  draft: string;
  onDraft: (v: string) => void;
  onParse: () => void;
  onSpec: (s: Spec) => void;
  parsing: boolean;
  trace: ParsedTask["trace"];
  addOpen: boolean;
  setAddOpen: (v: boolean) => void;
  edit: number | null;
  setEdit: (v: number | null) => void;
}) {
  const [query, setQuery] = useState("");
  const matches = FACETS.filter((f) =>
    query
      .toLowerCase()
      .split(/\s+/)
      .every((w) => (f.k + " " + f.label).toLowerCase().includes(w)),
  );
  const update = (i: number, c: Cond) =>
    onSpec({
      ...spec,
      bench:
        c.f === "type"
          ? Object.keys(BENCH).find((b) => BENCH[b].types.includes(c.v)) ||
            spec.bench
          : spec.bench,
      conds: spec.conds.map((x, j) => (j === i ? c : x)),
    });
  const remove = (i: number) => {
    onSpec({ ...spec, conds: spec.conds.filter((_, j) => i !== j) });
    setEdit(null);
  };
  const add = (c: Cond) => {
    const kept = spec.conds.filter(
      (x) =>
        !(x.f === c.f && (x.f !== "bench" || c.f !== "bench" || x.b === c.b)),
    );
    onSpec({ ...spec, conds: [...kept, c] });
    setEdit(kept.length);
    setAddOpen(false);
    setQuery("");
  };
  const ec = edit === null ? null : spec.conds[edit];
  return (
    <section className="panel spec-panel" aria-label="Your spec">
      <div className="spec-top">
        <label className="task-field">
          <span className="eyebrow">Task</span>
          <input
            aria-label="Task"
            value={draft}
            onChange={(e) => onDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                onParse();
              }
            }}
            placeholder="Describe your task (optional), then press Enter"
          />
        </label>
        <div>
          <div className="eyebrow">Tokens per task</div>
          <div className="token-inputs">
            <input
              aria-label="Input tokens per task"
              type="number"
              min="0"
              step="1000"
              value={spec.tokIn}
              onChange={(e) =>
                onSpec({ ...spec, tokIn: Math.max(0, Number(e.target.value)) })
              }
            />{" "}
            in{" "}
            <input
              aria-label="Output tokens per task"
              type="number"
              min="0"
              step="500"
              value={spec.tokOut}
              onChange={(e) =>
                onSpec({ ...spec, tokOut: Math.max(0, Number(e.target.value)) })
              }
            />{" "}
            out
          </div>
        </div>
        <div>
          <div className="eyebrow">Rank by (weights sum to 1)</div>
          <div className="weights">
            {(["cap", "cost", "speed"] as const).map((k) => (
              <label key={k}>
                <span>
                  {k === "cap"
                    ? spec.bench
                    : k === "cost"
                      ? "$ per task"
                      : "Tok/s"}{" "}
                  <strong>{spec.w[k].toFixed(2)}</strong>
                </span>
                <input
                  type="range"
                  aria-label={
                    "Weight on " +
                    (k === "cap"
                      ? spec.bench
                      : k === "cost"
                        ? "$ per task"
                        : "Tok/s")
                  }
                  min="0"
                  max="1"
                  step="0.05"
                  value={spec.w[k]}
                  onChange={(e) =>
                    onSpec({
                      ...spec,
                      w: setWeight(spec.w, k, Number(e.target.value)),
                    })
                  }
                />
              </label>
            ))}
          </div>
        </div>
      </div>
      <div className="chips">
        {parsing ? (
          <>
            <span className="skeleton chip" />
            <span className="skeleton chip" />
            <span className="skeleton chip" />
            <span role="status">Reading your task…</span>
          </>
        ) : (
          <>
            {spec.conds.map((c, i) => (
              <span
                key={i}
                className={`chip ${c.from ? "parsed" : ""} ${c.soft ? "soft" : ""} ${i === edit ? "editing" : ""}`}
              >
                <button
                  aria-label={"Edit condition: " + label(c)}
                  aria-expanded={i === edit}
                  onClick={() => {
                    setEdit(i === edit ? null : i);
                    setAddOpen(false);
                  }}
                >
                  {label(c)}{" "}
                  <small>
                    {[
                      c.soft ? "soft" : "",
                      c.from ? "from task" : "",
                      decision.explanation.funnel[i].n -
                      decision.explanation.funnel[i + 1].n
                        ? "−" +
                          (decision.explanation.funnel[i].n -
                            decision.explanation.funnel[i + 1].n) +
                          " removed"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" · ")}
                  </small>
                </button>
                <button
                  aria-label={"Remove condition: " + label(c)}
                  onClick={() => remove(i)}
                >
                  ×
                </button>
              </span>
            ))}
            <button
              className="add"
              aria-expanded={addOpen}
              onClick={() => {
                setAddOpen(!addOpen);
                setEdit(null);
              }}
            >
              + add condition
            </button>
          </>
        )}
      </div>
      {!!trace.length && !parsing && (
        <div className="trace">
          <span>Read from your task:</span>
          {trace.map((t, i) => (
            <span key={i}>
              “{t.word}” → {t.note}
            </span>
          ))}
        </div>
      )}
      {addOpen && (
        <div className="facet-search">
          <input
            autoFocus
            aria-label="Search facets"
            placeholder="Search any facet: residency, retention, latency, licence…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && matches[0]) add(matches[0].c);
            }}
          />
          <div role="listbox" aria-label="Facets">
            {matches.map((f) => (
              <button
                key={f.k}
                role="option"
                aria-selected={false}
                onClick={() => add(f.c)}
              >
                {f.label}
                <small>{f.hint}</small>
              </button>
            ))}
          </div>
        </div>
      )}
      {ec && edit !== null && (
        <div className="condition-editor">
          <div>
            <div className="eyebrow">Edit condition</div>
            <strong>{label(ec)}</strong>
          </div>
          {("min" in ec || "max" in ec) && (
            <label>
              {"min" in ec ? "Minimum" : "Maximum"}
              <span className="inline">
                <input
                  aria-label="Condition value"
                  type="number"
                  min="0"
                  step={
                    ec.f === "bench"
                      ? BENCH[ec.b].d === 3
                        ? 0.005
                        : 0.5
                      : ec.f === "task$"
                        ? 0.005
                        : 1
                  }
                  value={"min" in ec ? ec.min : ec.max}
                  onChange={(e) =>
                    update(
                      edit,
                      "min" in ec
                        ? { ...ec, min: Math.max(0, Number(e.target.value)) }
                        : { ...ec, max: Math.max(0, Number(e.target.value)) },
                    )
                  }
                />
                {ec.f === "bench"
                  ? BENCH[ec.b].unit
                  : ec.f === "ctx"
                    ? "tokens"
                    : ec.f === "tps"
                      ? "output tokens/s"
                      : ec.f === "ttft"
                        ? "ms to first token"
                        : ec.f === "in$"
                          ? "$ per 1M input tokens"
                          : "USD per task"}
              </span>
            </label>
          )}
          {ec.f === "open" && (
            <div className="segments">
              {[true, false].map((v) => (
                <button
                  key={String(v)}
                  aria-pressed={ec.v === v}
                  onClick={() => update(edit, { ...ec, v })}
                >
                  {v ? "Require" : "Exclude"}
                </button>
              ))}
            </div>
          )}
          {ec.f === "resid" && (
            <div className="segments">
              {(["EU", "US", "UK"] as const).map((v) => (
                <button
                  key={v}
                  aria-pressed={ec.v === v}
                  onClick={() => update(edit, { ...ec, v })}
                >
                  {v}
                </button>
              ))}
            </div>
          )}
          {ec.f === "bench" && (
            <div className="segments">
              {[true, false].map((indep) => (
                <button
                  key={String(indep)}
                  aria-pressed={!!ec.indep === indep}
                  onClick={() => update(edit, { ...ec, indep })}
                >
                  {indep ? "Independent only" : "Any source"}
                </button>
              ))}
            </div>
          )}
          {ec.f === "type" && (
            <div className="segments">
              {(Object.keys(TYPES) as (keyof typeof TYPES)[]).map((v) => (
                <button
                  key={v}
                  aria-pressed={ec.v === v}
                  onClick={() => update(edit, { ...ec, v })}
                >
                  {TYPES[v]}
                </button>
              ))}
            </div>
          )}
          {ec.f === "origin" && (
            <label>
              Exclude origin jurisdictions
              <input
                aria-label="Excluded origins"
                value={ec.ex.join(", ")}
                onChange={(e) =>
                  update(edit, {
                    ...ec,
                    ex: e.target.value
                      .split(",")
                      .map((v) => v.trim())
                      .filter(Boolean),
                  })
                }
              />
            </label>
          )}
          {!["type", "active"].includes(ec.f) && (
            <>
              <div className="segments" role="group" aria-label="Hard or soft">
                {[false, true].map((soft) => (
                  <button
                    key={String(soft)}
                    aria-pressed={!!ec.soft === soft}
                    onClick={() => update(edit, { ...ec, soft })}
                  >
                    {soft ? "Soft" : "Hard"}
                  </button>
                ))}
              </div>
              <small>
                {ec.soft
                  ? "Soft: models outside this are kept and flagged. It never adds points."
                  : "Also editable with the matching canvas handle."}
              </small>
            </>
          )}
          <div className="spacer" />
          <button onClick={() => remove(edit)}>Remove</button>
          <button className="ink-button" onClick={() => setEdit(null)}>
            Done
          </button>
        </div>
      )}
    </section>
  );
}
