import { useState } from "react";
import { BENCH } from "../adapter";
import type { Cond, Spec } from "../adapter";
import type { AdapterDecision } from "../adapter";
import { setWeight } from "../state/spec";
import type { ParsedTask } from "../engine/reference";
import type { FacetOp, FacetValue, TypeKey } from "../engine/types";
import { useVocab } from "../vocabulary/context";
import { domainForType, rankChoices, switchBenchmark } from "../vocabulary";
import { issuesFor } from "../vocabulary/issues";
import type { PlacedIssue } from "../vocabulary/issues";
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
  issues = [],
}: {
  spec: Spec;
  decision: AdapterDecision | null;
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
  /** A refused spec's issues, placed on the control that caused each. */
  issues?: PlacedIssue[];
}) {
  const vocab = useVocab();
  const { label } = vocab;
  const [query, setQuery] = useState("");
  const matches = vocab.facetOptions.filter((f) =>
    query
      .toLowerCase()
      .split(/\s+/)
      .every((w) => (f.k + " " + f.label).toLowerCase().includes(w)),
  );
  const update = (i: number, c: Cond) => {
    const retyped =
      c.f === "type" && vocab.vocabulary ? domainForType(vocab.vocabulary, c.v) : null;
    onSpec({
      ...spec,
      ...(retyped ?? {}),
      ...(c.f === "type" && !vocab.vocabulary
        ? {
            bench:
              Object.keys(BENCH).find((b) => BENCH[b].types.includes(c.v)) ||
              spec.bench,
          }
        : {}),
      conds: spec.conds.map((x, j) => (j === i ? c : x)),
    });
  };
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
  const conditionAvailable = (condition: Cond) => {
    if (!decision) return true;
    switch (condition.f) {
      case "task$":
      case "in$":
      case "ttft":
      case "tps":
      case "ctx":
        return decision.available_axes[condition.f];
      case "bench":
        return decision.explanation.inScope.some((row) =>
          row.m.bench.some((evidence) => evidence.b === condition.b),
        );
      case "open":
        return decision.explanation.inScope.some(
          (row) => row.m.open !== null,
        );
      default:
        return true;
    }
  };
  const benchLabel = vocab.benchName(spec.bench);
  const choices = vocab.vocabulary ? rankChoices(vocab.vocabulary, spec.domain) : [];
  const weightName = (k: "cap" | "cost" | "speed") =>
    k === "cap" ? benchLabel : k === "cost" ? "$ per task" : "Tok/s";
  const tokenIssues = issuesFor(issues, { kind: "tokens" });
  const weightIssues = issuesFor(issues, { kind: "weights" });
  const removed = (i: number) => {
    const funnel = decision?.explanation.funnel;
    const drop = funnel && funnel[i] && funnel[i + 1] ? funnel[i].n - funnel[i + 1].n : 0;
    return drop ? "−" + drop + " removed" : "";
  };
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
        <div className={tokenIssues.length ? "has-issue" : undefined}>
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
          {tokenIssues.map((text) => (
            <p key={text} className="issue-note" role="note">
              {text}
            </p>
          ))}
        </div>
        <div className={weightIssues.length ? "has-issue" : undefined}>
          <div className="eyebrow">Rank by (weights sum to 1)</div>
          <div className="weights">
            {vocab.weightKeys.map((k) => (
              <label key={k}>
                <span>
                  {weightName(k)} <strong>{spec.w[k].toFixed(2)}</strong>
                </span>
                <input
                  type="range"
                  aria-label={"Weight on " + weightName(k)}
                  min="0"
                  max="1"
                  step="0.05"
                  value={spec.w[k]}
                  onChange={(e) =>
                    onSpec({
                      ...spec,
                      w: setWeight(spec.w, k, Number(e.target.value), vocab.weightKeys),
                    })
                  }
                />
              </label>
            ))}
          </div>
          {choices.length > 1 && (
            <div className="rank-on" role="group" aria-label="Benchmark to rank on">
              <span>Measured by</span>
              {choices.map((b) => (
                <button
                  key={b.id}
                  aria-pressed={b.id === spec.bench}
                  title={`${b.models} lineup models with verified results, ${b.independent_models} measured independently`}
                  onClick={() => onSpec(switchBenchmark(vocab.vocabulary!, spec, b.id))}
                >
                  {b.name} <small>{b.models} {b.models === 1 ? "model" : "models"}</small>
                </button>
              ))}
            </div>
          )}
          {weightIssues.map((text) => (
            <p key={text} className="issue-note" role="note">
              {text}
            </p>
          ))}
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
            {spec.conds.map((c, i) => {
              const problems = issuesFor(issues, { kind: "condition", index: i });
              return (
              <span key={i} className="chip-wrap">
              <span
                className={`chip ${c.from ? "parsed" : ""} ${c.soft ? "soft" : ""} ${i === edit ? "editing" : ""} ${problems.length ? "has-issue" : ""}`}
                data-issue={problems.length ? "true" : undefined}
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
                      !conditionAvailable(c)
                        ? "not available in this snapshot"
                        : "",
                      removed(i),
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
              {problems.map((text) => (
                <span key={text} className="issue-note" role="note">
                  {text}
                </span>
              ))}
              </span>
              );
            })}
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
                      ? (vocab.benchmarks[ec.b]?.d ?? 2) === 3
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
                  ? vocab.benchmarks[ec.b]?.unit ??
                    "not available in this snapshot"
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
              {(Object.keys(vocab.types) as TypeKey[]).map((v) => (
                <button
                  key={v}
                  aria-pressed={ec.v === v}
                  onClick={() => update(edit, { ...ec, v })}
                >
                  {vocab.types[v]}
                </button>
              ))}
            </div>
          )}
          {ec.f === "facet" && (
            <FacetEditor
              cond={ec}
              onChange={(next) => update(edit, next)}
            />
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

const EDITABLE_OPS: readonly FacetOp[] = ["=", "!=", "<=", ">=", "in", "not in"];
const OP_NAMES: Readonly<Record<FacetOp, string>> = {
  "=": "is",
  "!=": "is not",
  "<=": "at most",
  ">=": "at least",
  in: "any of",
  "not in": "none of",
};

/** The editor for a condition on any vocabulary facet: its operators and its values. */
function FacetEditor({
  cond,
  onChange,
}: {
  cond: Extract<Cond, { f: "facet" }>;
  onChange: (c: Cond) => void;
}) {
  const { vocabulary } = useVocab();
  const row = vocabulary?.facets.find((facet) => facet.id === cond.facet);
  if (!row) return <small>not available in this snapshot</small>;
  const ops = EDITABLE_OPS.filter((op) => row.operators.includes(op));
  const choices = (row.values ?? []).map((item) => item.value);
  const listed = Array.isArray(cond.value) ? cond.value : [String(cond.value)];
  const setOp = (op: FacetOp) => {
    const many = op === "in" || op === "not in";
    const first = listed[0];
    const value: FacetValue = many
      ? listed
      : Array.isArray(cond.value)
        ? (choices.find((c) => String(c) === first) ?? first)
        : cond.value;
    onChange({ ...cond, op, value });
  };
  const toggle = (value: string) => {
    const next = listed.includes(value)
      ? listed.filter((item) => item !== value)
      : [...listed, value];
    if (next.length) onChange({ ...cond, value: next });
  };
  return (
    <>
      <div className="segments" role="group" aria-label="Operator">
        {ops.map((op) => (
          <button key={op} aria-pressed={cond.op === op} onClick={() => setOp(op)}>
            {OP_NAMES[op]}
          </button>
        ))}
      </div>
      {row.value_type === "number" && (
        <label>
          Value
          <span className="inline">
            <input
              aria-label="Condition value"
              type="number"
              value={typeof cond.value === "number" ? cond.value : 0}
              onChange={(e) => onChange({ ...cond, value: Number(e.target.value) })}
            />
            {row.unit?.replaceAll("_", " ")}
          </span>
        </label>
      )}
      {row.value_type === "date" && (
        <label>
          Date
          <input
            aria-label="Condition value"
            type="date"
            value={typeof cond.value === "string" ? cond.value : ""}
            onChange={(e) => e.target.value && onChange({ ...cond, value: e.target.value })}
          />
        </label>
      )}
      {row.value_type === "boolean" && (
        <div className="segments" role="group" aria-label="Value">
          {[true, false].map((value) => (
            <button
              key={String(value)}
              aria-pressed={cond.value === value}
              onClick={() => onChange({ ...cond, value })}
            >
              {value ? "Yes" : "No"}
            </button>
          ))}
        </div>
      )}
      {(row.value_type === "enum" || row.value_type === "set") && (
        <div className="segments" role="group" aria-label="Values">
          {choices.map((choice) => {
            const value = String(choice);
            const many = cond.op === "in" || cond.op === "not in";
            return (
              <button
                key={value}
                aria-pressed={listed.includes(value)}
                onClick={() => (many ? toggle(value) : onChange({ ...cond, value }))}
              >
                {value.replaceAll(/[_-]+/g, " ")}
              </button>
            );
          })}
        </div>
      )}
    </>
  );
}
