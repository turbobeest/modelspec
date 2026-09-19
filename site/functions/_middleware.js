// Markdown content negotiation for Cloudflare Pages Functions.
// Copied to <output>/functions/_middleware.js. The live deploy also ships
// <output>/_worker.js because wrangler pages deploy looks for functions/
// in cwd, and the deploy job has only the dist artifact.
//
// Serve the page's index.md twin when Accept includes text/markdown
// (https://blog.cloudflare.com/markdown-for-agents/).

const SKIP_EXT =
  /\.(json|xml|txt|png|jpe?g|gif|svg|webp|ico|css|js|mjs|woff2?|ya?ml|map|html)$/i;

export function wantsMarkdown(accept) {
  if (!accept) return false;
  for (const part of accept.split(",")) {
    const bits = part.trim().split(";").map((s) => s.trim());
    if ((bits[0] || "").toLowerCase() !== "text/markdown") continue;
    let q = 1;
    for (const p of bits.slice(1)) {
      if (p.toLowerCase().startsWith("q=")) q = Number(p.slice(2));
    }
    if (q > 0) return true;
  }
  return false;
}

export function markdownAssetPath(pathname) {
  if (!pathname || pathname.includes("..")) return null;
  let path = pathname.split("?")[0].split("#")[0];
  if (path.startsWith("/api/") || path === "/api") return null;
  if (path.startsWith("/fonts/") || path.startsWith("/.well-known/")) return null;
  if (path.endsWith(".md")) return path;
  if (SKIP_EXT.test(path)) return null;
  if (path === "/" || path === "") return "/index.md";
  if (path.endsWith("/")) return `${path}index.md`;
  return `${path}/index.md`;
}

export async function onRequest(context) {
  const { request, next, env } = context;
  if (!wantsMarkdown(request.headers.get("Accept") || "")) {
    return next();
  }
  const url = new URL(request.url);
  const mdPath = markdownAssetPath(url.pathname);
  if (!mdPath) return next();
  const asset = await env.ASSETS.fetch(new URL(mdPath, url.origin));
  if (!asset.ok) return next();
  const headers = new Headers(asset.headers);
  headers.set("content-type", "text/markdown; charset=utf-8");
  headers.set("vary", "Accept");
  return new Response(asset.body, { status: 200, headers });
}
