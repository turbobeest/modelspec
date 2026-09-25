import type { Question } from "../engine/reference";
import type { HostedDecisionEngine } from "./hosted";
import type { DecisionSpec } from "./contract";
import { contractCondition } from "./view-model";

type EvaluatedQuestion = Question;

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
      const answer = await engine.decide(
        {
          ...spec,
          where: [...(spec.where ?? []), contractCondition(job.option.c)],
          explain: "none",
          limit: 500,
        },
        { signal },
      );
      job.option.n = answer.results.length;
      job.option.may = answer.may_qualify.length;
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
