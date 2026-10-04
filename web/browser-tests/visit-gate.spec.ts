import { expect } from "@playwright/test";
import { test } from "./human-gate-fixtures";
import { readFileSync } from "node:fs";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/vocabulary.json", import.meta.url), "utf8");
const cors = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST, OPTIONS" };
const answer = readFileSync(new URL("../src/decide/__fixtures__/live-empty-board-full.json", import.meta.url), "utf8");

test.describe("managed visit gate", () => {
  test.use({ humanStatus: { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 } });
  test.skip(process.env.VITE_VISIT_GATE_ENABLED !== "true", "requires visit page variant");

  for (const expiry of ["none", "local", "worker"] as const) {
    test(`live facet updates after a silent check, expiry=${expiry}`, async ({ page }) => {
      let checks = 0;
      let refuseOnce = false;
      const sent: { token: string | undefined; intent: string | undefined }[] = [];
      await page.route("https://challenges.cloudflare.com/turnstile/**", (route) => route.fulfill({
        contentType: "application/javascript",
        body: `window.turnstile = {
          render(container, options) {
            if (options.appearance !== "interaction-only") throw new Error("visible challenge");
            options.callback("single-use-" + Math.random()); return "widget";
          }, remove() {}
        };`,
      }));
      await page.route("**/v1/visit-token", async (route) => {
        if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
        checks++;
        expect(route.request().headers()["x-modelspec-turnstile"]).toContain("single-use-");
        return route.fulfill({ headers: cors, contentType: "application/json", body: JSON.stringify({
          token: `visit-${checks}`, expires_at: Math.floor(await page.evaluate(() => Date.now()) / 1000) + 1800,
        }) });
      });
      await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) => {
        if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
        if (route.request().url().includes("/v1/vocabulary"))
          expect(route.request().headers()["x-modelspec-visit-token"]).toBe("visit-1");
        return route.fulfill({ headers: cors, contentType: "application/json", body: vocabulary });
      });
      await page.route("**/v1/decide", (route) => {
        if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
        const headers = route.request().headers();
        sent.push({ token: headers["x-modelspec-visit-token"], intent: headers["x-modelspec-intent"] });
        if (refuseOnce) {
          refuseOnce = false;
          return route.fulfill({ status: 401, headers: cors, contentType: "application/json", body: JSON.stringify({ error: { code: "visit_token_expired" } }) });
        }
        return route.fulfill({ headers: cors, contentType: "application/json", body: answer });
      });
      await page.clock.install();
      await page.goto("/decide.html?demo=1");
      await expect(page.getByLabel("Facet board answer")).toBeVisible();
      await expect.poll(() => sent.length).toBe(3);
      await expect(page.locator(".template-active")).toHaveText("Starting from: General assistant, balancedClear");
      expect(checks).toBe(1);
      expect(new Set(sent.map((request) => request.intent)).size).toBe(1);
      expect(sent.every((request) => request.token === "visit-1")).toBe(true);
      await expect(page.getByRole("button", { name: "Look up this decision" })).toHaveCount(0);
      if (expiry === "local") await page.clock.fastForward(1801 * 1000);
      if (expiry === "worker") refuseOnce = true;
      const first = sent.length;
      const capabilities = page.getByRole("button", { name: /What it.s good at/ });
      if (await capabilities.getAttribute("aria-expanded") !== "true") await capabilities.click();
      await page.locator('[data-facet="capability.software_engineering"]').getByLabel("Prefer", { exact: true }).check();
      await expect.poll(() => sent.length).toBeGreaterThanOrEqual(first + (expiry === "worker" ? 3 : 2));
      await expect(page.getByLabel("Facet board answer")).toBeVisible();
      expect(checks).toBe(expiry === "none" ? 1 : 2);
      expect(new Set(sent.slice(first).map((request) => request.intent)).size).toBe(1);
      expect(sent[first].intent).not.toBe(sent[0].intent);
      // Summary, full and plot: one action asks each question once, even when
      // its full explanation lands before its plot.
      expect(sent.filter((request) => request.intent === sent[0].intent)).toHaveLength(3);
      await expect(page.locator("#facet-board-answer .visit-gate")).toHaveCount(1);
    });
  }

  test("an interactive challenge stays in the answer panel and resumes without a lookup click", async ({ page }) => {
    let check = 0;
    let initialRequests = 0;
    let vocabularyRequests = 0;
    const specs: { explain?: string; optimize?: unknown }[] = [];
    await page.route("https://challenges.cloudflare.com/turnstile/**", (route) => route.fulfill({
      contentType: "application/javascript",
      body: `window.turnstile = { render(container, options) {
        const button = document.createElement("button"); button.textContent = "Verify fixture";
        button.onclick = () => options.callback("interactive-token"); container.append(button);
        return "widget";
      }, remove() { document.querySelectorAll(".visit-gate button").forEach(button => button.remove()); } };`,
    }));
    await page.route("**/v1/visit-token", async (route) => {
        if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
      check++;
      return route.fulfill({ headers: cors, contentType: "application/json", body: JSON.stringify({ token: "visit", expires_at: Math.floor(await page.evaluate(() => Date.now()) / 1000) + 1800 }) });
    });
    await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) => {
      vocabularyRequests++;
      return route.fulfill({ headers: cors, contentType: "application/json", body: vocabulary });
    });
    await page.route("**/v1/decide", (route) => { if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors }); initialRequests++; specs.push(route.request().postDataJSON()); return route.fulfill({ headers: cors, contentType: "application/json", body: answer }); });
    await page.goto("/decide.html?demo=1");
    await expect(page.locator(".board-answer").getByRole("button", { name: "Verify fixture" })).toBeVisible();
    await expect(page.getByText("One quick check keeps this free")).toBeVisible();
    await expect(page.getByText("For example: require open weights, prefer lower cost, and see which models fit.")).toBeVisible();
    await expect(page.getByLabel("Facet board answer")).toHaveCount(0);
    expect(initialRequests).toBe(0);
    expect(vocabularyRequests).toBe(0);
    expect(check).toBe(0);
    await page.getByRole("button", { name: "Verify fixture" }).click();
    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    await expect(page.getByText("One quick check keeps this free")).toHaveCount(0);
    await expect.poll(() => initialRequests).toBe(3);
    expect(specs.filter((spec) => spec.explain === "summary")).toHaveLength(1);
    expect(specs[0].optimize).toEqual({ weights: { chat_preference: 0.6, "-offering.cost_per_task": 0.4 } });
    await expect(page.locator(".template-active")).toHaveText("Starting from: General assistant, balancedClear");
    await page.route("**/v1/decide", async (route) => {
      if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: cors });
      if (check === 1) return route.fulfill({ status: 401, headers: cors, contentType: "application/json", body: JSON.stringify({ error: { code: "visit_token_expired" } }) });
      return route.fulfill({ headers: cors, contentType: "application/json", body: answer });
    });
    const capabilities = page.getByRole("button", { name: /What it.s good at/ });
    if (await capabilities.getAttribute("aria-expanded") !== "true") await capabilities.click();
    await page.locator('[data-facet="capability.software_engineering"]').getByLabel("Prefer", { exact: true }).check();
    const widget = page.locator("#facet-board-answer").getByRole("button", { name: "Verify fixture" });
    await expect(widget).toBeVisible();
    await page.clock.install();
    await page.clock.fastForward(60_000);
    await widget.click();
    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    expect(check).toBe(2);
  });
});
