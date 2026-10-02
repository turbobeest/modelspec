import { expect, test, type Page } from "@playwright/test";
import { z } from "zod";

// MODEL-203: the deployed decide page answers, against the live vocabulary and
// api.modelspec.dev, or shows the manual gate when the Worker enables it,
// with nothing stubbed. Run after each deploy with
// MODELSPEC_DECIDE_URL set to the page (playwright.corpus.config.ts).

const humanStatusSchema = z.discriminatedUnion("enabled", [
  z.object({ enabled: z.literal(false) }),
  z.object({ enabled: z.literal(true), remaining: z.number().int().min(0).max(20) }),
]);

async function answered(page: Page) {
  const answer = page.getByLabel("Facet board answer");
  await expect(answer).toBeVisible({ timeout: 45000 });
  await expect(page.getByText(/invalid_response|Decision unavailable/)).toHaveCount(0);
  await expect(page.locator(".board-routes").first()).toBeVisible();
}

test("the deployed page follows the Worker's human gate status", async ({ page }) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("");
  await expect(page.getByRole("heading", { name: "Set what matters. Watch the field narrow." })).toBeVisible({ timeout: 30000 });
  // Fetch in the browser so the deployed origin and visitor match the page's
  // status request, including the Worker's CORS policy.
  const response = await page.evaluate(async () => {
    const status = await fetch("https://api.modelspec.dev/v1/human-status", { mode: "cors" });
    return { status: status.status, body: await status.json() };
  });
  expect(response.status, "human-status endpoint").toBe(200);
  const status = humanStatusSchema.parse(response.body);
  const gate = page.getByRole("region", { name: "Manual lookups" });
  if (status.enabled) {
    await expect(gate).toBeVisible();
    await expect(gate.getByRole("button", { name: "Look up this decision" })).toBeVisible();
    await expect(gate.getByRole("link", { name: "paid API or MCP" })).toBeVisible();
    await expect(gate.getByRole("status")).toBeVisible();
    await expect(page.getByLabel("Facet board answer")).toHaveCount(0);
  } else {
    await expect(gate).toHaveCount(0);
    await answered(page);

    // The template card starts collapsed (MODEL-277); it is absent only when no template is available.
    const bar = page.getByRole("button", { name: /Start from a template/ });
    if ((await bar.count()) > 0) {
      await bar.click();
      await page.locator(".board-templates button").first().click();
      await answered(page);
    }
  }
  expect(errors, "uncaught page errors").toEqual([]);
});
