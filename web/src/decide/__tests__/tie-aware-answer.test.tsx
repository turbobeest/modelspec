import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import source from "../facet-board/TieAwareAnswer.tsx?raw";
import tiedJson from "../__fixtures__/compact-tied-full.json";
import separatedJson from "../__fixtures__/compact-full.json";
import vocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import { decisionSchema } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import type { Spec } from "../engine/types";
import { RankedAnswer } from "../facet-board/RankedAnswer";
import { realBaseSpec, vocabularySchema } from "../vocabulary";

const vocabulary = vocabularySchema.parse(vocabularyJson);
const ranked: Spec = {
  ...realBaseSpec(vocabulary),
  bench: "quality",
  domain: undefined,
  basis: undefined,
  boardWeights: { software_engineering: 0.78 },
};
const models = Object.fromEntries(["alpha", "beta", "gamma", "delta"].map((id) => [
  `lab/${id}`,
  { display_name: id.charAt(0).toUpperCase() + id.slice(1), lab: "lab", lab_name: "Lab" },
]));
const unranked: Spec = { ...realBaseSpec(vocabulary), boardWeights: {} };

const view = (json: unknown, spec = ranked) =>
  mapDecisionToViewModel(decisionSchema.parse(json), spec, { axis: "task$", dismissed: [], models });
const show = (json: unknown, spec = ranked) =>
  render(<RankedAnswer decision={view(json, spec)} spec={spec} vocabulary={vocabulary} />);

describe("tie-aware answer on the board", () => {
  it("shows the tied group unordered, under a heading, with the engine's tie-breakers", () => {
    show(tiedJson);
    const block = screen.getByRole("heading", { name: "These 2 fit. The evidence can't separate them." }).closest("section")!;
    expect(block).toHaveAttribute("aria-labelledby");
    const [group, breakers] = within(block).getAllByRole("list");
    expect(within(group).getAllByRole("listitem").map((item) => item.querySelector("strong")?.textContent))
      .toEqual(["Alpha", "Gamma"]);
    expect(within(block).getByText("Listed alphabetically, in no order of merit.")).toBeInTheDocument();
    expect(within(block).getByRole("heading", { name: "What breaks the tie" })).toBeInTheDocument();
    const items = within(breakers).getAllByRole("listitem");
    expect(items).toHaveLength(3);
    expect(items[0]).toHaveTextContent("Cheapest");
    expect(items[0]).toHaveTextContent("Gamma");
    expect(items[0]).toHaveTextContent("$0.112 per task");
    expect(items[1]).toHaveTextContent("Fastest");
    expect(items[1]).toHaveTextContent("Alpha");
    expect(items[1]).toHaveTextContent("95 tokens/s");
    expect(items[2]).toHaveTextContent("Open weights");
    expect(items[2]).toHaveTextContent("Gamma");
    expect(block).not.toHaveTextContent(/independently measured/i);
  });

  it("labels each pick by the tie-breaker that made it, never as a rank", () => {
    show(tiedJson);
    const block = screen.getByRole("heading", { name: /can't separate/ }).closest("section")!;
    const [group] = within(block).getAllByRole("list");
    const [alpha, gamma] = within(group).getAllByRole("listitem");
    expect(alpha).toHaveTextContent("picked by fastest");
    expect(gamma).toHaveTextContent("picked by cheapest, open weights");
    expect(block).not.toHaveTextContent(/#\s?1|\bbest\b|\bwinner\b|\btop pick\b/i);
  });

  it("names a clear winner with the evidence gap", () => {
    show(separatedJson);
    const heading = screen.getByRole("heading", { name: "Clear winner: Alpha" });
    const block = heading.closest("section")!;
    expect(block).toHaveTextContent("No other model's score interval overlaps its.");
    expect(block).toHaveTextContent("against");
    expect(block).toHaveTextContent("for Gamma, the next model.");
    expect(within(block).queryByText("What breaks the tie")).not.toBeInTheDocument();
  });

  it("has no answer block while the board is unranked", () => {
    show(tiedJson, unranked);
    expect(screen.queryByRole("heading", { name: /can't separate/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /Clear winner/ })).not.toBeInTheDocument();
    expect(screen.getByText(/qualify — set a Prefer to rank them/)).toBeInTheDocument();
  });

  it("still renders the ranked list when the response has no answer", () => {
    const { answer: _dropped, ...older } = tiedJson as Record<string, unknown>;
    expect(decisionSchema.safeParse(older).success).toBe(true);
    show(older);
    expect(screen.queryByRole("heading", { name: /can't separate/ })).not.toBeInTheDocument();
    expect(screen.getAllByRole("listitem").length).toBeGreaterThan(0);
    expect(document.body).not.toHaveTextContent("Tied groups are summarized in the ranked list");
  });

  it("does not claim a tie-breaker the engine did not send", () => {
    const quiet = { ...tiedJson, answer: {
      ...tiedJson.answer,
      tie_breakers: { cheapest: null, open_weights: null, most_independently_measured: null, fastest: null },
    } };
    show(quiet);
    const block = screen.getByRole("heading", { name: /can't separate/ }).closest("section")!;
    expect(within(block).queryByRole("heading", { name: "What breaks the tie" })).not.toBeInTheDocument();
    expect(block).not.toHaveTextContent("picked by");
    expect(block).toHaveTextContent("No tie-breaker separates them either.");
  });
});

describe("public copy guard", () => {
  it("the tied-answer copy never says #1, best or coming soon", () => {
    const strings = [...source.matchAll(/`([^`]*)`|"([^"\n]*)"|>([^<>{}\n]+)</g)].map((match) => match[1] ?? match[2] ?? match[3]);
    for (const text of strings) expect(text).not.toMatch(/#\s?1|\bbest\b|coming soon/i);
  });
});
