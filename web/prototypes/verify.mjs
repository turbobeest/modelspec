import assert from "node:assert/strict";
import { chromium } from "playwright";
import { expect } from "@playwright/test";

const origin = process.env.PROTO_ORIGIN ?? "http://127.0.0.1:5197";
const browser = await chromium.launch();
try {
  for (const variant of ["a", "b", "c"]) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("**/*", (route) => new URL(route.request().url()).origin === origin
      ? route.continue() : route.abort());
    await page.goto(`${origin}/prototypes/proto-${variant}.html`);
    assert.equal(await page.getByRole("heading", { name: "Which AI model fits your job?", exact: true }).count(), 1,
      `Variant ${variant.toUpperCase()} must offer the first-visit decision page`);
    await page.evaluate(() => document.fonts.ready);
    await expect(page.getByText(/No paid placement\. Sourced\./)).toBeVisible();
    if (variant === "a") {
      await expect(page.getByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
      assert.equal(await page.locator(".proto-shortlist li").count(), 6);
      assert.equal(await page.locator("input, textarea, select").count(), 0);
      assert.equal(await page.evaluate(() => document.documentElement.scrollHeight <= 844), true, "A must fit one mobile screen");
      await page.getByRole("button", { name: "Cheapest", exact: true }).click();
      await expect(page.locator(".proto-answer[aria-busy=true]")).toHaveCount(0);
      const budgetLink = await page.getByRole("link", { name: /See the full evidence/ }).getAttribute("href");
      assert.match(budgetLink, /^\/decide\/#s=/);
      const board = JSON.parse(decodeURIComponent(atob(budgetLink.split("#s=")[1])));
      assert.equal(board.board.selections["offering.cost_per_task"].value, 0.05);
      await page.getByRole("button", { name: /Use this from your agent/ }).click();
      await expect(page.getByText("Human lookup is free. CLI, API and MCP use requires an API key.")).toBeVisible();
      await page.getByRole("button", { name: "Spec", exact: true }).click();
      const spec = JSON.parse(await page.getByLabel("Spec snippet").textContent());
      assert.ok(spec.where.includes("offering.cost_per_task <= 0.05"));
    }
    if (variant === "b") {
      await page.getByRole("button", { name: /Coding/ }).focus();
      await page.keyboard.press("Enter");
      await expect(page.getByRole("heading", { name: "What matters most?" })).toBeFocused();
      await page.getByRole("button", { name: /Balance cost and quality/ }).click();
      await expect(page.getByRole("heading", { name: "Any hard limit?" })).toBeFocused();
      await page.getByRole("button", { name: /Must be open weights/ }).click();
      await page.getByRole("button", { name: /Show my options/ }).click();
      await expect(page.locator("[data-decision-id]")).toBeVisible();
      await page.getByRole("button", { name: /Back/ }).click();
      await expect(page.getByRole("button", { name: /Must be open weights/ })).toHaveAttribute("aria-pressed", "true");
    }
    if (variant === "c") {
      await expect(page.locator(".board-ranked-answer")).toBeVisible();
      for (const label of ["Refine", "Evidence", "For your agent"]) {
        const summary = page.locator("summary", { hasText: label });
        await summary.focus();
        await page.keyboard.press("Enter");
        await expect(summary.locator("..")).toHaveAttribute("open", "");
        await page.keyboard.press("Enter");
        await expect(summary.locator("..")).not.toHaveAttribute("open", "");
      }
    }
    await page.getByRole("button", { name: "Light mode" }).click();
    await expect(page.locator(".proto")).toHaveAttribute("data-theme", "light");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, "No mobile horizontal overflow");
    assert.deepEqual(errors, []);
    await page.close();
  }
  console.log("PASS: A mobile fold, honest six-way tie, budget spec, keyed agent handoff; B keyboard flow and back state; C native expanders; all themes, no overflow or runtime errors");
} finally {
  await browser.close();
}
