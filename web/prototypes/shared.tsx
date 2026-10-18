import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { BrandMark } from "../src/decide/components/BrandMark";
import { AgentHandoff } from "../src/decide/components/AgentHandoff";
import { decisionSchema } from "../src/decide/adapter/contract";
import type { Decision } from "../src/decide/adapter/contract";
import { prepareDecisionRequest } from "../src/decide/adapter/request-spec";
import { initialTheme } from "../src/decide/theme";
import { evidenceLink, vocabulary } from "./data";
import type { Selection, Budget } from "./data";
import "../src/decide/decide.css";
import "./prototype.css";

export type DecisionResult = { kind: "loading" } | { kind: "ready"; decision: Decision } | { kind: "error"; message: string };
const cache = new Map<string, Decision>();
export function usePrototypeDecision(selection: Selection): DecisionResult {
  const request = JSON.stringify(prepareDecisionRequest(vocabulary, selection.spec, "full").decisionSpec);
  const [settled, setSettled] = useState<{ request: string; result: DecisionResult }>();
  useEffect(() => {
    if (cache.has(request)) return;
    const controller = new AbortController();
    void fetch("/v1/decide", { method: "POST", headers: { "Content-Type": "application/json" }, body: request, signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("This local decision could not be calculated. Try another choice.");
        const decision = decisionSchema.parse(await response.json());
        cache.set(request, decision);
        setSettled({ request, result: { kind: "ready", decision } });
      }).catch((error: unknown) => {
        if (!controller.signal.aborted) setSettled({ request, result: { kind: "error", message: error instanceof Error ? error.message : "Decision unavailable." } });
      });
    return () => controller.abort();
  }, [request]);
  const cached = cache.get(request);
  return cached ? { kind: "ready", decision: cached } : settled?.request === request ? settled.result : { kind: "loading" };
}

export function PrototypeShell({ variant, children }: { variant: "a" | "b" | "c"; children: ReactNode }) {
  const [theme, setTheme] = useState(() => initialTheme(location.search, null));
  useEffect(() => { document.documentElement.dataset.decideTheme = theme; }, [theme]);
  return <div className={`decide-app proto proto-${variant}`} data-theme={theme}>
    <a className="proto-skip" href="#main">Skip to the decision</a>
    <header className="proto-header">
      <a className="lockup" href="/prototypes/proto-a.html" aria-label="ModelSpec prototype home"><BrandMark transparent={theme === "dark"} /><span className="wordmark"><b>Model</b>Spec</span></a>
      <nav aria-label="Prototype variants">{["a", "b", "c"].map((item) => <a key={item} href={`/prototypes/proto-${item}.html?theme=${theme}`} aria-current={item === variant ? "page" : undefined}>{item.toUpperCase()}</a>)}</nav>
      <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? "Light" : "Dark"} mode</button>
    </header>
    <main id="main" className="proto-main">{children}</main>
    <footer className="proto-footer">Design prototype · Saved engine data · Free for people</footer>
  </div>;
}

export function Hero({ guided = false }: { guided?: boolean }) {
  return <section className="proto-hero">
    <p className="proto-kicker">No paid placement. Sourced.</p>
    <h1>Which AI model fits your job?</h1>
    <p>{guided ? "A few choices. An answer you can check." : "Pick a job. See your options and what each task costs."}</p>
  </section>;
}

export function BudgetPicker({ value, onChange }: { value: Budget; onChange: (value: Budget) => void }) {
  const options: { id: Budget; label: string }[] = [{ id: "budget", label: "Cheapest" }, { id: "balanced", label: "Balanced" }, { id: "best", label: "Best quality" }];
  return <div className="proto-budget" role="group" aria-label="Budget preference">{options.map((option) => <button key={option.id} aria-pressed={value === option.id} onClick={() => onChange(option.id)}>{option.label}</button>)}</div>;
}

const money = (cost: number | null | undefined) => cost == null ? "Cost unknown" : `$${cost.toFixed(cost < 0.01 ? 4 : 3)}`;
export function AnswerCard({ selection, result, agent = true }: { selection: Selection; result: DecisionResult; agent?: boolean }) {
  const [agentOpen, setAgentOpen] = useState(false);
  if (result.kind === "loading") return <section className="proto-answer" aria-busy="true" role="status"><h2>Checking the evidence…</h2></section>;
  if (result.kind === "error") return <section className="proto-answer" role="alert"><h2>We couldn't answer this choice.</h2><p>{result.message}</p><a href={evidenceLink(selection)}>See the full evidence</a></section>;
  const { decision } = result;
  const answer = decision.answer;
  const members = answer?.deterministic_order ?? [];
  const name = (id: string) => vocabulary.models[id]?.display_name ?? id;
  const counts = decision.by_model.reduce((result, item) => ({ ...result, [item.status]: (result[item.status] ?? 0) + 1 }), { ranked: 0, may_qualify: 0, eliminated: 0 });
  const reason = decision.blend.length ? `Your mix weighs ${decision.blend.map((term) => `${Math.round(term.share * 100)}% ${term.dimension === "offering.cost_per_task" || term.dimension === "-offering.cost_per_task" ? "task cost" : vocabulary.domains.find((domain) => domain.id === term.dimension)?.name.toLowerCase() ?? term.dimension}`).join(" and ")}.` : answer?.basis ?? "The evidence is too limited to choose a model for this job.";
  return <section className="proto-answer" aria-label="Your answer" data-decision-id={decision.decision_id}>
    <div className="proto-answer-heading"><p className="proto-kicker">Your shortlist</p><span>{counts.ranked} qualify · {counts.may_qualify} uncertain</span></div>
    <h2>{answer?.kind === "tied" ? `These ${members.length} are too close to call.` : answer?.kind === "separated" ? name(answer.leader) : decision.status === "no_feasible" ? "No confirmed match for these limits." : "No clear pick yet."}</h2>
    <p className="proto-reason">{reason}</p>
    {answer?.kind === "tied" && <p className="proto-tie-note">All are in the best group. Compare their costs; this order is not a ranking.</p>}
    <ul className="proto-shortlist">{members.map((id) => {
      const row = decision.by_model.find((item) => item.model === id);
      const band = decision.bands?.best.find((item) => item.model === id);
      const ranked = decision.results.find((item) => item.offering.model === id);
      const cost = row?.cost_per_task ?? band?.cost_per_task ?? ranked?.cost_per_task;
      return <li key={id}><span><strong>{name(id)}</strong>{answer?.tie_breakers.most_independently_measured === id && <small>Most independently measured</small>}</span><span className="proto-price">{money(cost)}{cost != null && <small>per task</small>}</span></li>;
    })}</ul>
    {!answer && <p>Adjust a limit or open the evidence to see what is missing.</p>}
    <p className="proto-task-size">Task estimate: {selection.spec.tokIn.toLocaleString("en-US")} input + {selection.spec.tokOut.toLocaleString("en-US")} output tokens. API prices, not a chat subscription{selection.template.id === "private-self-host" ? " or your hardware running costs" : ""}.</p>
    <div className="proto-actions"><a className="proto-primary" href={evidenceLink(selection)}>See the full evidence <span aria-hidden="true">↗</span></a>{agent && <button aria-expanded={agentOpen} onClick={() => setAgentOpen(!agentOpen)}>Use this from your agent <span>Key required</span></button>}</div>
    {agent && agentOpen && <div className="proto-agent"><p>Human lookup is free. CLI, API and MCP use requires an API key.</p><AgentHandoff spec={prepareDecisionRequest(vocabulary, selection.spec, "full").decisionSpec} /></div>}
  </section>;
}
