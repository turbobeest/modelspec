import { money } from "../engine/reference";
import type {
  AccessKind,
  Decision,
  EstateMark,
  MayQualify,
  OfferingRef,
  PlanRoute,
  Result,
} from "../adapter/contract";
import type { VocabPlan, Vocabulary } from "../vocabulary";

/**
 * How a model is paid for and reached (MODEL-202). Every figure here is read
 * from the engine's answer; this module only names routes and words them.
 * No route is ever called "API": a plan, pay per use, or running it yourself.
 */

export type AccessAnswer = AccessKind | "any";

export const ACCESS_ANSWERS: readonly { id: AccessAnswer; label: string; hint: string }[] = [
  { id: "chat_app", label: "In a chat app", hint: "A provider's own chat app, paid by a monthly plan." },
  { id: "coding_tool", label: "In a coding tool", hint: "A monthly plan that covers the tool, or pay per use." },
  { id: "own_software", label: "From my own software or agent", hint: "Your code calls the model and pays per use." },
  { id: "own_hardware", label: "On my own hardware", hint: "Download the open weights and run them yourself." },
  { id: "any", label: "Doesn't matter", hint: "Every route counts; the cheapest one is named." },
];

export const COST_HEADING: Readonly<Record<AccessAnswer, string>> = {
  chat_app: "Monthly plan",
  coding_tool: "Pay per use",
  own_software: "Cost per task",
  own_hardware: "Fit",
  any: "Cheapest route",
};

export const accessAnswer = (access: AccessKind | undefined): AccessAnswer => access ?? "any";

export type RouteKind = "plan" | "pay_per_use" | "self_hosted";

export interface RouteView {
  key: string;
  kind: RouteKind;
  /** "Anthropic · pay per use", "Claude Max 20x · monthly plan", "Run it yourself". */
  name: string;
  /** The one-line explanation behind the name. */
  explain: string;
  figure: string;
  /** For a plan in a coding tool: where it pays for itself, or why that isn't known. */
  note?: string;
  /** The cost column's figure, when it differs from `figure`. */
  column?: string;
}

export interface RouteContext {
  vocabulary: Pick<Vocabulary, "providers" | "models" | "estate">;
}

const CHAT_SURFACES = new Set(["chat_app", "desktop_app", "mobile_app"]);
const UPPER_WORDS = new Set(["cli", "ide", "ai"]);

/**
 * Who you pay, as a route names them. The registry's display names often end
 * in "API" ("Anthropic API"); a route never says it, so the word is dropped.
 */
export const payee = (displayName: string): string =>
  displayName.replace(/\bAPI\b/g, "").replace(/\s{2,}/g, " ").replace(/\s+\)/g, ")").trim() || displayName;

export const providerName = (ctx: RouteContext, id: string): string =>
  payee(ctx.vocabulary.providers[id] ?? id);

const modelName = (ctx: RouteContext, id: string): string =>
  ctx.vocabulary.models[id]?.display_name ?? id;

function harnessName(id: string): string {
  return id.split("-").map((word) =>
    UPPER_WORDS.has(word) ? word.toUpperCase() : word.charAt(0).toUpperCase() + word.slice(1),
  ).join(" ");
}

function joinWords(words: readonly string[], conjunction = "and"): string {
  if (words.length <= 1) return words[0] ?? "";
  return `${words.slice(0, -1).join(", ")} ${conjunction} ${words[words.length - 1]}`;
}

/** Where a plan works, in words: "chat apps and Claude Code". */
export function surfacePhrase(surfaces: readonly string[]): string {
  const words: string[] = [];
  const add = (word: string) => { if (!words.includes(word)) words.push(word); };
  for (const surface of [...surfaces].sort()) {
    if (CHAT_SURFACES.has(surface)) add("chat apps");
    else if (surface === "api") add("your own software");
    else if (surface === "coding_tool") add("coding tools");
    else if (surface.startsWith("coding_tool:")) add(harnessName(surface.slice("coding_tool:".length)));
    else add(surface.replaceAll("_", " "));
  }
  const own = words.indexOf("your own software");
  if (own >= 0) words.push(...words.splice(own, 1));
  return joinWords(words);
}

export function planRecord(ctx: RouteContext, id: string): VocabPlan | undefined {
  return ctx.vocabulary.estate.plans.find((plan) => plan.id === id);
}

/** A plan as the board names it: its own name, never with "API" in it. */
export const planName = (name: string): string => payee(name);

function planExplain(surfaces: readonly string[] | null | undefined): string {
  if (!surfaces) return "A flat fee each month. Where it works isn't verified yet.";
  const ownSoftware = surfaces.includes("api");
  return `A flat fee each month. Works in ${surfacePhrase(surfaces)}${ownSoftware ? "" : "; not your own software"}.`;
}

/** Plans of `provider` known not to serve your own software. */
function plansNotForOwnSoftware(ctx: RouteContext, provider: string): VocabPlan[] {
  return ctx.vocabulary.estate.plans.filter((plan) =>
    plan.provider === provider && Array.isArray(plan.surfaces) && !plan.surfaces.includes("api"),
  );
}

function payPerUseExplain(ctx: RouteContext, offering: OfferingRef): string {
  const provider = offering.provider ?? "";
  const excluded = plansNotForOwnSoftware(ctx, provider).map((plan) => planName(plan.name));
  const base = `Billed per call by ${providerName(ctx, provider)}: what your software, or a tool using your own key, pays for ${modelName(ctx, offering.model)}.`;
  return excluded.length ? `${base} Not covered by ${joinWords(excluded, "or")}.` : base;
}

const SELF_HOSTED_EXPLAIN =
  "Download the open weights and run them on hardware you control; no per-task fee.";

const wholeDollars = (amount: number): string =>
  Number.isInteger(amount) ? `$${amount.toLocaleString("en-US")}` : money(amount);

const approx = (value: number): string =>
  Math.round(value).toLocaleString("en-US");

function breakEvenNote(route: PlanRoute): string {
  const tasks = route.break_even_tasks_per_month;
  if (tasks === null || tasks === undefined) return route.basis;
  const allowance = route.allowance?.tokens != null
    ? `its allowance is ${route.allowance.tokens.toLocaleString("en-US")} tokens${route.allowance.window ? ` per ${route.allowance.window.replaceAll("_", " ")}` : ""}`
    : "not published";
  return `${planName(route.name)} costs less than pay per use above ~${approx(tasks)} tasks a month, if its allowance covers your volume (${allowance}).`;
}

export function planRouteView(ctx: RouteContext, route: PlanRoute, access: AccessAnswer): RouteView {
  const record = planRecord(ctx, route.plan);
  const period = route.price?.period === "annual" ? "annual plan" : "monthly plan";
  return {
    key: `plan:${route.plan}`,
    kind: "plan",
    name: `${planName(route.name)} · ${period}`,
    explain: planExplain(record?.surfaces),
    figure: route.price_monthly_usd == null
      ? "price not published"
      : `${wholeDollars(route.price_monthly_usd)} a month`,
    ...(access === "coding_tool" ? { note: breakEvenNote(route) } : {}),
  };
}

function payPerUseView(ctx: RouteContext, result: Result): RouteView {
  const provider = result.offering.provider ?? "";
  return {
    key: `ppu:${provider}:${result.offering.region ?? ""}:${result.offering.tier ?? ""}`,
    kind: "pay_per_use",
    name: `${providerName(ctx, provider)} · pay per use`,
    explain: payPerUseExplain(ctx, result.offering),
    figure: taskCost(result) === null ? "price not published" : `${money(taskCost(result))} per task`,
  };
}

function selfHostedView(access: AccessAnswer): RouteView {
  return {
    key: "self",
    kind: "self_hosted",
    name: "Run it yourself",
    explain: SELF_HOSTED_EXPLAIN,
    figure: access === "own_hardware" ? "fit published" : "no per-task fee",
  };
}

/** The engine's cost per task; a decision older than 2.5 carries it only in its cost contribution. */
export const taskCost = (result: Result): number | null =>
  result.cost_per_task ??
  result.contributions.find((item) => item.dimension.replace(/^-/, "") === "offering.cost_per_task")?.raw_value ??
  null;

const byCost = (left: Result, right: Result): number =>
  (taskCost(left) ?? Infinity) - (taskCost(right) ?? Infinity);

/** The cheapest priced pay-per-use offering among a model's results. */
export function cheapestMetered(results: readonly Result[]): Result | undefined {
  return results.filter((result) => result.offering.provider !== null && taskCost(result) !== null)
    .sort(byCost)[0];
}

function planRoutes(ctx: RouteContext, results: readonly Result[], access: AccessAnswer): RouteView[] {
  const seen = new Map<string, PlanRoute>();
  for (const result of results)
    for (const route of result.plans ?? [])
      if (!seen.has(route.plan)) seen.set(route.plan, route);
  return [...seen.values()]
    .sort((left, right) =>
      (left.price_monthly_usd ?? Infinity) - (right.price_monthly_usd ?? Infinity) ||
      left.name.localeCompare(right.name))
    .map((route) => planRouteView(ctx, route, access));
}

/**
 * Every route to one model that serves `access`, cheapest first. `results`
 * are the engine's ranked offerings of that model. For "Doesn't matter", only
 * the cheapest route, with its type in its name.
 */
export function modelRoutes(ctx: RouteContext, results: readonly Result[], access: AccessAnswer): RouteView[] {
  const metered = results.filter((result) => result.offering.provider !== null).sort(byCost);
  const bare = results.some((result) => result.offering.provider === null);
  switch (access) {
    case "chat_app":
      return planRoutes(ctx, results, access);
    case "coding_tool":
      return [...metered.map((result) => payPerUseView(ctx, result)), ...planRoutes(ctx, results, access)];
    case "own_software":
      return [...metered.map((result) => payPerUseView(ctx, result)), ...planRoutes(ctx, results, access)];
    case "own_hardware":
      return bare ? [selfHostedView(access)] : [];
    case "any": {
      const cheapest = cheapestMetered(results);
      if (cheapest) return [payPerUseView(ctx, cheapest)];
      if (bare) return [selfHostedView(access)];
      return metered[0] ? [payPerUseView(ctx, metered[0])] : [];
    }
  }
}

const perTask = (cost: number | null | undefined): string =>
  cost == null ? "price not published" : cost === 0 ? "$0 per task" : `${money(cost)} per task`;

/** The route a held estate reaches a row by, and what one more task costs you. */
export function estateRouteView(ctx: RouteContext, mark: EstateMark, result: Result | undefined, offering: OfferingRef): RouteView {
  const { via } = mark;
  const column = perTask(mark.marginal_cost_per_task_usd);
  if (via.kind === "plan") {
    const record = planRecord(ctx, via.id);
    const quote = mark.coverage?.quote ? ` Its page says it covers “${mark.coverage.quote}”.` : "";
    return {
      key: `plan:${via.id}`,
      kind: "plan",
      name: `${planName(record?.name ?? via.id)} · monthly plan`,
      explain: planExplain(record?.surfaces) + quote,
      figure: "included in your plan",
      column,
    };
  }
  if (via.kind === "device") {
    return {
      key: `device:${via.id}`,
      kind: "self_hosted",
      name: "Run it yourself",
      explain: SELF_HOSTED_EXPLAIN,
      figure: `on your ${deviceName(via.id)}`,
      column,
    };
  }
  const cost = mark.marginal_cost_per_task_usd ?? (result ? taskCost(result) : null);
  return {
    key: `ppu:${via.id}`,
    kind: "pay_per_use",
    name: `${providerName(ctx, via.id)} · pay per use`,
    explain: payPerUseExplain(ctx, offering),
    figure: perTask(cost),
  };
}

const DEVICE_WORDS: Readonly<Record<string, string>> = {
  nvidia: "NVIDIA", amd: "AMD", rtx: "RTX", tpu: "TPU", dgx: "DGX", sxm: "SXM", pcie: "PCIe",
  nvl: "NVL", agx: "AGX", nx: "NX", sff: "SFF", xt: "XT", xtx: "XTX", gb: "GB", rx: "RX",
  ai: "AI", gpu: "GPU",
};

/** "apple_m3_max" → "Apple M3 Max"; "intel_arc_a770_16gb" → "Intel Arc A770 16GB". */
export function deviceName(id: string): string {
  return id.split("_").map((word) => {
    if (DEVICE_WORDS[word]) return DEVICE_WORDS[word];
    if (/\d/.test(word)) return word.toUpperCase();
    return word.charAt(0).toUpperCase() + word.slice(1);
  }).join(" ");
}

export interface HeldEstate { providers: readonly string[]; plans: readonly string[]; hardware: readonly string[] }

/**
 * Why a may-qualify row may qualify, when the missing fact is about a plan or
 * hardware fit. Stated plainly, never hidden: the row is not ranked because a
 * fact is not verified yet.
 */
export function mayQualifyNote(ctx: RouteContext, row: MayQualify, held: HeldEstate): string | null {
  const provider = row.offering?.provider ?? null;
  const notes: string[] = [];
  const coverage = row.unknown.includes("offering.subscription.models_covered");
  const surfaces = row.unknown.includes("offering.subscription.surfaces");
  if (provider && (coverage || surfaces)) {
    const who = providerName(ctx, provider);
    const heldPlans = held.plans.map((id) => planRecord(ctx, id))
      .filter((plan): plan is VocabPlan => plan?.provider === provider)
      .map((plan) => planName(plan.name));
    const subject = heldPlans.length ? `Your ${joinWords(heldPlans, "or")}` : `A monthly plan from ${who}`;
    const gaps = [coverage ? "coverage" : null, surfaces ? "where its plans work" : null]
      .filter((gap): gap is string => gap !== null);
    notes.push(`${subject} may cover this; ${who}'s ${joinWords(gaps)} ${gaps.length > 1 ? "aren't" : "isn't"} verified yet.`);
  }
  if (row.unknown.includes("model.fits_hardware"))
    notes.push(held.hardware.length
      ? `Whether it fits your ${joinWords(held.hardware.map(deviceName), "or")} isn't published yet.`
      : "Its hardware fit isn't published yet.");
  return notes.length ? notes.join(" ") : null;
}

/** Held plans the engine says cannot serve your own software, by name. */
export function plansExcludingOwnSoftware(ctx: RouteContext, decision: Decision, held: HeldEstate): VocabPlan[] {
  if (!decision.with_estate?.warnings.includes("plan_excludes_own_software")) return [];
  return held.plans.map((id) => planRecord(ctx, id)).filter((plan): plan is VocabPlan =>
    plan !== undefined && Array.isArray(plan.surfaces) && !plan.surfaces.includes("api"));
}

export function ownSoftwareNote(plan: VocabPlan): string {
  return `Your ${planName(plan.name)} doesn't cover this: it works in ${surfacePhrase(plan.surfaces ?? [])}, not your own software.`;
}

export const offeringKey = (ref: OfferingRef): string =>
  [ref.model, ref.provider, ref.region, ref.tier].map((part) => part ?? "").join("|");

/**
 * The estate answer as a decision the board can draw: `with_estate`'s rows,
 * each joined to the unrestricted result for the same offering (its evidence
 * and estimates), ranked and warned as the estate answer ranks them.
 */
export function estateAsDecision(decision: Decision): { decision: Decision; marks: Map<string, EstateMark> } | null {
  const estate = decision.with_estate;
  if (!estate) return null;
  const unrestricted = new Map(decision.results.map((result) => [offeringKey(result.offering), result]));
  const marks = new Map<string, EstateMark>();
  const results: Result[] = estate.results.map((row) => {
    marks.set(offeringKey(row.offering), row.estate);
    const base = unrestricted.get(offeringKey(row.offering));
    return {
      ...(base ?? {
        offering: row.offering,
        model: row.offering.model,
        harness: null,
        effort: null,
        evidence: [],
        estimates: null,
        p_best: null,
        top3_stability: null,
        contributions: [],
      }),
      rank: row.rank,
      soft_penalty: row.soft_penalty,
      warnings: row.warnings,
    } as Result;
  });
  return {
    decision: {
      ...decision,
      status: estate.status,
      answer: estate.answer ?? null,
      results,
      by_model: [],
      may_qualify: estate.may_qualify,
      truncated: estate.truncated,
      eliminated: { funnel: [], models: [], model_groups: [] },
      with_estate: null,
    },
    marks,
  };
}
