import { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { choose, jobs } from "./data";
import type { Budget } from "./data";
import { AnswerCard, BudgetPicker, Hero, PrototypeShell, usePrototypeDecision } from "./shared";

function VariantA() {
  const [job, setJob] = useState("assistant-balanced");
  const [budget, setBudget] = useState<Budget>("balanced");
  const selection = useMemo(() => choose(job, budget), [job, budget]);
  const result = usePrototypeDecision(selection);
  return <PrototypeShell variant="a">
    <Hero />
    <section className="proto-choices" aria-label="Choose your job">
      <div className="proto-job-grid">{jobs.map((item) => <button key={item.id} aria-pressed={job === item.id} onClick={() => setJob(item.id)}><strong>{item.label}</strong><span>{item.detail}</span></button>)}</div>
      <div className="proto-priority"><span>What matters most?</span><BudgetPicker value={budget} onChange={setBudget} /><small>Budget templates keep quality in the mix.</small></div>
    </section>
    <div aria-live="polite"><AnswerCard selection={selection} result={result} /></div>
  </PrototypeShell>;
}

const root = document.getElementById("root");
if (root) createRoot(root).render(<VariantA />);
