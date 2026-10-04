// The /decide layout contract (MODEL-325), measured with getBoundingClientRect.
// Shared by scripts/decide-layout.mjs and browser-tests/decide-layout.spec.ts.

import { readFileSync } from "node:fs";
import { decisionFixtureFor } from "./decision-fixtures.mjs";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/live-vocabulary.json", import.meta.url), "utf8");

export const GUTTER = 16;
export const GAP = 16;
const TOLERANCE = 0.5;

/** Answer the page offline from the recorded fixtures, as decide.spec.ts does. */
export async function routeFixtures(page) {
  await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { "access-control-allow-origin": "*" },
    body: vocabulary,
  }));
  await page.route("**/v1/decide", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: decisionFixtureFor(route.request().postDataJSON()),
  }));
  await page.route("**/v1/human-status", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { "access-control-allow-origin": "*" },
    body: JSON.stringify({ enabled: false }),
  }));
}

/** Open a clean first visit and wait until the answer, its chart and the table have drawn. */
export async function openDecide(page, base = "") {
  await page.goto(`${base}/decide.html`);
  await page.locator(".board-ranked-answer > ol > li").first().waitFor();
  await page.locator(".canvas-panel").waitFor();
  await page.locator(".decision-table").waitFor();
  await page.waitForFunction(() => document.querySelectorAll(".loading").length === 0);
  await page.evaluate(() => document.fonts.ready);
}

/** Runs in the page: every box the contract reads, in page coordinates. */
function collect() {
  const box = (node) => {
    const rect = node.getBoundingClientRect();
    return { left: rect.left, right: rect.right, top: rect.top + scrollY, bottom: rect.bottom + scrollY };
  };
  const name = (node) => node.getAttribute("aria-label")
    ?? [...node.classList].find((item) => item !== "panel")
    ?? node.tagName.toLowerCase();
  const inset = (node) => {
    const style = getComputedStyle(node);
    return {
      left: parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft),
      right: parseFloat(style.borderRightWidth) + parseFloat(style.paddingRight),
    };
  };
  const main = document.querySelector("main.work");
  const mainStyle = getComputedStyle(main);
  const mainBox = box(main);
  const grid = {
    left: mainBox.left + parseFloat(mainStyle.paddingLeft),
    right: mainBox.right - parseFloat(mainStyle.paddingRight),
  };
  const visible = (node) => node.getClientRects().length > 0;
  const panels = [...main.querySelectorAll(".board-intro, .panel")]
    .filter((node) => visible(node) && !node.parentElement.closest(".panel"))
    .map((node) => ({
      name: name(node),
      column: node.closest(".answer-column") ? "left" : node.closest(".chart-column") ? "right" : "full",
      ...box(node),
      inset: inset(node),
    }));
  const region = main.querySelector(".answer-region");
  const leftColumn = main.querySelector(".answer-column");
  const rightColumn = main.querySelector(".chart-column");
  // What a reader sees as each panel's content edge.
  const probes = [
    [".template-picker", ".template-shortcuts"],
    [".board-answer", ".narrowing-counts"],
    [".board-answer", ".board-answer-head"],
    [".board-answer", ".board-ranked-answer > ol > li"],
    [".board-may-qualify", ".board-may-qualify li"],
    [".refine", ".refine-head"],
    [".refine", ".facet-group-summary > span"],
    [".agent-handoff", ".agent-handoff > h2"],
    [".agent-handoff", ".agent-handoff pre"],
    [".canvas-panel", ".panel-heading"],
  ].flatMap(([panel, content]) => {
    const owner = main.querySelector(panel);
    const node = owner?.querySelector(content);
    return owner && node && visible(node) ? [{ panel, content, owner: box(owner), inset: inset(owner), ...box(node) }] : [];
  });
  // The top picks: the tied group's first model, else the named leader, else the first ranked row.
  const firstPick = main.querySelector(".board-tie-group li strong")
    ?? main.querySelector(".board-tie-answer h2")
    ?? main.querySelector(".board-ranked-answer > ol > li strong");
  const copy = main.querySelector(".answer-copy");
  return {
    viewport: { width: innerWidth, height: innerHeight },
    scrollWidth: document.documentElement.scrollWidth,
    grid,
    panels,
    region: region && visible(region) ? box(region) : null,
    columns: leftColumn && rightColumn && visible(rightColumn) ? { left: box(leftColumn), right: box(rightColumn) } : null,
    stacked: region ? getComputedStyle(region).display !== "grid" : true,
    tiles: [...main.querySelectorAll(".template-shortcut")].map(box),
    probes,
    firstPick: firstPick ? { text: firstPick.textContent, ...box(firstPick) } : null,
    copy: copy ? box(copy) : null,
  };
}

export const measure = (page) => page.evaluate(collect);

const near = (a, b) => Math.abs(a - b) <= TOLERANCE;
const px = (value) => `${Math.round(value * 10) / 10}`;

/** Every check the ticket names, as { check, pass, detail } rows. */
export function check(layout) {
  const rows = [];
  const add = (check, pass, detail) => rows.push({ check, pass, detail });
  const { grid, panels, columns, tiles, viewport } = layout;
  const desktop = !layout.stacked && columns !== null;

  add("no sideways page scroll", layout.scrollWidth <= viewport.width, `scrollWidth ${layout.scrollWidth} ≤ ${viewport.width}`);

  if (desktop) {
    const rowTiles = tiles.filter((tile) => near(tile.top, tiles[0].top));
    const gutters = [
      ...rowTiles.slice(1).map((tile, index) => ({ what: `tile ${index + 1}→${index + 2}`, gap: tile.left - rowTiles[index].right })),
      { what: "answer→chart", gap: columns.right.left - columns.left.right },
    ];
    const badGutters = gutters.filter(({ gap }) => !near(gap, GUTTER));
    add(`one gutter (${GUTTER}px)`, badGutters.length === 0,
      badGutters.length ? badGutters.map(({ what, gap }) => `${what} ${px(gap)}`).join(", ") : gutters.map(({ gap }) => px(gap)).join(" "));

    const split = rowTiles.length === 6
      ? near(rowTiles[2].right, columns.left.right) && near(rowTiles[3].left, columns.right.left)
      : false;
    add("split on a tile boundary", split, rowTiles.length === 6
      ? `tile 3 right ${px(rowTiles[2].right)} / answer right ${px(columns.left.right)}; tile 4 left ${px(rowTiles[3].left)} / chart left ${px(columns.right.left)}`
      : `${rowTiles.length} tiles in the first row, expected 6`);

    const edges = { full: [grid.left, grid.right], left: [grid.left, columns.left.right], right: [columns.right.left, grid.right] };
    const offEdge = panels.filter((panel) => !near(panel.left, edges[panel.column][0]) || !near(panel.right, edges[panel.column][1]));
    add("outer edges on the grid", offEdge.length === 0, offEdge.length
      ? offEdge.map((panel) => `${panel.name} ${px(panel.left)}–${px(panel.right)} (want ${px(edges[panel.column][0])}–${px(edges[panel.column][1])})`).join("; ")
      : `${panels.length} panels on ${px(grid.left)} | ${px(columns.left.right)} ${px(columns.right.left)} | ${px(grid.right)}`);
  }

  const flow = desktop
    ? [...panels.filter((panel) => panel.column === "full"), { name: "answer region", ...layout.region }]
    : panels;
  const stacks = desktop
    ? [flow, panels.filter((panel) => panel.column === "left"), panels.filter((panel) => panel.column === "right")]
    : [flow];
  const gaps = stacks.flatMap((stack) => {
    const ordered = [...stack].sort((a, b) => a.top - b.top);
    return ordered.slice(1).map((panel, index) => ({ what: `${ordered[index].name}→${panel.name}`, gap: panel.top - ordered[index].bottom }));
  });
  const badGaps = gaps.filter(({ gap }) => !near(gap, GAP));
  add(`one vertical gap (${GAP}px)`, badGaps.length === 0,
    badGaps.length ? badGaps.map(({ what, gap }) => `${what} ${px(gap)}`).join("; ") : `${gaps.length} gaps, all ${GAP}`);

  const insets = new Set(panels.flatMap((panel) => [px(panel.inset.left), px(panel.inset.right)]));
  add("one inner padding", insets.size === 1, `panel border+padding: ${[...insets].join(", ")}`);

  const offInner = layout.probes.filter((probe) => !near(probe.left, probe.owner.left + probe.inset.left));
  add("inner edges match", offInner.length === 0 && layout.probes.length > 0, offInner.length
    ? offInner.map((probe) => `${probe.content} at ${px(probe.left - probe.owner.left)} in ${probe.panel}`).join("; ")
    : `${layout.probes.length} content edges at panel edge + ${[...insets].join("/")}`);

  const fold = desktop ? viewport.height : 2 * viewport.height;
  const where = desktop ? "above the fold" : "within two screens";
  add(`top pick ${where}`, layout.firstPick !== null && layout.firstPick.bottom <= fold,
    layout.firstPick ? `"${layout.firstPick.text}" bottom ${px(layout.firstPick.bottom)} ≤ ${fold}` : "no ranked answer");
  add(`"Copy for my agent" ${where}`, layout.copy !== null && layout.copy.bottom <= fold,
    layout.copy ? `bottom ${px(layout.copy.bottom)} ≤ ${fold}` : "no copy button");
  return rows;
}

/** The counter card's visible text, and whether all of it sits in the first screen. */
export async function counterView(page) {
  return page.evaluate(() => {
    const card = document.querySelector(".narrowing .panel");
    if (!card) return null;
    const rect = card.getBoundingClientRect();
    const best = card.querySelector(".narrowing-best")?.textContent ?? "";
    const numbers = [...card.querySelectorAll(".narrowing-number")].map((node) => node.textContent).join("/");
    return { text: card.innerText, summary: `${numbers} · ${best}`, bottom: rect.bottom + scrollY, viewport: innerHeight };
  });
}
