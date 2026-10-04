import { useId, useMemo, useState } from "react";
import { money } from "../adapter";
import type { AdapterDecision, Spec } from "../adapter";
import { facetName } from "../adapter/condition-label";
import type { EstateMark } from "../adapter/contract";
import type { VocabPlan, Vocabulary } from "../vocabulary";
import { boardHasPreference } from "./model";
import { TieAwareAnswer } from "./TieAwareAnswer";
import {
  cheapestMetered, COST_HEADING, estateRouteView, mayQualifyNote, modelRoutes, offeringKey, payee, planName, providerName,
} from "./routes";
import type { AccessAnswer, HeldEstate, RouteView } from "./routes";

const COLLAPSED_COUNT = 8;

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const ordered = values.slice().sort((left, right) => left - right);
  const middle = Math.floor(ordered.length / 2);
  return ordered.length % 2 === 0
    ? (ordered[middle - 1] + ordered[middle]) / 2
    : ordered[middle];
}

function medianPosition(value: number, radius: number, lineupMedian: number): string {
  if (value - radius <= lineupMedian && value + radius >= lineupMedian) return "near the median";
  return value > lineupMedian ? "above the lineup median" : "below the median";
}

function sentenceCase(name: string): string {
  return name.charAt(0).toLocaleLowerCase() + name.slice(1);
}

function domainName(vocabulary: Vocabulary, id: string): string | undefined {
  return vocabulary.domains.find((domain) => domain.id === id)?.name
    ?? vocabulary.coverage?.domains.find((domain) => domain.id === id)?.name;
}

function Route({ route, showFigure }: { route: RouteView; showFigure: boolean }) {
  const id = useId();
  return <li className={`board-route route-${route.kind}`}>
    <span className="route-name" tabIndex={0} aria-describedby={id}>{route.name}</span>
    <span className="route-explain" role="tooltip" id={id}>{route.explain}</span>
    {showFigure && <span className="route-figure">{route.figure}</span>}
    {route.note && <small className="route-note">{route.note}</small>}
  </li>;
}

const NO_HOLDINGS: HeldEstate = { providers: [], plans: [], hardware: [] };

export function RankedAnswer({
  decision,
  spec,
  vocabulary,
  access = "any",
  held = NO_HOLDINGS,
  marks,
  excludedPlans = [],
}: {
  decision: AdapterDecision;
  spec: Spec;
  vocabulary: Vocabulary;
  /** The board's "How will you use it?" answer. */
  access?: AccessAnswer;
  /** What the caller holds, for may-qualify notes. */
  held?: HeldEstate;
  /** For the estate answer: how the estate reaches each offering. */
  marks?: ReadonlyMap<string, EstateMark>;
  /** Held plans the engine says cannot serve your own software. */
  excludedPlans?: readonly VocabPlan[];
}) {
  const routeContext = { vocabulary };
  const resultsFor = (model: string) =>
    decision.results.filter((result) => result.offering.model === model);
  const routesFor = (model: string): RouteView[] => marks
    ? resultsFor(model).flatMap((result) => {
        const mark = marks.get(offeringKey(result.offering));
        return mark ? [estateRouteView(routeContext, mark, result, result.offering)] : [];
      })
    : modelRoutes(routeContext, resultsFor(model), access);
  const costHeading = marks ? "Costs you" : COST_HEADING[access];
  // Without a route, only a per-task heading may show the row's per-task cost.
  const perTaskColumn = !marks && (access === "any" || access === "coding_tool" || access === "own_software");
  const [expanded, setExpanded] = useState(false);
  const ranked = boardHasPreference(spec);
  const capability = vocabulary.domains.find((domain) =>
    Object.keys(spec.boardWeights ?? {}).includes(domain.id),
  );
  const activeRefinements = (vocabulary.refinements ?? []).filter((refinement) =>
    Object.keys(spec.boardWeights ?? {}).includes(refinement.weight_key),
  );
  const rows = ranked
    ? decision.explanation.feasible
    : decision.explanation.feasible.slice().sort((left, right) =>
        left.m.name.localeCompare(right.m.name),
      );
  const visible = expanded ? rows : rows.slice(0, COLLAPSED_COUNT);
  const mayNote = (model: string): string | null => {
    for (const row of decision.may_qualify.filter((item) => item.model === model)) {
      const note = mayQualifyNote(routeContext, row, held);
      if (note) return note;
    }
    return null;
  };
  const may = decision.explanation.may.filter((row) =>
    (ranked && capability) || mayNote(`${row.m.lab}/${row.m.id}`) !== null,
  );
  if (!ranked) may.sort((left, right) => left.m.name.localeCompare(right.m.name));
  const mayReasoned = may.some((row) => mayNote(`${row.m.lab}/${row.m.id}`) !== null);
  const lineupMedian = useMemo(
    () => median(rows.flatMap((row) => row.cap === null ? [] : [row.cap])),
    [rows],
  );
  const extent = useMemo(() => {
    const values = rows.flatMap((row) => row.cap === null ? [] : [
      row.cap - (row.capR?.ci ?? 0),
      row.cap + (row.capR?.ci ?? 0),
    ]);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;
    return { min, span: Math.max(max - min, Number.EPSILON) };
  }, [rows]);
  const tied = new Set(ranked && decision.answer?.kind === "tied" ? decision.answer.members : []);
  const thin = new Set(ranked ? decision.bands?.thin.map((entry) => entry.model) ?? [] : []);
  const dimensionName = (key: string) => {
    const bare = key.replace(/^-/, "");
    return domainName(vocabulary, bare)
      ?? vocabulary.refinements?.find((refinement) => refinement.weight_key === bare)?.name
      ?? facetName(bare);
  };
  const showsTied = visible.some((row) => tied.has(`${row.m.lab}/${row.m.id}`));
  const warnedModels = new Set(
    decision.results
      .filter((result) => result.warnings.includes("not_separable"))
      .map((result) => result.offering.model),
  );
  const inseparable = decision.explanation.feasible.filter((row) =>
    warnedModels.has(`${row.m.lab}/${row.m.id}`) && decision.explanation.insep(row).length > 0,
  );

  return <section className="panel board-ranked-answer">
    {ranked && (decision.answer || decision.bands) && <TieAwareAnswer answer={decision.answer} decision={decision} dimensionName={dimensionName} />}
    {!ranked && <p className="board-unranked">Not ranked yet: listed alphabetically</p>}
    {ranked && !decision.answer && !decision.bands && inseparable.length > 0 && <p className="board-inseparable">
      The evidence can't separate {inseparable.map((row) => row.m.name).join(", ")}.
    </p>}
    {capability && <div className="board-ranked-columns" aria-hidden="true">
      <span />
      <span />
      <small>{capability.name}, estimated · 80% interval</small>
    </div>}
    {showsTied && <p className="board-tie-caption">Order within the tied group is not evidence that one is better.</p>}
    <ol>
      {visible.map((row) => {
        const value = row.cap ?? extent.min;
        const radius = row.capR?.ci ?? 0;
        const left = 100 * (value - radius - extent.min) / extent.span;
        const width = Math.max(2, 100 * (radius * 2) / extent.span);
        const model = `${row.m.lab}/${row.m.id}`;
        const routes = routesFor(model);
        const shownProvider = access === "any" && !marks
          ? cheapestMetered(resultsFor(model))?.offering.provider ?? resultsFor(model)[0]?.offering.provider
          : undefined;
        const otherProviders = access === "any" && !marks ? [...new Set(resultsFor(model)
          .filter((result) => result.offering.provider !== null && result.offering.provider !== shownProvider)
          .map((result) => providerName(routeContext, result.offering.provider ?? "")))] : [];
        const excluded = excludedPlans.filter((plan) =>
          resultsFor(model).some((result) => result.offering.provider === plan.provider));
        return <li className={`status-qualifies ${capability ? "" : "without-capability"}`} key={model}>
          <div className="board-ranked-copy">
            <strong>{row.m.name}{tied.has(model) && <span className="board-tie-tag">tied</span>}{thin.has(model) && <span className="board-thin-tag">not enough evidence</span>}</strong>
            <span className="eligibility status-qualifies"><span aria-hidden="true">✓</span> Qualifies</span>
            <small>{row.m.labName}</small>
            {otherProviders.length > 0 && <small>also via {otherProviders.join(", ")}</small>}
            {activeRefinements.map((refinement) => {
              const result = decision.results.find((item) => item.offering.model === `${row.m.lab}/${row.m.id}`);
              const hasEvidence = result?.evidence.some((group) => group.items.some((item) => item.sub_category === refinement.id || refinement.benchmarks.some((benchmark) => benchmark.id === item.benchmark))) ?? false;
              const parentName = domainName(vocabulary, refinement.parent_domain);
              return !hasEvidence && parentName && <small key={refinement.id}>no {refinement.name} evidence — estimated from general {sentenceCase(parentName)}</small>;
            })}
          </div>
          <div className="board-ranked-cost"><small>{costHeading}</small><span>{routes[0] ? routes[0].column ?? routes[0].figure : perTaskColumn ? money(row.cost) : "—"}</span></div>
          {capability && <div className="board-capability">
            {row.cap === null
              ? <small>no evidence for {capability.name}</small>
              : <>
                <span className="board-interval-track" aria-label={`${row.m.name} capability interval`}>
                  <i style={{ left: `${Math.max(0, left)}%`, width: `${Math.min(100 - Math.max(0, left), width)}%` }} />
                  <b style={{ left: `${Math.max(0, Math.min(100, 100 * (value - extent.min) / extent.span))}%` }} />
                </span>
                <small>{lineupMedian === null ? "near the median" : medianPosition(row.cap, radius, lineupMedian)}</small>
              </>}
          </div>}
          {(routes.length > 0 || excluded.length > 0) && <ul className="board-routes" aria-label={`Routes to ${row.m.name}`}>
            {routes.map((route, index) => <Route key={route.key} route={route} showFigure={index !== 0 || !route.figure.endsWith(" per task")} />)}
            {excluded.map((plan) => <li className="board-route route-excluded" key={plan.id}><small>Your {planName(plan.name)} doesn't cover this</small></li>)}
          </ul>}
        </li>;
      })}
    </ol>
    {rows.length > COLLAPSED_COUNT && <button className="text-button board-show-all" onClick={() => setExpanded((current) => !current)}>
      {expanded ? "Show fewer" : `Show all ${rows.length}`}
    </button>}
    {may.length > 0 && <section className="board-may-qualify">
      <h2>{mayReasoned || !capability ? `May qualify — not verified yet (${may.length})` : `May qualify — no ${capability.name} evidence (${may.length})`}</h2>
      <ul>
        {may.map((row) => {
          const note = mayNote(`${row.m.lab}/${row.m.id}`);
          const via = row.best.o.provider === "Provider not available" ? null : payee(row.best.o.provider);
          return <li className="status-may" key={row.best.o.id}>
            <div className="board-ranked-copy">
              <strong>{row.m.name}</strong>
              <span className="eligibility status-may"><span aria-hidden="true">?</span> May qualify</span>
              <small>{row.m.labName}{via && via !== row.m.labName ? ` · via ${via}` : ""}</small>
            </div>
            <div className="board-ranked-cost"><small>{perTaskColumn ? "Cost per task" : costHeading}</small><span>{perTaskColumn ? money(row.cost) : "—"}</span></div>
            {note && <p className="board-may-note">{note}</p>}
          </li>;
        })}
      </ul>
    </section>}
    {rows.length === 0 && <small>No model qualifies yet.</small>}
  </section>;
}
