import { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { choose, jobs } from "./data";
import type { Budget, Limit } from "./data";
import { AnswerCard, Hero, PrototypeShell, usePrototypeDecision } from "./shared";

type Step = "job" | "priority" | "limit" | "answer";
const steps: Step[] = ["job", "priority", "limit"];
const limits: { id: Limit; label: string; detail: string }[] = [
  { id: "none", label: "No hard limit", detail: "Keep my options open" },
  { id: "open", label: "Must be open weights", detail: "Downloadable model weights" },
  { id: "cost", label: "At most $0.05 per task", detail: "Using this template's task size" },
  { id: "eu", label: "EU data residency", detail: "EU inference, no customer-data training" },
];

function VariantB() {
  const [step, setStep] = useState<Step>("job");
  const [job, setJob] = useState("assistant-balanced");
  const [budget, setBudget] = useState<Budget>("balanced");
  const [limit, setLimit] = useState<Limit>("none");
  const title = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(step);
  const selection = useMemo(() => choose(job, budget, limit), [job, budget, limit]);
  const result = usePrototypeDecision(selection);
  useEffect(() => {
    if (previousStep.current !== step) title.current?.focus();
    previousStep.current = step;
  }, [step]);
  const previous: Record<Step, Step> = { job: "job", priority: "job", limit: "priority", answer: "limit" };
  const currentJob = jobs.find((item) => item.id === job);
  return <PrototypeShell variant="b">
    <Hero guided />
    <div className="proto-guide">
      <ol className="proto-progress" aria-label="Your progress">{steps.map((item, i) => <li key={item} aria-current={step === item ? "step" : undefined}><span>{i + 1}</span>{item === "job" ? "The job" : item === "priority" ? "Priorities" : "Limits"}</li>)}</ol>
      {step !== "job" && <button className="proto-back" onClick={() => setStep(previous[step])}>← Back</button>}
      {step === "job" && <section><p className="proto-kicker">Start with the work</p><h2 ref={title} tabIndex={-1}>What's the job?</h2><p className="proto-step-hint">Choose the closest fit.</p><div className="proto-guided-choices">{jobs.map((item) => <button key={item.id} onClick={() => { setJob(item.id); setStep("priority"); }}><strong>{item.label}</strong><span>{item.detail}</span><span aria-hidden="true">→</span></button>)}</div></section>}
      {step === "priority" && <section><p className="proto-kicker">{currentJob?.label}</p><h2 ref={title} tabIndex={-1}>What matters most?</h2><div className="proto-guided-choices proto-priority-choices">{([{ id: "budget", label: "Spend less", detail: "A budget template that still weighs quality" }, { id: "balanced", label: "Balance cost and quality", detail: "A practical starting point" }, { id: "best", label: "Best quality", detail: "Give capability the strongest say" }] satisfies { id: Budget; label: string; detail: string }[]).map((item) => <button key={item.id} aria-pressed={budget === item.id} onClick={() => { setBudget(item.id); setStep("limit"); }}><strong>{item.label}</strong><span>{item.detail}</span><span aria-hidden="true">→</span></button>)}</div></section>}
      {step === "limit" && <section><p className="proto-kicker">{currentJob?.label}</p><h2 ref={title} tabIndex={-1}>Any hard limit?</h2><p className="proto-step-hint">We will only shortlist confirmed matches.</p><div className="proto-guided-choices proto-limits">{limits.map((item) => <button key={item.id} aria-pressed={limit === item.id} onClick={() => setLimit(item.id)}><strong>{item.label}</strong><span>{item.detail}</span></button>)}</div><button className="proto-primary" onClick={() => setStep("answer")}>Show my options →</button></section>}
      {step === "answer" && <section><h2 ref={title} tabIndex={-1} className="proto-result-label">{currentJob?.label} · {budget === "best" ? "Best quality" : budget === "budget" ? "Budget" : "Balanced"}</h2><p className="proto-step-hint">{limits.find((item) => item.id === limit)?.label}</p><AnswerCard selection={selection} result={result} /></section>}
    </div>
  </PrototypeShell>;
}

const root = document.getElementById("root");
if (root) createRoot(root).render(<VariantB />);
