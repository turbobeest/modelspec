import { expect, test as base } from "@playwright/test";

type HumanStatus = { enabled: false } | { enabled: true; remaining: number }
  | { enabled: true; mode: "visit"; day_limit: number; burst_limit: number };

export const test = base.extend<{ humanStatus: HumanStatus }>({
  humanStatus: [{ enabled: false }, { option: true }],
  page: async ({ page, humanStatus }, runPage) => {
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
