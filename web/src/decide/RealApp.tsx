import { useEffect, useRef, useState } from "react";
import {
  DecideApiError,
  decisionSpecSchema,
  hostedEngine,
} from "./adapter";
import type {
  Decision,
  DecisionSpec,
  EvidenceItem,
  OfferingRef,
  Result,
} from "./adapter";

const DEFAULT_SPEC: DecisionSpec = {
  spec_version: 1,
  snapshot: "latest",
  task_type: "refactor",
  where: ["model.class = text-generator"],
  optimize: { min: "offering.price.input" },
  unknowns: "default",
  explain: "full",
  limit: 20,
};

type RequestState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; decision: Decision }
  | { kind: "error"; message: string; code: string | null };

function value(value: string | number | boolean | null): string {
  if (value === null) return "Not available";
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}

function Empty({ children = "None" }: { children?: string }) {
  return <p className="real-empty">{children}</p>;
}

function Values({ values }: { values: string[] }) {
  if (!values.length) return <Empty />;
  return (
    <ul className="real-codes">
      {values.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function Offering({ offering }: { offering: OfferingRef }) {
  return (
    <dl className="real-fields">
      <div><dt>Model</dt><dd>{offering.model}</dd></div>
      <div><dt>Provider</dt><dd>{value(offering.provider)}</dd></div>
      <div><dt>Region</dt><dd>{value(offering.region)}</dd></div>
      <div><dt>Tier</dt><dd>{value(offering.tier)}</dd></div>
    </dl>
  );
}

function Evidence({ item }: { item: EvidenceItem }) {
  return (
    <article className="real-evidence">
      <h5>{item.benchmark}</h5>
      <dl className="real-fields">
        <div><dt>Version</dt><dd>{value(item.version)}</dd></div>
        <div><dt>Sub-category</dt><dd>{value(item.sub_category)}</dd></div>
        <div><dt>Value</dt><dd>{item.value}</dd></div>
        <div><dt>Unit</dt><dd>{value(item.unit)}</dd></div>
        <div><dt>Count</dt><dd>{value(item.n)}</dd></div>
        <div><dt>Measured by</dt><dd>{item.measured_by}</dd></div>
        <div><dt>Effort</dt><dd>{value(item.effort)}</dd></div>
        <div><dt>Harness</dt><dd>{value(item.harness)}</dd></div>
        <div><dt>Date</dt><dd>{item.date}</dd></div>
        <div><dt>Date type</dt><dd>{item.date_type}</dd></div>
        <div><dt>Directness</dt><dd>{item.directness}</dd></div>
        <div><dt>Source snapshot</dt><dd>{value(item.source_snapshot)}</dd></div>
      </dl>
      <p className="real-source">
        Source: <a href={item.source} target="_blank" rel="noreferrer">{item.source}</a>
      </p>
    </article>
  );
}

function ResultCard({ result }: { result: Result }) {
  return (
    <article
      className="real-result"
      aria-label={`Result ${result.rank}: ${result.offering.model}`}
    >
      <header>
        <span className="real-rank">#{result.rank}</span>
        <h3>{result.offering.model}</h3>
      </header>
      <Offering offering={result.offering} />
      <dl className="real-fields">
        <div><dt>Harness</dt><dd>{value(result.harness)}</dd></div>
        <div><dt>Effort</dt><dd>{value(result.effort)}</dd></div>
        <div><dt>P(best)</dt><dd>{value(result.p_best)}</dd></div>
        <div><dt>Top-3 stability</dt><dd>{value(result.top3_stability)}</dd></div>
        <div><dt>Soft penalty</dt><dd>{result.soft_penalty}</dd></div>
      </dl>

      <h4>Capability estimates</h4>
      {result.estimates === null ? (
        <Empty>Not available</Empty>
      ) : result.estimates.length ? (
        <div className="real-list">
          {result.estimates.map((estimate) => (
            <dl className="real-fields" key={`${estimate.domain}:${estimate.harness}:${estimate.effort}`}>
              <div><dt>Domain</dt><dd>{estimate.domain}</dd></div>
              <div><dt>Value</dt><dd>{estimate.value}</dd></div>
              <div><dt>Interval</dt><dd>{estimate.interval.join(" to ")}</dd></div>
              <div><dt>Harness</dt><dd>{value(estimate.harness)}</dd></div>
              <div><dt>Effort</dt><dd>{value(estimate.effort)}</dd></div>
            </dl>
          ))}
        </div>
      ) : <Empty />}

      <h4>Evidence by domain</h4>
      {result.evidence.length ? result.evidence.map((domain) => (
        <section key={domain.domain} className="real-domain">
          <h5>{domain.domain}</h5>
          {domain.items.length ? domain.items.map((item, index) => (
            <Evidence key={`${item.benchmark}:${item.source}:${index}`} item={item} />
          )) : <Empty />}
        </section>
      )) : <Empty />}

      <h4>Objective contributions</h4>
      {result.contributions.length ? result.contributions.map((contribution) => (
        <section key={contribution.dimension} className="real-contribution">
          <dl className="real-fields">
            <div><dt>Dimension</dt><dd>{contribution.dimension}</dd></div>
            <div><dt>Weight</dt><dd>{value(contribution.weight)}</dd></div>
            <div><dt>Value</dt><dd>{value(contribution.value)}</dd></div>
            <div><dt>Normalisation</dt><dd>{value(contribution.normalisation)}</dd></div>
          </dl>
          <h5>Contribution evidence</h5>
          {contribution.evidence.length ? contribution.evidence.map((item, index) => (
            <Evidence key={`${item.benchmark}:${item.source}:${index}`} item={item} />
          )) : <Empty />}
        </section>
      )) : <Empty />}
      <h4>Result warnings</h4>
      <Values values={result.warnings} />
    </article>
  );
}

function DecisionView({ decision }: { decision: Decision }) {
  return (
    <section className="real-decision" aria-label="Decision">
      <header className="real-decision-head">
        <div>
          <p className="eyebrow">Decision {decision.decision_id}</p>
          <h2>{decision.snapshot}</h2>
        </div>
        <span className={`real-status ${decision.status}`}>{decision.status}</span>
      </header>
      <dl className="real-fields real-metadata">
        <div><dt>Contract version</dt><dd>{decision.contract_version}</dd></div>
        <div><dt>Decision ID</dt><dd>{decision.decision_id}</dd></div>
        <div><dt>Snapshot</dt><dd>{decision.snapshot}</dd></div>
        <div><dt>Spec hash</dt><dd>{decision.spec_hash}</dd></div>
        <div><dt>Explanation level</dt><dd>{decision.explain}</dd></div>
        <div><dt>Status</dt><dd>{decision.status}</dd></div>
      </dl>

      <h2>Results</h2>
      {decision.results.length ? decision.results.map((result) => (
        <ResultCard key={`${result.rank}:${result.offering.model}`} result={result} />
      )) : <Empty>No feasible results</Empty>}

      <section className="real-section">
        <h2>May qualify</h2>
        {decision.may_qualify.length ? decision.may_qualify.map((candidate) => (
          <article key={`${candidate.model}:${candidate.offering?.provider}`} className="real-item">
            <h3>{candidate.model}</h3>
            {candidate.offering ? <Offering offering={candidate.offering} /> : <p>Offering: Not available</p>}
            <p>Unknown facets: {candidate.unknown.length ? candidate.unknown.join(", ") : "None"}</p>
          </article>
        )) : <Empty />}
      </section>

      <section className="real-section">
        <h2>Eliminated</h2>
        <h3>Funnel</h3>
        {decision.eliminated.funnel.length ? (
          <ol className="real-list">
            {decision.eliminated.funnel.map((step, index) => (
              <li key={`${step.condition}:${index}`}>
                <strong>{step.condition}</strong>: {step.before} before, {step.after} after, {step.may_qualify} may qualify
              </li>
            ))}
          </ol>
        ) : <Empty />}
        <h3>Models</h3>
        {decision.eliminated.models.length ? (
          <ul className="real-list">
            {decision.eliminated.models.map((model) => (
              <li key={`${model.model}:${model.condition}`}>
                <strong>{model.model}</strong>: {model.condition}, value {value(model.value)}
              </li>
            ))}
          </ul>
        ) : <Empty />}
      </section>

      <section className="real-section">
        <h2>Constraint costs</h2>
        {decision.constraint_costs.length ? decision.constraint_costs.map((cost) => (
          <article key={cost.condition} className="real-item">
            <h3>{cost.condition}</h3>
            <p>admits {cost.admits}</p>
            <p>Gain: {Object.keys(cost.gain).length ? Object.entries(cost.gain).map(([key, gain]) => `${key} ${gain}`).join(", ") : "None"}</p>
          </article>
        )) : <Empty />}
      </section>

      <section className="real-section">
        <h2>Tipping points</h2>
        {decision.tipping_points.length ? decision.tipping_points.map((point) => (
          <article key={point.description} className="real-item">
            <h3>{point.description}</h3>
            <dl className="real-fields">
              <div><dt>Dimension</dt><dd>{value(point.dimension)}</dd></div>
              <div><dt>Threshold</dt><dd>{value(point.threshold)}</dd></div>
              <div><dt>New top</dt><dd>{value(point.new_top)}</dd></div>
            </dl>
          </article>
        )) : <Empty />}
      </section>

      <section className="real-section">
        <h2>Minimal relaxations</h2>
        <Values values={decision.relax} />
      </section>
      <section className="real-section">
        <h2>Decision warnings</h2>
        <Values values={decision.warnings} />
      </section>
    </section>
  );
}

export function RealApp() {
  const [specText, setSpecText] = useState(() => JSON.stringify(DEFAULT_SPEC, null, 2));
  const [state, setState] = useState<RequestState>({ kind: "idle" });
  const active = useRef<AbortController | null>(null);

  useEffect(() => () => active.current?.abort(), []);

  async function run() {
    let raw: unknown;
    try {
      raw = JSON.parse(specText);
    } catch {
      setState({ kind: "error", code: "invalid_json", message: "The spec is not valid JSON." });
      return;
    }
    const parsed = decisionSpecSchema.safeParse(raw);
    if (!parsed.success) {
      setState({
        kind: "error",
        code: "invalid_spec",
        message: parsed.error.issues.map((issue) => `${issue.path.join(".")}: ${issue.message}`).join("; "),
      });
      return;
    }

    active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    setState({ kind: "loading" });
    try {
      const decision = await hostedEngine.decide(parsed.data, { signal: controller.signal });
      if (active.current === controller) setState({ kind: "success", decision });
    } catch (error) {
      if (controller.signal.aborted || active.current !== controller) return;
      setState({
        kind: "error",
        code: error instanceof DecideApiError ? error.code : null,
        message: error instanceof Error ? error.message : "The decision failed.",
      });
    }
  }

  return (
    <div className="decide-app real-app">
      <header className="global-header">
        <a className="brand" href="/" aria-label="ModelSpec home">
          <span>Model<span>Spec</span></span>
        </a>
        <div className="spacer" />
        <a href="/legal/neutrality/">Neutrality</a>
      </header>
      <main className="real-main">
        <section className="real-intro">
          <p className="eyebrow">Model decision engine</p>
          <h1>Which model fits your task, under your constraints, and why?</h1>
          <p>
            Submit a version 1 spec. ModelSpec filters on constraints and orders the
            feasible results from verified evidence. The response below is the public
            decision contract without invented fields.
          </p>
        </section>
        <section className="real-spec" aria-label="Decision spec">
          <label htmlFor="decision-spec">Decision spec JSON</label>
          <textarea
            id="decision-spec"
            value={specText}
            onChange={(event) => setSpecText(event.target.value)}
            spellCheck={false}
            rows={14}
          />
          <div className="real-actions">
            <button className="primary" onClick={run}>Run decision</button>
            <a href="/legal/terms/">Terms</a>
            <a href="/legal/privacy/">Privacy</a>
          </div>
        </section>

        {state.kind === "loading" && (
          <div className="loading real-loading" role="status" aria-busy="true">
            Running decision against the requested snapshot…
          </div>
        )}
        {state.kind === "error" && (
          <div className="error real-error" role="alert">
            <div>
              <strong>Decision unavailable{state.code ? ` (${state.code})` : ""}</strong>
              <p>{state.message}</p>
            </div>
          </div>
        )}
        {state.kind === "success" && <DecisionView decision={state.decision} />}
      </main>
      <footer className="real-footer">
        <a href="/legal/terms/">Terms</a>
        <a href="/legal/privacy/">Privacy</a>
        <a href="/legal/neutrality/">Neutrality</a>
      </footer>
    </div>
  );
}
