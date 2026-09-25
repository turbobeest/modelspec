/** Response fields from decision/contract.py, contract 1.0. UI-only material is
 * carried in AdapterDecision.explanation, never sent as a real API response. */
export interface OfferingRef {
  model: string;
  provider: string | null;
  region: string | null;
  tier: string | null;
}
export interface EvidenceItem {
  benchmark: string;
  version: string | null;
  sub_category: string | null;
  value: number;
  unit: string | null;
  n: number | null;
  measured_by:
    | "independent"
    | "provider_self_report"
    | "benchmark_author"
    | "modelspec"
    | "outcome_protocol";
  effort: string | null;
  harness: string | null;
  date: string;
  date_type: "published" | "observed";
  source: string;
  source_snapshot: string | null;
  directness: "direct" | "proxy";
}
export interface Result {
  rank: number;
  offering: OfferingRef;
  harness: string | null;
  effort: string | null;
  evidence: { domain: string; items: EvidenceItem[] }[];
  estimates: null;
  p_best: null;
  top3_stability: null;
  soft_penalty: number;
  contributions: {
    dimension: string;
    weight: number | null;
    value: number | null;
    normalisation: string | null;
    evidence: EvidenceItem[];
  }[];
  warnings: string[];
}
export interface Decision {
  contract_version: "1.0";
  decision_id: string;
  snapshot: string;
  spec_hash: string;
  explain: "full";
  status: "answered" | "partial" | "no_feasible";
  results: Result[];
  may_qualify: {
    model: string;
    offering: OfferingRef | null;
    unknown: string[];
  }[];
  eliminated: {
    funnel: {
      condition: string;
      before: number;
      after: number;
      may_qualify: number;
    }[];
    models: {
      model: string;
      condition: string;
      value: string | number | boolean | null;
    }[];
  };
  constraint_costs: {
    condition: string;
    admits: number;
    gain: Record<string, number>;
  }[];
  tipping_points: {
    description: string;
    dimension: string | null;
    threshold: number | null;
    new_top: string | null;
  }[];
  relax: string[];
  warnings: string[];
}
