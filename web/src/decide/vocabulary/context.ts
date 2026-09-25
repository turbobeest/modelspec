// What the components ask of the vocabulary. Demo mode answers from the
// fictional catalogue; real mode from the published vocabulary.json.
import { createContext, useContext } from "react";
import {
  FACETS,
  TYPES,
  label as fictionalLabel,
  relaxLabel as fictionalRelaxLabel,
} from "../adapter";
import { BENCH } from "../engine/catalogue";
import type { BenchDef, Cond, Facet, TypeKey, Weights } from "../engine/types";
import type { Axis } from "../state/spec";
import { renderContractCondition } from "../adapter/condition-label";
import { contractCondition } from "../adapter/view-model";
import {
  facetOptions,
  offeredAxes,
  offeredBenchmarks,
  offeredTypes,
  offeredWeights,
} from "./index";
import type { Vocabulary } from "./index";

export interface DecideVocab {
  vocabulary: Vocabulary | null;
  label(c: Cond): string;
  relaxLabel(c: Cond): string;
  benchName(id: string): string;
  facetOptions: Facet[];
  types: Partial<Record<TypeKey, string>>;
  axes: Axis[];
  weightKeys: (keyof Weights)[];
  /** The y-axis choices, with their units and direction. */
  benchmarks: Record<string, BenchDef>;
}

const ALL_TYPES = Object.keys(TYPES) as TypeKey[];

export const fictionalVocab: DecideVocab = {
  vocabulary: null,
  label: fictionalLabel,
  relaxLabel: fictionalRelaxLabel,
  benchName: (id) => id,
  facetOptions: FACETS,
  types: TYPES,
  axes: ["task$", "in$", "ttft", "tps", "ctx"],
  weightKeys: ["cap", "cost", "speed"],
  benchmarks: BENCH,
};

const UNIT_NAMES: Readonly<Record<string, string>> = { percent: "%" };

export function realVocab(v: Vocabulary): DecideVocab {
  const benchmarks = offeredBenchmarks(v);
  const label = (c: Cond) => renderContractCondition(contractCondition(c));
  return {
    vocabulary: v,
    label,
    relaxLabel: (c) => "Relax to " + label(c).replace(/^.*?: /, ""),
    benchName: (id) => benchmarks.find((b) => b.id === id)?.name ?? id,
    facetOptions: facetOptions(v),
    types: offeredTypes(v),
    axes: offeredAxes(v),
    weightKeys: offeredWeights(v),
    benchmarks: Object.fromEntries(
      benchmarks.map((b) => [
        b.id,
        {
          unit: b.unit ? (UNIT_NAMES[b.unit] ?? b.unit) : "unit not recorded",
          pct: b.unit === "percent",
          d: 2,
          hi: b.higher_is_better,
          types: ALL_TYPES,
        },
      ]),
    ),
  };
}

export const VocabContext = createContext<DecideVocab>(fictionalVocab);
export const useVocab = () => useContext(VocabContext);
