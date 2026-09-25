import { useRef, useState } from "react";
import {
  axisDefs,
  plotDomain,
  fmtB,
  fmtCI,
  status,
  reason,
  relaxLabel,
} from "../adapter";
import type { AdapterDecision, Cond, Spec, Row } from "../adapter";
import type { Axis } from "../state/spec";
export function Canvas({
  decision,
  spec,
  axis,
  onAxis,
  onSpec,
  onAdd,
  selected,
  onSelect,
  onRelax,
  compact,
}: {
  decision: AdapterDecision;
  spec: Spec;
  axis: Axis;
  onAxis: (a: Axis) => void;
  onSpec: (s: Spec) => void;
  onAdd: (c: Cond) => void;
  selected: string | null;
  onSelect: (id: string) => void;
  onRelax: (index: number) => void;
  compact: boolean;
}) {
  const plot = useRef<HTMLDivElement>(null),
    [hover, setHover] = useState<Row | null>(null),
    drag = useRef<"x" | "y" | null>(null);
  const e = decision.explanation,
    ax = axisDefs[axis],
    bd = decision.benchmarks[spec.bench],
    pd = plotDomain(e.inScope, spec, axis, bd);
  const xc = spec.conds.find((c) => c.f === axis),
    yc = spec.conds.find((c) => c.f === "bench" && c.b === spec.bench);
  const xp = pd.xv == null ? (ax.low ? 0.985 : 0.015) : pd.fx(pd.xv),
    yp = pd.yv == null ? 0.985 : pd.fy(pd.yv);
  const percent = (v: number) => Math.max(0, Math.min(1, v)) * 100 + "%";
  function setX(value: number) {
    let v = value;
    if (axis === "ctx") {
      const snaps = [
        32000, 64000, 128000, 200000, 256000, 400000, 500000, 1000000, 2000000,
      ];
      v = snaps.reduce((a, b) =>
        Math.abs(Math.log(b / value)) < Math.abs(Math.log(a / value)) ? b : a,
      );
    } else if (axis === "ttft") v = Math.round(v / 10) * 10;
    else if (axis === "tps") v = Math.round(v / 5) * 5;
    else v = Number(v.toPrecision(2));
    v = Math.max(0, v);
    const meta = { soft: xc?.soft, from: xc?.from, id: xc?.id };
    switch (axis) {
      case "ctx":
        onAdd({ ...meta, f: "ctx", min: v });
        break;
      case "tps":
        onAdd({ ...meta, f: "tps", min: v });
        break;
      case "task$":
        onAdd({ ...meta, f: "task$", max: v });
        break;
      case "in$":
        onAdd({ ...meta, f: "in$", max: v });
        break;
      case "ttft":
        onAdd({ ...meta, f: "ttft", max: v });
        break;
    }
  }
  function setY(value: number) {
    const step = bd.d === 3 ? 0.005 : bd.d === 2 ? 0.01 : 0.5;
    onAdd({
      ...(yc?.f === "bench" ? yc : {}),
      f: "bench",
      b: spec.bench,
      min: Number(Math.max(0, Math.round(value / step) * step).toFixed(bd.d)),
      indep: yc?.f === "bench" ? yc.indep : true,
    });
  }
  function move(clientX: number, clientY: number) {
    const r = plot.current?.getBoundingClientRect();
    if (!r) return;
    const clamp = (n: number) => Math.max(0, Math.min(1, n));
    if (drag.current === "x") setX(pd.xi(clamp((clientX - r.left) / r.width)));
    if (drag.current === "y") setY(pd.yi(clamp((clientY - r.top) / r.height)));
  }
  const path = decision.frontier
    .map(
      (r, i) =>
        `${i ? "L" : "M"}${100 * pd.fx(ax.get(r) ?? 0)} ${100 * pd.fy(r.cap ?? 0)}`,
    )
    .join(" ");
  const height = compact ? 300 : 460,
    placed: { y: number; a0: number; a1: number }[] = [];
  const labels = pd.values.flatMap(({ r, x, y }) => {
    if (
      r.status === -1 ||
      !(
        decision.frontier.includes(r) ||
        Object.values(e.shortlist).some(
          (s) => s && typeof s === "object" && "m" in s && s.m.id === r.m.id,
        ) ||
        r.m.id === selected ||
        status(r) === "May qualify"
      )
    )
      return [];
    const xx = pd.fx(x),
      right = xx > 0.72,
      a0 = right ? xx - 0.17 : xx,
      a1 = right ? xx : xx + 0.17;
    let dy = 0;
    for (let i = 0; i < 8; i++) {
      if (
        !placed.some(
          (p) =>
            Math.abs(p.y - (pd.fy(y) * height + dy)) < 15 &&
            p.a0 < a1 &&
            a0 < p.a1,
        )
      )
        break;
      dy += 15;
    }
    placed.push({ y: pd.fy(y) * height + dy, a0, a1 });
    return [{ r, x, y, dy, right }];
  });
  const niceStep = (span: number, n: number) => {
    const r = span / n,
      p = 10 ** Math.floor(Math.log10(r));
    return [1, 2, 2.5, 5, 10].map((m) => m * p).find((m) => m >= r) || 1;
  };
  const yTicks: number[] = [],
    ystep = niceStep(pd.y1 - pd.y0, 5);
  for (let v = Math.ceil(pd.y0 / ystep) * ystep; v <= pd.y1; v += ystep)
    yTicks.push(v);
  const xTicks: number[] = [];
  if (ax.log) {
    for (
      let n = Math.floor(Math.log10(Math.max(pd.x0, 1e-9)));
      n <= Math.ceil(Math.log10(pd.x1));
      n++
    )
      for (const m of [1, 2, 5]) {
        const v = m * 10 ** n;
        if (pd.fx(v) >= 0.02 && pd.fx(v) <= 0.98) xTicks.push(v);
      }
  } else {
    const step = niceStep(pd.x1 - pd.x0, 6);
    for (let v = Math.ceil(pd.x0 / step) * step; v <= pd.x1; v += step)
      xTicks.push(v);
  }
  const missing = e.inScope.filter((r) => ax.get(r) === null || r.cap === null);
  return (
    <section className="panel canvas-panel" aria-label="Trade-off canvas">
      <div className="panel-heading">
        <span className="eyebrow">Trade-off canvas</span>
        <small>Every point is a model, via its best qualifying offering</small>
      </div>
      <div className="axis-selects">
        <label>
          x{" "}
          <select
            aria-label="X axis"
            value={axis}
            onChange={(e) => {
              const key = e.target.value;
              if (
                key === "task$" ||
                key === "in$" ||
                key === "ttft" ||
                key === "tps" ||
                key === "ctx"
              )
                onAxis(key);
            }}
          >
            {(["task$", "in$", "ttft", "tps", "ctx"] satisfies Axis[]).map((k) => (
              <option value={k} key={k}>
                {axisDefs[k].label} ({axisDefs[k].unit})
                {decision.available_axes[k]
                  ? ""
                  : " — not available in this snapshot"}
              </option>
            ))}
          </select>
        </label>
        <label>
          y{" "}
          <select
            aria-label="Y axis"
            value={spec.bench}
            onChange={(e) => onSpec({ ...spec, bench: e.target.value })}
          >
            {Object.entries(decision.benchmarks).map(([k, b]) => (
                <option key={k} value={k}>
                  {k} ({b.unit})
                </option>
              ))}
          </select>
        </label>
      </div>
      <div className="chart-title">
        {spec.bench} ({bd.unit}
        {bd.hi ? "" : ", lower is better"})
      </div>
      <div className="plot-wrap" style={{ height }}>
        <div
          className="plot"
          ref={plot}
          onPointerMove={(ev) => {
            if (drag.current) move(ev.clientX, ev.clientY);
          }}
          onPointerUp={() => {
            drag.current = null;
          }}
          onPointerCancel={() => {
            drag.current = null;
          }}
        >
          {yTicks.map((v) => (
            <div
              key={v}
              className="grid-line"
              style={{ top: percent(pd.fy(v)) }}
            >
              <span>{fmtB(spec.bench, v).replace(/\.0%$/, "%")}</span>
            </div>
          ))}
          {xTicks.map((v) => (
            <span
              key={v}
              className="vertical-grid"
              style={{ left: percent(pd.fx(v)) }}
            />
          ))}
          {xc && (
            <div
              className="shade"
              style={{
                left: ax.low ? percent(xp) : 0,
                width: ax.low ? percent(1 - xp) : percent(xp),
                top: 0,
                bottom: 0,
              }}
            />
          )}
          {yc && (
            <div
              className="shade"
              style={{ left: 0, right: 0, top: percent(yp), bottom: 0 }}
            />
          )}
          <svg
            className="frontier"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-label="Pareto frontier"
          >
            <path
              d={decision.frontier.length > 1 ? path : ""}
              fill="none"
              stroke="var(--ink)"
              strokeWidth="2"
              vectorEffect="non-scaling-stroke"
            />
          </svg>
          {pd.values
            .filter((p) => p.r.capR?.ci != null && p.r.status !== -1)
            .map(({ r, x, y }) => (
              <span
                key={r.m.id}
                className={
                  "interval " + (status(r) === "May qualify" ? "may" : "")
                }
                style={{
                  left: percent(pd.fx(x)),
                  top: percent(pd.fy(y + (bd.hi ? 1 : -1) * (r.capR?.ci || 0))),
                  height:
                    Math.abs(
                      pd.fy(y + (r.capR?.ci || 0)) -
                        pd.fy(y - (r.capR?.ci || 0)),
                    ) *
                      100 +
                    "%",
                }}
              />
            ))}
          {pd.values.map(({ r, x, y }) => (
            <button
              key={r.m.id}
              className={`point ${r.status === -1 ? "excluded" : status(r) === "May qualify" ? "may" : r.labOnly ? "lab" : ""} ${selected === r.m.id ? "selected" : ""}`}
              style={{ left: percent(pd.fx(x)), top: percent(pd.fy(y)) }}
              aria-label={`${r.m.name}, ${status(r)}, ${spec.bench} ${fmtB(spec.bench, y)} ${r.labOnly ? "Lab-reported" : "Independent"}, ${ax.label} ${ax.fmt(x)}`}
              onClick={() => onSelect(r.m.id)}
              onPointerEnter={() => setHover(r)}
              onPointerLeave={() => setHover(null)}
              onFocus={() => setHover(r)}
              onBlur={() => setHover(null)}
            />
          ))}
          {labels.map(({ r, x, y, dy, right }) => (
            <span
              key={r.m.id}
              className={
                "point-label " + (status(r) === "May qualify" ? "warn" : "")
              }
              style={{
                left: percent(pd.fx(x)),
                top: percent(pd.fy(y)),
                transform: `translate(${right ? "calc(-100% - 12px)" : "12px"}, calc(-50% + ${dy}px))`,
              }}
            >
              {r.m.name}
              {status(r) === "May qualify"
                ? " · may qualify"
                : r.labOnly
                  ? " · lab-reported"
                  : ""}
            </span>
          ))}
          <div
            role="slider"
            tabIndex={0}
            aria-label={`${ax.label} ${ax.low ? "cap" : "minimum"}, ${ax.unit}`}
            aria-orientation="horizontal"
            aria-valuemin={Math.min(pd.x0, pd.xv ?? pd.x0)}
            aria-valuemax={Math.max(pd.x1, pd.xv ?? pd.x1)}
            aria-valuenow={pd.xv ?? pd.xi(xp)}
            aria-valuetext={pd.xv == null ? "Not set" : ax.fmt(pd.xv)}
            className={"handle x-handle " + (!xc ? "ghost" : "")}
            style={{ left: percent(xp) }}
            onPointerDown={(ev) => {
              ev.preventDefault();
              drag.current = "x";
              ev.currentTarget.setPointerCapture(ev.pointerId);
              move(ev.clientX, ev.clientY);
            }}
            onKeyDown={(ev) => {
              const d =
                ev.key === "ArrowLeft" ? -1 : ev.key === "ArrowRight" ? 1 : 0;
              if (d) {
                ev.preventDefault();
                const cur = pd.xv ?? pd.xi(xp);
                if (axis === "ctx") {
                  const sizes = [
                    32000, 64000, 128000, 200000, 256000, 400000, 500000,
                    1000000, 2000000,
                  ];
                  const next =
                    d > 0
                      ? sizes.findIndex((v) => v > cur)
                      : sizes.findLastIndex((v) => v < cur);
                  const index =
                    next < 0 ? (d > 0 ? sizes.length - 1 : 0) : next;
                  setX(
                    sizes[
                      Math.max(
                        0,
                        Math.min(
                          sizes.length - 1,
                          index + (ev.shiftKey ? d : 0),
                        ),
                      )
                    ],
                  );
                } else {
                  const positive =
                    cur > 0
                      ? cur
                      : axis === "ttft"
                        ? 10
                        : axis === "in$"
                          ? 0.01
                          : 0.001;
                  setX(
                    ax.log
                      ? positive * (ev.shiftKey ? 1.3 : 1.08) ** d
                      : cur + d * (ev.shiftKey ? 50 : 5),
                  );
                }
              }
            }}
          >
            <span
              style={{
                transform:
                  xp > 0.7
                    ? "translate(calc(-100% - 2px), -18px)"
                    : "translateY(-18px)",
              }}
            >
              {xc
                ? `${ax.low ? "≤" : "≥"} ${ax.fmt(pd.xv ?? 0)}`
                : `Drag to set a ${ax.low ? "cap" : "minimum"}`}
            </span>
          </div>
          <div
            role="slider"
            tabIndex={0}
            aria-label={`${spec.bench} floor, ${bd.unit}`}
            aria-orientation="vertical"
            aria-valuemin={pd.y0}
            aria-valuemax={pd.y1}
            aria-valuenow={pd.yv ?? pd.yi(yp)}
            aria-valuetext={
              pd.yv === null ? "Not set" : fmtB(spec.bench, pd.yv)
            }
            className={"handle y-handle " + (!yc ? "ghost" : "")}
            style={{ top: percent(yp) }}
            onPointerDown={(ev) => {
              ev.preventDefault();
              drag.current = "y";
              ev.currentTarget.setPointerCapture(ev.pointerId);
              move(ev.clientX, ev.clientY);
            }}
            onKeyDown={(ev) => {
              const d =
                ev.key === "ArrowUp" ? 1 : ev.key === "ArrowDown" ? -1 : 0;
              if (d) {
                ev.preventDefault();
                setY(
                  (pd.yv ?? pd.yi(yp)) +
                    d *
                      (bd.hi ? 1 : -1) *
                      (bd.d === 3 ? 0.005 : 0.5) *
                      (ev.shiftKey ? 10 : 1),
                );
              }
            }}
          >
            <span>
              {yc
                ? `${spec.bench} ${bd.hi ? "≥" : "≤"} ${fmtB(spec.bench, pd.yv)}${yc.f === "bench" && yc.indep ? " · independent" : ""}`
                : `Drag to set a ${spec.bench} floor`}
            </span>
          </div>
          {hover && (
            <div
              className="chart-tooltip"
              role="tooltip"
              style={{
                left: percent(pd.fx(ax.get(hover) ?? 0)),
                top: percent(pd.fy(hover.cap ?? 0)),
                transform: `translate(${pd.fx(ax.get(hover) ?? 0) > 0.6 ? "calc(-100% - 14px)" : "14px"},${pd.fy(hover.cap ?? 0) > 0.6 ? "calc(-100% - 8px)" : "8px"})`,
              }}
            >
              <strong>{hover.m.name}</strong>
              <small>
                {hover.m.labName} · via {hover.best.o.provider}
              </small>
              <span>
                {spec.bench}: {fmtB(spec.bench, hover.cap)}{" "}
                {hover.capR ? fmtCI(spec.bench, hover.capR) : "no interval"} ·{" "}
                {hover.labOnly ? "Lab-reported" : "Independent"}
              </span>
              <span>
                {ax.label}: {ax.fmt(ax.get(hover) ?? 0)}
              </span>
              <span>
                {status(hover)}
                {reason(hover)
                  ? ": " + reason(hover)
                  : " · #" + hover.rank + " on your weights"}
              </span>
            </div>
          )}
          {e.feasible.length === 0 && (
            <div className="empty-canvas">
              <strong>
                {e.may.length
                  ? `Nothing is confirmed. ${e.may.length} may qualify.`
                  : "Nothing qualifies under these conditions."}
              </strong>
              <p>These are one condition away:</p>
              {decision.nearMisses.slice(0, 3).map((n, i) => (
                <div key={n.row.m.id}>
                  <strong>{n.row.m.name}</strong>
                  <small>{n.why}</small>
                  <button onClick={() => onRelax(i)}>
                    {n.relaxed ? relaxLabel(n.relaxed) : "Drop condition"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="x-ticks">
        {xTicks.map((v) => (
          <span key={v} style={{ left: percent(pd.fx(v)) }}>
            {ax.fmt(v)}
          </span>
        ))}
      </div>
      <div className="x-title">
        {ax.label} ({ax.unit}
        {ax.log ? ", log scale" : ""})
      </div>
      <div className="winning-caption">
        Best {spec.bench} you can get at each {ax.label.toLowerCase()}{" "}
        {ax.low ? "cap" : "minimum"}
      </div>
      <div className="winning-strip">
        {decision.winning_strip.map((g, i) => (
          <span
            key={i}
            style={{
              left: (g.start / 60) * 100 + "%",
              width: (g.count / 60) * 100 + "%",
              background:
                g.row?.m.id === e.shortlist.top?.m.id
                  ? "var(--accentSoft)"
                  : g.row
                    ? "var(--surface)"
                    : "transparent",
            }}
            title={
              g.row
                ? g.row.m.name + ": " + fmtB(spec.bench, g.row.cap)
                : "Nothing qualifies"
            }
          >
            {g.count >= 5 ? g.row?.m.name : ""}
          </span>
        ))}
      </div>
      <div className="legend">
        <span>
          <i className="legend-dot" />
          Qualifies · independent
        </span>
        <span>
          <i className="legend-dot lab" />
          Qualifies · lab-reported only
        </span>
        <span>
          <i className="legend-dot may" />
          May qualify
        </span>
        <span>
          <i className="legend-dot excluded" />
          Excluded
        </span>
        <span>
          <i className="legend-interval" />
          Interval
        </span>
      </div>
      {missing.length > 0 && (
        <small className="not-plotted">
          Not plotted:{" "}
          {missing
            .map(
              (r) =>
                `${r.m.name} (${r.cap === null ? "no " + spec.bench : "no " + ax.label.toLowerCase()})`,
            )
            .join(", ")}
        </small>
      )}
    </section>
  );
}
