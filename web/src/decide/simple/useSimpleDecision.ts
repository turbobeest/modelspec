import { useEffect, useRef, useState } from "react";
import {
  DecideApiError, decisionAction, hostedEngine, retryOnSnapshotChange, sharedReload,
} from "../adapter/hosted";
import type { DecideOptions, SpecIssue } from "../adapter/hosted";
import type { Decision, Spec } from "../adapter";
import { prepareDecisionRequest } from "../adapter/request-spec";
import { prepareVisit, VISIT_GATE_ENABLED } from "../adapter/visit";
import { HUMAN_GATE_ENABLED } from "../components/HumanGate";
import { loadVocabulary, VocabularyError, type Vocabulary } from "../vocabulary";
import { specHash } from "../state/spec";

export const SIMPLE_DECISION_WATCHDOG_MS = 20_000;

type VocabularyState =
  | { kind: "loading" }
  | { kind: "ready"; vocabulary: Vocabulary }
  | { kind: "error"; error: VocabularyError };
type RequestState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "success"; details: "loading" | "ready" | "unavailable" }
  | { kind: "error"; message: string; code: string | null; status: number | null; issues: SpecIssue[] };

/** Uses the detailed board's hosted transport and verification for a smaller form. */
export function useSimpleDecision(makeSpec: (vocabulary: Vocabulary) => Spec | null) {
  const [vocabularyState, setVocabularyState] = useState<VocabularyState>({ kind: "loading" });
  const [vocabularyAttempt, setVocabularyAttempt] = useState(0);
  const [gateStatus, setGateStatus] = useState<boolean | null>(
    HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED ? null : false,
  );
  const [gateRefresh, setGateRefresh] = useState(0);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [answeredSpec, setAnsweredSpec] = useState<Spec | null>(null);
  const [requestState, setRequestState] = useState<RequestState>({ kind: "idle" });
  const requestAbort = useRef<AbortController | null>(null);
  const actionQuestion = useRef<{ key: string | null; gate: boolean } | null>(null);
  const requestTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [reloadVocabulary] = useState(() => sharedReload(() => loadVocabulary(undefined, true)));
  const vocabulary = vocabularyState.kind === "ready" ? vocabularyState.vocabulary : null;
  const spec = vocabulary ? makeSpec(vocabulary) : null;
  const requestKey = spec ? specHash(spec) : null;

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    setVocabularyState({ kind: "loading" });
    void prepareVisit().catch(() => {
      throw new VocabularyError(
        "Human verification did not complete, so the catalogue vocabulary was not requested.", "network",
      );
    }).then(() => {
      controller.signal.throwIfAborted();
      if (!VISIT_GATE_ENABLED) timer = setTimeout(() => {
        controller.abort();
        if (active) setVocabularyState({
          kind: "error", error: new VocabularyError("The catalogue vocabulary did not load in time.", "network"),
        });
      }, SIMPLE_DECISION_WATCHDOG_MS);
      return loadVocabulary(controller.signal);
    }).then((loaded) => {
      if (active && !controller.signal.aborted) setVocabularyState({ kind: "ready", vocabulary: loaded });
    }).catch((cause: unknown) => {
      if (!active || controller.signal.aborted) return;
      setVocabularyState({
        kind: "error",
        error: cause instanceof VocabularyError ? cause : new VocabularyError("The catalogue vocabulary could not be reached.", "network"),
      });
    }).finally(() => clearTimeout(timer));
    return () => { active = false; clearTimeout(timer); controller.abort(); };
  }, [vocabularyAttempt]);

  async function lookup(humanToken?: string, onRemaining?: DecideOptions["onRemaining"]) {
    if (!vocabulary || !spec || gateStatus === null || (gateStatus && !humanToken)) return;
    clearTimeout(requestTimer.current);
    requestAbort.current?.abort();
    const controller = new AbortController();
    requestAbort.current = controller;
    actionQuestion.current = { key: requestKey, gate: gateStatus };
    const options = decisionAction(humanToken, onRemaining);
    setDecision(null);
    setAnsweredSpec(null);
    setRequestState({ kind: "loading" });
    const fail = (cause: unknown) => setRequestState({
      kind: "error",
      message: cause instanceof DecideApiError ? cause.message : "The decision service could not be reached.",
      code: cause instanceof DecideApiError ? cause.code : null,
      status: cause instanceof DecideApiError ? cause.status : null,
      issues: cause instanceof DecideApiError ? cause.issues : [],
    });
    try { await prepareVisit(); }
    catch (cause) { if (!controller.signal.aborted) fail(cause); return; }
    if (controller.signal.aborted) return;
    const watchdog = VISIT_GATE_ENABLED ? undefined : setTimeout(() => {
      if (controller.signal.aborted) return;
      controller.abort();
      fail(new DecideApiError(
        `The decision service did not answer within ${SIMPLE_DECISION_WATCHDOG_MS / 1000} seconds.`, null, "timeout",
      ));
    }, SIMPLE_DECISION_WATCHDOG_MS);
    const refreshedSpec = (current: Vocabulary | null, source: Spec) =>
      current && current !== vocabulary ? makeSpec(current) : source;
    const installVocabulary = (fresh: Vocabulary) => {
      if (controller.signal.aborted) return;
      const next = makeSpec(fresh);
      actionQuestion.current = { key: next ? specHash(next) : null, gate: gateStatus };
      setVocabularyState({ kind: "ready", vocabulary: fresh });
      const original = prepareDecisionRequest(vocabulary, spec, "summary").decisionSpec;
      const updated = next ? prepareDecisionRequest(fresh, next, "summary").decisionSpec : null;
      if (JSON.stringify(original) !== JSON.stringify(updated)) {
        throw new DecideApiError(
          gateStatus
            ? "The data changed these choices. Review them, then verify and look up this decision again."
            : "The data changed these choices. Review them, then retry the lookup.",
          null, "question_changed",
        );
      }
    };
    const ask = (current: Vocabulary | null, explain: "summary" | "full", source: Spec) => {
      controller.signal.throwIfAborted();
      const next = refreshedSpec(current, source);
      if (!next) throw new DecideApiError("These choices are unavailable in the current data.", null, "template_unavailable");
      const prepared = prepareDecisionRequest(current, next, explain);
      return hostedEngine.decide(prepared.decisionSpec, {
        ...options, signal: controller.signal, snapshot: current?.snapshot,
      }).then((answer) => ({ decision: answer, spec: prepared.boardSpec }));
    };
    let used: Vocabulary | null = vocabulary;
    let nextSpec: Spec;
    try {
      const answer = await retryOnSnapshotChange(
        vocabulary, (current) => ask(current, "summary", spec), reloadVocabulary,
        installVocabulary,
      );
      if (controller.signal.aborted) return;
      used = answer.vocabulary;
      nextSpec = answer.result.spec;
      setDecision(answer.result.decision);
      setAnsweredSpec(nextSpec);
      setRequestState({ kind: "success", details: "loading" });
    } catch (cause) {
      if (controller.signal.aborted) return;
      if ((HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED) && cause instanceof DecideApiError && cause.code === "human_challenge_required") {
        setGateStatus(null);
        setGateRefresh((value) => value + 1);
      }
      fail(cause);
      return;
    } finally { clearTimeout(watchdog); }
    try {
      const answer = used !== vocabulary
        ? { result: await ask(used, "full", nextSpec), vocabulary: used }
        : await retryOnSnapshotChange(used, (current) => ask(current, "full", nextSpec), reloadVocabulary, installVocabulary);
      if (controller.signal.aborted) return;
      if (answer.vocabulary && answer.vocabulary !== used) {
        setVocabularyState({ kind: "ready", vocabulary: answer.vocabulary });
      }
      setDecision(answer.result.decision);
      setAnsweredSpec(answer.result.spec);
      setRequestState({ kind: "success", details: "ready" });
    } catch (cause) {
      if (controller.signal.aborted || (cause instanceof Error && cause.name === "AbortError")) return;
      if (cause instanceof DecideApiError && cause.code === "question_changed") {
        setDecision(null);
        setAnsweredSpec(null);
        fail(cause);
        return;
      }
      setRequestState({ kind: "success", details: "unavailable" });
    }
  }

  useEffect(() => {
    // A reload can change template defaults within the same verified action.
    if (requestAbort.current && !requestAbort.current.signal.aborted
      && actionQuestion.current?.key === requestKey && actionQuestion.current.gate === gateStatus) return;
    requestAbort.current?.abort();
    setDecision(null);
    setAnsweredSpec(null);
    setRequestState({ kind: "idle" });
    if (spec && gateStatus === false) {
      requestTimer.current = setTimeout(() => { void lookup(); }, 300);
    }
    return () => { clearTimeout(requestTimer.current); };
    // The question's value owns the action; a fresh builder or vocabulary object does not.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey, gateStatus]);
  useEffect(() => () => requestAbort.current?.abort(), []);

  return {
    vocabulary, vocabularyState, spec, decision, answeredSpec, requestState,
    gateStatus, gateRefresh, setGateStatus, lookup,
    retry: () => lookup(),
    retryVocabulary: () => setVocabularyAttempt((value) => value + 1),
  };
}
