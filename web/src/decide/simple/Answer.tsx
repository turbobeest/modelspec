import type { Ref } from "react";
import type { Decision } from "../adapter/contract";
import type { Vocabulary } from "../vocabulary";
import { ACCESS_ANSWERS, payee } from "../facet-board/routes";
import { evidenceLink } from "./model";
import type { Selection } from "./model";

const dimensionNames: Record<string, string> = {
  chat_preference: "ratings of conversational responses", software_engineering: "software engineering evidence",
  writing: "writing evidence", reasoning: "reasoning evidence", "offering.cost_per_task": "estimated running cost",
};
const money = (cost: number | null | undefined) => cost == null ? "Task cost unknown" : `$${cost.toFixed(cost < 0.01 ? 4 : 3)} per task`;

export function SimpleAnswer({ decision, vocabulary, selection, onRemoveLimit, onTryAllRoutes, verdictRef }: {
  decision: Decision;
  vocabulary: Vocabulary;
  selection: Selection;
  onRemoveLimit: (facet: string) => void;
  onTryAllRoutes: () => void;
  verdictRef?: Ref<HTMLHeadingElement>;
}) {
  const answer = decision.answer;
  const name = (id: string) => vocabulary.models[id]?.display_name ?? id;
  const members = [...(answer?.members ?? [])].sort((a, b) => name(a).localeCompare(name(b), "en"));
  const ranked = decision.by_model.filter((row) => row.status === "ranked").length + decision.truncated.models;
  const possible = decision.by_model.filter((row) => row.status === "may_qualify").length;
  const dimensions = decision.blend.map((term) => term.dimension.replace(/^-/, ""));
  const blend = dimensions.map((dimension) => dimensionNames[dimension] ?? vocabulary.domains.find((domain) => domain.id === dimension)?.name ?? dimension);
  const largestShare = Math.max(...decision.blend.map((term) => term.share));
  const heavier = blend.filter((_label, index) => decision.blend[index].share === largestShare);
  const emphasis = blend.length > 1 ? heavier.length === blend.length ? " Each carries equal weight."
    : ` More weight goes to ${new Intl.ListFormat("en", { style: "long", type: "conjunction" }).format(heavier)}.` : "";
  const sources = decision.results.flatMap((row) => row.evidence.filter((group) => dimensions.includes(group.domain)).flatMap((group) => group.items));
  const source = sources[0] ?? decision.results.flatMap((row) => row.contributions.flatMap((term) => term.evidence))[0]
    ?? decision.top.flatMap((row) => [...row.evidence.flatMap((group) => group.items), ...row.contributions.flatMap((term) => term.evidence)])[0];
  const scope = [
    ...selection.limits.map((limit) => limit.label),
    ...(selection.choices.route === "any" ? [] : [ACCESS_ANSWERS.find((route) => route.id === selection.choices.route)?.label]),
  ].filter(Boolean).join("; ") || "No hard limit";
  const blocker = selection.limits.filter((limit) => decision.relax.some((condition) => condition === limit.condition || condition.startsWith(`${limit.facet} `)));
  const rows = (ids: string[]) => ids.map((id) => {
    const model = decision.by_model.find((row) => row.model === id);
    const routes = model?.offerings.filter((row) => row.status === "ranked") ?? [];
    const cheapest = [...routes].sort((a, b) => (a.cost_per_task ?? Infinity) - (b.cost_per_task ?? Infinity))[0];
    const result = decision.results.find((row) => row.offering.model === id);
    const band = decision.bands?.best.find((row) => row.model === id) ?? decision.bands?.rest.find((row) => row.model === id);
    const route = cheapest ?? result ?? band;
    const provider = route?.offering.provider;
    return <li key={id} className="simple-model"><span><strong>{name(id)}</strong><span className="simple-provider">{provider ? `via ${payee(vocabulary.providers[provider] ?? provider)}` : route ? "Run on your own hardware" : "Route unknown"}</span></span><span className="simple-price">{money(route?.cost_per_task)}</span></li>;
  });
  return <section className="simple-answer" aria-label="Decision answer" data-decision-id={decision.decision_id}>
    <p className="simple-scope">{selection.jobLabel}. {selection.priorityLabel}. {scope}.</p>
    <h2 ref={verdictRef} tabIndex={-1}>{answer?.kind === "tied" ? `These ${members.length} are too close to call.`
      : answer?.kind === "separated" ? `${name(answer.leader)} is ahead for these choices.`
      : decision.status === "no_feasible" ? "No confirmed match." : "No clear pick yet."}</h2>
    <p className="simple-neutrality"><a href="/legal/neutrality/">ModelSpec is neutral: no referral fees, no paid placement.</a></p>
    {answer?.kind === "tied" && <p className="simple-tie">The evidence can't separate them for these choices. <span>Listed alphabetically, not ranked.</span></p>}
    {answer && <ul className="simple-shortlist" aria-label="Best matches">{rows(members)}</ul>}
    {!answer && <div className="simple-empty">
      <p>{decision.status === "no_feasible" ? "Nothing can be confirmed for these choices. Missing facts can keep a model possible."
        : `The available evidence cannot determine a shortlist for ${selection.jobLabel}. These results are not a recommendation.`}</p>
      {decision.status === "no_feasible" && <>
        {blocker.map((limit) => <p key={limit.facet}>Blocking limit: {limit.label}. <button onClick={() => onRemoveLimit(limit.facet)}>Remove {limit.label}</button></p>)}
        {selection.choices.route !== "any"
          ? <p>No comparison is available for the selected route with these choices. <button onClick={onTryAllRoutes}>Try all routes</button></p>
          : blocker.length === 0 && <p>{decision.relax.length ? decision.relax.join(". ") : "The evidence page shows which requirements or missing measurements prevent an answer."}</p>}
      </>}
    </div>}
    <a className="simple-primary" href={evidenceLink(selection)}>See the full evidence</a>
    <div className="simple-proof">
      <p>Task size used for these prices: {selection.spec.tokIn.toLocaleString("en-US")} input and {selection.spec.tokOut.toLocaleString("en-US")} output tokens. List API price, not a chat subscription.</p>
      {(selection.choices.job === "self-host" || selection.choices.route === "own_hardware") && <p>API prices do not include your hardware running costs or confirm that a model fits your device.</p>}
      <p>{blend.length ? `This choice compares ${new Intl.ListFormat("en", { style: "long", type: "conjunction" }).format(blend)}.${emphasis}` : "There is not enough evidence to compare these choices."}</p>
      {source ? <p>Source: <a href={source.source}>{vocabulary.benchmarks.find((benchmark) => benchmark.id === source.benchmark)?.name ?? source.benchmark}</a>, {source.date}.</p>
        : <p>Source dates are unavailable in this answer. Check the full evidence.</p>}
      <p>{ranked} pass these limits. {possible} more are missing a fact, so they stay possible.</p>
      {answer?.tie_breakers.most_independently_measured && <p>Most independently measured: {name(answer.tie_breakers.most_independently_measured)}. That does not change the order.</p>}
      {answer?.kind === "separated" && !!decision.bands?.rest.length && <details><summary>The rest</summary><ul className="simple-shortlist">{rows(decision.bands.rest.map((row) => row.model))}</ul></details>}
    </div>
  </section>;
}
