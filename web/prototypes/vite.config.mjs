import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import base from "../vite.config.ts";
import { prototypeFixtures } from "./fixture-server.mjs";

export default defineConfig({
  ...base,
  root: fileURLToPath(new URL("../", import.meta.url)),
  define: {
    ...base.define,
    "import.meta.env.VITE_DECIDE_ENDPOINT": JSON.stringify("/v1/decide"),
    "import.meta.env.VITE_VOCABULARY_URL": JSON.stringify("/v1/vocabulary"),
    "import.meta.env.VITE_HUMAN_GATE_ENABLED": JSON.stringify("false"),
    "import.meta.env.VITE_VISIT_GATE_ENABLED": JSON.stringify("false"),
  },
  plugins: [...base.plugins, prototypeFixtures()],
  server: { ...base.server, host: "127.0.0.1", proxy: {} },
  build: {
    outDir: "../.scratch/proto/build",
    rolldownOptions: { input: {
      a: "prototypes/proto-a.html", b: "prototypes/proto-b.html", c: "prototypes/proto-c.html",
    } },
  },
});
