import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Local development proxies. `/api` is the static export (the decide page reads
// /api/decision/vocabulary.json from it); `/v1` is the decision API. Set
// VITE_DECIDE_ENDPOINT=/v1/decide so the page calls through the proxy instead
// of api.modelspec.dev, whose CORS allows only the deployed origins.
const exportOrigin = process.env.EXPORT_ORIGIN ?? "http://localhost:8000";
const decideOrigin = process.env.DECIDE_API_ORIGIN ?? "https://api.modelspec.dev";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
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
