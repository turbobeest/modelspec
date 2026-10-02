import { expect } from "@playwright/test";
import { test } from "./human-gate-fixtures";
import { readFileSync } from "node:fs";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/vocabulary.json", import.meta.url), "utf8");
const decision = readFileSync(new URL("../src/decide/__fixtures__/live-empty-board-full.json", import.meta.url), "utf8");

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
    body: decision,
  }));
});

async function openBoard(page: import("@playwright/test").Page) {
  await page.goto("/decide.html?demo=1");
  await expect(
    page.getByRole("heading", { name: "Set what matters. Watch the field narrow." }),
  ).toBeVisible();
  await expect(page.locator("textarea")).toHaveCount(0);
}

test("the public decision page opens on the facet board", async ({ page }) => {
  await openBoard(page);
  await expect(page.getByRole("region", { name: "Trade-off canvas" })).toBeVisible();
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
  await expect(page.getByRole("button", { name: "Share or act" })).toBeVisible();
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
  const trigger = page.getByRole("button", { name: "Share or act" });
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

test("the board and its explanation fit a 320px viewport in light and dark mode", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await openBoard(page);
  const scrollWidth = () => page.evaluate(() => document.documentElement.scrollWidth);
  await expect.poll(scrollWidth).toBeLessThanOrEqual(320);
  await page.getByRole("button", { name: /Start from a template/ }).click();
  await page.locator(".board-templates button").nth(1).click();
  await expect(page.locator(".why-panel .contribution").first()).toBeVisible();
  for (const buttonName of ["Light mode", "Dark mode"]) {
    await page.getByRole("button", { name: buttonName }).click();
    await expect.poll(scrollWidth).toBeLessThanOrEqual(320);
  }
});

test.describe("the Worker gate is enabled", () => {
  test.use({ humanStatus: { enabled: true, remaining: 20 } });
  test.skip(process.env.VITE_HUMAN_GATE_ENABLED !== "true", "requires the gated page build");

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
    await page.getByRole("button", { name: "Share or act" }).click();
    await page.getByRole("dialog").getByRole("tab", { name: "Procurement review" }).click();
    await expect(page.getByRole("dialog").getByRole("button", { name: /CSV/ })).toHaveCount(0);
  });
});
