import type { AdapterDecision } from "../adapter";
import type { Vocabulary } from "../vocabulary";
import { handoffData } from "../handoff-data";
import { answerSource } from "../simple/source";

export function AnswerProof({ decision, vocabulary }: { decision: AdapterDecision; vocabulary: Vocabulary }) {
  const member = [...decision.results, ...decision.top].find((row) =>
    decision.answer?.members.includes(row.offering.model) && row.evidence.some((group) => group.items.length > 0));
  const evidence = member?.evidence.flatMap((group) => group.items)[0];
  const source = answerSource(decision, vocabulary) ?? (evidence ? {
    name: vocabulary.benchmarks.find((benchmark) => benchmark.id === evidence.benchmark)?.name ?? evidence.benchmark,
    date: evidence.date,
    url: evidence.source,
  } : null);
  return <div className="answer-proof">
    <p><a className="answer-trust" href={handoffData.neutrality.href}>ModelSpec is neutral: no referral fees, no paid placement.</a></p>
    {source && <p className="answer-source">Source: <a href={source.url}>{source.name}</a>, <time dateTime={source.date}>{source.date}</time>.</p>}
  </div>;
}
