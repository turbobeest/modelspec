import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import rawDecision from "../__fixtures__/live-assistant-balanced-full.json";
import { decisionSchema } from "../adapter/contract";
import type { Decision, EvidenceItem } from "../adapter/contract";
import { vocabularySchema } from "../vocabulary";
import { SimpleAnswer } from "../simple/Answer";
import { defaultChoices, selectJob } from "../simple/model";

const vocabulary = vocabularySchema.parse(rawVocabulary);
const decision = decisionSchema.parse(rawDecision);
const fallback = "Sources and dates: see the full evidence";
const claude = "anthropic/claude-opus-5-5";
const gemini = "google/gemini-3-8-flash";

function props(answer: Decision) {
  const selection = selectJob(vocabulary, defaultChoices);
  if (!selection) throw new Error("Expected the Everyday help template");
  return { vocabulary, selection, decision: answer, onRemoveLimit: vi.fn(), onTryAllRoutes: vi.fn() };
}

function evidence(overrides: Partial<EvidenceItem> = {}): EvidenceItem {
  const item = decision.results.find((row) => row.offering.model === claude)
    ?.contributions.find((part) => part.dimension === "chat_preference")?.evidence[0];
  if (!item) throw new Error("Expected the fixture's chat contribution evidence");
  return { ...item, ...overrides };
}

function separated(model = claude): Decision {
  const changed = structuredClone(decision);
  if (!changed.answer) throw new Error("Expected a fixture answer");
  changed.answer = { ...changed.answer, kind: "separated", members: [model], leader: model, deterministic_order: [model] };
  return changed;
}

function contribution(answer: Decision, model = claude) {
  const part = answer.results.find((row) => row.offering.model === model)
    ?.contributions.find((item) => item.dimension === "chat_preference");
  if (!part) throw new Error("Expected a chat contribution");
  return part;
}

describe("simple answer objective source", () => {
  it("keeps the literal objective source when results and evidence are reordered", () => {
    const { rerender } = render(<SimpleAnswer {...props(decision)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
    const changed = structuredClone(decision);
    changed.results.sort((a, b) => Number(b.offering.model === gemini) - Number(a.offering.model === gemini));
    for (const row of changed.results) {
      row.contributions.reverse();
      for (const part of row.contributions) part.evidence.reverse();
    }
    rerender(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
    expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
  });

  it("uses only the separated verdict member, even when another result has stronger evidence", () => {
    const changed = separated(gemini);
    const unrelated = changed.results.find((row) => row.offering.model === claude);
    if (!unrelated) throw new Error("Expected an unrelated result");
    const other = evidence({ benchmark: "swe_bench_verified", estimate_weight: 1, date: "2026-10-16" });
    unrelated.evidence = [{ domain: "chat_preference", items: [other] }];
    contribution(changed).evidence = [other];
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByRole("heading", { name: "Gemini 3.8 Flash is ahead for these choices." })).toBeVisible();
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
  });

  it("chooses the largest capability share even when cost has the largest overall share", () => {
    const changed = separated();
    const chat = changed.blend.find((term) => term.dimension === "chat_preference");
    const cost = changed.blend.find((term) => term.dimension === "-offering.cost_per_task");
    const row = changed.results.find((item) => item.offering.model === claude);
    if (!chat || !cost || !row) throw new Error("Expected weighted fixture terms");
    changed.blend = [{ ...cost, share: 0.8 }, { ...chat, share: 0.05 }, { ...chat, dimension: "-software_engineering", share: 0.15 }];
    row.contributions.push({ ...contribution(changed), dimension: "-software_engineering", evidence: [evidence({ benchmark: "arena_elo_coding", date: "2026-09-13", estimate_weight: 0.1 })] });
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena Elo — Coding, 2026-09-13.");
  });

  it.each([
    {
      rule: "higher estimate weight before directness",
      items: [evidence({ estimate_weight: 0.2 }), evidence({ benchmark: "arena_elo_coding", estimate_weight: 0.8, directness: "proxy", date: "2026-09-13" })],
      expected: "Source: Arena Elo — Coding, 2026-09-13.",
    },
    {
      rule: "direct before proxy at equal estimate weight",
      items: [evidence({ benchmark: "arena_elo_coding", estimate_weight: 0.5, directness: "proxy" }), evidence({ estimate_weight: 0.5 })],
      expected: "Source: Arena WebDev (Code Arena), 2026-09-23.",
    },
    {
      rule: "record id after equal weight and directness",
      items: [evidence({ record_id: "z-record", estimate_weight: 0.5 }), evidence({ benchmark: "arena_elo_coding", record_id: "a-record", estimate_weight: 0.5, date: "2026-09-13" })],
      expected: "Source: Arena Elo — Coding, 2026-09-13.",
    },
    {
      rule: "Python code-point record ordering rather than locale or UTF-16 ordering",
      items: [evidence({ record_id: "𐀀-record", estimate_weight: 0.5 }), evidence({ benchmark: "arena_elo_coding", record_id: "\uE000-record", estimate_weight: 0.5, date: "2026-09-13" })],
      expected: "Source: Arena Elo — Coding, 2026-09-13.",
    },
  ])("uses engine priority: $rule", ({ items, expected }) => {
    const changed = separated();
    contribution(changed).evidence = items;
    const { rerender } = render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent(expected);
    contribution(changed).evidence.reverse();
    rerender(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent(expected);
  });

  it("breaks equal evidence priority across members independently of answer and result order", () => {
    const changed = structuredClone(decision);
    if (!changed.answer) throw new Error("Expected a fixture answer");
    changed.answer.members = [gemini, claude];
    contribution(changed, gemini).evidence = [evidence({ benchmark: "arena_elo_coding", record_id: null, date: "2026-09-13" })];
    contribution(changed).evidence = [evidence({ record_id: null })];
    changed.results.reverse();
    const { rerender } = render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
    changed.answer.members.reverse();
    changed.results.reverse();
    rerender(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
  });

  it.each([null, undefined])("shows the full-evidence fallback when estimate weight is %s", (weight) => {
    const changed = separated();
    contribution(changed).evidence = [evidence({ estimate_weight: weight })];
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
    expect(screen.getByRole("link", { name: "See the full evidence" })).toBeVisible();
  });

  it("does not substitute domain evidence when the objective contribution is absent", () => {
    const changed = separated();
    contribution(changed).evidence = [];
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("uses the fallback when missing record ids leave different sources tied within one member", () => {
    const changed = separated();
    contribution(changed).evidence = [
      evidence({ record_id: null }),
      evidence({ record_id: null, benchmark: "arena_elo_coding", date: "2026-09-13" }),
    ];
    const { rerender } = render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
    contribution(changed).evidence.reverse();
    rerender(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("shows the fallback when two capability terms share the largest weight", () => {
    const changed = separated();
    const chat = changed.blend.find((term) => term.dimension === "chat_preference");
    if (!chat) throw new Error("Expected a chat blend term");
    changed.blend = [{ ...chat, share: 0.5 }, { ...chat, dimension: "software_engineering", share: 0.5 }];
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("shows the fallback when a verdict member's objective evidence is truncated", () => {
    const changed = structuredClone(decision);
    changed.results = changed.results.filter((row) => row.offering.model !== claude);
    changed.truncated.models += 1;
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("reads each member's best ranked offering independently of result order", () => {
    const changed = separated();
    const later = changed.results.filter((row) => row.offering.model === claude)[1];
    const part = later?.contributions.find((item) => item.dimension === "chat_preference");
    if (!part) throw new Error("Expected another ranked route");
    part.evidence = [evidence({ record_id: "a-record", benchmark: "arena_elo_coding", date: "2026-09-13" })];
    changed.results.reverse();
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
  });

  it("uses retained top contributions for a member whose best offering was truncated", () => {
    const changed = structuredClone(decision);
    const best = changed.results.find((row) => row.offering.model === claude);
    const retained = changed.top.find((row) => row.offering.model === claude);
    if (!best || !retained) throw new Error("Expected retained best offering");
    retained.contributions = structuredClone(best.contributions);
    for (const part of retained.contributions) for (const item of part.evidence) item.date = "2026-10-16";
    changed.results = changed.results.filter((row) => row.offering.model !== claude);
    changed.truncated.models += 1;
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-10-16.");
  });

  it.each(["results", "top"])("uses the fallback when repeated %s offering evidence conflicts", (location) => {
    const changed = separated();
    const best = changed.results.find((row) => row.offering.model === claude);
    if (!best) throw new Error("Expected the best ranked offering");
    const conflicting = structuredClone(best);
    for (const part of conflicting.contributions) for (const item of part.evidence) item.date = "2026-10-16";
    if (location === "results") changed.results.push(conflicting);
    else changed.top.push({ offering: conflicting.offering, facts: [], contributions: conflicting.contributions, evidence: [] });
    const { rerender } = render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
    changed.results.reverse();
    changed.top.reverse();
    rerender(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("accepts repeated offering evidence whose records are merely reordered", () => {
    const changed = separated(gemini);
    const best = changed.results.find((row) => row.offering.model === gemini);
    if (!best) throw new Error("Expected Gemini's best ranked offering");
    const repeated = structuredClone(best);
    for (const part of repeated.contributions) part.evidence.reverse();
    changed.top.push({ offering: repeated.offering, facts: [], contributions: repeated.contributions, evidence: [] });
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
  });

  it("keeps a faithful source when only unrelated results were truncated", () => {
    const changed = structuredClone(decision);
    changed.results = changed.results.filter((row) => changed.answer?.members.includes(row.offering.model));
    changed.truncated.models += 1;
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena WebDev (Code Arena), 2026-09-23.");
  });

  it("matches a refinement contribution to the selected capability term", () => {
    const changed = separated();
    const chat = changed.blend.find((term) => term.dimension === "chat_preference");
    const row = changed.results.find((item) => item.offering.model === claude);
    if (!chat || !row) throw new Error("Expected chat objective data");
    changed.blend = [{ ...chat, dimension: "chat_preference/instruction_following", share: 1 }];
    row.contributions.push({ ...contribution(changed), refinement: "instruction_following", evidence: [evidence({ benchmark: "arena_elo_coding", date: "2026-09-13" })] });
    render(<SimpleAnswer {...props(changed)} />);
    expect(screen.getByText(/Source:/)).toHaveTextContent("Source: Arena Elo — Coding, 2026-09-13.");
  });

  it("uses the fallback when the vocabulary has no name for the selected benchmark", () => {
    render(<SimpleAnswer {...props(separated())} vocabulary={{ ...vocabulary, benchmarks: vocabulary.benchmarks.filter((benchmark) => benchmark.id !== "arena_webdev") }} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });

  it("does not borrow a source from results when there is no verdict or capability term", () => {
    const { rerender } = render(<SimpleAnswer {...props({ ...decision, answer: null })} />);
    expect(screen.getByText(fallback)).toBeVisible();
    rerender(<SimpleAnswer {...props({ ...decision, blend: decision.blend.filter((term) => !term.estimated) })} />);
    expect(screen.getByText(fallback)).toBeVisible();
  });
});
