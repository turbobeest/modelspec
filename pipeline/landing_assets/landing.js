(() => {
  const data = JSON.parse(document.getElementById("landing-data").textContent);
  const svg = document.getElementById("plot");
  svg.style.transition = "opacity .22s ease";
  const caption = document.getElementById("plot-caption");
  const ns = "http://www.w3.org/2000/svg";
  const mobile = () => innerWidth < 900;
  const el = (name, attrs = {}, text = "") => {
    const node = document.createElementNS(ns, name);
    for (const [key, value] of Object.entries(attrs))
      node.setAttribute(key, value);
    node.textContent = text;
    return node;
  };
  const leader = data.models.find((model) => model.id === data.leader_id);
  const cheapest = data.models.find((model) => model.id === data.cheapest_id);
  const tiedOthers = data.models.filter((model) => model.tied).length - 1;
  const money = (value) => `$${value.toFixed(3)}`;
  const priceTick = (value) => {
    const decimals = Math.max(0, -Math.floor(Math.log10(value)) + 1);
    return `$${value.toFixed(decimals)}`;
  };
  const captions = [
    `${data.models.length} language models, by coding ability and cost per task.`,
    `The top estimate: ${leader.name}, at ${money(leader.cost)} a task. The one you would probably pick.`,
    `The evidence can't tell ${tiedOthers} of the other ${data.models.length - 1} apart from it. Each bar is the range the evidence allows.`,
    `${cheapest.name} is in that tie at ${money(cheapest.cost)} a task: ${data.ratio.toFixed(1)}× less, for a difference the evidence can't measure.`,
  ];
  let stage = matchMedia("(prefers-reduced-motion: reduce)").matches ? 3 : 0;
  const x = (cost) =>
    56 +
    ((Math.log(cost) - Math.log(data.axes.cost_min)) /
      (Math.log(data.axes.cost_max) - Math.log(data.axes.cost_min))) *
      580;
  const y = (value) =>
    500 -
    ((value - data.axes.capability_min) /
      (data.axes.capability_max - data.axes.capability_min)) *
      460;
  function draw() {
    svg.replaceChildren(
      el("rect", { width: 680, height: 560, fill: "#0E1A30", rx: 6 }),
      el("line", {
        x1: 56,
        y1: 20,
        x2: 56,
        y2: 500,
        stroke: "#F2C94C",
        "stroke-width": 2,
      }),
      el("line", {
        x1: 56,
        y1: 500,
        x2: 660,
        y2: 500,
        stroke: "#3FB68B",
        "stroke-width": 3,
      }),
    );
    for (const cost of data.axes.cost_ticks) {
      const px = x(cost);
      svg.append(
        el("line", { x1: px, y1: 20, x2: px, y2: 500, stroke: "#1d2c48" }),
        el(
          "text",
          {
            x: px,
            y: 524,
            fill: "#8795ad",
            "font-size": 13,
            "text-anchor": "middle",
            "font-family": "JetBrains Mono, monospace",
          },
          priceTick(cost),
        ),
      );
    }
    for (const capability of data.axes.capability_ticks) {
      const py = y(capability);
      svg.append(
        el("line", { x1: 56, y1: py, x2: 660, y2: py, stroke: "#1d2c48" }),
        el(
          "text",
          {
            x: 48,
            y: py + 4,
            fill: "#8795ad",
            "font-size": 12,
            "text-anchor": "end",
            "font-family": "JetBrains Mono, monospace",
          },
          capability.toFixed(1),
        ),
      );
    }
    svg.append(
      el(
        "text",
        {
          x: 358,
          y: 552,
          fill: "#8795ad",
          "font-size": 13,
          "text-anchor": "middle",
        },
        "cost per coding task (40K tokens in, 4K out)",
      ),
      el(
        "text",
        {
          x: 20,
          y: 260,
          fill: "#8795ad",
          "font-size": 13,
          "text-anchor": "middle",
          transform: "rotate(-90 20 260)",
        },
        `coding ability, estimated from ${data.benchmark_count} benchmarks`,
      ),
    );
    for (const model of data.models) {
      const lead = model.id === leader.id,
        cheap = model.id === cheapest.id;
      let color = "#5AA9EC",
        opacity = 1,
        r = 6,
        bar = 0;
      if (stage >= 1) {
        if (lead) {
          color = "#F2C94C";
          r = 8;
          bar = 0.9;
        } else opacity = 0.45;
      }
      if (stage >= 2 && model.tied && !lead) {
        color = "#3FB68B";
        r = 6.5;
        opacity = 1;
        bar = 0.7;
      }
      if (stage >= 2 && !model.tied) {
        color = "#3a4a68";
        opacity = 0.35;
      }
      if (stage >= 3 && !cheap && !lead) {
        opacity = model.tied ? 0.4 : 0.25;
        bar = model.tied ? 0.3 : 0;
      }
      if (stage >= 3 && cheap) {
        color = "#3FB68B";
        r = 9;
        bar = 1;
      }
      svg.append(
        el("line", {
          class: "bar",
          x1: x(model.cost),
          y1: y(model.low),
          x2: x(model.cost),
          y2: y(model.high),
          stroke: color,
          "stroke-width": 3,
          "stroke-linecap": "round",
          opacity: bar,
        }),
        el("circle", {
          class: "dot",
          cx: x(model.cost),
          cy: y(model.estimate),
          r,
          fill: color,
          opacity,
        }),
      );
    }
    if (stage >= 1 && !mobile())
      svg.append(
        el(
          "text",
          {
            x: x(leader.cost) + 12,
            y: y(leader.estimate) - 10,
            fill: "#EEF2F7",
            "font-size": 14,
            "font-weight": 600,
          },
          `${leader.name}, ${money(leader.cost)}`,
        ),
      );
    if (stage >= 3 && !mobile())
      svg.append(
        el(
          "text",
          {
            x: x(cheapest.cost) + 12,
            y: y(cheapest.estimate) + 26,
            fill: "#EEF2F7",
            "font-size": 14,
            "font-weight": 600,
          },
          `${cheapest.name}, ${money(cheapest.cost)}`,
        ),
      );
    const mobileCaptions = [
      `${data.models.length} models, by coding ability and cost.`,
      `Top estimate: ${leader.name}, ${money(leader.cost)} a task.`,
      `${tiedOthers} of the other ${data.models.length - 1} can't be told apart from it.`,
      `${cheapest.name} is in the tie at ${money(cheapest.cost)}: ${data.ratio.toFixed(1)}× less.`,
    ];
    caption.textContent = mobile() ? mobileCaptions[stage] : captions[stage];
    document.querySelectorAll(".chips span").forEach((chip) => {
      if (Number(chip.dataset.stage) <= stage) chip.dataset.active = "";
      else delete chip.dataset.active;
    });
    if (mobile()) svg.setAttribute("viewBox", "0 0 680 560");
  }
  draw();
  if (stage !== 3)
    setInterval(() => {
      svg.style.opacity = ".35";
      setTimeout(() => {
        stage = (stage + 1) % 4;
        draw();
        svg.style.opacity = "1";
      }, 220);
    }, 2600);
  document.getElementById("pick-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const model = data.models.find(
      (row) => row.id === document.getElementById("model-pick").value,
    );
    const tie = model.tied ? "is in" : "is not in";
    const difference = (model.cost - cheapest.cost) * 10000;
    const relation =
      difference === 0
        ? "has the same monthly cost as"
        : `${difference < 0 ? "saves" : "costs"} $${Math.abs(difference).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })} ${difference < 0 ? "against" : "more than"}`;
    document.getElementById("pick-result").textContent =
      `${model.name} ${tie} the tie with the top estimate. It costs ${money(model.cost)} per task. At 10,000 tasks, it ${relation} the cheapest tied model, ${cheapest.name}.`;
  });
})();
