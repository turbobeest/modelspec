import { defineConfig } from "@playwright/test";

// MODEL-203. The built decide page (`npm run build`, served by `vite preview`)
// over the spec corpus, with the vocabulary and /v1/decide stubbed
// (corpus.spec.ts), plus automatic and manual flows (decide.spec.ts); or a
// deployed page with nothing stubbed (live.spec.ts) when
// MODELSPEC_DECIDE_URL names it. Python's http.server resets connections under
// four parallel browsers, so it does not serve this run.
const url = process.env.MODELSPEC_DECIDE_URL;
const preview = "http://127.0.0.1:4173/decide.html";

export default defineConfig({
  testDir: "./browser-tests",
  testMatch: url ? /live\.spec\.ts$/ : /(?:corpus|decide)\.spec\.ts$/,
  timeout: 30000,
  fullyParallel: true,
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI ? [["github"], ["list"]] : "list",
  use: {
    baseURL: url ?? preview,
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
    trace: "retain-on-failure",
  },
  webServer: url
    ? undefined
    : {
        command: "npx vite preview --host 127.0.0.1 --port 4173 --strictPort",
        url: preview,
        reuseExistingServer: !process.env.CI,
      },
  outputDir: process.env.MODELSPEC_BROWSER_OUTPUT || "test-results",
});
