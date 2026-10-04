import { VISIT_GATE_ENABLED, prepareVisit } from "./adapter/visit";
import { VisitGate, HumanGate, HUMAN_GATE_ENABLED } from "./components/HumanGate";
import { decisionAction } from "./adapter/hosted";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  hostedEngine,
  retryOnSnapshotChange,
  sharedReload,
  DecideApiError,
  fmtB,
  fmtCI,
} from "./adapter";
import type {
  DecideOptions,
  Cond,
  Decision,
  Evidence,
  Spec,
  SpecIssue,
} from "./adapter";
import {
  VocabularyError,
  VOCABULARY_URL,
  loadVocabulary,
  realBaseSpec,
  sendable as sendableSpec,
} from "./vocabulary";
import type { Vocabulary } from "./vocabulary";
import { VocabContext, fictionalVocab, realVocab } from "./vocabulary/context";
import { placeIssues } from "./vocabulary/issues";
import {
  registerBenchmarks,
  registerProviders,
  registerValueLabels,
} from "./adapter/condition-label";
import { baseSpec, decodeSpec, specHash } from "./state/spec";
import type { Axis } from "./state/spec";
import { Field } from "./components/Field";
import { Canvas } from "./components/Canvas";
import { FreeAxisCanvas } from "./components/FreeAxisCanvas";
import type { CanvasAxes } from "./components/FreeAxisCanvas";
import {
  canvasAxisOptions,
  canvasPlotSpec,
} from "./components/canvas-axis";
import { RankedAnswer } from "./facet-board/RankedAnswer";
import { DecisionTable } from "./components/DecisionTable";
import { FeedbackForm, FeedbackLauncher } from "./feedback/FeedbackForm";
import { Why } from "./components/Why";
import { Coverage } from "./components/Coverage";
import { AnswerBoundary } from "./components/AnswerBoundary";
import { Share } from "./components/Share";
import { SnapshotId } from "./components/SnapshotId";
import { BrandMark } from "./components/BrandMark";
import { initialTheme, storeTheme, storedTheme, type Theme } from "./theme";
import "./decide.css";
import { mapDecisionToViewModel } from "./adapter/view-model";
import { BoardIntro, FacetBoard, readEstate, writeEstate } from "./facet-board/FacetBoard";
import {
  boardHasPreference, boardToSpec, decodeBoardState, encodeBoardSpec, estatePayload, foldRefinementWeights, hasEstate,
  allocateBoardWeights, nextMustOrder, legacyBoardBaseSpec, legacySpecToBoard, refinementWeightKeys,
  sanitizeBoardState,
  toBoardDecisionSpec,
} from "./facet-board/model";
import type { BoardSelections, Estate, FacetSelection } from "./facet-board/model";
import type { CanvasAxisOption } from "./components/canvas-axis";
import {
  accessAnswer, estateAsDecision, ownSoftwareNote, plansExcludingOwnSoftware,
} from "./facet-board/routes";
import type { AccessAnswer } from "./facet-board/routes";

/** The spec with `access` set, or without the key for "Doesn't matter". */
function withAccess(spec: Spec, access: AccessAnswer): Spec {
  const next = { ...spec };
  if (access === "any") delete next.access;
  else next.access = access;
  return next;
}

/**
 * The main decision shows Retry if it has not resolved by then, whatever it is
 * waiting on: the request, its body, or a vocabulary reload after a 409.
 */
export const DECISION_WATCHDOG_MS = 20_000;

type EstateRequestState =
  | { kind: "idle"; settledSpecHash: string | null; generation: number }
  | { kind: "loading"; settledSpecHash: string; requestKey: string; generation: number }
  | { kind: "done"; settledSpecHash: string; requestKey: string; generation: number; decision: Decision }
  | { kind: "error"; settledSpecHash: string; requestKey: string; generation: number };

export function DesignedApp({
  simulate,
}: {
  simulate?: "loading" | "error" | "none";
}) {
  const [gateStatus, setGateStatus] = useState<boolean | null>(HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED ? null : false);
  const [gateRefresh, setGateRefresh] = useState(0);
  const humanGateEnabled = gateStatus === true;
  const action = useRef<DecideOptions>({});
  const pendingSpec = useRef<Spec | null>(null);
  const [initial] = useState(() => decodeSpec(location.hash)),
    [initialBoard] = useState(() => decodeBoardState(location.hash)),
    [spec, setSpec] = useState<Spec>(initial?.spec || baseSpec),
    [boardBaseSpec, setBoardBaseSpec] = useState<Spec>(initial?.spec || baseSpec),
    [boardSelections, setBoardSelections] = useState<BoardSelections>(initialBoard?.selections ?? {}),
    [boardMustOrder, setBoardMustOrder] = useState<string[]>(initialBoard?.mustOrder ?? []),
    [refinementFallbackKeys, setRefinementFallbackKeys] = useState<Set<string>>(new Set()),
    [lastSentSpec, setLastSentSpec] = useState<Spec | null>(null),
    [axis, setAxis] = useState<Axis>(initial?.x || "task$"),
    [canvasAxes, setCanvasAxes] = useState<CanvasAxes | null>(
      initialBoard?.canvas ?? null,
    ),
    [legacyNotes, setLegacyNotes] = useState<string[]>([]),
    [initialRestored, setInitialRestored] = useState(!initial);
  const [theme, setTheme] = useState<Theme>(() =>
      initialTheme(location.search, storedTheme()),
    );
  const [selected, setSelected] = useState<string | null>(null),
    [dismissed, setDismissed] = useState<string[]>([]),
    [share, setShare] = useState(false),
    [provenance, setProvenance] = useState<{
      e: Evidence;
      x: number;
      y: number;
    } | null>(null),
    [retried, setRetried] = useState(false);
  const [estate, setEstate] = useState<Estate>(() => initialBoard?.estate ?? readEstate()),
    [estateRequest, setEstateRequest] = useState<EstateRequestState>({
      kind: "idle",
      settledSpecHash: null,
      generation: 0,
    });
  const requestTimer = useRef<ReturnType<typeof setTimeout> | null>(null),
    requestAbort = useRef<AbortController | null>(null),
    plotKey = useRef(""),
    // The plot request in flight, if any. It outlives effect re-runs that
    // leave its key unchanged (the full explanation replacing the summary).
    plotRequest = useRef<AbortController | null>(null),
    provTrigger = useRef<HTMLElement | null>(null),
    hashNavigation = useRef<() => void>(() => undefined),
    initialAnswered = useRef(false);
  // A site deploy can change the snapshot under an open page (MODEL-159). The
  // Worker says so with a 409; every request that hears it shares one reload.
  const [reloadVocabulary] = useState(() => sharedReload(() => loadVocabulary(undefined, true)));
  const [activeTemplateId, setActiveTemplateId] = useState<string | null>(null);
  const [hasAdjustedBoard, setHasAdjustedBoard] = useState(false);
  // Bumped by the answer's Reset: remounting the board drops its open groups and template too.
  const [boardGeneration, setBoardGeneration] = useState(0);
  const [hostedDecision, setHostedDecision] = useState<Decision | null>(null),
    [plotDecision, setPlotDecision] = useState<Decision | null>(null),
    [requestState, setRequestState] = useState<
      | { kind: "idle" }
      | { kind: "loading" }
      | {
          kind: "error";
          message: string;
          code: string | null;
          status: number | null;
          issues: SpecIssue[];
        }
      // The summary is drawn at once; `details` tracks the `full` explanation behind it.
      | { kind: "success"; details: "loading" | "ready" | "unavailable" }
    >({ kind: "idle" }),
    [vocabState, setVocabState] = useState<
      | { kind: "loading" }
      | { kind: "ready"; vocabulary: Vocabulary }
      | { kind: "error"; error: VocabularyError }
    >({ kind: "loading" }),
    [vocabAttempt, setVocabAttempt] = useState(0);
  const vocabulary = vocabState.kind === "ready" ? vocabState.vocabulary : null;
  const shownCanvasAxes = useMemo((): CanvasAxes | null => {
    if (!vocabulary) return null;
    const enabled = canvasAxisOptions(vocabulary).filter((option) => !option.disabled);
    if (enabled.length === 0) return null;
    const fallback = { x: enabled[0].id, y: (enabled[1] ?? enabled[0]).id };
    if (!canvasAxes) return fallback;
    const ids = new Set(enabled.map((option) => option.id));
    return {
      x: ids.has(canvasAxes.x) ? canvasAxes.x : fallback.x,
      y: ids.has(canvasAxes.y) ? canvasAxes.y : fallback.y,
    };
  }, [canvasAxes, vocabulary]);
  const vocab = useMemo(() => {
    if (!vocabulary) return fictionalVocab;
    registerBenchmarks(vocabulary.benchmarks);
    registerProviders(vocabulary.providers);
    registerValueLabels(vocabulary.facets);
    return realVocab(vocabulary);
  }, [vocabulary]);
  const shownAxis = vocab.axes.includes(axis) ? axis : (vocab.axes[0] ?? axis);
  const shownSpec = useMemo(() => {
    if (!hostedDecision || vocabulary) return spec;
    const availableBenchmarks = [
      ...new Set(
        hostedDecision.top.flatMap((candidate) =>
          candidate.evidence.flatMap((group) =>
            group.items.map((item) => item.benchmark),
          ),
        ),
      ),
    ];
    return availableBenchmarks.length > 0 &&
      !availableBenchmarks.includes(spec.bench)
      ? { ...spec, bench: availableBenchmarks[0] }
      : spec;
  }, [hostedDecision, spec, vocabulary]);
  const boardRanked = shownSpec.boardWeights === undefined || boardHasPreference(shownSpec);
  const mapped = useMemo(() => {
    if (!hostedDecision) return { decision: null, error: null };
    try {
      return {
        decision: mapDecisionToViewModel(hostedDecision, shownSpec, {
          axis: shownAxis,
          dismissed,
          questions: [],
          ...(vocabulary
            ? { benchmarks: vocab.benchmarks, models: vocabulary.models, providers: vocabulary.providers }
            : {}),
        }),
        error: null,
      };
    } catch (cause) {
      // A decision that cannot be drawn is reported, never left as a blank page.
      return {
        decision: null,
        error: cause instanceof Error ? cause.message : String(cause),
      };
    }
  }, [hostedDecision, shownSpec, shownAxis, dismissed, vocabulary, vocab]);
  const liveDecision = mapped.decision;
  useEffect(() => {
    if (requestTimer.current) return;
    if (
      !vocabulary ||
      !hostedDecision ||
      !lastSentSpec ||
      !shownCanvasAxes
    ) {
      plotRequest.current?.abort();
      plotRequest.current = null;
      plotKey.current = "";
      setPlotDecision(null);
      return;
    }
    const intentOptions = action.current;
    const options = new Map(
      canvasAxisOptions(vocabulary).map((option) => [option.id, option]),
    );
    const x = options.get(shownCanvasAxes.x);
    const y = options.get(shownCanvasAxes.y);
    if (!x || !y) return;
    const rankingSpec = toBoardDecisionSpec(lastSentSpec, "summary");
    const numericFallback = [...options.values()].find(
      (option) => !option.disabled && option.valueType === "number",
    );
    const plotSpec = canvasPlotSpec(rankingSpec, x, y, numericFallback);
    const key = `${hostedDecision.snapshot}:${JSON.stringify(plotSpec)}`;
    // Asked already, answered or still in flight: the same question is never
    // sent twice. Aborting it on every re-run and asking again sent one action's
    // plot twice whenever the full explanation landed first.
    if (plotKey.current === key) return;
    plotRequest.current?.abort();
    const controller = new AbortController();
    plotRequest.current = controller;
    plotKey.current = key;
    setPlotDecision(null);
    void retryOnSnapshotChange(
      vocabulary,
      (current) =>
        hostedEngine.decide(plotSpec, {
          ...intentOptions,
          signal: controller.signal,
          snapshot: (current ?? vocabulary).snapshot,
        }),
      reloadVocabulary,
      (fresh) => setVocabState({ kind: "ready", vocabulary: fresh }),
    )
      .then(({ result: plotDecision }) => {
        if (!controller.signal.aborted) setPlotDecision(plotDecision);
      })
      .catch((cause: unknown) => {
        if (!(cause instanceof Error && cause.name === "AbortError"))
          setPlotDecision(null);
      })
      .finally(() => {
        if (plotRequest.current === controller) plotRequest.current = null;
      });
  }, [
    humanGateEnabled,
    hostedDecision,
    lastSentSpec,
    shownCanvasAxes,
    vocabulary,
    reloadVocabulary,
  ]);
  useEffect(() => () => plotRequest.current?.abort(), []);
  const access = accessAnswer(boardBaseSpec.access);
  // Routes are drawn for the access the shown decision answered, not the one
  // just chosen: until the new answer arrives, the old one keeps its routes.
  const answeredAccess = accessAnswer((lastSentSpec ?? spec).access);
  const estateAnswer = useMemo(() => {
    if (estateRequest.kind !== "done" || !vocabulary) return null;
    const estateView = estateAsDecision(estateRequest.decision);
    if (!estateView) return null;
    try {
      return {
        decision: mapDecisionToViewModel(estateView.decision, shownSpec, {
          axis: shownAxis,
          dismissed,
          benchmarks: vocab.benchmarks,
          models: vocabulary.models,
          providers: vocabulary.providers,
        }),
        marks: estateView.marks,
        excludedPlans: plansExcludingOwnSoftware({ vocabulary }, estateRequest.decision, estate),
      };
    } catch {
      return null;
    }
  }, [estateRequest, shownSpec, shownAxis, dismissed, vocabulary, vocab, estate]);
  const estateDecision = estateAnswer?.decision ?? null;
  const decision = liveDecision,
    e = decision?.explanation,
    boardIsRanked = shownSpec.boardWeights === undefined || Object.values(shownSpec.boardWeights).some((weight) => (typeof weight === "number" ? weight : weight.weight) > 0),
    selectedId = selected || (boardIsRanked ? e?.shortlist.top?.m.id || e?.may[0]?.m.id : null) || null,
    row = e?.rows.find((candidate) => candidate.m.id === selectedId) || null;
  const sim = simulate || new URLSearchParams(location.search).get("simulate"),
    simulatedError = sim === "error" && !retried,
    error = simulatedError || requestState.kind === "error" || !!mapped.error,
    loading = sim === "loading" || requestState.kind === "loading";
  const placed = useMemo(
    () => (requestState.kind === "error" ? placeIssues(requestState.issues) : []),
    [requestState],
  );
  const specIssues = placed.filter((issue) => issue.target.kind === "spec");

  async function runDecision(requested: Spec, humanToken?: string, onRemaining?: (remaining: number) => void) {
    if (gateStatus === null || (humanGateEnabled && !humanToken)) return;
    const intentOptions = decisionAction(humanToken, onRemaining);
    action.current = intentOptions;
    requestAbort.current?.abort();
    const controller = new AbortController();
    requestAbort.current = controller;
    setHostedDecision(null);
    setLastSentSpec(null);
    setEstateRequest((current) => ({
      kind: "idle",
      settledSpecHash: null,
      generation: current.generation,
    }));
    setRequestState({ kind: "loading" });
    const fail = (cause: unknown) =>
      setRequestState({
        kind: "error",
        message:
          cause instanceof DecideApiError
            ? cause.message
            : "The decision service could not be reached.",
        code: cause instanceof DecideApiError ? cause.code : null,
        status: cause instanceof DecideApiError ? cause.status : null,
        issues: cause instanceof DecideApiError ? cause.issues : [],
      });
    try { await prepareVisit(); }
    catch (cause) { if (!controller.signal.aborted) fail(cause); return; }
    if (controller.signal.aborted) return;
    const watchdog = VISIT_GATE_ENABLED ? undefined : setTimeout(() => {
      controller.abort();
      fail(
        new DecideApiError(
          `The decision service did not answer within ${DECISION_WATCHDOG_MS / 1000} seconds.`,
          null,
          "timeout",
        ),
      );
    }, DECISION_WATCHDOG_MS);
    const ask = (current: Vocabulary | null, explain: "summary" | "full", override?: Spec) => {
      const source = override ?? requested;
      const nextSpec = current ? sendableSpec(current, source) : source;
      return hostedEngine
        .decide({ ...toBoardDecisionSpec(nextSpec, explain) }, {
          ...intentOptions,
          signal: controller.signal,
          snapshot: current?.snapshot,
        })
        .then((decision) => ({ decision, nextSpec }));
    };
    let used = vocabulary,
      reloaded = false,
      nextSpec: Spec;
    const installReloadedVocabulary = (fresh: Vocabulary) => {
      used = fresh;
      reloaded = true;
      setVocabState({ kind: "ready", vocabulary: fresh });
    };
    try {
      // Summary first: it is small and answers well inside the Worker's limits,
      // so the ranking draws at once. The full explanation and plot
      // follow only once it has answered, so a cold Worker meets one request
      // before the burst; if `full` fails, the summary stands (MODEL-153).
      const answer = await retryOnSnapshotChange(
        vocabulary,
        (current) => ask(current, "summary"),
        reloadVocabulary,
        installReloadedVocabulary,
      );
      if (controller.signal.aborted) return;
      used = answer.vocabulary;
      reloaded = used !== vocabulary;
      nextSpec = answer.result.nextSpec;
      setHostedDecision(answer.result.decision);
      setLastSentSpec(nextSpec);
      setRefinementFallbackKeys(new Set());
      setEstateRequest((current) => ({
        kind: "idle",
        settledSpecHash: specHash(requested),
        generation: current.generation,
      }));
      setRequestState({ kind: "success", details: "loading" });
    } catch (cause) {
      // Aborted by a newer request or by the watchdog: whichever did owns the state.
      if (controller.signal.aborted) return;
      if ((HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED) && cause instanceof DecideApiError && cause.code === "human_challenge_required") {
        setGateStatus(null);
        setGateRefresh((value) => value + 1);
      }
      const refinementKeys = used ? refinementWeightKeys(used) : new Set<string>();
      const requestHadRefinementWeights = Object.keys(
        used ? sendableSpec(used, requested).boardWeights ?? {} : {},
      ).some((key) => refinementKeys.has(key));
      if (
        used &&
        cause instanceof DecideApiError &&
        cause.status === 400 &&
        requestHadRefinementWeights
      ) {
        const folded = foldRefinementWeights(requested, used);
        const fallbackVocabulary = used;
        try {
          const answer = await retryOnSnapshotChange(fallbackVocabulary, (current) => ask(current, "summary", folded), reloadVocabulary, installReloadedVocabulary);
          if (controller.signal.aborted) return;
          const effectiveVocabulary = answer.vocabulary ?? fallbackVocabulary;
          used = effectiveVocabulary;
          nextSpec = answer.result.nextSpec;
          setHostedDecision(answer.result.decision);
          setRefinementFallbackKeys(refinementWeightKeys(effectiveVocabulary));
          setLastSentSpec(nextSpec);
          setEstateRequest((current) => ({
            kind: "idle",
            settledSpecHash: specHash(requested),
            generation: current.generation,
          }));
          setRequestState({ kind: "success", details: "loading" });
        } catch (fallbackCause) {
          if (controller.signal.aborted || (fallbackCause instanceof Error && fallbackCause.name === "AbortError"))
            return;
          fail(fallbackCause);
          return;
        }
      } else {
        fail(cause);
        return;
      }
    } finally {
      clearTimeout(watchdog);
    }
    try {
      // Once the summary has reloaded, a second 409 here leaves the summary
      // standing: the background request never starts another reload.
      const answer = reloaded
        ? { result: await ask(used, "full", nextSpec), vocabulary: used }
        : await retryOnSnapshotChange(used, (current) => ask(current, "full", nextSpec), reloadVocabulary);
      if (controller.signal.aborted) return;
      if (answer.vocabulary && answer.vocabulary !== used)
        setVocabState({ kind: "ready", vocabulary: answer.vocabulary });
      setHostedDecision(answer.result.decision);
      setRequestState({ kind: "success", details: "ready" });
    } catch (cause) {
      if (controller.signal.aborted || (cause instanceof Error && cause.name === "AbortError"))
        return;
      setRequestState({ kind: "success", details: "unavailable" });
    }
  }

  function scheduleDecision(nextSpec: Spec) {
    if (gateStatus === null || humanGateEnabled) return;
    if (requestTimer.current) clearTimeout(requestTimer.current);
    requestTimer.current = setTimeout(() => {
      requestTimer.current = null;
      void runDecision(nextSpec);
    }, 300);
  }

  function changeSpec(nextSpec: Spec) {
    if (gateStatus === null) pendingSpec.current = nextSpec;
    if (humanGateEnabled) {
      requestAbort.current?.abort();
      setHostedDecision(null);
      setLastSentSpec(null);
      setRequestState({ kind: "idle" });
      setEstateRequest((current) => ({ kind: "idle", settledSpecHash: null, generation: current.generation }));
    }
    setSpec(nextSpec);
    scheduleDecision(nextSpec);
  }

  function changeAccess(next: AccessAnswer) {
    setBoardBaseSpec((current) => withAccess(current, next));
    changeSpec(withAccess(spec, next));
  }

  function changeBoardSelections(next: BoardSelections) {
    if (JSON.stringify(next) !== JSON.stringify(boardSelections)) setHasAdjustedBoard(true);
    setBoardSelections(next);
  }

  function setCanvasMust(axisOption: CanvasAxisOption, value: number | string) {
    if (!vocabulary || !axisOption.mustOp) return;
    const selectionId =
      axisOption.kind === "capability"
        ? `capability.${axisOption.key}`
        : axisOption.key;
    const current = boardSelections[selectionId];
    const next: FacetSelection = {
      ...current,
      mode:
        current?.mode === "prefer" || current?.mode === "both"
          ? "both"
          : "must",
      op: axisOption.mustOp,
      value,
    };
    const all = allocateBoardWeights(vocabulary, {
      ...boardSelections,
      [selectionId]: next,
    }).selections;
    const nextOrder = nextMustOrder(
      boardMustOrder,
      boardSelections,
      selectionId,
      next,
    );
    const sanitized = sanitizeBoardState(
      { selections: all, mustOrder: nextOrder, estate },
      vocabulary,
      legacyNotes,
    );
    changeBoardSelections(sanitized.selections);
    setBoardMustOrder(sanitized.mustOrder);
    setLegacyNotes(sanitized.notes);
    changeSpec(
      boardToSpec(boardBaseSpec, vocabulary, sanitized.selections, sanitized.mustOrder),
    );
  }

  /** The answer area's Reset (MODEL-294): back to the default board, as "Reset all" does. */
  function resetBoard() {
    if (!vocabulary) return;
    const empty = sanitizeBoardState({ selections: {}, mustOrder: [], estate }, vocabulary);
    changeBoardSelections(empty.selections);
    setBoardMustOrder([]);
    setLegacyNotes([]);
    setActiveTemplateId(null);
    setSelected(null);
    setBoardGeneration((generation) => generation + 1);
    changeSpec(boardToSpec(boardBaseSpec, vocabulary, empty.selections, []));
  }

  const effectiveSpec = lastSentSpec ?? spec;
  const estateRequestKey = `${specHash(spec)}:${JSON.stringify(estate)}`;
  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    setVocabState({ kind: "loading" });
    prepareVisit().catch(() => {
      throw new VocabularyError(
        "Human verification did not complete, so the catalogue vocabulary was not requested.",
        "network",
      );
    }).then(() => {
      controller.signal.throwIfAborted();
      timer = VISIT_GATE_ENABLED ? undefined : setTimeout(() => controller.abort(), 20_000);
      return loadVocabulary(controller.signal);
    })
      .then((loaded) => setVocabState({ kind: "ready", vocabulary: loaded }))
      .catch((cause: unknown) => {
        if (cause instanceof Error && cause.name === "AbortError" && !controller.signal.aborted)
          return;
        setVocabState({
          kind: "error",
          error:
            cause instanceof VocabularyError
              ? cause
              : new VocabularyError(
                  "The catalogue vocabulary did not load in time.",
                  "network",
                ),
        });
      })
      .finally(() => clearTimeout(timer));
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [vocabAttempt]);
  useEffect(() => {
    if (!vocabulary || gateStatus === null) return;
    if (pendingSpec.current) {
      const edited = pendingSpec.current;
      pendingSpec.current = null;
      initialAnswered.current = true;
      setInitialRestored(true);
      void runDecision(edited);
      return;
    }
    if (initial) {
      // A shared link: answer it as written. What the engine refuses is shown on its chip.
      // Once: a vocabulary reloaded after a deploy must not answer it again.
      if (initialAnswered.current) return;
      initialAnswered.current = true;
      const legacyBoard = initialBoard ? null : legacySpecToBoard(initial.spec, vocabulary, estate);
      const restoredBoard = initialBoard
        ? sanitizeBoardState(initialBoard, vocabulary)
        : legacyBoard;
      if (!restoredBoard) {
        setInitialRestored(true);
        return;
      }
      const restoredBase = legacyBoard ? legacyBoardBaseSpec(initial.spec) : initial.spec;
      const restored = boardToSpec(
        restoredBase,
        vocabulary,
        restoredBoard.selections,
        restoredBoard.mustOrder,
      );
      setBoardBaseSpec(restoredBase);
      setBoardSelections(restoredBoard.selections);
      setBoardMustOrder(restoredBoard.mustOrder);
      setCanvasAxes(restoredBoard.canvas ?? null);
      setEstate(restoredBoard.estate);
      setLegacyNotes(restoredBoard.notes);
      setSpec(restored);
      setInitialRestored(true);
      void runDecision(restored);
      return;
    }
    const base = realBaseSpec(vocabulary);
    const emptyBoard = sanitizeBoardState(
      { selections: {}, mustOrder: [], estate },
      vocabulary,
    );
    if (emptyBoard.notes.length) {
      // A saved estate that names ids this snapshot no longer lists.
      setEstate(emptyBoard.estate);
      writeEstate(emptyBoard.estate);
      setLegacyNotes(emptyBoard.notes);
    }
    const initialBase = boardToSpec({ ...base, conds: [] }, vocabulary, emptyBoard.selections);
    setBoardBaseSpec({ ...base, conds: [] });
    setSpec((current) => (current === baseSpec ? initialBase : current));
    if (!initialAnswered.current) {
      initialAnswered.current = true;
      void runDecision(initialBase);
    }
    // Once per loaded vocabulary; runDecision reads the latest state itself.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vocabulary, gateStatus]);
  useEffect(() => {
    if (requestTimer.current) return;
    const intentOptions = action.current;
    if (
      !vocabulary ||
      !hasEstate(estate) ||
      estateRequest.settledSpecHash !== specHash(spec)
    ) {
      setEstateRequest((current) => ({
        kind: "idle",
        settledSpecHash: current.settledSpecHash,
        generation: current.generation,
      }));
      return;
    }
    const settledSpecHash = estateRequest.settledSpecHash;
    const requestKey = estateRequestKey;
    if (
      (estateRequest.kind === "done" || estateRequest.kind === "error") &&
      estateRequest.requestKey === requestKey
    ) return;
    const controller = new AbortController();
    let active = true;
    setEstateRequest({
      kind: "loading",
      settledSpecHash,
      requestKey,
      generation: estateRequest.generation,
    });
    const watchdog = VISIT_GATE_ENABLED ? undefined : setTimeout(() => {
      controller.abort();
      if (active) setEstateRequest({
        kind: "error",
        settledSpecHash,
        requestKey,
        generation: estateRequest.generation,
      });
    }, DECISION_WATCHDOG_MS);
    const timer = setTimeout(() => {
      void retryOnSnapshotChange(
        vocabulary,
        (current) => {
          const pinned = current ?? vocabulary;
          return hostedEngine.decide({
            ...toBoardDecisionSpec(sendableSpec(pinned, effectiveSpec), "summary"),
            estate: estatePayload(estate),
          }, {
            signal: controller.signal,
            ...intentOptions,
            snapshot: pinned.snapshot,
          });
        },
        reloadVocabulary,
      ).then((answer) => {
        if (!answer.result.with_estate) throw new Error("The engine did not answer with what you have.");
        if (!controller.signal.aborted) {
          active = false;
          setEstateRequest({
            kind: "done",
            settledSpecHash,
            requestKey,
            generation: estateRequest.generation,
            decision: answer.result,
          });
        }
      }).catch(() => {
        if (active) {
          active = false;
          setEstateRequest({
            kind: "error",
            settledSpecHash,
            requestKey,
            generation: estateRequest.generation,
          });
        }
      }).finally(() => clearTimeout(watchdog));
    }, 300);
    return () => {
      const aborted = active;
      active = false;
      clearTimeout(timer);
      clearTimeout(watchdog);
      controller.abort();
      if (aborted)
        setEstateRequest((current) =>
          current.kind === "loading" && current.requestKey === requestKey
            ? {
                kind: "idle",
                settledSpecHash: current.settledSpecHash,
                generation: current.generation,
              }
            : current,
        );
    };
    // The key, not the summary/full response object, owns this request.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [humanGateEnabled, vocabulary, estateRequest.settledSpecHash, estateRequest.generation, estateRequestKey]);
  useEffect(() => {
    if (!vocabulary || !initialRestored) return;
    history.replaceState(
      null,
      "",
      location.pathname + location.search + encodeBoardSpec(
        boardBaseSpec,
        axis,
        {
          selections: boardSelections,
          mustOrder: boardMustOrder,
          estate,
          ...(shownCanvasAxes ? { canvas: shownCanvasAxes } : {}),
        },
      ),
    );
  }, [vocabulary, initialRestored, spec, axis, boardBaseSpec, boardSelections, boardMustOrder, estate, shownCanvasAxes]);
  useEffect(() => {
    document.documentElement.dataset.decideTheme = theme;
    return () => {
      delete document.documentElement.dataset.decideTheme;
    };
  }, [theme]);
  hashNavigation.current = () => {
    const restored = decodeSpec(location.hash);
    if (!restored) return;
    const encodedBoard = decodeBoardState(location.hash);
    const legacyBoard = !encodedBoard && vocabulary
      ? legacySpecToBoard(restored.spec, vocabulary, estate)
      : null;
    const restoredBoard = encodedBoard && vocabulary
      ? sanitizeBoardState(encodedBoard, vocabulary)
      : legacyBoard;
    const restoredBase = legacyBoard ? legacyBoardBaseSpec(restored.spec) : restored.spec;
    const nextSpec = vocabulary && restoredBoard
      ? boardToSpec(restoredBase, vocabulary, restoredBoard.selections, restoredBoard.mustOrder)
      : restored.spec;
    setBoardBaseSpec(restoredBase);
    setBoardSelections(restoredBoard?.selections ?? {});
    setBoardMustOrder(restoredBoard?.mustOrder ?? []);
    setCanvasAxes(restoredBoard?.canvas ?? null);
    if (restoredBoard) setEstate(restoredBoard.estate);
    setLegacyNotes(restoredBoard?.notes ?? []);
    changeSpec(nextSpec);
    setAxis(restored.x);
    setSelected(null);
  };
  useEffect(() => {
    const esc = (ev: KeyboardEvent) => {
      if (ev.key === "Escape") {
        setShare(false);
        setProvenance(null);
        provTrigger.current?.focus();
      }
    };
    const hash = () => hashNavigation.current();
    window.addEventListener("keydown", esc);
    window.addEventListener("hashchange", hash);
    return () => {
      window.removeEventListener("keydown", esc);
      window.removeEventListener("hashchange", hash);
      if (requestTimer.current) clearTimeout(requestTimer.current);
      requestAbort.current?.abort();
    };
  }, []);
  function add(c: Cond) {
    const i = spec.conds.findIndex(
        (x) =>
          x.f === c.f && (x.f !== "bench" || c.f !== "bench" || x.b === c.b),
      );
    changeSpec({
        ...spec,
        conds:
          i < 0
            ? [...spec.conds, c]
            : spec.conds.map((x, j) => (j === i ? c : x)),
    });
  }
  function relax(i: number) {
    const n = decision?.nearMisses[i];
    if (n)
      changeSpec({
        ...spec,
        conds: spec.conds.flatMap((c, j) =>
          j === n.ci ? (n.relaxed ? [n.relaxed] : []) : [c],
        ),
      });
  }
  const vocabAlert =
    vocabState.kind === "error" ? (
      <div role="alert" className="error">
        <div>
          <strong>
            {vocabState.error.kind === "missing"
              ? "No snapshot yet."
              : "Couldn't load what the snapshot can answer."}
          </strong>
          <p>{vocabState.error.message}</p>
        </div>
        <button className="ink-button" onClick={() => setVocabAttempt((n) => n + 1)}>
          Retry
        </button>
      </div>
    ) : null;
  const errorTitle = () => {
    if (simulatedError) return "Couldn't load snapshot.";
    if (mapped.error) return "This decision could not be shown.";
    if (requestState.kind !== "error") return "Decision unavailable.";
    if (requestState.status === 400 && requestState.issues.length)
      return "The engine could not read part of this spec.";
    if (requestState.code === "no_snapshot") return "No snapshot yet.";
    if (requestState.code === "timeout") return "The decision service is taking too long.";
    if (requestState.status === null) return "Couldn't reach the decision service.";
    return `Decision unavailable${requestState.code ? ` (${requestState.code})` : ""}.`;
  };
  const errorText = () => {
    if (mapped.error) return `${mapped.error}.`;
    if (requestState.kind !== "error")
      return "The catalogue service did not respond. Your spec is kept in the link, so nothing is lost.";
    if (requestState.status === 400 && requestState.issues.length)
      return placed.some((issue) => issue.target.kind !== "spec")
        ? "Each problem is marked beside the condition or control that caused it."
        : "";
    if (requestState.code === "no_snapshot")
      return `The decision engine has no published snapshot to answer from yet. ${requestState.message}`;
    return requestState.message;
  };
  return (
    <VocabContext.Provider value={vocab}>
    <div className="decide-app" data-theme={theme}>
      <header className="global-header">
        <button
          className="brand lockup"
          aria-label="ModelSpec home"
          onClick={() => { window.location.href = "/"; }}
        >
          <BrandMark transparent={theme === "dark"} />
          <span className="wordmark">
            <b>Model</b>Spec
          </span>
        </button>
        <div className="spacer" />
        {decision && <SnapshotId snapshot={decision.snapshot} />}
        <button
          onClick={() => {
            const next = theme === "dark" ? "light" : "dark";
            setTheme(next);
            storeTheme(next);
          }}
        >
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
        <button className="primary" onClick={() => setShare(true)}>
          Share or give to my agent
        </button>
      </header>
      <main className="work">
          <BoardIntro />
          {(HUMAN_GATE_ENABLED || VISIT_GATE_ENABLED) && <HumanGate key={gateRefresh} onEnabled={setGateStatus} disabled={!vocabulary} onLookup={(token, onRemaining) => runDecision(spec, token, onRemaining)} />}
          {VISIT_GATE_ENABLED && !vocabulary && <aside className="board-answer"><VisitGate /></aside>}
          {vocabAlert}
          {vocabState.kind === "loading" && (
            <div role="status" aria-busy="true" className="loading">
              <span>Loading what the current snapshot can answer…</span>
            </div>
          )}
          {vocabulary && <FacetBoard
            key={boardGeneration}
            vocabulary={vocabulary}
            spec={boardBaseSpec}
            onSpec={changeSpec}
            selections={boardSelections}
            onSelections={changeBoardSelections}
            mustOrder={boardMustOrder}
            onMustOrder={setBoardMustOrder}
            estate={estate}
            onEstate={(next) => {
              setEstate(next);
              changeSpec(spec);
            }}
            access={access}
            onAccess={changeAccess}
            fit={decision?.explanation.feasible.length}
            may={decision?.explanation.may.length}
            notes={legacyNotes}
            onNotes={setLegacyNotes}
            refinementFallbackKeys={refinementFallbackKeys}
            onCanvasAxes={setCanvasAxes}
            onTemplate={(id) => {
              setActiveTemplateId(id);
              if (id !== null) setHasAdjustedBoard(true);
            }}
            verification={VISIT_GATE_ENABLED ? <VisitGate /> : undefined}
            answer={decision ? <AnswerBoundary resetKey={decision} onReset={resetBoard}>
              <Field
                decision={decision}
                spec={shownSpec}
                onAdd={add}
                onDismiss={(id) => setDismissed([...dismissed, id])}
                showQuestions={false}
                boardOnly
                vocabulary={vocabulary}
              />
              <section className="board-answer-head" aria-label="Facet board answer">
                <span className="eyebrow">The answer</span>
                {hasEstate(estate) && <div className="answer-pair"><div><strong>With what you have</strong><span>{estateDecision ? `${estateDecision.explanation.feasible.length} models qualify · ${estateDecision.explanation.may.length} may qualify` : estateRequest.kind === "error" || estateRequest.kind === "done" ? <>Couldn't load: <button className="text-button" onClick={() => { if (humanGateEnabled) changeSpec(spec); else { action.current = decisionAction(); setEstateRequest((current) => ({ kind: "idle", settledSpecHash: current.settledSpecHash, generation: current.generation + 1 })); } }}>retry</button></> : "Checking…"}</span></div><div><strong>If you could use anything</strong><span>{decision.explanation.feasible.length} models qualify · {decision.explanation.may.length} may qualify</span></div></div>}
                {answeredAccess === "own_software" && estateAnswer?.excludedPlans.map((plan) => <p className="board-own-software-note" role="note" key={plan.id}>{ownSoftwareNote(plan)}</p>)}
              </section>
              {hasEstate(estate) && estateAnswer
                ? <div className="answer-lists">
                    <section><strong>With what you have</strong><RankedAnswer decision={estateAnswer.decision} spec={shownSpec} vocabulary={vocabulary} access={answeredAccess} held={estate} marks={estateAnswer.marks} /></section>
                    <section><strong>If you could use anything</strong><RankedAnswer decision={decision} spec={shownSpec} vocabulary={vocabulary} access={answeredAccess} held={estate} excludedPlans={answeredAccess === "own_software" ? estateAnswer.excludedPlans : []} /></section>
                  </div>
                : <RankedAnswer decision={decision} spec={shownSpec} vocabulary={vocabulary} access={answeredAccess} held={estate} />}
              {!error && !loading && <AnswerBoundary resetKey={decision} onReset={resetBoard}>
                <Coverage decision={decision} spec={shownSpec} onSpec={changeSpec} />
              </AnswerBoundary>}
              {hostedDecision && hasAdjustedBoard && <section className="answer-feedback" aria-label="Was this answer reliable?">
                <FeedbackForm key={hostedDecision.decision_id} compact question="Was this answer reliable?" decisionId={hostedDecision.decision_id} template={activeTemplateId} page="/decide/" />
              </section>}
            </AnswerBoundary> : <section className="panel board-answer-loading" aria-live="polite">{humanGateEnabled ? "Choose your facets, then verify and look up this decision." : "The live answer will appear here."}</section>}
          />}
          {error ? (
            <div role="alert" className="error">
              <div>
                <strong>{errorTitle()}</strong>
                <p>
                  {errorText()} Results below are hidden rather than shown stale.
                </p>
                {!!specIssues.length && (
                  <ul className="issue-list">
                    {specIssues.map((issue) => (
                      <li key={issue.text}>{issue.text}</li>
                    ))}
                  </ul>
                )}
              </div>
              {!humanGateEnabled && <button
                className="ink-button"
                onClick={() => {
                  setRetried(true);
                  void runDecision(spec);
                }}
              >
                Retry
              </button>}
              {humanGateEnabled && <p>Verify again above before your next lookup.</p>}
            </div>
          ) : loading ? (
            <div role="status" aria-busy="true" className="loading">
              <div className="loading-canvas">
                <span className="skeleton" />
                <div className="skeleton" />
                <p>
                  Running decision against the current snapshot
                </p>
              </div>
              <div className="loading-cards">
                <span />
                <span />
                <span />
              </div>
            </div>
          ) : decision ? (
            <>
            {/* MODEL-298: the trade-off canvas spans the page under the facets and
                the narrowing, in its own boundary: a canvas failure hides only
                the canvas. */}
            {vocabulary && <AnswerBoundary resetKey={decision} onReset={resetBoard}>
              {hostedDecision && shownCanvasAxes ? (
                <FreeAxisCanvas
                  decision={decision}
                  rankingDecision={hostedDecision}
                  plotDecision={plotDecision}
                  vocabulary={vocabulary}
                  axes={shownCanvasAxes}
                  onAxes={(next) => {
                    if (humanGateEnabled) changeSpec(spec);
                    else action.current = decisionAction();
                    setCanvasAxes(next);
                  }}
                  onMust={setCanvasMust}
                  selections={boardSelections}
                  selected={selectedId}
                  onSelect={setSelected}
                />
              ) : (
                <Canvas
                  decision={decision}
                  spec={shownSpec}
                  axis={shownAxis}
                  onAxis={setAxis}
                  onSpec={changeSpec}
                  onAdd={add}
                  selected={selectedId}
                  onSelect={setSelected}
                  onRelax={relax}
                  boardRanked={boardRanked}
                />
              )}
            </AnswerBoundary>}
            <AnswerBoundary resetKey={decision} onReset={resetBoard}>
            <div className="results">
              <DecisionTable
                decision={decision}
                spec={shownSpec}
                selected={selectedId}
                onSelect={setSelected}
              />
              <Why
                decision={decision}
                spec={shownSpec}
                row={row}
                onRelax={relax}
                details={requestState.kind === "success" ? requestState.details : "ready"}
                onProvenance={(ev) => {
                  provTrigger.current =
                    document.activeElement instanceof HTMLElement
                      ? document.activeElement
                      : null;
                  const rect = provTrigger.current?.getBoundingClientRect();
                  setProvenance({
                    e: ev,
                    x: Math.max(
                      8,
                      Math.min(window.innerWidth - 340, rect?.left || 0),
                    ),
                    y: Math.max(
                      64,
                      Math.min(
                        window.innerHeight - 270,
                        (rect?.bottom || 0) + 6,
                      ),
                    ),
                  });
                }}
                boardRanked={boardRanked}
              />
            </div>
            </AnswerBoundary>
            </>
          ) : null}
      </main>
      <footer className="site-footer" aria-label="About ModelSpec">
        <span>ModelSpec is neutral: no referral fees, no paid placement.</span>
        <nav aria-label="Legal and API">
          <a href="/pricing/">Pricing</a>
          <a href="/method/">How we decide</a>
          <a href="/legal/neutrality/">Neutrality</a>
          <a href="/legal/terms/">Terms</a>
          <a href="/legal/privacy/">Privacy</a>
          <a href={VOCABULARY_URL.includes("/v1/vocabulary") ? "/openapi.yaml" : "/api/decision/vocabulary.json"}>Data</a>
          <a href="/feedback/">Feedback</a>
        </nav>
      </footer>
      <FeedbackLauncher page="/decide/" />
      {provenance && (
        <div
          className="provenance-popover"
          style={{ left: provenance.x, top: provenance.y }}
          role="dialog"
          aria-label="Evidence provenance"
        >
          <div className="panel-heading">
            <strong>{provenance.e.b}</strong>
            <button
              autoFocus
              aria-label="Close provenance"
              onClick={() => {
                setProvenance(null);
                provTrigger.current?.focus();
              }}
            >
              ×
            </button>
          </div>
          <dl>
            {[
              [
                "Value",
                fmtB(provenance.e.b, provenance.e.v) +
                  " " +
                  fmtCI(provenance.e.b, provenance.e),
              ],
              [
                "Measured by",
                provenance.e.who +
                  (provenance.e.by === "lab"
                    ? " (lab-reported)"
                    : " (independent)"),
              ],
              ["Effort setting", provenance.e.effort],
              ["Harness", provenance.e.harness],
              ["Date", provenance.e.date],
              ["Source", provenance.e.src],
            ].map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>
                  {k === "Source" ? (
                    <a href={v} target="_blank" rel="noreferrer">
                      {v}
                    </a>
                  ) : (
                    v
                  )}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}
      {share && (
        <Share
          humanGateEnabled={humanGateEnabled}
          spec={lastSentSpec ?? shownSpec}
          snapshot={decision?.snapshot ?? "latest"}
          axis={shownAxis}
          row={row}
          demo={false}
          refinementsFolded={refinementFallbackKeys.size > 0}
          boardPermalink={{
            spec: boardBaseSpec,
            state: {
              selections: boardSelections,
              mustOrder: boardMustOrder,
              estate,
              ...(shownCanvasAxes ? { canvas: shownCanvasAxes } : {}),
            },
          }}
          onClose={() => setShare(false)}
        />
      )}
    </div>
    </VocabContext.Provider>
  );
}

export default function App(props: { simulate?: "loading" | "error" | "none" }) {
  return <DesignedApp {...props} />;
}
