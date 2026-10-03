import { useEffect, useMemo, useRef, useState } from "react";
import type { AdapterDecision, Decision, Row } from "../adapter";
import { reason, status } from "../adapter";
import type { Vocabulary } from "../vocabulary";
import type { BoardSelections } from "../facet-board/model";
import {
  canvasAxisOptions,
  isCanvasAxisId,
  type CanvasAxisId,
  type CanvasAxisOption,
} from "./canvas-axis";
import { placeLabels, plotHeight } from "./labels";

export interface CanvasAxes {
  x: CanvasAxisId;
  y: CanvasAxisId;
}

interface Datum {
  value: number;
  interval: readonly [number, number] | null;
}

interface PlotPoint {
  row: Row;
  x: Datum;
  y: Datum;
}

const modelId = (row: Row) => `${row.m.lab}/${row.m.id}`;

function factValue(value: string | number | boolean | (string | number | boolean)[] | null, date: boolean) {
  if (typeof value === "number") return value;
  if (date && typeof value === "string") {
    const parsed = Date.parse(`${value}T00:00:00Z`);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function legacyFacet(row: Row, facet: string): number | null {
  switch (facet) {
    case "offering.cost_per_task":
      return row.cost;
    case "offering.price.input":
      return row.best.o.in;
    case "offering.price.output":
      return row.best.o.out;
    case "offering.speed.time_to_first_token":
      return row.best.o.ttft;
    case "offering.speed.throughput":
      return row.tps;
    case "model.context_window":
      return row.m.ctx;
    default:
      return null;
  }
}

function axisDatum(
  row: Row,
  axis: CanvasAxisOption,
  decisions: readonly Decision[],
): Datum | null {
  const id = modelId(row);
  if (axis.kind === "capability") {
    for (const decision of decisions) {
      const estimate = decision.results
        .find((result) => result.offering.model === id)
        ?.estimates?.find((item) => item.domain === axis.key);
      if (estimate)
        return { value: estimate.value, interval: estimate.interval };
    }
    return null;
  }
  for (const decision of decisions) {
    const raw = decision.results
      .find((result) => result.offering.model === id)
      ?.contributions.find(
        (item) => item.dimension.replace(/^-/, "") === axis.key,
      )?.raw_value;
    if (typeof raw === "number") return { value: raw, interval: null };
    const candidates = decision.top.filter((candidate) => candidate.offering.model === id);
    const exact = candidates.find(
      (candidate) => candidate.offering.provider === row.best.o.provider,
    );
    const fact = (exact ?? candidates[0])?.facts.find(
      (item) => item.facet === axis.key,
    );
    const value = factValue(fact?.value ?? null, axis.valueType === "date");
    if (value !== null) return { value, interval: null };
  }
  const fallback = legacyFacet(row, axis.key);
  return fallback === null ? null : { value: fallback, interval: null };
}

const percent = (value: number) => `${Math.max(0, Math.min(1, value)) * 100}%`;

function format(option: CanvasAxisOption, value: number): string {
  if (option.valueType === "date") return new Date(value).toISOString().slice(0, 10);
  return `${Number(value.toPrecision(4)).toLocaleString("en-US")}${option.unit ? ` ${option.unit.replaceAll("_", " ")}` : ""}`;
}

function scale(values: number[]) {
  if (values.length === 0)
    return { min: 0, max: 1, at: () => 0.5, from: (ratio: number) => ratio };
  const low = Math.min(...values);
  const high = Math.max(...values);
  const pad = (high - low || Math.max(Math.abs(high), 1)) * 0.08;
  const min = low - pad;
  const max = high + pad;
  return {
    min,
    max,
    at: (value: number) => (value - min) / (max - min),
    from: (ratio: number) => min + ratio * (max - min),
  };
}

function frontierIds(
  points: readonly PlotPoint[],
  xAxis: CanvasAxisOption,
  yAxis: CanvasAxisOption,
): Set<string> {
  const qualifies = points.filter(({ row }) => row.status === 1);
  const better = (left: number, right: number, lower: boolean) =>
    lower ? left <= right : left >= right;
  const strictlyBetter = (left: number, right: number, lower: boolean) =>
    lower ? left < right : left > right;
  return new Set(
    qualifies.flatMap((candidate) => {
      const dominated = qualifies.some(
        (other) =>
          other !== candidate &&
          better(other.x.value, candidate.x.value, xAxis.lowerIsBetter) &&
          better(other.y.value, candidate.y.value, yAxis.lowerIsBetter) &&
          (strictlyBetter(
            other.x.value,
            candidate.x.value,
            xAxis.lowerIsBetter,
          ) ||
            strictlyBetter(
              other.y.value,
              candidate.y.value,
              yAxis.lowerIsBetter,
            )),
      );
      return dominated ? [] : [candidate.row.m.id];
    }),
  );
}

function mustValue(
  axis: CanvasAxisOption,
  selections: BoardSelections,
): number | null {
  const id = axis.kind === "capability" ? `capability.${axis.key}` : axis.key;
  const selection = selections[id];
  if (!selection || (selection.mode !== "must" && selection.mode !== "both"))
    return null;
  if (typeof selection.value === "number") return selection.value;
  if (axis.valueType === "date" && typeof selection.value === "string") {
    const value = Date.parse(`${selection.value}T00:00:00Z`);
    return Number.isFinite(value) ? value : null;
  }
  return null;
}

export function FreeAxisCanvas({
  decision,
  rankingDecision,
  plotDecision,
  vocabulary,
  axes,
  onAxes,
  onMust,
  selections,
  selected,
  onSelect,
}: {
  decision: AdapterDecision;
  rankingDecision: Decision;
  plotDecision: Decision | null;
  vocabulary: Vocabulary;
  axes: CanvasAxes;
  onAxes: (axes: CanvasAxes) => void;
  onMust: (axis: CanvasAxisOption, value: number | string) => void;
  selections: BoardSelections;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const options = useMemo(() => canvasAxisOptions(vocabulary), [vocabulary]);
  const byId = useMemo(
    () => new Map(options.map((option) => [option.id, option])),
    [options],
  );
  const xAxis = byId.get(axes.x) ?? options.find((option) => !option.disabled);
  const yAxis = byId.get(axes.y) ?? options.find((option) => !option.disabled);
  const plot = useRef<HTMLDivElement>(null);
  const drag = useRef<"x" | "y" | null>(null);
  const [hover, setHover] = useState<Row | null>(null);
  const [plotWidth, setPlotWidth] = useState(800);
  useEffect(() => {
    const element = plot.current;
    if (!element || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) setPlotWidth(entry.contentRect.width);
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  if (!xAxis || !yAxis) return null;
  const decisions = plotDecision
    ? [plotDecision, rankingDecision]
    : [rankingDecision];
  const measured = decision.explanation.rows.map((row) => ({
    row,
    x: axisDatum(row, xAxis, decisions),
    y: axisDatum(row, yAxis, decisions),
  }));
  const points: PlotPoint[] = measured.flatMap(({ row, x, y }) =>
    x && y ? [{ row, x, y }] : [],
  );
  const missing = measured.filter(({ x, y }) => x === null || y === null);
  const xScale = scale(
    points.flatMap(({ x }) => (x.interval ? [...x.interval] : [x.value])),
  );
  const yScale = scale(
    points.flatMap(({ y }) => (y.interval ? [...y.interval] : [y.value])),
  );
  const xMust = mustValue(xAxis, selections);
  const yMust = mustValue(yAxis, selections);
  const height = plotHeight(plotWidth);
  const frontier = frontierIds(points, xAxis, yAxis);
  const winner = decision.explanation.shortlist.top?.m.id;
  const nearMisses = new Set(
    decision.nearMisses.map((nearMiss) => nearMiss.row.m.id),
  );
  const labelRank = (row: Row) =>
    row.m.id === selected
      ? 0
      : row.m.id === winner
        ? 1
        : frontier.has(row.m.id)
          ? 2
          : nearMisses.has(row.m.id)
            ? 3
            : row.status === 0
              ? 4
              : row.m.id === hover?.m.id
                ? 5
                : null;
  const labelText = (row: Row) =>
    `${row.m.name}${row.status === 0 ? " · may qualify" : nearMisses.has(row.m.id) ? " · near miss" : ""}`;
  const labelled = points
    .flatMap((point) => {
      const rank = labelRank(point.row);
      return rank === null ? [] : [{ ...point, rank }];
    })
    .sort((left, right) => left.rank - right.rank);
  const placements = placeLabels(
    labelled.map(({ row, x, y }) => ({
      id: row.m.id,
      text: labelText(row),
      x: xScale.at(x.value),
      y: 1 - yScale.at(y.value),
    })),
    points.map(({ x, y }) => ({
      x: xScale.at(x.value),
      y: 1 - yScale.at(y.value),
    })),
    plotWidth,
    height,
  );
  const labels = labelled.map((point, index) => ({
    ...point,
    dy: placements[index].dy,
    right: placements[index].side === "left",
  }));
  const setThreshold = (axis: CanvasAxisOption, raw: number) =>
    onMust(
      axis,
      axis.valueType === "date"
        ? new Date(raw).toISOString().slice(0, 10)
        : Number(raw.toPrecision(4)),
    );
  const pointerThreshold = (
    axis: CanvasAxisOption,
    coordinate: number,
    vertical: boolean,
  ) => {
    const bounds = plot.current?.getBoundingClientRect();
    if (!bounds) return;
    const ratio = vertical
      ? 1 - (coordinate - bounds.top) / bounds.height
      : (coordinate - bounds.left) / bounds.width;
    setThreshold(axis, (vertical ? yScale : xScale).from(Math.max(0, Math.min(1, ratio))));
  };
  const dimensions: ("x" | "y")[] = ["x", "y"];
  return (
    <section className="panel canvas-panel free-axis-canvas" aria-label="Trade-off canvas">
      <div className="panel-heading">
        <span className="eyebrow">Trade-off canvas</span>
        <small>Every measured model stays visible, including models that fail a Must</small>
      </div>
      <div className="axis-selects">
        {dimensions.map((dimension) => (
          <label key={dimension}>
            {dimension}{" "}
            <select
              aria-label={`${dimension.toUpperCase()} axis`}
              value={dimension === "x" ? xAxis.id : yAxis.id}
              onChange={(event) => {
                if (isCanvasAxisId(event.target.value))
                  onAxes({ ...axes, [dimension]: event.target.value });
              }}
            >
              {options.map((option) => (
                <option key={option.id} value={option.id} disabled={option.disabled}>
                  {option.label}
                  {option.unit ? ` (${option.unit.replaceAll("_", " ")})` : ""}
                  {option.disabled ? ` — unavailable: ${option.disabledReason}` : ""}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <div className="chart-title">
        {yAxis.label}{yAxis.unit ? ` (${yAxis.unit.replaceAll("_", " ")})` : ""}
      </div>
      <div className="plot-wrap" style={{ height }}>
        <div
          className="plot"
          ref={plot}
          onPointerMove={(event) => {
            if (drag.current === "x")
              pointerThreshold(xAxis, event.clientX, false);
            if (drag.current === "y")
              pointerThreshold(yAxis, event.clientY, true);
          }}
          onPointerUp={() => {
            drag.current = null;
          }}
          onPointerCancel={() => {
            drag.current = null;
          }}
        >
          <svg
            className="frontier"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {labels
              .filter(({ dy }) => dy !== 0)
              .map(({ row, x, y, dy, right }) => (
                <line
                  key={modelId(row)}
                  className="label-leader"
                  x1={100 * xScale.at(x.value)}
                  y1={100 * (1 - yScale.at(y.value))}
                  x2={
                    100 *
                    (xScale.at(x.value) +
                      ((right ? -1 : 1) * 10) / plotWidth)
                  }
                  y2={
                    100 * (1 - yScale.at(y.value) + dy / height)
                  }
                  vectorEffect="non-scaling-stroke"
                />
              ))}
          </svg>
          {points.map(({ row, x, y }) => {
            const left = xScale.at(x.value);
            const top = 1 - yScale.at(y.value);
            const state = status(row);
            return (
              <div key={modelId(row)}>
                {x.interval && (
                  <span
                    className="axis-interval x"
                    style={{
                      left: percent(xScale.at(x.interval[0])),
                      width: percent(xScale.at(x.interval[1]) - xScale.at(x.interval[0])),
                      top: percent(top),
                    }}
                  />
                )}
                {y.interval && (
                  <span
                    className="axis-interval y"
                    style={{
                      left: percent(left),
                      top: percent(1 - yScale.at(y.interval[1])),
                      height: percent(yScale.at(y.interval[1]) - yScale.at(y.interval[0])),
                    }}
                  />
                )}
                <button
                  className={`point ${state === "Excluded" ? "excluded" : state === "May qualify" ? "may" : ""} ${selected === row.m.id ? "selected" : ""}`}
                  style={{ left: percent(left), top: percent(top) }}
                  aria-label={`${row.m.name}, ${state}, ${xAxis.label} ${format(xAxis, x.value)}, ${yAxis.label} ${format(yAxis, y.value)}`}
                  onClick={() => onSelect(row.m.id)}
                  onPointerEnter={() => setHover(row)}
                  onPointerLeave={() => setHover(null)}
                  onFocus={() => setHover(row)}
                  onBlur={() => setHover(null)}
                />
              </div>
            );
          })}
          {labels.map(({ row, x, y, dy, right }) => (
            <span
              key={modelId(row)}
              className={`point-label ${row.status === 0 ? "warn" : ""}`}
              style={{
                left: percent(xScale.at(x.value)),
                top: percent(1 - yScale.at(y.value)),
                transform: `translate(${right ? "calc(-100% - 12px)" : "12px"}, calc(-50% + ${dy}px))`,
              }}
            >
              {labelText(row)}
            </span>
          ))}
          {xAxis.mustOp && (
            <div
              role="slider"
              tabIndex={0}
              aria-label={`${xAxis.label} Must threshold`}
              aria-valuemin={xScale.min}
              aria-valuemax={xScale.max}
              aria-valuenow={xMust ?? xScale.from(0.5)}
              aria-valuetext={xMust === null ? "Not set" : format(xAxis, xMust)}
              className={`handle x-handle ${xMust === null ? "ghost" : ""}`}
              style={{ left: percent(xScale.at(xMust ?? xScale.from(0.5))) }}
              onPointerDown={(event) => {
                event.preventDefault();
                drag.current = "x";
                event.currentTarget.setPointerCapture(event.pointerId);
                pointerThreshold(xAxis, event.clientX, false);
              }}
              onKeyDown={(event) => {
                if (event.key === "ArrowLeft" || event.key === "ArrowRight")
                  setThreshold(
                    xAxis,
                    (xMust ?? xScale.from(0.5)) +
                      (event.key === "ArrowLeft" ? -1 : 1) *
                        (xScale.max - xScale.min) *
                        0.05,
                  );
              }}
            >
              <span>Drag to set a Must {xAxis.mustOp === "<=" ? "cap" : "floor"}</span>
            </div>
          )}
          {yAxis.mustOp && (
            <div
              role="slider"
              tabIndex={0}
              aria-label={`${yAxis.label} Must threshold`}
              aria-orientation="vertical"
              aria-valuemin={yScale.min}
              aria-valuemax={yScale.max}
              aria-valuenow={yMust ?? yScale.from(0.5)}
              aria-valuetext={yMust === null ? "Not set" : format(yAxis, yMust)}
              className={`handle y-handle ${yMust === null ? "ghost" : ""}`}
              style={{ top: percent(1 - yScale.at(yMust ?? yScale.from(0.5))) }}
              onPointerDown={(event) => {
                event.preventDefault();
                drag.current = "y";
                event.currentTarget.setPointerCapture(event.pointerId);
                pointerThreshold(yAxis, event.clientY, true);
              }}
              onKeyDown={(event) => {
                if (event.key === "ArrowDown" || event.key === "ArrowUp")
                  setThreshold(
                    yAxis,
                    (yMust ?? yScale.from(0.5)) +
                      (event.key === "ArrowDown" ? -1 : 1) *
                        (yScale.max - yScale.min) *
                        0.05,
                  );
              }}
            >
              <span>Drag to set a Must {yAxis.mustOp === "<=" ? "cap" : "floor"}</span>
            </div>
          )}
          {hover && (
            <div role="tooltip" className="chart-tooltip">
              <strong>{hover.m.name}</strong>
              <span>{status(hover)}{reason(hover) ? `: ${reason(hover)}` : ""}</span>
            </div>
          )}
        </div>
      </div>
      <div className="x-title">
        {xAxis.label}{xAxis.unit ? ` (${xAxis.unit.replaceAll("_", " ")})` : ""}
      </div>
      <div className="legend">
        <span><i className="legend-dot" />Qualifies</span>
        <span><i className="legend-dot excluded" />Fails a Must · remains visible</span>
        <span><i className="legend-dot may" />May qualify · missing Must data</span>
        <span><i className="legend-interval" />80% capability interval</span>
      </div>
      {missing.length > 0 && (
        <small className="not-plotted">
          Not plotted: no data — {missing.map(({ row }) => row.m.name).join(", ")}
        </small>
      )}
    </section>
  );
}
