import type { Decision, EvidenceItem, OfferingRef } from "../adapter/contract";
import type { Vocabulary } from "../vocabulary";

function codePointOrder(a: string, b: string) {
  const left = Array.from(a, (character) => character.codePointAt(0) ?? 0);
  const right = Array.from(b, (character) => character.codePointAt(0) ?? 0);
  for (let index = 0; index < Math.min(left.length, right.length); index++) {
    const difference = left[index] - right[index];
    if (difference) return difference;
  }
  return left.length - right.length;
}

function sameOffering(a: OfferingRef, b: OfferingRef) {
  return a.model === b.model && a.provider === b.provider && a.region === b.region && a.tier === b.tier;
}

function sourceMetadata(items: EvidenceItem[]) {
  return items.map((item) => JSON.stringify([
    item.record_id ?? null, item.estimate_weight ?? null, item.directness, item.benchmark, item.date, item.source,
  ])).sort(codePointOrder).join("\n");
}

type MemberEvidence = { model: string; item: EvidenceItem };

function evidencePriority(a: MemberEvidence, b: MemberEvidence) {
  // decision/explain.py::_evidence_priority, with a stable member tie-break.
  return (b.item.estimate_weight ?? -Infinity) - (a.item.estimate_weight ?? -Infinity)
    || Number(a.item.directness !== "direct") - Number(b.item.directness !== "direct")
    || codePointOrder(a.item.record_id ?? "", b.item.record_id ?? "")
    || codePointOrder(a.model, b.model);
}

export function answerSource(decision: Decision, vocabulary: Vocabulary) {
  const capabilities = decision.blend.filter((term) => term.estimated);
  const largestShare = Math.max(...capabilities.map((term) => term.share));
  const largest = capabilities.filter((term) => term.share === largestShare);
  const objective = largest[0];
  if (!decision.answer?.members.length || largest.length !== 1 || !objective || largestShare <= 0) return null;

  const candidates: MemberEvidence[] = [];
  for (const model of decision.answer.members) {
    const result = decision.results.filter((row) => row.offering.model === model).sort((a, b) => a.rank - b.rank)[0];
    const bestRoute = decision.by_model.find((row) => row.model === model)?.offerings
      .filter((route) => route.status === "ranked" && route.rank != null)
      .sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity))[0];
    const offering = bestRoute?.offering ?? result?.offering;
    if (!offering) return null;

    // Full explanations retain contributions in top when limit cuts a member's result.
    const contributions = [...decision.results, ...decision.top]
      .filter((row) => sameOffering(row.offering, offering))
      .flatMap((row) => row.contributions)
      .filter((part) => `${part.dimension}${part.refinement ? `/${part.refinement}` : ""}` === objective.dimension && part.evidence.length > 0);
    const contribution = contributions[0];
    if (!contribution || contribution.evidence.some((item) => item.estimate_weight == null)) return null;
    const metadata = sourceMetadata(contribution.evidence);
    if (contributions.some((part) => sourceMetadata(part.evidence) !== metadata)) return null;
    candidates.push(...contribution.evidence.map((item) => ({ model, item })));
  }

  candidates.sort(evidencePriority);
  const selected = candidates[0];
  if (!selected) return null;
  const { item } = selected;
  if (candidates.some((candidate) => evidencePriority(selected, candidate) === 0
    && (candidate.item.benchmark !== item.benchmark || candidate.item.date !== item.date || candidate.item.source !== item.source))) return null;
  const benchmark = vocabulary.benchmarks.find((entry) => entry.id === item.benchmark);
  return benchmark?.name ? { name: benchmark.name, date: item.date, url: item.source } : null;
}
