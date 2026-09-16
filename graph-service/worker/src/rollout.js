// Rolling the graph container onto a newly deployed version (MODEL-9 part 2).
// No imports, so tests can run it under plain node.
//
// `wrangler deploy` replaces the Worker and the Durable Object code, but a
// container instance that is already running survives: it keeps serving the
// previous image until it stops. `sleepAfter` is 15m and the deploy's own smoke
// test polls /graph/health every 10s, so the instance never goes idle and the
// just-deployed image is never exercised. The Durable Object therefore has to
// roll the container itself, exactly once per deployed version.
//
// The version marker is `BUILD_COMMIT`, injected by the deploy
// (`wrangler deploy --var BUILD_COMMIT:$GITHUB_SHA`) and handed to the container
// as an env var at start. The container echoes it back as `service_commit`.
// That is the only field that proves which *image* answered: the manifest's
// `build_commit` only proves which *export* was loaded, and a stale container
// that restarts for any other reason reloads `latest` and reports the new
// `build_commit` while still running old code. That is how #77, #78 and #79
// shipped without ever being exercised.

// Durable Object storage key holding the BUILD_COMMIT we last rolled for.
// Distinct from the library's own keys (`__CF_CONTAINER_STATE`,
// `OUTBOUND_CONFIGURATION` in @cloudflare/containers 0.3.7).
export const ROLLED_KEY = "ROLLED_FOR_BUILD";

/**
 * Destroy a container left over from an earlier deployed version.
 *
 * At most one roll per BUILD_COMMIT: the marker is written *before* the
 * container is destroyed, so a container that starts and then fails to load its
 * export is never killed again on the next request. There is no restart loop;
 * that failure stays visible as `export_not_loaded` on /graph/health.
 *
 * @param {object}   a
 * @param {{get: (k: string) => unknown, put: (k: string, v: unknown) => void}} a.kv
 *        Durable Object KV storage (`ctx.storage.kv`, synchronous).
 * @param {{running: boolean, destroy: () => Promise<void>}} a.container
 *        `ctx.container`. `destroy()` sends SIGKILL; the next request starts a
 *        fresh instance, which picks up the current envVars and image.
 * @param {string|undefined} a.want  env.BUILD_COMMIT.
 * @param {(message: string) => void} [a.log]
 * @returns {Promise<"unversioned"|"current"|"fresh"|"rolled">}
 */
export async function rollStaleContainer({ kv, container, want, log }) {
  if (!want) return "unversioned"; // local dev with no BUILD_COMMIT: never roll.
  if (kv.get(ROLLED_KEY) === want) return "current";
  kv.put(ROLLED_KEY, want);
  if (!container || !container.running) return "fresh";
  log?.(`rolling container onto build ${want}`);
  await container.destroy();
  return "rolled";
}

/**
 * Gate a /graph/health body on the version of the container that answered.
 *
 * Returns null when the answer came from the deployed version (pass the
 * upstream response through unchanged, including its own `export_not_loaded`
 * diagnosis), or the body of a 503 that says the instance is still the old one.
 * That keeps "wrong version, rolling" and "right version, failed to load"
 * apart: the first is `version_rolling`, the second is `export_not_loaded`.
 *
 * An unparseable body counts as a mismatch: an answer we cannot read is not
 * proof of a fresh instance.
 *
 * @param {unknown} body  the parsed upstream body, or null.
 * @param {string|undefined} want  env.BUILD_COMMIT.
 */
export function staleHealth(body, want) {
  if (!want) return null;
  const got = body && typeof body === "object" ? body.service_commit ?? null : null;
  if (got === want) return null;
  return {
    status: "rolling",
    error: "version_rolling",
    expected_service_commit: want,
    service_commit: got,
  };
}
