import { expect } from "@playwright/test";
import { test } from "./human-gate-fixtures";
import { readFileSync } from "node:fs";
import { decisionFixtureFor } from "../scripts/decision-fixtures.mjs";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/live-vocabulary.json", import.meta.url), "utf8");
const narrowedDecision = readFileSync(new URL("../src/decide/__fixtures__/live-budget-coding-full.json", import.meta.url), "utf8");

test.beforeEach(async ({ page }) => {
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
});

async function openBoard(page: import("@playwright/test").Page) {
  await page.goto("/decide.html?demo=1");
  await expect(
    page.getByRole("heading", { name: "Which AI model fits your job?" }),
  ).toBeVisible();
  await expect(page.locator("textarea")).toHaveCount(0);
}

test("the public decision page opens on the facet board", async ({ page }) => {
  const requests: { explain?: string; where?: string[]; optimize?: unknown }[] = [];
  page.on("request", (request) => {
    if (request.url().endsWith("/v1/decide") && request.method() === "POST") requests.push(request.postDataJSON());
  });
  await openBoard(page);
  await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
  await expect(page.getByRole("region", { name: "Trade-off canvas" })).toBeVisible();
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
  await expect(page.getByRole("button", { name: "Share or give to my agent" })).toBeVisible();
  await expect(page.locator(".template-active")).toHaveText("Starting from: General assistant, balancedClear");
  await expect(page.locator(".template-shortcuts button")).toHaveCount(6);
  await expect(page.getByLabel("X axis")).toHaveValue("facet:offering.cost_per_task");
  await expect(page.getByLabel("Y axis")).toHaveValue("capability:chat_preference");
  await expect(page.getByText("Up and left is better")).toBeVisible();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests.filter((request) => request.explain === "summary")).toHaveLength(1);
  expect(requests[0].where).toEqual(["model.class = text-generator", "model.lifecycle = active"]);
  expect(requests[0].optimize).toEqual({ weights: { chat_preference: 0.6, "-offering.cost_per_task": 0.4 } });
});

test("Clear opens an alphabetic empty board and that saved board wins on reload", async ({ page }) => {
  await openBoard(page);
  await page.getByRole("button", { name: "Clear", exact: true }).click();
  await expect(page.locator(".board-unranked")).toHaveText("Not ranked yet: listed alphabetically");
  await page.getByRole("button", { name: "Show all 28", exact: true }).click();
  await expect(page.locator(".board-ranked-answer > .board-class-heading"))
    .toHaveText(["Class not recorded", "Decision model", "Text generator"]);
  await expect(page.getByRole("region", { name: "Narrowing", exact: true }).getByRole("status"))
    .toHaveText("28 qualify · 13 may qualify · 3 out");
  await expect(page.locator(".template-active")).toHaveCount(0);
  await page.reload();
  await expect(page.locator(".board-unranked")).toHaveText("Not ranked yet: listed alphabetically");
  await expect(page.locator(".template-active")).toHaveCount(0);
});

test("a shared board wins over the default and keeps its chosen chart axes", async ({ page }) => {
  const state = {
    tokIn: 40000, tokOut: 4000, bench: "swe_bench_pro", w: { cap: 0.6, cost: 0.3, speed: 0.1 }, conds: [], x: "task$",
    board: { selections: { "model.context_window": { mode: "must", op: ">=", value: 200000 } }, mustOrder: ["model.context_window"], estate: { providers: [], plans: [], hardware: [] }, canvas: { x: "facet:model.context_window", y: "capability:software_engineering" } },
  };
  await page.goto(`/decide.html#s=${btoa(encodeURIComponent(JSON.stringify(state)))}`);
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
  await expect(page.locator(".template-active")).toHaveCount(0);
  await expect(page.getByLabel("X axis")).toHaveValue("facet:model.context_window");
  await expect(page.locator('[data-facet="model.context_window"]').getByLabel("Must")).toBeChecked();
});

test("the counter announces exact values and does not animate with reduced motion", async ({ page }) => {
  await openBoard(page);
  const narrowing = page.getByRole("region", { name: "Narrowing", exact: true });
  const status = narrowing.getByRole("status");
  await expect(status).toHaveAttribute("aria-live", "polite");
  await expect(status).toHaveAttribute("aria-atomic", "true");
  await expect(status).toHaveText("24 qualify · 10 may qualify · 10 out");
  await expect(narrowing.locator(".narrowing-number")).toHaveText(["24", "10", "10"]);
  await expect(narrowing.locator(".narrowing-counts")).toHaveAttribute("aria-hidden", "true");
  expect(await narrowing.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("none");
  const shortcuts = await page.locator(".template-shortcuts").boundingBox();
  const counter = await narrowing.boundingBox();
  const access = await page.getByRole("region", { name: "How will you use it?" }).boundingBox();
  if (!shortcuts || !counter || !access) throw new Error("The opening view is missing a region");
  expect(counter.y).toBeGreaterThanOrEqual(shortcuts.y + shortcuts.height);
  expect(access.y).toBeGreaterThanOrEqual(counter.y + counter.height);

  const liveRegion = await status.elementHandle();
  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/v1/decide", async (route) => { await held; await route.fulfill({ contentType: "application/json", body: narrowedDecision }); });
  await page.getByRole("button", { name: /^Size of work/ }).click();
  await page.locator('[data-facet="model.context_window"]').getByLabel("Must", { exact: true }).check();
  await expect(page.locator(".loading-cards")).toBeVisible();
  await expect(status).toHaveText("24 qualify · 10 may qualify · 10 out");
  expect(await status.evaluate((node, original) => node === original, liveRegion)).toBe(true);
  release();
  await expect(status).toHaveText("15 qualify · 3 may qualify · 14 out");
  expect(await status.evaluate((node, original) => node === original, liveRegion)).toBe(true);
  await expect(narrowing.locator(".narrowing-number")).toHaveText(["15", "3", "14"]);
  expect(await narrowing.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("none");
});

test("the counter animates exact digits when motion is enabled", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await openBoard(page);
  await expect(page.locator(".narrowing-number")).toHaveText(["24", "10", "10"]);
  expect(await page.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("narrowing-count");
  await page.route("**/v1/decide", (route) => route.fulfill({ contentType: "application/json", body: narrowedDecision }));
  await page.locator(".template-shortcuts button").nth(1).click();
  await expect(page.locator(".narrowing-number")).toHaveText(["15", "3", "14"]);
  await expect(page.getByRole("region", { name: "Narrowing", exact: true }).getByRole("status")).toHaveText("15 qualify · 3 may qualify · 14 out");
  expect(await page.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("narrowing-count");
});

test("a board facet updates the decision and survives reload", async ({ page }) => {
  await openBoard(page);
  await page.getByRole("button", { name: /Size of work/ }).click();
  const context = page.locator('[data-facet="model.context_window"]');
  await context.getByLabel("Must").check();
  await expect(page).toHaveURL(/#s=/);
  await page.reload();
  await expect(page.locator('[data-facet="model.context_window"]').getByLabel("Must")).toBeChecked();
});

test("share dialog copies the board permalink and restores focus", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await openBoard(page);
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
  const trigger = page.getByRole("button", { name: "Share or give to my agent" });
  await trigger.click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("tab", { name: "Procurement review" }).click();
  await expect(dialog.getByRole("button", { name: "Download CSV" })).toBeVisible();
  await dialog.getByRole("tab", { name: "Permalink" }).click();
  await dialog.getByRole("button", { name: "Copy", exact: true }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain("#s=");
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
});

test("the board fits a 390px viewport in light and dark mode", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openBoard(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  for (const buttonName of ["Light mode", "Dark mode"]) {
    await page.getByRole("button", { name: buttonName }).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  }
});

/** Open the board at `width` and apply a template, so every region has content. */
async function applyTemplate(page: import("@playwright/test").Page, width: number) {
  await page.setViewportSize({ width, height: width >= 1000 ? 900 : 844 });
  // The gated build re-renders the board when /v1/human-status answers; apply
  // the template only after that, or the template can be applied and reset.
  const status = process.env.VITE_HUMAN_GATE_ENABLED === "true"
    ? page.waitForResponse((response) => response.url().includes("/v1/human-status"))
    : null;
  // Old table-first links load the same fixed composition.
  await page.goto("/decide.html?layout=table");
  if (status) await status;
  await expect(page.getByRole("group", { name: "Layout" })).toHaveCount(0);
  await page.getByRole("button", { name: /^(All \d+ templates|Hide templates)$/ }).click();
  await page.locator(".board-templates").getByRole("button", { name: /^Assistant · Balanced:/ }).click();
  await expect(page.getByRole("region", { name: "Trade-off canvas" })).toBeVisible();
  await expect(page.locator(".decision-table")).toBeVisible();
  await expect(page.locator(".loading")).toHaveCount(0);
  // Every measured region must exist before its box is read; the gated build
  // settles its status fetch a beat later than the ungated one.
  for (const region of [
    page.getByRole("region", { name: "Facets", exact: true }),
    page.locator(".board-answer"),
    page.locator(".board-ranked-answer").last(),
    page.locator(".board-workspace"),
    page.locator(".why-panel"),
  ]) await expect(region).toBeVisible();
}

for (const [width, scrollbar] of [[1440, 0], [1124, 0], [1100, 0], [1000, 0], [1000, 15]] as const) {
  test(`the ranked answer fits inside the narrowing card, and both cards share one height, at ${width}px${scrollbar ? ` with a ${scrollbar}px scrollbar` : ""}`, async ({ page }) => {
    await applyTemplate(page, width);
    if (scrollbar) {
      // A classic scrollbar takes its width from the page but not from the
      // media query, which still reads 1000px. Headless Chromium hides
      // scrollbars, so the page gives up the same width as padding instead.
      await page.addStyleTag({ content: `html { padding-right: ${scrollbar}px; }` });
      await expect.poll(() => page.evaluate(() => document.body.clientWidth)).toBe(width - scrollbar);
    }
    // MODEL-298: at 1100px the facets track once took 600px and left the
    // ranked rows 26px wider than the card. Measure the overflow, not the CSS.
    const overflow = () => page.evaluate(() => {
      const nodes = [
        ...document.querySelectorAll<HTMLElement>(".board-answer"),
        ...document.querySelectorAll<HTMLElement>(".board-ranked-answer"),
        ...document.querySelectorAll<HTMLElement>(".board-ranked-answer > ol > li"),
      ];
      return nodes.length === 0
        ? ["no narrowing card"]
        : nodes.filter((node) => node.scrollWidth > node.clientWidth)
          .map((node) => `${node.tagName.toLowerCase()}.${node.className}: ${node.scrollWidth} > ${node.clientWidth}`);
    });
    await expect.poll(overflow).toEqual([]);
    await page.evaluate(() => document.fonts.ready);
    const headline = await page.getByRole("heading", { level: 1 }).evaluate((node) => ({
      height: node.getBoundingClientRect().height,
      lineHeight: parseFloat(getComputedStyle(node).lineHeight),
    }));
    expect(headline.height).toBeLessThanOrEqual(headline.lineHeight + 1);
    const boxes = () => Promise.all([
      page.getByRole("region", { name: "Facets", exact: true }).boundingBox(),
      page.locator(".board-answer").boundingBox(),
    ]);
    await expect.poll(async () => (await boxes()).every(Boolean)).toBe(true);
    const [facets, answers] = await boxes();
    if (!facets || !answers) throw new Error("the board did not render both cards");
    expect(answers.x).toBeGreaterThanOrEqual(facets.x + facets.width);
    expect(Math.abs(answers.y - facets.y)).toBeLessThanOrEqual(1);
    expect(Math.abs(answers.height - facets.height)).toBeLessThanOrEqual(1);
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
  });
}

for (const width of [1440, 1024, 390, 320]) {
  test(`a template puts facets and narrowing side by side or stacked, then the canvas and table at full width, at ${width}px`, async ({ page }) => {
    await applyTemplate(page, width);
    const canvas = page.getByRole("region", { name: "Trade-off canvas" });

    const measure = () => Promise.all([
      page.getByRole("region", { name: "Facets", exact: true }).boundingBox(),
      canvas.boundingBox(),
      page.locator(".board-answer").boundingBox(),
      page.locator(".decision-table").boundingBox(),
      page.locator(".board-workspace").boundingBox(),
      page.locator(".why-panel").boundingBox(),
    ]);
    // A live update can briefly remount a region; read the boxes once all exist.
    await expect.poll(async () => (await measure()).every(Boolean)).toBe(true);
    const [facets, chart, answers, table, workspace, details] = await measure();
    if (!facets || !chart || !answers || !table || !workspace || !details) {
      throw new Error("the applied template did not render all layout regions");
    }
    // The narrowing card holds the funnel, the answer, the ranked list and the
    // feedback form; the canvas is no longer inside it (MODEL-298).
    const [narrowing, ranked, feedback] = await Promise.all([
      page.locator(".board-answer-head").boundingBox(),
      page.locator(".board-ranked-answer").last().boundingBox(),
      page.locator(".answer-feedback").boundingBox(),
    ]);
    if (!narrowing || !ranked) throw new Error("the narrowing did not render");
    for (const inside of [narrowing, ranked, ...(feedback ? [feedback] : [])]) {
      expect(inside.y).toBeGreaterThanOrEqual(answers.y);
      expect(inside.y + inside.height).toBeLessThanOrEqual(answers.y + answers.height + 1);
    }
    await expect(page.locator(".board-answer").getByRole("region", { name: "Trade-off canvas" })).toHaveCount(0);
    expect(await page.locator(".board-answer").evaluate((node) => getComputedStyle(node).position)).toBe("static");

    // Jamie, 2026-10-03: the facets and narrowing cards share one height,
    // whichever is longer.
    if (width >= 1024) {
      expect(answers.x).toBeGreaterThanOrEqual(facets.x + facets.width);
      expect(Math.abs(answers.y - facets.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(answers.height - facets.height)).toBeLessThanOrEqual(1);
    } else {
      expect(answers.y).toBeGreaterThanOrEqual(facets.y + facets.height);
    }
    // ...and the canvas spans the page below both, as wide as the table.
    expect(chart.y).toBeGreaterThanOrEqual(Math.max(facets.y + facets.height, answers.y + answers.height));
    expect(Math.abs(chart.width - table.width)).toBeLessThanOrEqual(2);
    expect(Math.abs(chart.x - table.x)).toBeLessThanOrEqual(1);
    expect(table.y).toBeGreaterThanOrEqual(chart.y + chart.height);
    expect(Math.abs(table.width - workspace.width)).toBeLessThanOrEqual(2);
    expect(Math.abs(table.x - workspace.x)).toBeLessThanOrEqual(1);
    expect(details.y).toBeGreaterThanOrEqual(table.y + table.height);
    // The plot keeps a sensible shape at full width: never a thin strip.
    const plot = await canvas.locator(".plot-wrap").boundingBox();
    if (!plot) throw new Error("the canvas drew no plot");
    expect(plot.height).toBeGreaterThanOrEqual(460);
    expect(plot.height).toBeLessThanOrEqual(560);
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
    expect(await page.locator(".board-answer").evaluate((node) => getComputedStyle(node).overflowY)).toBe("visible");

    if (process.env.MODELSPEC_SCREENSHOT_DIR) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: `${process.env.MODELSPEC_SCREENSHOT_DIR}/decide-298-${width}.png`, fullPage: true });
    }
  });
}

test("the loading skeleton fits a 390px viewport", async ({ page }) => {
  // Hold the decision so the skeleton stays up: a fixed 400px cards column once
  // made a phone scroll sideways while a decision loaded.
  let release = () => {};
  const held = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/v1/decide", async (route) => { await held; await route.fallback(); });
  await page.setViewportSize({ width: 390, height: 844 });
  await openBoard(page);
  await expect(page.locator(".loading-cards")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  release();
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
});

test("the board and its explanation fit a 320px viewport in light and dark mode", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await openBoard(page);
  const scrollWidth = () => page.evaluate(() => document.documentElement.scrollWidth);
  await expect.poll(scrollWidth).toBeLessThanOrEqual(320);
  await page.getByRole("button", { name: /^(All \d+ templates|Hide templates)$/ }).click();
  await page.locator(".board-templates").getByRole("button", { name: /^Assistant · Balanced:/ }).click();
  await expect(page.locator(".why-panel .contribution").first()).toBeVisible();
  for (const buttonName of ["Light mode", "Dark mode"]) {
    await page.getByRole("button", { name: buttonName }).click();
    await expect.poll(scrollWidth).toBeLessThanOrEqual(320);
  }
});

test.describe("the Worker gate is enabled", () => {
  test.use({ humanStatus: { enabled: true, remaining: 20 } });
  test.skip(process.env.VITE_HUMAN_GATE_ENABLED !== "true" && process.env.VITE_VISIT_GATE_ENABLED !== "true", "requires a gated page build");

  test("shows verification and waits for a manual lookup", async ({ page }) => {
    let decisions = 0;
    page.on("request", (request) => {
      if (request.url().endsWith("/v1/decide") && request.method() === "POST") decisions++;
    });
    await page.route("https://challenges.cloudflare.com/turnstile/**", (route) => route.fulfill({
      contentType: "application/javascript",
      body: `window.turnstile = {
        render(container, options) { options.callback("browser-test-token"); return "test-widget"; },
        remove() {}
      };`,
    }));
    await openBoard(page);
    const gate = page.getByRole("region", { name: "Manual lookups" });
    await expect(gate).toBeVisible();
    await expect(gate.getByText("20 decisions remaining today. Resets at midnight UTC.")).toBeVisible();
    await expect(gate.getByRole("link", { name: "paid API or MCP" })).toBeVisible();
    const lookup = gate.getByRole("button", { name: "Look up this decision" });
    await expect(lookup).toBeEnabled();
    await expect(page.getByLabel("Facet board answer")).toHaveCount(0);
    expect(decisions).toBe(0);

    const request = page.waitForRequest((request) =>
      request.url().endsWith("/v1/decide") && request.method() === "POST",
    );
    await lookup.click();
    expect((await request).headers()["x-modelspec-turnstile"]).toBe("browser-test-token");
    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    expect(decisions).toBeGreaterThan(0);
    await page.getByRole("button", { name: "Share or give to my agent" }).click();
    await page.getByRole("dialog").getByRole("tab", { name: "Procurement review" }).click();
    await expect(page.getByRole("dialog").getByRole("button", { name: /CSV/ })).toHaveCount(0);
  });
});
