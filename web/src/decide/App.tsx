import { useEffect, useMemo, useRef, useState } from "react";
import {
  fictionalEngine,
  templates,
  catalogue,
  candidateQuestions,
  hostedEngine,
  DecideApiError,
  parseTask,
  fmtB,
  fmtCI,
} from "./adapter";
import type { Cond, Decision, Evidence, Spec, SpecIssue } from "./adapter";
import {
  VocabularyError,
  loadVocabulary,
  parseRealTask,
  realBaseSpec,
  realQuestions,
  realTemplates,
  sendable as sendableSpec,
} from "./vocabulary";
import type { Vocabulary } from "./vocabulary";
import { VocabContext, fictionalVocab, realVocab } from "./vocabulary/context";
import { placeIssues } from "./vocabulary/issues";
import { registerBenchmarks } from "./adapter/condition-label";
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
import { mapDecisionToViewModel, toDecisionSpec } from "./adapter/view-model";
import { evaluateQuestionOptions } from "./adapter/questions";
import type { Question } from "./engine/reference";

function DesignedApp({
  demo,
  simulate,
}: {
  demo: boolean;
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
    requestTimer = useRef<ReturnType<typeof setTimeout> | null>(null),
    requestAbort = useRef<AbortController | null>(null),
    questionsAbort = useRef<AbortController | null>(null),
    provTrigger = useRef<HTMLElement | null>(null);
  const [hostedDecision, setHostedDecision] = useState<Decision | null>(null),
    [hostedQuestions, setHostedQuestions] = useState<Question[]>([]),
    [requestState, setRequestState] = useState<
      | { kind: "idle" }
      | { kind: "loading" }
      | {
          kind: "error";
          message: string;
          code: string | null;
          status: number | null;
          issues: SpecIssue[];
        }
      | { kind: "success" }
    >({ kind: "idle" }),
    [vocabState, setVocabState] = useState<
      | { kind: "loading" }
      | { kind: "ready"; vocabulary: Vocabulary }
      | { kind: "error"; error: VocabularyError }
    >({ kind: "loading" }),
    [vocabAttempt, setVocabAttempt] = useState(0);
  const vocabulary = !demo && vocabState.kind === "ready" ? vocabState.vocabulary : null;
  const vocab = useMemo(() => {
    if (!vocabulary) return fictionalVocab;
    registerBenchmarks(vocabulary.benchmarks);
    return realVocab(vocabulary);
  }, [vocabulary]);
  const shownAxis = vocab.axes.includes(axis) ? axis : (vocab.axes[0] ?? axis);
  const liveTemplates = useMemo(
    () => (vocabulary ? realTemplates(vocabulary) : []),
    [vocabulary],
  );
  /** Only the sliders the snapshot can answer, as the engine will be asked. */
  const sendable = (next: Spec): Spec =>
    vocabulary ? sendableSpec(vocabulary, next) : next;
  const questionsFor = (next: Spec) =>
    vocabulary ? realQuestions(vocabulary, next, dismissed) : candidateQuestions(next, dismissed);
  // The fictional engine knows only the fictional catalogue: demo mode only.
  const sampleDecision = useMemo(
      () => (demo ? fictionalEngine.decide(spec, { axis, dismissed }) : null),
      [demo, spec, axis, dismissed],
    );
  const shownSpec = useMemo(() => {
    if (demo || !hostedDecision || vocabulary) return spec;
    const availableBenchmarks = [
      ...new Set(
        hostedDecision.top.flatMap((candidate) =>
          candidate.evidence.flatMap((group) =>
            group.items.map((item) => item.benchmark),
          ),
        ),
      ),
    ];
    return availableBenchmarks.length > 0 &&
      !availableBenchmarks.includes(spec.bench)
      ? { ...spec, bench: availableBenchmarks[0] }
      : spec;
  }, [demo, hostedDecision, spec, vocabulary]);
  const mapped = useMemo(() => {
    if (!hostedDecision) return { decision: null, error: null };
    try {
      return {
        decision: mapDecisionToViewModel(hostedDecision, shownSpec, {
          axis: shownAxis,
          dismissed,
          questions: hostedQuestions,
          ...(vocabulary ? { benchmarks: vocab.benchmarks } : {}),
        }),
        error: null,
      };
    } catch (cause) {
      // A decision that cannot be drawn is reported, never left as a blank page.
      return {
        decision: null,
        error: cause instanceof Error ? cause.message : String(cause),
      };
    }
  }, [hostedDecision, shownSpec, shownAxis, dismissed, hostedQuestions, vocabulary, vocab]);
  const liveDecision = mapped.decision;
  const decision = demo ? sampleDecision : liveDecision,
    e = decision?.explanation,
    selectedId = selected || e?.shortlist.top?.m.id || e?.may[0]?.m.id || null,
    row = e?.rows.find((candidate) => candidate.m.id === selectedId) || null;
  const sim = simulate || new URLSearchParams(location.search).get("simulate"),
    simulatedError = demo && sim === "error" && !retried,
    error = simulatedError || requestState.kind === "error" || !!mapped.error,
    loading = (demo && sim === "loading") || requestState.kind === "loading";
  const placed = useMemo(
    () => (requestState.kind === "error" ? placeIssues(requestState.issues) : []),
    [requestState],
  );
  const specIssues = placed.filter((issue) => issue.target.kind === "spec");

  async function runDecision(requested: Spec) {
    if (demo) return;
    const nextSpec = sendable(requested);
    requestAbort.current?.abort();
    questionsAbort.current?.abort();
    const controller = new AbortController();
    requestAbort.current = controller;
    setHostedDecision(null);
    setHostedQuestions([]);
    setRequestState({ kind: "loading" });
    try {
      const answer = await hostedEngine.decide(toDecisionSpec(nextSpec, "full"), {
        signal: controller.signal,
      });
      if (controller.signal.aborted) return;
      setHostedDecision(answer);
      setHostedQuestions(questionsFor(nextSpec));
      setRequestState({ kind: "success" });
    } catch (cause) {
      if (cause instanceof Error && cause.name === "AbortError") return;
      const apiError = cause instanceof DecideApiError ? cause : null;
      setRequestState({
        kind: "error",
        message: apiError?.message ?? "The decision service could not be reached.",
        code: apiError?.code ?? null,
        status: apiError?.status ?? null,
        issues: apiError?.issues ?? [],
      });
    }
  }

  function scheduleDecision(nextSpec: Spec) {
    if (demo) return;
    if (requestTimer.current) clearTimeout(requestTimer.current);
    requestTimer.current = setTimeout(() => void runDecision(nextSpec), 300);
  }

  function changeSpec(nextSpec: Spec) {
    setSpec(nextSpec);
    scheduleDecision(nextSpec);
  }

  useEffect(() => {
    if (demo || !hostedDecision) return;
    questionsAbort.current?.abort();
    const controller = new AbortController();
    questionsAbort.current = controller;
    const candidates = questionsFor(spec);
    void evaluateQuestionOptions({
      engine: hostedEngine,
      spec: toDecisionSpec(sendable(spec), "none"),
      questions: candidates,
      signal: controller.signal,
      onUpdate: (next) =>
        setHostedQuestions(
          next.map((question) => ({
            ...question,
            opts: question.opts.map((option) => ({ ...option })),
          })),
        ),
    })
      .then(setHostedQuestions)
      .catch((cause: unknown) => {
        if (!(cause instanceof Error && cause.name === "AbortError"))
          setHostedQuestions([]);
      });
    return () => controller.abort();
    // questionsFor and sendable read only vocabulary and dismissed, listed here.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demo, hostedDecision, spec, dismissed, vocabulary]);
  useEffect(() => {
    if (demo) return;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 20_000);
    setVocabState({ kind: "loading" });
    loadVocabulary(controller.signal)
      .then((loaded) => setVocabState({ kind: "ready", vocabulary: loaded }))
      .catch((cause: unknown) => {
        if (cause instanceof Error && cause.name === "AbortError" && !controller.signal.aborted)
          return;
        setVocabState({
          kind: "error",
          error:
            cause instanceof VocabularyError
              ? cause
              : new VocabularyError(
                  "The catalogue vocabulary did not load in time.",
                  "network",
                ),
        });
      })
      .finally(() => clearTimeout(timer));
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [demo, vocabAttempt]);
  useEffect(() => {
    if (!vocabulary) return;
    if (initial) {
      // A shared link: answer it as written. What the engine refuses is shown on its chip.
      void runDecision(initial.spec);
      return;
    }
    const base = realBaseSpec(vocabulary);
    setSpec((current) => (current === baseSpec ? base : current));
    // Once per loaded vocabulary; runDecision reads the latest state itself.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vocabulary]);
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
      if (requestTimer.current) clearTimeout(requestTimer.current);
      requestAbort.current?.abort();
      questionsAbort.current?.abort();
    };
  }, []);
  function find() {
    setView("work");
    setParsing(true);
    setAddOpen(false);
    setEdit(null);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      const p: ReturnType<typeof parseTask> & { domain?: string | null } = vocabulary
          ? parseRealTask(vocabulary, draft)
          : parseTask(draft),
        keep = spec.conds.filter(
          (c) =>
            !c.from &&
            !p.conds.some(
              (n) =>
                n.f === c.f &&
                (n.f !== "bench" || c.f !== "bench" || n.b === c.b),
            ),
        );
      const nextSpec: Spec = {
        ...spec,
        task: draft,
        bench: p.bench,
        w: p.w,
        conds: [...p.conds, ...keep],
        ...(p.domain ? { domain: p.domain } : {}),
      };
      setSpec(nextSpec);
      setTrace(p.trace);
      setParsing(false);
      setSelected(null);
      setAxis(p.bench === "RetrievalEval v2" ? "in$" : "task$");
      if (!demo && !vocabulary) {
        // The vocabulary failed or is still loading; its own message says which.
        setVocabAttempt((n) => (vocabState.kind === "error" ? n + 1 : n));
        return;
      }
      void runDecision(nextSpec);
    }, 420);
  }
  function add(c: Cond) {
    const i = spec.conds.findIndex(
        (x) =>
          x.f === c.f && (x.f !== "bench" || c.f !== "bench" || x.b === c.b),
      );
    changeSpec({
        ...spec,
        conds:
          i < 0
            ? [...spec.conds, c]
            : spec.conds.map((x, j) => (j === i ? c : x)),
    });
  }
  function relax(i: number) {
    const n = decision?.nearMisses[i];
    if (n)
      changeSpec({
        ...spec,
        conds: spec.conds.flatMap((c, j) =>
          j === n.ci ? (n.relaxed ? [n.relaxed] : []) : [c],
        ),
      });
  }
  function start(s: Spec) {
    setSpec(structuredClone(s));
    setDraft(s.task || "");
    setView("work");
    setSelected(null);
    setTrace([]);
    setDismissed([]);
    void runDecision(s);
  }
  const vocabAlert =
    !demo && vocabState.kind === "error" ? (
      <div role="alert" className="error">
        <div>
          <strong>
            {vocabState.error.kind === "missing"
              ? "No snapshot yet."
              : "Couldn't load what the snapshot can answer."}
          </strong>
          <p>{vocabState.error.message}</p>
        </div>
        <button className="ink-button" onClick={() => setVocabAttempt((n) => n + 1)}>
          Retry
        </button>
      </div>
    ) : null;
  const errorTitle = () => {
    if (simulatedError) return "Couldn't load snapshot.";
    if (mapped.error) return "This decision could not be shown.";
    if (requestState.kind !== "error") return "Decision unavailable.";
    if (requestState.status === 400 && requestState.issues.length)
      return "The engine could not read part of this spec.";
    if (requestState.status === 503 || requestState.code === "no_snapshot")
      return "No snapshot yet.";
    if (requestState.code === "timeout") return "The decision service is taking too long.";
    if (requestState.status === null) return "Couldn't reach the decision service.";
    return `Decision unavailable${requestState.code ? ` (${requestState.code})` : ""}.`;
  };
  const errorText = () => {
    if (mapped.error) return `${mapped.error}.`;
    if (requestState.kind !== "error")
      return "The catalogue service did not respond. Your spec is kept in the link, so nothing is lost.";
    if (requestState.status === 400 && requestState.issues.length)
      return placed.some((issue) => issue.target.kind !== "spec")
        ? "Each problem is marked beside the condition or control that caused it."
        : "";
    if (requestState.status === 503 || requestState.code === "no_snapshot")
      return `The decision engine has no published snapshot to answer from yet. ${requestState.message}`;
    return requestState.message;
  };
  return (
    <VocabContext.Provider value={vocab}>
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
        {demo && <span className="sample-badge">Fictional sample data</span>}
        <div className="spacer" />
        {view === "work" && (
          decision && <span className="snapshot">{decision.snapshot}</span>
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
          <>
            {!demo && (
              <button className="ink-button" onClick={() => void runDecision(spec)}>
                Run decision
              </button>
            )}
            <button className="primary" onClick={() => setShare(true)}>
              Share or act
            </button>
          </>
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
              {demo
                ? `${catalogue.models.length} models across ${catalogue.offerings} provider offerings`
                : "models in the current snapshot"}
              , ranks what is left on evidence, and shows the source of every
              number. Independent measurements sit next to lab claims.
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
          {vocabAlert}
          {!demo && vocabState.kind === "loading" && (
            <div role="status" aria-busy="true" className="loading">
              <span>Loading what the current snapshot can answer…</span>
            </div>
          )}
          <div>
            <div className="eyebrow">Or start from a template</div>
            <div className="templates">
              {(demo ? templates : liveTemplates).map((t) => (
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
                        <span key={i}>{vocab.label(c)}</span>
                      ))}
                  </div>
                  <footer>
                    {demo && "counts" in t ? (
                      <>
                        <strong>{t.counts.feasible.length}</strong> qualify{" "}
                        <span className="warn">
                          {t.counts.may.length
                            ? "+ " + t.counts.may.length + " may qualify"
                            : ""}
                        </span>
                      </>
                    ) : (
                      <span>{"ranks" in t ? t.ranks : "Counts load from the current snapshot"}</span>
                    )}
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
                start(vocabulary ? realBaseSpec(vocabulary) : baseSpec);
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
          {parsing && !decision && demo && (
            <div role="status" aria-busy="true" className="loading">
              <span>Reading your task…</span>
            </div>
          )}
          {vocabAlert}
          {(decision || !demo) && <SpecPanel
            spec={shownSpec}
            decision={decision}
            issues={placed}
            draft={draft}
            onDraft={setDraft}
            onParse={find}
            onSpec={changeSpec}
            parsing={parsing}
            trace={trace}
            addOpen={addOpen}
            setAddOpen={setAddOpen}
            edit={edit}
            setEdit={setEdit}
          />}
          {decision && <Field
            decision={decision}
            onAdd={add}
            onDismiss={(id) => setDismissed([...dismissed, id])}
          />}
          {error ? (
            <div role="alert" className="error">
              <div>
                <strong>{errorTitle()}</strong>
                <p>
                  {errorText()} Results below are hidden rather than shown stale.
                </p>
                {!!specIssues.length && (
                  <ul className="issue-list">
                    {specIssues.map((issue) => (
                      <li key={issue.text}>{issue.text}</li>
                    ))}
                  </ul>
                )}
              </div>
              <button
                className="ink-button"
                onClick={() => {
                  setRetried(true);
                  if (!demo) void runDecision(spec);
                }}
              >
                Retry
              </button>
            </div>
          ) : loading ? (
            <div role="status" aria-busy="true" className="loading">
              <div className="loading-canvas">
                <span className="skeleton" />
                <div className="skeleton" />
                <p>
                  {demo
                    ? `${catalogue.models.length} models, ${catalogue.offerings} offerings`
                    : "Running decision against the current snapshot"}
                </p>
              </div>
              <div className="loading-cards">
                <span />
                <span />
                <span />
              </div>
            </div>
          ) : decision ? (
            <div className="results">
              <Canvas
                decision={decision}
                spec={shownSpec}
                axis={shownAxis}
                onAxis={setAxis}
                onSpec={changeSpec}
                onAdd={add}
                selected={selectedId}
                onSelect={setSelected}
                onRelax={relax}
                compact={layout === "table"}
              />
              <Shortlist
                decision={decision}
                spec={shownSpec}
                selected={selectedId}
                onSelect={setSelected}
              />
              <DecisionTable
                decision={decision}
                spec={shownSpec}
                selected={selectedId}
                onSelect={setSelected}
              />
              <Why
                decision={decision}
                spec={shownSpec}
                row={row}
                onSpec={changeSpec}
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
          ) : null}
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
          {demo && <small>Fictional sample evidence</small>}
        </div>
      )}
      {share && (
        <Share
          spec={shownSpec}
          snapshot={decision?.snapshot ?? "latest"}
          axis={shownAxis}
          row={row}
          demo={demo}
          onClose={() => setShare(false)}
        />
      )}
    </div>
    </VocabContext.Provider>
  );
}

export function DemoApp(props: { simulate?: "loading" | "error" | "none" }) {
  return <DesignedApp demo {...props} />;
}

export default function App(props: { simulate?: "loading" | "error" | "none" }) {
  return new URLSearchParams(location.search).get("demo") === "1" ? (
    <DemoApp {...props} />
  ) : (
    <DesignedApp demo={false} {...props} />
  );
}
