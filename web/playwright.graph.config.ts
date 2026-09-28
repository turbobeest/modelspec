import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./browser-tests",
  testMatch: "graph.spec.ts",
  timeout: 45_000,
  use: {
    baseURL: process.env.MODELSPEC_GRAPH_BASE_URL ?? "http://127.0.0.1:8000",
    browserName: "chromium",
    reducedMotion: "reduce",
    viewport: { width: 1440, height: 1000 },
    launchOptions: { args: ["--use-angle=swiftshader"] },
  },
  outputDir: process.env.MODELSPEC_BROWSER_OUTPUT ?? "test-results-graph",
});
