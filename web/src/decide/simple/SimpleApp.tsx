import { useEffect, useRef, useState } from "react";
import { BrandMark } from "../components/BrandMark";
import { HumanGate, HUMAN_GATE_ENABLED, VisitGate } from "../components/HumanGate";
import { VISIT_GATE_ENABLED } from "../adapter/visit";
import { initialTheme, storedTheme, storeTheme } from "../theme";
import { specHash } from "../state/spec";
import { ACCESS_ANSWERS } from "../facet-board/routes";
import { availableTemplates } from "../facet-board/templates";
import { SimpleAnswer } from "./Answer";
import { defaultChoices, jobs, limitDefinitions, priorities, selectJob, supportedLimits } from "./model";
import type { Choices } from "./model";
import { useSimpleDecision } from "./useSimpleDecision";
import "../decide.css";
import "./simple.css";

export default function SimpleApp() {
  const [choices, setChoices] = useState(defaultChoices);
  const [picked, setPicked] = useState(false);
  const [limitsOpen, setLimitsOpen] = useState(false);
  const [theme, setTheme] = useState(() => initialTheme(location.search, storedTheme()));
  const pendingFocus = useRef(false);
  const verdict = useRef<HTMLHeadingElement>(null);
  const result = useSimpleDecision((vocabulary) => selectJob(vocabulary, choices)?.spec ?? null);
  const { vocabulary, vocabularyState, decision, answeredSpec, requestState } = result;
  const selection = vocabulary ? selectJob(vocabulary, choices) : null;
  const current = selection && answeredSpec && specHash(selection.spec) === specHash(answeredSpec) ? decision : null;
  useEffect(() => { document.documentElement.dataset.decideTheme = theme; storeTheme(theme); }, [theme]);
  useEffect(() => {
    if (current && pendingFocus.current) {
      verdict.current?.focus({ preventScroll: true });
      pendingFocus.current = false;
    }
  }, [current]);
  function change(next: Choices) {
    const nextSelection = vocabulary ? selectJob(vocabulary, next) : null;
    const unchanged = current && selection && nextSelection && specHash(selection.spec) === specHash(nextSelection.spec);
    if (unchanged) verdict.current?.focus({ preventScroll: true });
    pendingFocus.current = !unchanged;
    setChoices(next);
  }
  function removeLimit(facet: string) {
    const changesJob = choices.job === "self-host" && (facet === "model.weights_openness" || facet === "licence.commercial_use");
    change({ ...choices, job: changesJob ? "everyday" : choices.job,
      removedFacets: [...choices.removedFacets, facet],
      limits: choices.limits.filter((id) => !limitDefinitions.some((limit) => limit.id === id && limit.facet === facet)),
    });
  }
  const limitsSummary = [
    ...(selection?.limits.map((limit) => limit.label) ?? []),
    ...(choices.route === "any" ? [] : [ACCESS_ANSWERS.find((route) => route.id === choices.route)?.label]),
  ].filter(Boolean).join("; ") || "No hard limit";
  return <div className="decide-app simple-app" data-theme={theme}>
    <a className="simple-skip" href="#main">Skip to the decision</a>
    <header className="simple-header">
      <a className="lockup" href="/" aria-label="ModelSpec home"><BrandMark transparent={theme === "dark"} /><span className="wordmark"><b>Model</b>Spec</span></a>
      <span className="simple-date">{vocabulary?.coverage?.as_of ? `Data as of ${vocabulary.coverage.as_of}` : "Data date unavailable"}</span>
      <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? "Light" : "Dark"} mode</button>
    </header>
    <main id="main" className="simple-main">
      <div className="simple-hero"><h1>Which AI model fits your job?</h1><p>Pick a job. See your options and what each task costs.</p></div>
      {!picked && <p className="simple-example">Example: Everyday help. Pick a job if this isn't yours.</p>}
      <div className="simple-jobs" role="group" aria-label="Choose your job">
        {jobs.map((job) => <button key={job.id} disabled={!vocabulary || !selectJob(vocabulary, { ...choices, job: job.id, removedFacets: [] })} aria-pressed={choices.job === job.id} onClick={() => { setPicked(true); change({ ...choices, job: job.id, removedFacets: [] }); }}><strong>{job.label}</strong><span>{job.subtitle}</span></button>)}
      </div>
      <div className="simple-priority" role="group" aria-label="What matters most?">
        {priorities.map((priority) => <button key={priority.id} disabled={!vocabulary || !selectJob(vocabulary, { ...choices, priority: priority.id, removedFacets: [] })} aria-pressed={choices.priority === priority.id} onClick={() => change({ ...choices, priority: priority.id, removedFacets: [] })}>{priority.label}</button>)}
      </div>
      <p className="simple-helper">Spend less still weighs quality. It is not the lowest price.</p>
      <div className="simple-limit-heading"><span>Hard limit: {limitsSummary}.</span><button aria-expanded={limitsOpen} aria-controls="simple-limits" onClick={() => setLimitsOpen(!limitsOpen)}>{limitsOpen ? "Done" : "Change"}</button></div>
      {limitsOpen && <section id="simple-limits" className="simple-limits" aria-label="Hard limits">
        <p>We will only shortlist confirmed matches.</p>
        {vocabulary && supportedLimits(vocabulary).map((limit) => <label key={limit.id}><input type="checkbox" checked={choices.limits.includes(limit.id) || !!selection?.limits.some((item) => item.facet === limit.facet)} onChange={(event) => event.target.checked ? change({ ...choices,
          limits: [...choices.limits, limit.id], removedFacets: choices.removedFacets.filter((facet) => facet !== limit.facet),
        }) : removeLimit(limit.facet)} />{limit.label}</label>)}
        <label className="simple-route">How will you use the model?<select value={choices.route} onChange={(event) => {
          const route = ACCESS_ANSWERS.find((item) => item.id === event.target.value);
          if (route) change({ ...choices, route: route.id });
        }}>{ACCESS_ANSWERS.map((route) => <option key={route.id} value={route.id}>{route.label}</option>)}</select></label>
        <p>Routes can use different providers. Plans have no per-task API price; hardware fit needs the full evidence.</p>
      </section>}
      {(HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED) && <HumanGate key={result.gateRefresh} onEnabled={result.setGateStatus} disabled={!selection} onLookup={result.lookup} />}
      {VISIT_GATE_ENABLED && <VisitGate />}
      {vocabularyState.kind === "error" && <section role="alert"><p>{vocabularyState.error.message}</p><button onClick={result.retryVocabulary}>Retry</button></section>}
      {requestState.kind === "error" && <section role="alert"><p>{requestState.message}</p>{result.gateStatus === false && <button onClick={() => void result.retry()}>Retry</button>}</section>}
      {vocabulary && !selection && <section role="status"><p>These choices are unavailable in the current data. Choose another priority or <a href="/decide/details/">open the full evidence</a>.</p>
        {limitDefinitions.filter((limit) => choices.limits.includes(limit.id) && !supportedLimits(vocabulary).some((supported) => supported.id === limit.id))
          .map((limit) => <p key={limit.id}>{limit.label} is no longer supported by this data. <button onClick={() => removeLimit(limit.facet)}>Remove {limit.label}</button></p>)}
      </section>}
      {current && selection && vocabulary ? <SimpleAnswer decision={current} selection={selection} vocabulary={vocabulary} verdictRef={verdict} onRemoveLimit={removeLimit} onTryAllRoutes={() => change({ ...choices, route: "any" })} />
        : requestState.kind !== "error" && (selection || vocabularyState.kind === "loading") && <p role="status" className="simple-loading">{result.gateStatus === true ? "Choose your job, then verify and look up this decision." : "Checking the evidence…"}</p>}
      {requestState.kind === "success" && requestState.details === "unavailable" && <p role="status">The summary is available, but the full explanation could not load.</p>}
      <p className="simple-agent"><a href="/agents.md">An agent can ask this same question.</a> <a href="/pricing/">A key is required.</a> Looking this up here is free.</p>
      {vocabulary && <a className="simple-all" href="/decide/details/">All {availableTemplates(vocabulary).length} templates</a>}
    </main>
    <footer className="simple-footer"><nav aria-label="About ModelSpec"><a href="/method/">How we decide</a><a href="/pricing/">Pricing</a><a href="/legal/neutrality/">Neutrality</a><a href="/legal/terms/">Terms</a><a href="/legal/privacy/">Privacy</a></nav></footer>
  </div>;
}
