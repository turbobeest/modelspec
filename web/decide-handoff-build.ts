import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export function handoffDefines() {
  return {
    __DECIDE_HANDOFF__: execFileSync(
      process.env.MODELSPEC_PYTHON ?? "python",
      ["-m", "pipeline.decide_handoff"],
      { cwd: fileURLToPath(new URL("../", import.meta.url)), encoding: "utf8" },
    ).trim(),
  };
}
