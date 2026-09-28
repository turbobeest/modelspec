export function packCost(credits, packs) {
  if (credits <= 0) return { usd: 0, how: "" };
  const big = packs[packs.length - 1];
  const bigCount = Math.floor(credits / big.credits);
  const remainder = credits - bigCount * big.credits;
  let best = null;
  for (const pack of packs) {
    const count = remainder > 0 ? Math.ceil(remainder / pack.credits) : 0;
    const usd = count * pack.usd;
    if (best === null || usd < best.usd) best = { usd, count, pack };
  }
  const parts = [];
  if (bigCount) parts.push(`${bigCount} × ${big.credits.toLocaleString("en-US")}`);
  if (best.count) parts.push(`${best.count} × ${best.pack.credits.toLocaleString("en-US")}`);
  return { usd: bigCount * big.usd + best.usd, how: `${parts.join(" + ")} packs` };
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
