import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/vocabulary.json", import.meta.url), "utf8");
const decision = readFileSync(new URL("../src/decide/__fixtures__/live-empty-board-full.json", import.meta.url), "utf8");

test.beforeEach(async ({ page }) => {
  await page.route("**/api/decision/vocabulary.json", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
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
  const trigger = page.getByRole("button", { name: "Share or act" });
  await trigger.click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Copy", exact: true }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain("#s=");
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
});

test("the board fits a 390px viewport in light and dark mode", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openBoard(page);
  for (const buttonName of ["Dark mode", "Light mode"]) {
    await page.getByRole("button", { name: buttonName }).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  }
});
