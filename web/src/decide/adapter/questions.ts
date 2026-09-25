import type { Question } from "../engine/reference";
import type { HostedDecisionEngine } from "./hosted";
import type { DecisionSpec } from "./contract";
import { contractCondition } from "./view-model";

type EvaluatedQuestion = Question;

/** The spec that counts what one answer to a next question would leave. */
export function probeSpec(spec: DecisionSpec, option: Question["opts"][number]): DecisionSpec {
  return {
    ...spec,
    where: [...(spec.where ?? []), contractCondition(option.c)],
    explain: "none",
    limit: 500,
  };
}

export async function evaluateQuestionOptions({
  engine,
  spec,
  questions,
  signal,
  onUpdate,
}: {
  engine: HostedDecisionEngine;
  spec: DecisionSpec;
  questions: Question[];
  signal?: AbortSignal;
  onUpdate?: (questions: EvaluatedQuestion[]) => void;
}): Promise<EvaluatedQuestion[]> {
  await new Promise<void>((resolve, reject) => {
    const timer = window.setTimeout(resolve, 300);
    signal?.addEventListener(
      "abort",
      () => {
        window.clearTimeout(timer);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });
  const output = questions.map((question) => ({
    ...question,
    opts: question.opts.map((option) => ({ ...option })),
  }));
  const jobs = output.flatMap((question) =>
    question.opts.map((option) => ({ question, option })),
  );
  let next = 0;
  const worker = async () => {
    while (next < jobs.length) {
      const job = jobs[next];
      next += 1;
      try {
        const answer = await engine.decide(probeSpec(spec, job.option), { signal });
        job.option.n = answer.results.length;
        job.option.may = answer.may_qualify.length;
      } catch (error) {
        if (signal?.aborted || (error instanceof Error && error.name === "AbortError")) throw error;
        // One refused probe costs that answer its count, not every question.
        // The console names the condition, so a refusal can be traced to its spec.
        job.option.failed = true;
        console.warn("next-question probe failed", contractCondition(job.option.c), error);
      }
      onUpdate?.(output);
    }
  };
  await Promise.all(Array.from({ length: Math.min(6, jobs.length) }, worker));
  return output.map((question) => ({
    ...question,
    gain: Math.max(
      0,
      ...question.opts.map((option) =>
        option.removes ?? 0,
      ),
    ),
  }));
}
