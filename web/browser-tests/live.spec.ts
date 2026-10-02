import { expect, test, type Page } from "@playwright/test";

// MODEL-203: the deployed decide page answers, against the live vocabulary and
// api.modelspec.dev, with nothing stubbed. Run after each deploy with
// MODELSPEC_DECIDE_URL set to the page (playwright.corpus.config.ts).

async function answered(page: Page) {
  const answer = page.getByLabel("Facet board answer");
  await expect(answer).toBeVisible({ timeout: 45000 });
  await expect(page.getByText(/invalid_response|Decision unavailable/)).toHaveCount(0);
  await expect(page.locator(".board-routes").first()).toBeVisible();
}

test("the deployed page draws a decision, and another after a template", async ({ page }) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("");
  await expect(page.getByRole("heading", { name: "Set what matters. Watch the field narrow." })).toBeVisible({ timeout: 30000 });
  await answered(page);

  // The template card starts collapsed (MODEL-277); it is absent only when no template is available.
  const bar = page.getByRole("button", { name: /Start from a template/ });
  if ((await bar.count()) > 0) {
    await bar.click();
    await page.locator(".board-templates button").first().click();
    await answered(page);
  }
  expect(errors, "uncaught page errors").toEqual([]);
});
