import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./browser-tests",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:5173",
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1",
    url: "http://127.0.0.1:5173/decide.html",
    reuseExistingServer: true,
  },
  outputDir: process.env.MODELSPEC_BROWSER_OUTPUT || "test-results",
});
