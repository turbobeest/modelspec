import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// The handoff's reference engine, kept verbatim in docs/, is imported by the
// parity test so the TypeScript port can be checked against it.
const handoff = fileURLToPath(
  new URL(
    "../docs/design/handoff/core-flow/modelspec-data.js",
    import.meta.url,
  ),
);

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@handoff/modelspec-data": handoff } },
  server: { fs: { allow: [".."] } },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/decide/__tests__/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
