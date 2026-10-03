import { expect, test as base } from "@playwright/test";

type HumanStatus = { enabled: false } | { enabled: true; remaining: number }
  | { enabled: true; mode: "visit"; day_limit: number; burst_limit: number };

export const test = base.extend<{ humanStatus: HumanStatus }>({
  humanStatus: [{ enabled: false }, { option: true }],
  page: async ({ page, humanStatus }, runPage) => {
    // The gate renders Turnstile only when the page was built with a site key;
    // without one it fails closed and no answer appears. deploy-sites.yml sets
    // it for the build and the test run alike.
    if (humanStatus.enabled)
      expect(process.env.VITE_TURNSTILE_SITE_KEY, "build and test the gated page with VITE_TURNSTILE_SITE_KEY set, as deploy-sites.yml does").toBeTruthy();
    await page.route("**/v1/human-status", (route) => route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "access-control-allow-origin": "*" },
      body: JSON.stringify(humanStatus),
    }));
    const turnstileRequests: string[] = [];
    await page.route("https://challenges.cloudflare.com/**", (route) => {
      turnstileRequests.push(route.request().url());
      return route.abort();
    });
    await runPage(page);
    if (!humanStatus.enabled) {
      expect(turnstileRequests, "a disabled Worker must never load Turnstile").toEqual([]);
    }
  },
});
