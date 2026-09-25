import { useEffect, useMemo, useRef, useState } from "react";
import {
  fictionalEngine,
  templates,
  catalogue,
  parseTask,
  label,
  fmtB,
  fmtCI,
} from "./adapter";
import type { Cond, Evidence, Spec } from "./adapter";
import { baseSpec, decodeSpec, encodeSpec } from "./state/spec";
import type { Axis } from "./state/spec";
import { SpecPanel } from "./components/SpecPanel";
import { Field } from "./components/Field";
import { Canvas } from "./components/Canvas";
import { Shortlist } from "./components/Shortlist";
import { DecisionTable } from "./components/DecisionTable";
import { Why } from "./components/Why";
import { Share } from "./components/Share";
import "./decide.css";
import { RealApp } from "./RealApp";

export function DemoApp({
  simulate,
}: {
  simulate?: "loading" | "error" | "none";
}) {
  const [initial] = useState(() => decodeSpec(location.hash)),
    [spec, setSpec] = useState<Spec>(initial?.spec || baseSpec),
    [axis, setAxis] = useState<Axis>(initial?.x || "task$"),
    [view, setView] = useState(initial ? "work" : "arrive");
  const [draft, setDraft] = useState(
      initial?.spec.task ?? "Refactor a large Rust codebase, precision matters",
    ),
    [theme, setTheme] = useState(() =>
      new URLSearchParams(location.search).get("theme") === "dark"
        ? "dark"
        : "light",
    ),
    [layout, setLayout] = useState(() =>
      new URLSearchParams(location.search).get("layout") === "table"
        ? "table"
        : "canvas",
    );
  const [selected, setSelected] = useState<string | null>(null),
    [parsing, setParsing] = useState(false),
    [trace, setTrace] = useState<ReturnType<typeof parseTask>["trace"]>([]),
    [addOpen, setAddOpen] = useState(false),
    [edit, setEdit] = useState<number | null>(null),
    [dismissed, setDismissed] = useState<string[]>([]),
    [share, setShare] = useState(false),
    [provenance, setProvenance] = useState<{
      e: Evidence;
      x: number;
      y: number;
    } | null>(null),
    [retried, setRetried] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null),
    provTrigger = useRef<HTMLElement | null>(null);
  const decision = useMemo(
      () => fictionalEngine.decide(spec, { axis, dismissed }),
      [spec, axis, dismissed],
    ),
    e = decision.explanation,
    selectedId = selected || e.shortlist.top?.m.id || e.may[0]?.m.id || null,
    row = e.rows.find((r) => r.m.id === selectedId) || null;
  const sim = simulate || new URLSearchParams(location.search).get("simulate"),
    error = sim === "error" && !retried,
    loading = sim === "loading";
  useEffect(() => {
    if (view === "work")
      history.replaceState(
        null,
        "",
        location.pathname + location.search + encodeSpec(spec, axis),
      );
  }, [spec, axis, view]);
  useEffect(() => {
    document.documentElement.dataset.decideTheme = theme;
    return () => {
      delete document.documentElement.dataset.decideTheme;
    };
  }, [theme]);
  useEffect(() => {
    const esc = (ev: KeyboardEvent) => {
      if (ev.key === "Escape") {
        setShare(false);
        setProvenance(null);
        setAddOpen(false);
        setEdit(null);
        provTrigger.current?.focus();
      }
    };
    const hash = () => {
      const restored = decodeSpec(location.hash);
      if (restored) {
        setSpec(restored.spec);
        setAxis(restored.x);
        setDraft(restored.spec.task || "");
        setView("work");
        setSelected(null);
      }
    };
    window.addEventListener("keydown", esc);
    window.addEventListener("hashchange", hash);
    return () => {
      window.removeEventListener("keydown", esc);
      window.removeEventListener("hashchange", hash);
      if (timer.current) clearTimeout(timer.current);
    };
  }, []);
  function find() {
    setView("work");
    setParsing(true);
    setAddOpen(false);
    setEdit(null);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      const p = parseTask(draft),
        keep = spec.conds.filter(
          (c) =>
            !c.from &&
            !p.conds.some(
              (n) =>
                n.f === c.f &&
                (n.f !== "bench" || c.f !== "bench" || n.b === c.b),
            ),
        );
      setSpec({
        ...spec,
        task: draft,
        bench: p.bench,
        w: p.w,
        conds: [...p.conds, ...keep],
      });
      setTrace(p.trace);
      setParsing(false);
      setSelected(null);
      setAxis(p.bench === "RetrievalEval v2" ? "in$" : "task$");
    }, 420);
  }
  function add(c: Cond) {
    setSpec((s) => {
      const i = s.conds.findIndex(
        (x) =>
          x.f === c.f && (x.f !== "bench" || c.f !== "bench" || x.b === c.b),
      );
      return {
        ...s,
        conds:
          i < 0 ? [...s.conds, c] : s.conds.map((x, j) => (j === i ? c : x)),
      };
    });
  }
  function relax(i: number) {
    const n = decision.near_misses[i];
    if (n)
      setSpec((s) => ({
        ...s,
        conds: s.conds.flatMap((c, j) =>
          j === n.ci ? (n.relaxed ? [n.relaxed] : []) : [c],
        ),
      }));
  }
  function start(s: Spec) {
    setSpec(structuredClone(s));
    setDraft(s.task || "");
    setView("work");
    setSelected(null);
    setTrace([]);
    setDismissed([]);
  }
  return (
    <div className="decide-app" data-theme={theme} data-layout={layout}>
      <header className="global-header">
        <button
          className="brand"
          aria-label="ModelSpec home"
          onClick={() => setView("arrive")}
        >
          <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">
            <rect width="32" height="32" rx="3" fill="var(--navy)" />
            <path
              d="M6 4.5V26H28"
              fill="none"
              stroke="#8fa3c2"
              strokeWidth="1.2"
            />
            <path
              d="M8.6 23.2C9.8 17.4 10.9 10.6 12.6 9.8C14.3 9 15 17.2 16.2 18.6C17.3 17.4 18.1 9.9 19.9 9.8C21.7 9.7 21.8 18.6 23.4 21.2C24.2 22.5 25.4 22.4 26.4 21.2"
              fill="none"
              stroke="white"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {[
              [8.6, 23.2],
              [12.6, 9.8],
              [16.2, 18.6],
              [19.9, 9.8],
              [23.4, 21.2],
            ].map(([cx, cy]) => (
              <circle key={cx} cx={cx} cy={cy} r="1.5" fill="#5aa9ec" />
            ))}
          </svg>
          <span>
            Model<span>Spec</span>
          </span>
        </button>
        <span className="sample-badge">Fictional sample data</span>
        <div className="spacer" />
        {view === "work" && (
          <span className="snapshot">{decision.snapshot}</span>
        )}
        <div className="segments" role="group" aria-label="Layout">
          <button
            aria-pressed={layout === "canvas"}
            onClick={() => setLayout("canvas")}
          >
            Canvas first
          </button>
          <button
            aria-pressed={layout === "table"}
            onClick={() => setLayout("table")}
          >
            Table first
          </button>
        </div>
        <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
        {view === "work" && (
          <button className="primary" onClick={() => setShare(true)}>
            Share or act
          </button>
        )}
      </header>
      {view === "arrive" ? (
        <main className="arrive">
          <div className="arrival-intro">
            <div className="eyebrow">Model decision engine</div>
            <h1>
              Which AI model fits your task, under your constraints, and why.
            </h1>
            <p>
              Describe the task or set conditions. ModelSpec filters{" "}
              {catalogue.models.length} models across {catalogue.offerings}{" "}
              provider offerings, ranks what is left on evidence, and shows the
              source of every number. Independent measurements sit next to lab
              claims.
            </p>
          </div>
          <div className="task-box">
            <label htmlFor="task" className="eyebrow">
              Describe your task
            </label>
            <textarea
              id="task"
              rows={2}
              value={draft}
              onChange={(ev) => setDraft(ev.target.value)}
              onKeyDown={(ev) => {
                if (ev.key === "Enter" && !ev.shiftKey) {
                  ev.preventDefault();
                  find();
                }
              }}
            />
            <div>
              <span>
                A small classifier turns this into conditions you can see and
                edit. There is no chat.
              </span>
              <button className="primary" onClick={find}>
                Find models ↵
              </button>
            </div>
          </div>
          <div>
            <div className="eyebrow">Or start from a template</div>
            <div className="templates">
              {templates.map((t) => (
                <button
                  key={t.id}
                  onClick={() => start({ ...t.spec, task: t.task })}
                >
                  <strong>{t.name}</strong>
                  <span>{t.task}</span>
                  <div className="mini-chips">
                    {t.spec.conds
                      .filter((c) => c.f !== "active")
                      .map((c, i) => (
                        <span key={i}>{label(c)}</span>
                      ))}
                  </div>
                  <footer>
                    <strong>{t.counts.feasible.length}</strong> qualify{" "}
                    <span className="warn">
                      {t.counts.may.length
                        ? "+ " + t.counts.may.length + " may qualify"
                        : ""}
                    </span>
                  </footer>
                </button>
              ))}
            </div>
          </div>
          <div className="start-constraints">
            Or{" "}
            <button
              className="link"
              onClick={() => {
                start(baseSpec);
                setAddOpen(true);
              }}
            >
              start from constraints
            </button>{" "}
            and add conditions one at a time.
          </div>
        </main>
      ) : (
        <main className="work">
          <SpecPanel
            spec={spec}
            decision={decision}
            draft={draft}
            onDraft={setDraft}
            onParse={find}
            onSpec={setSpec}
            parsing={parsing}
            trace={trace}
            addOpen={addOpen}
            setAddOpen={setAddOpen}
            edit={edit}
            setEdit={setEdit}
          />
          <Field
            decision={decision}
            onAdd={add}
            onDismiss={(id) => setDismissed([...dismissed, id])}
          />
          {error ? (
            <div role="alert" className="error">
              <div>
                <strong>Couldn't load snapshot {decision.snapshot}.</strong>
                <p>
                  The catalogue service didn't respond in 8 s. Your spec is kept
                  in the link, so nothing is lost. Results below are hidden
                  rather than shown stale.
                </p>
              </div>
              <button className="ink-button" onClick={() => setRetried(true)}>
                Retry
              </button>
            </div>
          ) : loading ? (
            <div role="status" aria-busy="true" className="loading">
              <div className="loading-canvas">
                <span className="skeleton" />
                <div className="skeleton" />
                <p>
                  Loading snapshot {decision.snapshot} · 25 models, 60 offerings
                </p>
              </div>
              <div className="loading-cards">
                <span />
                <span />
                <span />
              </div>
            </div>
          ) : (
            <div className="results">
              <Canvas
                decision={decision}
                spec={spec}
                axis={axis}
                onAxis={setAxis}
                onSpec={setSpec}
                onAdd={add}
                selected={selectedId}
                onSelect={setSelected}
                onRelax={relax}
                compact={layout === "table"}
              />
              <Shortlist
                decision={decision}
                spec={spec}
                selected={selectedId}
                onSelect={setSelected}
              />
              <DecisionTable
                decision={decision}
                spec={spec}
                selected={selectedId}
                onSelect={setSelected}
              />
              <Why
                decision={decision}
                spec={spec}
                row={row}
                onSpec={setSpec}
                onRelax={relax}
                onProvenance={(ev) => {
                  provTrigger.current =
                    document.activeElement instanceof HTMLElement
                      ? document.activeElement
                      : null;
                  const rect = provTrigger.current?.getBoundingClientRect();
                  setProvenance({
                    e: ev,
                    x: Math.max(
                      8,
                      Math.min(window.innerWidth - 340, rect?.left || 0),
                    ),
                    y: Math.max(
                      64,
                      Math.min(
                        window.innerHeight - 270,
                        (rect?.bottom || 0) + 6,
                      ),
                    ),
                  });
                }}
              />
            </div>
          )}
        </main>
      )}
      {provenance && (
        <div
          className="provenance-popover"
          style={{ left: provenance.x, top: provenance.y }}
          role="dialog"
          aria-label="Evidence provenance"
        >
          <div className="panel-heading">
            <strong>{provenance.e.b}</strong>
            <button
              autoFocus
              aria-label="Close provenance"
              onClick={() => {
                setProvenance(null);
                provTrigger.current?.focus();
              }}
            >
              ×
            </button>
          </div>
          <dl>
            {[
              [
                "Value",
                fmtB(provenance.e.b, provenance.e.v) +
                  " " +
                  fmtCI(provenance.e.b, provenance.e),
              ],
              [
                "Measured by",
                provenance.e.who +
                  (provenance.e.by === "lab"
                    ? " (lab-reported)"
                    : " (independent)"),
              ],
              ["Effort setting", provenance.e.effort],
              ["Harness", provenance.e.harness],
              ["Date", provenance.e.date],
              ["Source", provenance.e.src],
            ].map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>
                  {k === "Source" ? (
                    <a href={v} target="_blank" rel="noreferrer">
                      {v}
                    </a>
                  ) : (
                    v
                  )}
                </dd>
              </div>
            ))}
          </dl>
          <small>Fictional sample evidence</small>
        </div>
      )}
      {share && (
        <Share
          spec={spec}
          snapshot={decision.snapshot}
          axis={axis}
          row={row}
          onClose={() => setShare(false)}
        />
      )}
    </div>
  );
}

export default function App(props: { simulate?: "loading" | "error" | "none" }) {
  return new URLSearchParams(location.search).get("demo") === "1" ? (
    <DemoApp {...props} />
  ) : (
    <RealApp />
  );
}
