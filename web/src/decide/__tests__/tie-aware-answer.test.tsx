import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import source from "../facet-board/TieAwareAnswer.tsx?raw";
import tiedJson from "../__fixtures__/compact-tied-full.json";
import separatedJson from "../__fixtures__/compact-full.json";
import bandsJson from "../__fixtures__/compact-bands-full.json";
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
const models = Object.fromEntries(["alpha", "beta", "gamma", "delta", "strong", "steady", "cheap", "weak", "unproven"].map((id) => [
  `lab/${id}`,
  { display_name: id.charAt(0).toUpperCase() + id.slice(1), lab: "lab", lab_name: "Lab" },
]));
const unranked: Spec = { ...realBaseSpec(vocabulary), boardWeights: {} };

const view = (json: unknown, spec = ranked) =>
  mapDecisionToViewModel(decisionSchema.parse(json), spec, { axis: "task$", dismissed: [], models });
const show = (json: unknown, spec = ranked) =>
  render(<RankedAnswer decision={view(json, spec)} spec={spec} vocabulary={vocabulary} />);

const blended: Spec = { ...ranked, bench: realBaseSpec(vocabulary).bench, boardWeights: { software_engineering: 0.6, "-offering.cost_per_task": 0.4 } };

describe("the banded answer on the board", () => {
  it("shows the best band with the engine's tie-breakers and no claim of equal merit", () => {
    show(tiedJson);
    const block = screen.getByRole("heading", { name: "Best for your weights: these 2. The evidence can't separate them." }).closest("section")!;
    expect(block).toHaveAttribute("aria-labelledby");
    const group = within(block).getAllByRole("list")[0];
    expect(within(group).getAllByRole("listitem").map((item) => item.querySelector("strong")?.textContent))
      .toEqual(["Alpha", "Gamma"]);
    expect(block).not.toHaveTextContent(/order of merit|alphabetical/i);
    expect(block).toHaveTextContent("In score order; the order is not evidence that one is better.");
    expect(within(group).getAllByRole("listitem")[1]).toHaveTextContent("45% likely to score at least as well as Alpha");
    expect(within(block).getByRole("heading", { name: "What breaks the tie" })).toBeInTheDocument();
    const breakers = within(block).getAllByRole("list")[1];
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

  it("lists the rest in order with how likely each is to match the leader", () => {
    show(tiedJson);
    const block = screen.getByRole("heading", { name: /Best for your weights/ }).closest("section")!;
    expect(within(block).getByRole("heading", { name: "The rest, in order" })).toBeInTheDocument();
    const rest = block.querySelector(".board-band-rest")!;
    const [beta] = within(rest as HTMLElement).getAllByRole("listitem");
    expect(beta).toHaveTextContent("Beta");
    expect(beta).toHaveTextContent("1% likely to score at least as well as Alpha");
  });

  it("omits a certain chance of matching the leader", () => {
    const certain = structuredClone(tiedJson);
    const gamma = certain.bands.best.find((entry) => entry.model === "lab/gamma");
    const beta = certain.bands.rest.find((entry) => entry.model === "lab/beta");
    if (!gamma || !beta) throw new Error("fixture bands");
    gamma.p_beats_leader = 0;
    beta.p_beats_leader = 1;
    certain.bands.rest.push({
      ...beta,
      model: "lab/delta",
      offering: { ...beta.offering, model: "lab/delta" },
      p_beats_leader: 0.36,
    });
    show(certain);
    const block = screen.getByRole("heading", { name: /Best for your weights/ }).closest("section")!;
    const group = block.querySelector(".board-tie-group") as HTMLElement;
    const gammaRow = within(group).getAllByRole("listitem").find((item) => item.textContent?.includes("Gamma"));
    expect(gammaRow).toBeTruthy();
    expect(gammaRow).not.toHaveTextContent(/likely to score/);
    const rest = block.querySelector(".board-band-rest") as HTMLElement;
    const rows = within(rest).getAllByRole("listitem");
    const betaRow = rows.find((item) => item.querySelector("strong")?.textContent === "Beta");
    const deltaRow = rows.find((item) => item.querySelector("strong")?.textContent === "lab/delta");
    expect(betaRow).not.toHaveTextContent(/likely to score/);
    expect(deltaRow).toHaveTextContent("36% likely to score at least as well as Alpha");
  });

  it("labels each pick by the tie-breaker that made it, never as a rank", () => {
    show(tiedJson);
    const block = screen.getByRole("heading", { name: /can't separate/ }).closest("section")!;
    const [group] = within(block).getAllByRole("list");
    const [alpha, gamma] = within(group).getAllByRole("listitem");
    expect(alpha).toHaveTextContent("picked by fastest");
    expect(gamma).toHaveTextContent("picked by cheapest, open weights");
    expect(block).not.toHaveTextContent(/#\s?1|\bwinner\b|\btop pick\b/i);
  });

  it("names a separated leader and what separates it", () => {
    show(separatedJson);
    const block = screen.getByRole("heading", { name: "Best for your weights: Alpha" }).closest("section")!;
    expect(block).toHaveTextContent("Every other model with enough evidence is behind it with probability over 75%.");
    expect(within(block).queryByText("What breaks the tie")).not.toBeInTheDocument();
  });

  it("names the blend, and who leads each part of it alone", () => {
    show(bandsJson, blended);
    const block = screen.getByRole("heading", { name: /Best for your weights/ }).closest("section")!;
    expect(block.querySelector(".board-blend")).toHaveTextContent("On your 60/40 mix of software engineering and cost per task.");
    const terms = block.querySelector(".board-blend-terms") as HTMLElement;
    const [coding, cost] = within(terms).getAllByRole("listitem");
    expect(coding).toHaveTextContent("Software engineering alone: Strong leads, 61% likely the strongest of the well-measured models; Steady is ahead of it with probability 33%.");
    expect(cost).toHaveTextContent("Cost per task alone: cheapest is Unproven");
  });

  it("orders the best band by chance of being best, and says so", () => {
    show(bandsJson, blended);
    const block = screen.getByRole("heading", { name: "Best for your weights: these 2. The evidence can't separate them." }).closest("section")!;
    expect(block).toHaveTextContent("Ordered by chance of being best.");
    const group = block.querySelector(".board-tie-group") as HTMLElement;
    const items = within(group).getAllByRole("listitem");
    expect(items.map((item) => item.querySelector("strong")?.textContent)).toEqual(["Steady", "Cheap"]);
    expect(items[0]).toHaveTextContent("32% chance of being best");
    expect(items[1]).toHaveTextContent("11% chance of being best");
  });

  it("keeps a thin-evidence model out of the best band, even with the top point score", () => {
    show(bandsJson, blended);
    const block = screen.getByRole("heading", { name: /Best for your weights/ }).closest("section")!;
    const group = block.querySelector(".board-tie-group") as HTMLElement;
    expect(group).not.toHaveTextContent("Unproven");
    expect(within(block).getByRole("heading", { name: "Not enough evidence yet" })).toBeInTheDocument();
    const thin = block.querySelector(".board-band-thin") as HTMLElement;
    const [unproven] = within(thin).getAllByRole("listitem");
    expect(unproven).toHaveTextContent("Unproven");
    expect(unproven).toHaveTextContent("measured on 1 benchmark, not directly");
    const list = screen.getAllByRole("list").find((candidate) => candidate.tagName === "OL" && !candidate.closest("section.board-tie-answer"))!;
    const row = within(list).getAllByRole("listitem").find((item) => item.querySelector("strong")?.textContent?.startsWith("Unproven"))!;
    expect(within(row).getByText("not enough evidence")).toBeInTheDocument();
    expect(within(row).queryByText("tied")).not.toBeInTheDocument();
  });

  it("says no model can lead when every ranked model is thin", () => {
    const { best, rest, thin } = bandsJson.bands;
    const allThin = {
      ...bandsJson,
      answer: null,
      bands: { ...bandsJson.bands, leader: null, best: [], rest: [],
        thin: [...best, ...rest, ...thin].map((entry) => ({ ...entry, p_beats_leader: null })) },
    };
    show(allThin, blended);
    const block = screen.getByRole("heading", { name: "No model has enough evidence to lead yet" }).closest("section")!;
    expect(block.querySelector(".board-tie-group")).toBeNull();
    expect(within(block).queryByRole("heading", { name: "What breaks the tie" })).not.toBeInTheDocument();
    expect(within(block.querySelector(".board-band-thin") as HTMLElement).getAllByRole("listitem")).toHaveLength(5);
    expect(block).not.toHaveTextContent(/likely to score at least as well/);
  });

  it("names the most independently measured model with no count", () => {
    const named = { ...tiedJson, answer: {
      ...tiedJson.answer,
      tie_breakers: { cheapest: null, open_weights: null, fastest: null, most_independently_measured: "lab/alpha" },
    } };
    show(named);
    const block = screen.getByRole("heading", { name: /can't separate/ }).closest("section")!;
    const [, breakers] = within(block).getAllByRole("list");
    const [item] = within(breakers).getAllByRole("listitem");
    expect(item).toHaveTextContent("Most independently measured");
    expect(item).toHaveTextContent("Alpha");
    expect(item.textContent).not.toMatch(/\d/);
  });

  it("marks tied members in the ranked list and says their order is not merit", () => {
    show(tiedJson);
    expect(screen.getByText("Order within the tied group is not evidence that one is better.")).toBeInTheDocument();
    expect(screen.queryByText(/by tie-breaker/)).not.toBeInTheDocument();
    const list = screen.getAllByRole("list").find((candidate) => candidate.tagName === "OL" && !candidate.closest("section.board-tie-answer"))!;
    const rows = within(list).getAllByRole("listitem");
    const tagged = rows.filter((row) => within(row).queryByText("tied"));
    expect(tagged.map((row) => row.querySelector("strong")?.textContent?.replace("tied", ""))).toEqual(["Alpha", "Gamma"]);
  });

  it("marks nothing as tied after a separated answer", () => {
    show(separatedJson);
    expect(screen.queryByText("tied")).not.toBeInTheDocument();
    expect(screen.queryByText(/not merit/)).not.toBeInTheDocument();
  });

  it("never skips a heading level", () => {
    show(bandsJson, blended);
    const levels = screen.getAllByRole("heading").map((heading) => Number(heading.tagName.slice(1)));
    expect(levels[0]).toBe(2);
    levels.forEach((level, index) => { if (index > 0) expect(level - levels[index - 1]).toBeLessThanOrEqual(1); });
    expect(levels).toContain(3);
  });

  it("has no answer block while the board is unranked", () => {
    show(tiedJson, unranked);
    expect(screen.queryByRole("heading", { name: /Best for your weights/ })).not.toBeInTheDocument();
    expect(screen.getByText(/Not ranked yet: listed alphabetically/)).toBeInTheDocument();
  });

  it("still renders the ranked list when the response has no answer and no bands", () => {
    const older = Object.fromEntries(Object.entries(tiedJson).filter(([key]) => !["answer", "bands", "blend"].includes(key)));
    expect(decisionSchema.safeParse(older).success).toBe(true);
    show(older);
    expect(screen.queryByRole("heading", { name: /Best for your weights/ })).not.toBeInTheDocument();
    expect(screen.getAllByRole("listitem").length).toBeGreaterThan(0);
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
  it("the answer copy never says #1, winner or coming soon, and says best only in the band's two phrases", () => {
    const strings = [...source.matchAll(/`([^`]*)`|"([^"\n]*)"|>([^<>{}\n]+)</g)].map((match) => match[1] ?? match[2] ?? match[3]);
    for (const text of strings) {
      expect(text).not.toMatch(/#\s?1|\bwinner\b|coming soon/i);
      // MODEL-206: the band is "Best for your weights"; P(best) is "chance of being best".
      expect(text.replaceAll(/Best for your weights|chance of being best/g, "")).not.toMatch(/\bbest\b/i);
    }
  });
});
