import { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { prepareDecisionRequest } from "../src/decide/adapter/request-spec";
import { mapDecisionToViewModel } from "../src/decide/adapter/view-model";
import { AgentHandoff } from "../src/decide/components/AgentHandoff";
import { DecisionTable } from "../src/decide/components/DecisionTable";
import { FreeAxisCanvas } from "../src/decide/components/FreeAxisCanvas";
import type { CanvasAxisOption } from "../src/decide/components/canvas-axis";
import { FacetBoard } from "../src/decide/facet-board/FacetBoard";
import { RankedAnswer } from "../src/decide/facet-board/RankedAnswer";
import { TemplatePicker } from "../src/decide/facet-board/TemplatePicker";
import {
  allocateBoardWeights,
  boardToSpec,
  nextMustOrder,
  refinementSelectionId,
  sanitizeBoardState,
} from "../src/decide/facet-board/model";
import type { BoardUrlState, FacetSelection } from "../src/decide/facet-board/model";
import { templateCanvasAxes } from "../src/decide/facet-board/templates";
import type { ActiveTemplate } from "../src/decide/facet-board/templates";
import type { VocabRefinement, VocabTemplate } from "../src/decide/vocabulary";
import { realVocab, VocabContext } from "../src/decide/vocabulary/context";
import { evidenceLink, initialSelection, selectTemplate, vocabulary } from "./data";
import { PrototypeShell, usePrototypeDecision } from "./shared";

const vocab = realVocab(vocabulary);

function PrototypeC() {
  const [selection, setSelection] = useState(initialSelection);
  const [activeTemplate, setActiveTemplate] = useState<ActiveTemplate | null>(() => ({
    id: selection.template.id,
    refinement: null,
  }));
  const [templatesOpen, setTemplatesOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [notes, setNotes] = useState<string[]>([]);
  const result = usePrototypeDecision(selection);
  const decision = useMemo(() => result.kind === "ready"
    ? mapDecisionToViewModel(result.decision, selection.spec, {
      axis: "task$",
      dismissed: [],
      benchmarks: vocab.benchmarks,
      models: vocabulary.models,
      providers: vocabulary.providers,
    })
    : null, [result, selection.spec]);
  const axes = selection.board.canvas ?? templateCanvasAxes(selection.template, vocabulary);

  function updateBoard(board: BoardUrlState) {
    const sanitized = sanitizeBoardState(board, vocabulary);
    setNotes(sanitized.notes);
    setSelection((current) => ({
      ...current,
      board: sanitized,
      spec: boardToSpec(current.spec, vocabulary, sanitized.selections, sanitized.mustOrder),
    }));
  }

  function applyTemplate(template: VocabTemplate, refinement: VocabRefinement | null) {
    const next = selectTemplate(template);
    if (refinement) {
      const selections = allocateBoardWeights(vocabulary, {
        ...next.board.selections,
        [refinementSelectionId(refinement.id)]: {
          mode: "prefer",
          reason: `Subcategory: ${refinement.name}.`,
        },
      }).selections;
      const board = sanitizeBoardState({ ...next.board, selections }, vocabulary);
      setSelection({ ...next, board, spec: boardToSpec(next.spec, vocabulary, board.selections, board.mustOrder) });
      setNotes(board.notes);
    } else {
      setSelection(next);
      setNotes([]);
    }
    setActiveTemplate({ id: template.id, refinement: refinement?.id ?? null });
    setTemplatesOpen(false);
    setSelectedModel(null);
  }

  function setCanvasMust(axis: CanvasAxisOption, value: number | string) {
    if (!axis.mustOp) return;
    const id = axis.kind === "capability" ? `capability.${axis.key}` : axis.key;
    const current = selection.board.selections[id];
    const next: FacetSelection = {
      ...current,
      mode: current?.mode === "prefer" || current?.mode === "both" ? "both" : "must",
      op: axis.mustOp,
      value,
    };
    updateBoard({
      ...selection.board,
      selections: allocateBoardWeights(vocabulary, { ...selection.board.selections, [id]: next }).selections,
      mustOrder: nextMustOrder(selection.board.mustOrder, selection.board.selections, id, next),
    });
  }

  return <PrototypeShell variant="c">
    <VocabContext.Provider value={vocab}>
      <style>{`.proto-c-refine .template-picker, .proto-c-refine .estate-strip { display: none; }`}</style>
      <section className="proto-hero">
        <p className="proto-kicker">Free for people · No paid placement. Sourced.</p>
        <h1>Which AI model fits your job?</h1>
        <p>Start with a template. See the answer, then refine what matters to you.</p>
      </section>

      <TemplatePicker
        vocabulary={vocabulary}
        active={activeTemplate}
        open={templatesOpen}
        onOpen={setTemplatesOpen}
        onApply={applyTemplate}
        onClear={() => {
          updateBoard({ ...selection.board, selections: {}, mustOrder: [] });
          setActiveTemplate(null);
        }}
      />

      <section className="proto-c-answer" aria-labelledby="proto-c-answer-heading" aria-live="polite" aria-busy={result.kind === "loading"}>
        <div className="proto-c-answer-heading">
          <h2 id="proto-c-answer-heading">The answer</h2>
          <a className="proto-primary" href={evidenceLink(selection)}>See the full evidence</a>
        </div>
        {result.kind === "loading" && <p role="status">Checking this job against the evidence…</p>}
        {result.kind === "error" && <p role="alert">{result.message}</p>}
        {decision && <RankedAnswer decision={decision} spec={selection.spec} vocabulary={vocabulary} />}
      </section>

      <details className="proto-expander proto-c-refine">
        <summary>Refine</summary>
        <p>Set requirements and preferences. The answer updates as you change them.</p>
        <FacetBoard
          vocabulary={vocabulary}
          spec={selection.spec}
          onSpec={(spec) => setSelection((current) => ({ ...current, spec }))}
          selections={selection.board.selections}
          onSelections={(selections) => setSelection((current) => ({ ...current, board: { ...current.board, selections } }))}
          mustOrder={selection.board.mustOrder}
          onMustOrder={(mustOrder) => setSelection((current) => ({ ...current, board: { ...current.board, mustOrder } }))}
          estate={selection.board.estate}
          onEstate={(estate) => setSelection((current) => ({ ...current, board: { ...current.board, estate } }))}
          activeTemplate={activeTemplate}
          onTemplate={setActiveTemplate}
          notes={notes}
          onNotes={setNotes}
          pending={result.kind === "loading"}
        />
      </details>

      <details className="proto-expander proto-c-evidence">
        <summary>Evidence</summary>
        <p>Compare the trade-offs and inspect every offering, including those that miss a requirement.</p>
        {decision && result.kind === "ready" && <>
          {axes && <FreeAxisCanvas
            decision={decision}
            rankingDecision={result.decision}
            plotDecision={null}
            vocabulary={vocabulary}
            axes={axes}
            onAxes={(canvas) => setSelection((current) => ({ ...current, board: { ...current.board, canvas } }))}
            onMust={setCanvasMust}
            selections={selection.board.selections}
            selected={selectedModel}
            onSelect={setSelectedModel}
          />}
          <DecisionTable decision={decision} spec={selection.spec} selected={selectedModel} onSelect={setSelectedModel} />
        </>}
      </details>

      <details className="proto-expander">
        <summary>For your agent</summary>
        <p>Human lookup is free. CLI, API and MCP access needs an API key.</p>
        <AgentHandoff spec={prepareDecisionRequest(vocabulary, selection.spec, "summary").decisionSpec} />
      </details>
    </VocabContext.Provider>
  </PrototypeShell>;
}

const root = document.getElementById("root");
if (!root) throw new Error("Prototype C needs a root element.");
createRoot(root).render(<PrototypeC />);
