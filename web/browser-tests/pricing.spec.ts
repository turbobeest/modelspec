import { expect, test } from "@playwright/test";

const pricingUrl = process.env.MODELSPEC_PRICING_URL;
test.skip(!pricingUrl, "Set MODELSPEC_PRICING_URL to the assembled live /pricing/ URL");

for (const width of [1440, 390]) {
  test(`pricing is responsive and interactive at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto(pricingUrl!);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width);
    const before = await page.locator("[data-best-cost]").textContent();
    await page.getByRole("button", { name: "10,000", exact: true }).first().click();
    await expect(page.locator("[data-credits]")).toContainText("300,000 credits");
    await expect(page.locator("[data-best-cost]")).not.toHaveText(before || "");
    const forms = page.locator(`form[action="https://api.modelspec.dev/v1/billing/checkout"]`);
    await expect(forms).toHaveCount(0);
    await expect(page.getByText("Or let your agents pay as they go")).toHaveCount(0);
    await expect(page.getByText("Pay per call (x402)")).toHaveCount(0);
    if (process.env.MODELSPEC_SCREENSHOT_DIR) {
      await page.screenshot({
        path: `${process.env.MODELSPEC_SCREENSHOT_DIR}/pricing-${width}.png`,
        fullPage: true,
      });
    }
  });
}
