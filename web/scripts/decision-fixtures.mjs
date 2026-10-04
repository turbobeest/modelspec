import { readFileSync } from "node:fs";

const root = new URL("../src/decide/__fixtures__/", import.meta.url);
const read = (file) => readFileSync(new URL(file, root), "utf8");
const captures = JSON.parse(read("live-decision-requests.json"));

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value !== null && typeof value === "object")
    return Object.fromEntries(Object.entries(value)
      .filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => [key, canonical(item)]));
  return value;
}

function requestKey(spec) {
  const { snapshot: _snapshot, ...request } = spec;
  return JSON.stringify(canonical(request));
}

const answers = new Map(captures.map(({ spec, file }) => [requestKey(spec), read(file)]));
const emptySummary = read("live-empty-board-summary.json");
const emptyFull = read("live-empty-board-full.json");

/** Match the whole request; snapshot pins and JSON object key order may differ. */
export function decisionFixtureFor(spec) {
  if (spec === null || typeof spec !== "object") return emptyFull;
  return answers.get(requestKey(spec)) ?? (spec.explain === "summary" ? emptySummary : emptyFull);
}
