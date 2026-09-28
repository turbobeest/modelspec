export function packCost(credits, packs) {
  if (credits <= 0) return { usd: 0, how: "" };

  const gcd = (left, right) => right === 0 ? left : gcd(right, left % right);
  const unit = packs.reduce((value, pack) => gcd(value, pack.credits), packs[0].credits);
  const scaled = packs.map((pack) => ({ ...pack, units: pack.credits / unit }));
  const target = Math.ceil(credits / unit);
  const limit = target + Math.max(...scaled.map((pack) => pack.units));
  const costs = Array(limit + 1).fill(Infinity);
  const previous = Array(limit + 1).fill(null);
  costs[0] = 0;

  for (let covered = 1; covered <= limit; covered += 1) {
    for (let index = 0; index < scaled.length; index += 1) {
      const pack = scaled[index];
      if (covered >= pack.units && costs[covered - pack.units] + pack.usd < costs[covered]) {
        costs[covered] = costs[covered - pack.units] + pack.usd;
        previous[covered] = index;
      }
    }
  }

  let bestCovered = target;
  for (let covered = target + 1; covered <= limit; covered += 1) {
    if (costs[covered] < costs[bestCovered]) bestCovered = covered;
  }
  const counts = Array(packs.length).fill(0);
  for (let covered = bestCovered; covered > 0;) {
    const index = previous[covered];
    counts[index] += 1;
    covered -= scaled[index].units;
  }
  const parts = counts.flatMap((count, index) => count
    ? [`${count} × ${packs[index].credits.toLocaleString("en-US")}`]
    : []);
  return { usd: costs[bestCovered], how: `${parts.join(" + ")} packs` };
}

export function calculate(data, state) {
  const monthly = Math.round(30 * (
    state.decisions * (state.full ? data.weights.decideFull : data.weights.decide)
    + state.checks * data.weights.check
  ));
  const options = [{
    name: "Pay per call (x402)",
    how: `${monthly.toLocaleString("en-US")} credits at ${rate(data.perCall)}`,
    usd: monthly * data.perCall,
  }];
  const packsOnly = packCost(monthly, data.packs);
  options.push({ name: "Packs only", how: packsOnly.how, usd: packsOnly.usd });
  for (const plan of data.plans) {
    const extra = packCost(monthly - plan.credits, data.packs);
    options.push({
      name: `${plan.name} plan`,
      how: extra.usd ? `${plan.name} + ${extra.how}` : `${plan.credits.toLocaleString("en-US")} credits a month`,
      usd: plan.usd + extra.usd,
    });
  }
  options.sort((a, b) => a.usd - b.usd);
  return { monthly, options, best: options[0] };
}

function money(value) {
  return "$" + (value >= 100
    ? Math.round(value).toLocaleString("en-US")
    : value.toFixed(2));
}

function rate(value) {
  return "$" + (value < .001 ? value.toFixed(5) : value.toFixed(4)).replace(/0+$/, "");
}

function start() {
  const node = document.getElementById("pricing-data");
  if (!node) return;
  const data = JSON.parse(node.textContent);
  const state = { decisions: 1000, full: false, checks: 0 };
  const controls = document.querySelector(".controls");
  const render = () => {
    const result = calculate(data, state);
    document.querySelector("[data-credits]").textContent = `${result.monthly.toLocaleString("en-US")} credits a month`;
    document.querySelector("[data-best-name]").textContent = result.best.name;
    document.querySelector("[data-best-cost]").textContent = money(result.best.usd);
    document.querySelector("[data-options]").innerHTML = result.options.map((option, index) =>
      `<div class="option${index === 0 ? " best" : ""}"><span>${option.name}<small>${option.how}</small></span><strong>${money(option.usd)}</strong></div>`
    ).join("");
  };
  controls.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const field = button.closest("fieldset");
    field.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    const key = field.dataset.control;
    state[key] = key === "full" ? button.dataset.value === "true" : Number(button.dataset.value);
    render();
  });
  render();
}

if (typeof document !== "undefined") start();
