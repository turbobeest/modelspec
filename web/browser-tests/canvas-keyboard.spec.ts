import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { decisionSpecSchema, type DecisionSpec } from "../src/decide/adapter/contract";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/live-vocabulary.json", import.meta.url), "utf8");
const decision = readFileSync(new URL("../src/decide/__fixtures__/live-assistant-balanced-full.json", import.meta.url), "utf8");
const thresholdName = "Chat and preference capability Must threshold";
const cors = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST, OPTIONS" };
const verticalThreshold = (page: Page) => page.getByRole("slider", { name: thresholdName, exact: true })
  .and(page.locator('[aria-orientation="vertical"]'));

async function offlineDecisions(page: Page, baseURL: string) {
  const origin = new URL(baseURL).origin;
  const requests: DecisionSpec[] = [];
  const completed: DecisionSpec[] = [];
  let heldSummary: Promise<void> | null = null;
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const reply = (body: string) => route.fulfill({ status: 200, contentType: "application/json", headers: cors, body });
    if (/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)$/.test(url.pathname)) return reply(vocabulary);
    if (url.pathname === "/v1/human-status") return reply('{"enabled":false}');
    if (url.pathname === "/v1/decide") {
      if (request.method() === "OPTIONS") return reply("{}");
      expect(request.method()).toBe("POST");
      const sent = decisionSpecSchema.parse(request.postDataJSON());
      requests.push(sent);
      if (sent.explain === "summary" && heldSummary) await heldSummary;
      // Keep the replacement in flight long enough for its loading state to render.
      await new Promise((resolve) => setTimeout(resolve, 100));
      await reply(decision);
      completed.push(sent);
      return;
    }
    return url.origin === origin ? route.continue() : route.abort("blockedbyclient");
  });

  return {
    requests,
    holdNextSummary() {
      let release = () => {};
      heldSummary = new Promise<void>((resolve) => { release = resolve; });
      return () => {
        heldSummary = null;
        release();
      };
    },
    async settled(cycles: number, extraPlots = 0) {
      await expect.poll(() => completed.filter((sent) => sent.explain === "summary").length).toBe(cycles);
      await expect.poll(() => completed.filter((sent) => sent.explain === "full").length).toBe(cycles * 2 + extraPlots);
      await expect(page.getByLabel("Facet board answer")).toBeVisible();
      await expect(verticalThreshold(page)).toBeVisible();
      await expect(page.locator(".loading")).toHaveCount(0);
      await page.waitForLoadState("networkidle");
      expect(requests).toHaveLength(cycles * 3 + extraPlots);
    },
  };
}

async function thresholdValue(page: Page) {
  const value = await verticalThreshold(page).getAttribute("aria-valuenow");
  expect(value).not.toBeNull();
  if (value === null) throw new Error("The threshold must report its current value");
  const number = Number(value);
  expect(Number.isFinite(number)).toBe(true);
  return number;
}

const scrollPosition = (page: Page) => page.evaluate(() => ({ x: scrollX, y: scrollY }));

test.use({ viewport: { width: 768, height: 844 }, reducedMotion: "reduce" });

test("MODEL-458 AUD-12-F7: two threshold adjustments preserve keyboard focus and scroll", async ({ page, baseURL }) => {
  if (!baseURL) throw new Error("An isolated preview baseURL is required");
  const api = await offlineDecisions(page, baseURL);
  await page.goto("/decide/details/?template=assistant-balanced");
  await api.settled(1);
  await page.evaluate(() => document.fonts.ready);
  const slider = page.getByRole("slider", { name: thresholdName, exact: true });
  const callsBeforeFocus = api.requests.length;
  await slider.focus();
  await expect(slider).toBeFocused();
  // Wait through the board's debounce to observe any request caused by focus alone.
  await page.waitForTimeout(400);
  expect(api.requests).toHaveLength(callsBeforeFocus);
  let value = await thresholdValue(page);
  const scroll = await scrollPosition(page);

  for (const cycle of [2, 3]) {
    await page.keyboard.press("ArrowUp");
    await api.settled(cycle);
    await expect(slider).toBeFocused();
    const next = await thresholdValue(page);
    expect(next).toBeGreaterThan(value);
    expect(await scrollPosition(page)).toEqual(scroll);
    const summary = api.requests.filter((sent) => sent.explain === "summary").at(-1);
    expect(summary).toBeDefined();
    if (!summary) throw new Error("The threshold change must submit a summary request");
    expect(summary.where).toContain(`chat_preference >= ${next}`);
    value = next;
  }
});

test("MODEL-458 AUD-12-F7: a settled threshold response respects focus moved to another control", async ({ page, baseURL }) => {
  if (!baseURL) throw new Error("An isolated preview baseURL is required");
  const api = await offlineDecisions(page, baseURL);
  await page.goto("/decide/details/?template=assistant-balanced");
  await api.settled(1);
  const slider = page.getByRole("slider", { name: thresholdName, exact: true });
  await slider.focus();
  const release = api.holdNextSummary();
  const otherControl = page.getByRole("button", { name: "Share", exact: true });
  try {
    await page.keyboard.press("ArrowUp");
    await expect.poll(() => api.requests.filter((sent) => sent.explain === "summary").length).toBe(2);
    await otherControl.focus();
    await expect(otherControl).toBeFocused();
  } finally {
    release();
  }
  await api.settled(2);
  await expect(otherControl).toBeFocused();
});

test("MODEL-458 AUD-12-F7: matching chart axes retain the vertical threshold focus", async ({ page, baseURL }) => {
  if (!baseURL) throw new Error("An isolated preview baseURL is required");
  const api = await offlineDecisions(page, baseURL);
  await page.goto("/decide/details/?template=assistant-balanced");
  await api.settled(1);
  await page.getByLabel("X axis", { exact: true }).selectOption("capability:chat_preference");
  await api.settled(1, 1);
  const slider = verticalThreshold(page);
  await slider.focus();
  let value = await thresholdValue(page);
  const scroll = await scrollPosition(page);
  for (const cycle of [2, 3]) {
    await page.keyboard.press("ArrowUp");
    await api.settled(cycle, 1);
    await expect(slider).toBeFocused();
    const next = await thresholdValue(page);
    expect(next).toBeGreaterThan(value);
    expect(await scrollPosition(page)).toEqual(scroll);
    value = next;
  }
});
