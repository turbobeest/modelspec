// A 400 from /v1/decide lists `issues`, each with the spec path it concerns.
// Place each beside the control that produced it, in plain language.
import type { SpecIssue } from "../adapter/hosted";

export type IssueTarget =
  | { kind: "condition"; index: number }
  | { kind: "weights" }
  | { kind: "tokens" }
  | { kind: "spec" };

export interface PlacedIssue {
  target: IssueTarget;
  text: string;
}

const quoted = (list: string) =>
  list
    .split(/,\s*/)
    .map((item) => `“${item.replaceAll("'", "")}”`)
    .join(" or ");

/** The engine's reason, as a sentence a person can act on. */
export function plainIssue(issue: SpecIssue): string {
  const reason = issue.reason.trim();
  const unknown = /^unknown facet '([^']+)'(?:.*?; did you mean (.+?)\?)?/.exec(reason);
  if (unknown)
    return (
      `The engine does not know “${unknown[1]}”, so it cannot ${issue.path.startsWith("optimize") ? "rank on it" : "check this condition"}` +
      (unknown[2] ? `. Did you mean ${quoted(unknown[2])}?` : ".")
    );
  if (/which has no order/.test(reason))
    return "This can only be matched with “is” or a list of values, not with at least or at most.";
  if (/evidence qualifiers are only valid on evidence facets/.test(reason))
    return "“Independent only” applies to benchmark results, not to this condition.";
  if (reason === "not a spec field")
    return `The engine does not accept “${issue.path}” in a spec.`;
  if (reason === "required") return `“${issue.path}” is required.`;
  if (/free-text task/.test(reason))
    return "Free text is not sent to the engine yet; the conditions below are.";
  const sentence = reason.charAt(0).toUpperCase() + reason.slice(1);
  return /[.?!]$/.test(sentence) ? sentence : sentence + ".";
}

export function targetOf(path: string): IssueTarget {
  const where = /^where\[(\d+)\]/.exec(path);
  if (where) return { kind: "condition", index: Number(where[1]) };
  if (path.startsWith("optimize")) return { kind: "weights" };
  if (path.startsWith("task_tokens")) return { kind: "tokens" };
  return { kind: "spec" };
}

export function placeIssues(issues: readonly SpecIssue[]): PlacedIssue[] {
  return issues.map((issue) => ({ target: targetOf(issue.path), text: plainIssue(issue) }));
}

export function issuesFor(
  placed: readonly PlacedIssue[],
  target: IssueTarget,
): string[] {
  return placed
    .filter(
      (issue) =>
        issue.target.kind === target.kind &&
        (issue.target.kind !== "condition" ||
          (target.kind === "condition" && issue.target.index === target.index)),
    )
    .map((issue) => issue.text);
}
