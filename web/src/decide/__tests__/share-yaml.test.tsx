import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import { Share } from "../components/Share";
import { baseSpec } from "../state/spec";
import type { Spec } from "../adapter";
import { vocabularySchema } from "../vocabulary";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import { selectJob, defaultChoices } from "../simple/model";
import { ACCESS_ANSWERS } from "../facet-board/routes";
import type { BoardUrlState } from "../facet-board/model";

const vocabulary = vocabularySchema.parse(rawVocabulary);

function selection(overrides: Partial<typeof defaultChoices> = {}) {
  const selected = selectJob(vocabulary, { ...defaultChoices, ...overrides });
  if (!selected) throw new Error("Expected an available template");
  return selected;
}

function parseYamlScalar(raw: string): unknown {
  if (raw.startsWith("{") || raw.startsWith("[") || raw.startsWith('"')) return JSON.parse(raw);
  if (raw === "null") return null;
  if (raw === "true") return true;
  if (raw === "false") return false;
  if (/^-?\d+(?:\.\d+)?$/.test(raw)) return Number(raw);
  return raw;
}

/** Comments stay out of the object. Lists use the same one-item lines the share tab prints. */
function parseContractYaml(text: string): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.length === 0 || line.startsWith("#")) continue;
    const match = /^([A-Za-z0-9_]+):(?: (.*))?$/.exec(line);
    if (!match) throw new Error(`Unparsed YAML line: ${line}`);
    const key = match[1];
    const raw = match[2];
    if (raw === undefined) {
      const items: unknown[] = [];
      while (lines[i + 1]?.startsWith("  - ")) {
        i += 1;
        items.push(JSON.parse(lines[i].slice(4)));
      }
      out[key] = items;
      continue;
    }
    out[key] = parseYamlScalar(raw);
  }
  return out;
}

function apiPayload(curl: string): unknown {
  const marker = "-d '";
  const start = curl.lastIndexOf(marker);
  if (start < 0 || !curl.endsWith("'")) throw new Error("API tab has no JSON body");
  return JSON.parse(curl.slice(start + marker.length, -1).replaceAll("'\\''", "'"));
}

function shareText(spec: Spec, extra: Partial<Parameters<typeof Share>[0]> = {}) {
  render(<Share spec={spec} snapshot="snap_fixture" axis="task$" row={null} demo={false} onClose={() => undefined} {...extra} />);
  const dialog = screen.getByRole("dialog", { name: "Share" });
  fireEvent.click(within(dialog).getByRole("tab", { name: "API call" }));
  const api = within(dialog).getByRole("tabpanel").querySelector("pre")?.textContent ?? "";
  fireEvent.click(within(dialog).getByRole("tab", { name: "Spec YAML" }));
  const yaml = within(dialog).getByRole("tabpanel").querySelector("pre")?.textContent ?? "";
  return { api, yaml };
}

it("parses Spec YAML to the same decision the API tab sends, for both workloads and every access route", () => {
  const everyday = shareText(selection().spec);
  const everydayPayload = apiPayload(everyday.api);
  expect(parseContractYaml(everyday.yaml)).toEqual(everydayPayload);
  expect(everydayPayload).not.toHaveProperty("access");
  expect(everydayPayload).toMatchObject({ task_tokens: expect.any(Object) });

  for (const route of ACCESS_ANSWERS) {
    cleanup();
    const shared = shareText(selection({ job: "volume", route: route.id }).spec);
    const payload = apiPayload(shared.api);
    expect(parseContractYaml(shared.yaml)).toEqual(payload);
    if (route.id === "any") expect(payload).not.toHaveProperty("access");
    else expect(payload).toMatchObject({ access: route.id, task_tokens: { input: 2000, output: 500 } });
  }
});

it("keeps an empty board's YAML valid and leaves share comments outside the parsed spec", () => {
  const empty = shareText({ ...baseSpec, conds: [], boardWeights: {} });
  expect(empty.yaml).toContain("where: []");
  expect(empty.yaml).toContain("# unranked: no Prefer set; this objective only lets the spec run, it does not rank");
  const emptyParsed = parseContractYaml(empty.yaml);
  expect(emptyParsed).toEqual(apiPayload(empty.api));
  expect(emptyParsed.where).toEqual([]);

  cleanup();
  const folded = shareText(selection({ job: "volume", route: "own_software" }).spec, { refinementsFolded: true });
  expect(folded.yaml).toContain("# refinement weights folded into their parent domains until nested ranking is available");
  expect(parseContractYaml(folded.yaml)).toEqual(apiPayload(folded.api));

  cleanup();
  const canvas: BoardUrlState = {
    selections: {},
    mustOrder: [],
    estate: { providers: [], plans: [], hardware: [] },
    canvas: { x: "capability:software_engineering", y: "facet:offering.cost_per_task" },
  };
  const noted = shareText(selection().spec, { boardPermalink: { spec: selection().spec, state: canvas } });
  expect(noted.yaml).toContain("# canvas x: capability:software_engineering");
  expect(noted.yaml).toContain("# canvas y: facet:offering.cost_per_task");
  expect(parseContractYaml(noted.yaml)).toEqual(apiPayload(noted.api));
});
