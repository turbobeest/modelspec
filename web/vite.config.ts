import { defineConfig } from "vite";
import type { Plugin } from "vite";
import { readFile } from "node:fs/promises";
import { basename } from "node:path";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { handoffDefines } from "./decide-handoff-build";

// Local development proxies. `/api` is the static export (the decide page reads
// /api/decision/vocabulary.json from it); `/v1` is the decision API. Set
// VITE_DECIDE_ENDPOINT=/v1/decide so the page calls through the proxy instead
// of api.modelspec.dev, whose CORS allows only the deployed origins.
const exportOrigin = process.env.EXPORT_ORIGIN ?? "http://localhost:8000";
const decideOrigin = process.env.DECIDE_API_ORIGIN ?? "https://api.modelspec.dev";

// The deployed page shares /fonts/ with the landing page (pipeline/build.py
// copies site/fonts there). In development, serve the same files from the repo.
const siteFonts = (): Plugin => ({
  name: "modelspec-site-fonts",
  configureServer(server) {
    server.middlewares.use("/fonts", (req, res, next) => {
      const name = basename((req.url ?? "").split("?")[0]);
      if (!name.endsWith(".woff2")) return next();
      readFile(new URL(`../site/fonts/${name}`, import.meta.url))
        .then((body) => { res.setHeader("content-type", "font/woff2"); res.end(body); })
        .catch(() => next());
    });
  },
});

// https://vite.dev/config/
export default defineConfig({
  define: handoffDefines(),
  plugins: [react(), tailwindcss(), siteFonts()],
  build: {
    rolldownOptions: { input: { main: "index.html", decide: "decide.html" } },
  },
  server: {
    fs: { allow: [".."] },
    proxy: {
      "/api": { target: exportOrigin, changeOrigin: true },
      "/v1": { target: decideOrigin, changeOrigin: true },
    },
  },
});
