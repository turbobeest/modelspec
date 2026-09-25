// Vocabulary fixtures for the real-mode tests. `realVocabulary` is the file
// decision/vocabulary.py wrote from the live snapshot (snap_7bf37267f8f2b2eb);
// `smallVocabulary` narrows it to the synthetic `quality` benchmark that
// __fixtures__/full-decision.json ranks on.
import { vi } from "vitest";
import vocabularyJson from "../__fixtures__/vocabulary.json";
import { VOCABULARY_URL, vocabularySchema } from "../vocabulary";
import type { Vocabulary } from "../vocabulary";
import { DECIDE_ENDPOINT } from "../adapter";

export const realVocabulary: Vocabulary = vocabularySchema.parse(vocabularyJson);

export const smallVocabulary: Vocabulary = {
  ...realVocabulary,
  benchmarks: [
    {
      id: "quality",
      name: "Quality Bench",
      unit: "percent",
      higher_is_better: true,
      models: 4,
      independent_models: 4,
      range: { min: 60, max: 90 },
      domains: [{ id: "software_engineering", directness: "direct" }],
    },
  ],
  domains: [
    { id: "software_engineering", name: "Software engineering", proxy_only: false, benchmarks: ["quality"] },
  ],
};

export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

type Handler = (init: RequestInit | undefined) => Response | Promise<Response>;

/** A fetch mock that answers the vocabulary and the decide endpoint separately. */
export function routeFetch({
  vocabulary = () => json(smallVocabulary),
  decide,
}: {
  vocabulary?: Handler;
  decide: Handler;
}) {
  return vi.fn().mockImplementation((url: string, init?: RequestInit) => {
    if (url === VOCABULARY_URL) return Promise.resolve(vocabulary(init));
    if (url === DECIDE_ENDPOINT) return Promise.resolve(decide(init));
    return Promise.reject(new Error(`unexpected fetch ${url}`));
  });
}

export const sentSpecs = (fetch: ReturnType<typeof routeFetch>) =>
  fetch.mock.calls
    .filter(([url]) => url === DECIDE_ENDPOINT)
    .map(([, init]) => JSON.parse(String((init as RequestInit).body)));
