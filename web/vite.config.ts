import { defineConfig } from "vite";
import type { Plugin, PreviewServer, ViteDevServer } from "vite";
import { readFile } from "node:fs/promises";
import { basename } from "node:path";
import type { IncomingMessage } from "node:http";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { handoffDefines } from "./decide-handoff-build";

// Local development proxies. `/api` is the static export (the decide page reads
// /api/decision/vocabulary.json from it); `/v1` is the decision API. Set
// VITE_DECIDE_ENDPOINT=/v1/decide so the page calls through the proxy instead
// of api.modelspec.dev, whose CORS allows only the deployed origins.
const exportOrigin = process.env.EXPORT_ORIGIN ?? "http://localhost:8000";
const decideOrigin = process.env.DECIDE_API_ORIGIN ?? "https://api.modelspec.dev";
// Your own key, from the environment only: the /v1 proxy sends it, since machine
// access is keyed. Only the page itself (same-origin) or a local non-browser
// client gets it, so another site open in the browser cannot spend it through
// the proxy. Vite's allowedHosts check already refuses DNS-rebound hosts.
const apiKey = process.env.MODELSPEC_API_KEY;
const mayUseKey = (req: IncomingMessage) => {
  const site = req.headers["sec-fetch-site"];
  if (site !== undefined) return site === "same-origin";
  return req.headers.origin === undefined;
};

// The deployed page shares /fonts/ with the landing page (pipeline/build.py
// copies site/fonts there). In development and in `vite preview`, which the
// browser suite measures (MODEL-325's fold checks), serve the same files from
// the repo so the page sets in its real type, not a fallback.
const serveFonts = (server: ViteDevServer | PreviewServer) => {
  server.middlewares.use("/fonts", (req, res, next) => {
    const name = basename((req.url ?? "").split("?")[0]);
    if (!name.endsWith(".woff2")) return next();
    readFile(new URL(`../site/fonts/${name}`, import.meta.url))
      .then((body) => { res.setHeader("content-type", "font/woff2"); res.end(body); })
      .catch(() => next());
  });
};
const siteFonts = (): Plugin => ({
  name: "modelspec-site-fonts",
  configureServer: serveFonts,
  configurePreviewServer: serveFonts,
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
      "/v1": {
        target: decideOrigin,
        changeOrigin: true,
        configure: (proxy) => {
          if (!apiKey) return;
          proxy.on("proxyReq", (proxyReq, req) => {
            if (mayUseKey(req)) proxyReq.setHeader("authorization", `Bearer ${apiKey}`);
            else proxyReq.removeHeader("authorization");
          });
        },
      },
    },
  },
});
