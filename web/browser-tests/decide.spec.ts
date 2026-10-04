import { expect } from "@playwright/test";
import { test } from "./human-gate-fixtures";
import { readFileSync } from "node:fs";
import { decisionFixtureFor } from "../scripts/decision-fixtures.mjs";
import { check, counterView, measure, openDecide, routeFixtures } from "../scripts/decide-layout-measure.mjs";

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
  await expect(page.getByRole("button", { name: "Share" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Give this to my agent" })).toBeVisible();
  await expect(page.getByText(/^Your agent gets this answer from \d+\.\d+¢$/)).toBeVisible();
  await expect(page.getByRole("link", { name: "no paid placement · sourced" })).toHaveAttribute("href", "https://modelspec.dev/legal/neutrality/");
  await expect(page.locator(".template-active")).toHaveText("Starting from: General assistant, balancedClear");
  await expect(page.locator(".template-shortcuts button")).toHaveCount(6);
  await expect(page.getByLabel("X axis")).toHaveValue("facet:offering.cost_per_task");
  await expect(page.getByLabel("Y axis")).toHaveValue("capability:chat_preference");
  await expect(page.getByText("Up and left is better")).toBeVisible();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests.filter((request) => request.explain === "summary")).toHaveLength(1);
  expect(requests[0].where).toEqual(["model.class = text-generator", "model.lifecycle = active"]);
  expect(requests[0].optimize).toEqual({ weights: { chat_preference: 0.6, "-offering.cost_per_task": 0.4 } });
  expect(requests[0]).not.toHaveProperty("task_type");
  await expect(page.locator(".board-intro .eyebrow")).toHaveText("Free for people · No paid placement");
  await page.getByRole("region", { name: "Give this to my agent" }).getByRole("button", { name: "Spec", exact: true }).click();
  expect(JSON.parse(await page.getByLabel("Spec snippet").innerText())).toEqual(requests[0]);
});

test("agent hand-off leads with the CLI and copies one message with the current Spec", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await openBoard(page);
  const card = page.getByRole("region", { name: "Give this to my agent" });
  await expect(card).toBeVisible();
  await expect(page.locator(".agent-handoff")).toHaveCount(1);
  const [answer, handoff] = await Promise.all([
    page.locator(".board-ranked-answer").last().boundingBox(), card.boundingBox(),
  ]);
  if (!answer || !handoff) throw new Error("Answer or hand-off did not render");
  expect(handoff.y).toBeGreaterThanOrEqual(answer.y + answer.height);
  await expect(card.getByRole("group", { name: "Agent snippet format" }).getByRole("button"))
    .toHaveText(["CLI", "MCP", "Spec", "curl"]);
  await expect(card.getByRole("button", { name: "CLI", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(card.getByLabel("CLI snippet")).toHaveText(
    "uvx --from modelspec-dev modelspec help agent\nuvx --from modelspec-dev modelspec decide --spec spec.json");
  await card.getByRole("button", { name: "CLI", exact: true }).focus();
  await page.keyboard.press("Tab");
  const mcp = card.getByRole("button", { name: "MCP", exact: true });
  await expect(mcp).toBeFocused();
  expect(await mcp.evaluate((node) => getComputedStyle(node).outlineStyle)).toBe("solid");
  await page.keyboard.press("Enter");
  await expect(card.getByLabel("MCP snippet")).toHaveText("uvx --from modelspec-dev modelspec setup mcp --client claude-code");
  await card.getByLabel("MCP client").selectOption("cursor");
  await expect(card.getByLabel("MCP snippet")).toHaveText("uvx --from modelspec-dev modelspec setup mcp --client cursor");
  await card.getByRole("button", { name: "curl", exact: true }).click();
  await expect(card.getByLabel("curl snippet")).toContainText('Authorization: Bearer $MODELSPEC_API_KEY');
  await card.getByRole("button", { name: "Copy curl" }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(await card.getByLabel("curl snippet").innerText());
  await expect(card.getByRole("status")).toHaveText("curl copied.");
  await card.getByRole("button", { name: "Spec", exact: true }).click();
  const snippet = await card.getByLabel("Spec snippet").innerText();
  const message = `Run \`uvx --from modelspec-dev modelspec help agent\`, then decide with this spec:\n\n${snippet}`;
  await card.getByRole("button", { name: "Copy for my agent" }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(message);
  await expect(card.getByRole("status")).toHaveText("Hand-off copied for your agent.");

  const price = page.locator(".answer-assurances");
  await page.evaluate(() => navigator.clipboard.writeText(""));
  await price.getByRole("button", { name: "Copy for my agent" }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(message);
  await expect(price.getByRole("status")).toHaveText("Hand-off copied for your agent.");

  const updatedRequest = page.waitForRequest((request) => request.url().endsWith("/v1/decide") && request.method() === "POST" && request.postDataJSON().explain === "summary");
  await page.getByRole("button", { name: "Clear", exact: true }).click();
  const updated = (await updatedRequest).postDataJSON();
  await expect(card.getByRole("status")).toBeEmpty();
  await card.getByRole("button", { name: "Spec", exact: true }).click();
  expect(JSON.parse(await card.getByLabel("Spec snippet").innerText())).toEqual(updated);
});

test("the accent card meets AA in both themes and every format", async ({ page }) => {
  await openBoard(page);
  const card = page.getByRole("region", { name: "Give this to my agent" });
  await expect(card).toBeVisible();
  for (const theme of ["dark", "light"]) {
    if (theme === "light") await page.getByRole("button", { name: "Light mode" }).click();
    for (const format of ["CLI", "MCP", "Spec", "curl"]) {
      await card.getByRole("button", { name: format, exact: true }).click();
      const ratios = await card.evaluate((root) => {
        const luminance = (color: string) => {
          const rgb = color.match(/[\d.]+/g)?.slice(0, 3).map(Number);
          if (!rgb || rgb.length !== 3) throw new Error(`Unknown color ${color}`);
          return rgb.map((value) => value / 255)
            .map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4)
            .reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
        };
        return [...root.querySelectorAll("h2, p, small, a, pre, button, code, label, select")].map((node) => {
          let background: Element | null = node;
          while (background && ["rgba(0, 0, 0, 0)", "transparent"].includes(getComputedStyle(background).backgroundColor)) background = background.parentElement;
          if (!background) throw new Error("Text has no background");
          const foreground = luminance(getComputedStyle(node).color);
          const behind = luminance(getComputedStyle(background).backgroundColor);
          return (Math.max(foreground, behind) + 0.05) / (Math.min(foreground, behind) + 0.05);
        });
      });
      for (const ratio of ratios) expect(ratio, `${theme} ${format}`).toBeGreaterThanOrEqual(4.5);
    }
  }
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
  await expect(status).toHaveText("24 qualify · 10 may qualify · 10 out · 6 best for your weights");
  await expect(narrowing.locator(".narrowing-number")).toHaveText(["24", "10", "10", "6"]);
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
  await expect(status).toHaveText("24 qualify · 10 may qualify · 10 out · 6 best for your weights");
  expect(await status.evaluate((node, original) => node === original, liveRegion)).toBe(true);
  release();
  await expect(status).toHaveText("15 qualify · 3 may qualify · 14 out");
  expect(await status.evaluate((node, original) => node === original, liveRegion)).toBe(true);
  await expect(narrowing.locator(".narrowing-number")).toHaveText(["15", "3", "14", "—"]);
  expect(await narrowing.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("none");
});

test("the counter animates exact digits when motion is enabled", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await openBoard(page);
  await expect(page.locator(".narrowing-number")).toHaveText(["24", "10", "10", "6"]);
  expect(await page.locator(".narrowing-number").first().evaluate((node) => getComputedStyle(node).animationName)).toBe("narrowing-count");
  await page.route("**/v1/decide", (route) => route.fulfill({ contentType: "application/json", body: narrowedDecision }));
  await page.locator(".template-shortcuts button").nth(1).click();
  await expect(page.locator(".narrowing-number")).toHaveText(["15", "3", "14", "—"]);
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
  const trigger = page.getByRole("button", { name: "Share" });
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
  await page.locator(".board-templates").getByRole("button", { name: /^General assistant · Balanced:/ }).click();
  await expect(page.getByRole("region", { name: "Trade-off canvas" })).toBeVisible();
  await expect(page.locator(".decision-table")).toBeVisible();
  await expect(page.locator(".loading")).toHaveCount(0);
  // Every measured region must exist before its box is read; the gated build
  // settles its status fetch a beat later than the ungated one.
  for (const region of [
    page.getByRole("region", { name: "Facets", exact: true }),
    page.locator(".board-answer"),
    page.locator(".board-ranked-answer").last(),
    page.getByRole("region", { name: "Give this to my agent" }),
    page.locator(".why-panel"),
  ]) await expect(region).toBeVisible();
}

for (const [width, scrollbar] of [[1440, 0], [1236, 0], [1124, 0], [1100, 0], [1000, 0], [1000, 15]] as const) {
  test(`the answer card holds its ranked rows and the page reads answer, refine, hand-off, table at ${width}px${scrollbar ? ` with a ${scrollbar}px scrollbar` : ""}`, async ({ page }) => {
    await applyTemplate(page, width);
    if (scrollbar) {
      // A classic scrollbar takes its width from the page but not from the
      // media query. Headless Chromium hides scrollbars, so the page gives up
      // the same width as padding instead.
      await page.addStyleTag({ content: `html { padding-right: ${scrollbar}px; }` });
      await expect.poll(() => page.evaluate(() => document.body.clientWidth)).toBe(width - scrollbar);
    }
    // MODEL-298: ranked rows once ran wider than their card. Measure the overflow, not the CSS.
    const overflow = () => page.evaluate(() => {
      const nodes = [
        ...document.querySelectorAll<HTMLElement>(".board-answer"),
        ...document.querySelectorAll<HTMLElement>(".board-ranked-answer"),
        ...document.querySelectorAll<HTMLElement>(".board-ranked-answer > ol > li"),
      ];
      return nodes.length === 0
        ? ["no answer card"]
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

    const measure = () => Promise.all([
      page.locator(".board-answer").boundingBox(),
      page.getByRole("region", { name: "Trade-off canvas" }).boundingBox(),
      page.getByRole("region", { name: "Refine the answer" }).boundingBox(),
      page.getByRole("region", { name: "Give this to my agent" }).boundingBox(),
      page.locator(".decision-table").boundingBox(),
    ]);
    // A gated build remounts the board when /v1/human-status answers: keep the
    // boxes from the one reading that saw every region.
    let boxes = await measure();
    await expect.poll(async () => (boxes = await measure()).every(Boolean)).toBe(true);
    const [answer, chart, refine, handoff, table] = boxes;
    if (!answer || !chart || !refine || !handoff || !table) throw new Error("the page did not render every region");
    // MODEL-325: from 1100px the chart sits beside the answer, six columns each; below, it follows the answer.
    if (width - scrollbar >= 1100) {
      expect(chart.x).toBeGreaterThanOrEqual(answer.x + answer.width);
      expect(Math.abs(chart.y - answer.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(chart.width - answer.width)).toBeLessThanOrEqual(1);
    } else {
      expect(chart.y).toBeGreaterThanOrEqual(answer.y + answer.height);
    }
    expect(refine.y).toBeGreaterThanOrEqual(answer.y + answer.height);
    expect(handoff.y).toBeGreaterThanOrEqual(refine.y + refine.height);
    expect(table.y).toBeGreaterThanOrEqual(handoff.y + handoff.height);
    expect(Math.abs(table.x - refine.x)).toBeLessThanOrEqual(1);
    expect(Math.abs(table.width - refine.width)).toBeLessThanOrEqual(1);
    // The plot keeps a sensible shape at half width: never a thin strip.
    const plotHeight = () => page.locator(".canvas-panel .plot-wrap").boundingBox().then((plot) => plot?.height ?? 0);
    await expect.poll(plotHeight).toBeGreaterThanOrEqual(460);
    expect(await plotHeight()).toBeLessThanOrEqual(560);
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
  });
}

// MODEL-325: one gutter, one gap, one panel inset, the split on a tile
// boundary, and the answer above the fold, as scripts/decide-layout.mjs prints them.
const gated = process.env.VITE_HUMAN_GATE_ENABLED === "true" || process.env.VITE_VISIT_GATE_ENABLED === "true";
for (const viewport of [{ width: 1236, height: 800 }, { width: 1440, height: 800 }, { width: 390, height: 844 }]) {
  test(`a clean first visit meets the layout contract at ${viewport.width}×${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await routeFixtures(page);
    await openDecide(page);
    const rows = check(await measure(page))
      // A gated page adds its verification panel above the answer.
      .filter((row) => !gated || !/fold|two screens/.test(row.check));
    expect(rows.filter((row) => !row.pass)).toEqual([]);
  });
}

test("a template click changes the first screen without scrolling", async ({ page }) => {
  await page.setViewportSize({ width: 1236, height: 800 });
  await routeFixtures(page);
  await openDecide(page);
  const before = await counterView(page);
  const shortcut = page.locator(".template-shortcut").nth(1);
  await shortcut.click();
  await expect(shortcut).toHaveAttribute("aria-pressed", "true");
  await expect(shortcut.locator(".template-check")).toHaveText("✓");
  await expect.poll(async () => (await counterView(page))?.summary).not.toBe(before?.summary);
  const after = await counterView(page);
  expect(after?.bottom).toBeLessThanOrEqual(800);
  expect(await page.evaluate(() => scrollY)).toBe(0);
});

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
  await page.locator(".board-templates").getByRole("button", { name: /^General assistant · Balanced:/ }).click();
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
    await page.getByRole("button", { name: "Share" }).click();
    await page.getByRole("dialog").getByRole("tab", { name: "Procurement review" }).click();
    await expect(page.getByRole("dialog").getByRole("button", { name: /CSV/ })).toHaveCount(0);
  });
});
