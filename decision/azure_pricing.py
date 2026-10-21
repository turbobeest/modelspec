"""Confirm Azure's displayed USD prices against its selected-region metadata."""

from typing import Any


_SELECTED_PRICES_READY = r"""() => {
    const regions = document.querySelectorAll('#region-selector');
    const currencies = document.querySelectorAll('#currency-selector');
    if (regions.length !== 1 || currencies.length !== 1 ||
        regions[0].value !== 'us-east' || currencies[0].value !== 'usd') return false;
    const region = regions[0].value;
    for (const label of ['GPT-6 Series', 'GPT-5.6 Series', 'GPT 5.4 Series']) {
        const tables = document.querySelectorAll(`table[aria-label="${label}"]`);
        if (tables.length !== 1) return false;
        const prices = tables[0].querySelectorAll('tbody .price-data');
        if (!prices.length) return false;
        for (const price of prices) {
            let amounts;
            try {
                amounts = JSON.parse(price.getAttribute('data-amount'))?.regional;
            } catch {
                return false;
            }
            if (!amounts || !Object.hasOwn(amounts, region)) return false;
            const expected = amounts[region];
            if (typeof expected !== 'number' || !Number.isFinite(expected) || expected < 0)
                return false;
            const precision = price.getAttribute('data-decimals') ?? '4';
            if (!/^\d{1,2}$/.test(precision) || Number(precision) > 20) return false;
            const scale = 10 ** Number(precision);
            // Azure's pricing-layout formatter rounds upward after removing floating-point noise.
            const formatted = Math.ceil(Number((expected * scale).toPrecision(15))) / scale;
            if (!Number.isFinite(formatted)) return false;
            const values = price.querySelectorAll('.price-value');
            if (values.length !== 1) return false;
            const displayed = values[0].textContent.trim();
            if (!/^\$(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?$/.test(displayed)) return false;
            if (Number(displayed.slice(1).replaceAll(',', '')) !== formatted) return false;
        }
    }
    return true;
}"""


def wait_for_selected_prices(page: Any, timeout: float) -> None:
    """Wait within the recipe's remaining budget; unknown table shapes fail closed."""
    page.wait_for_function(_SELECTED_PRICES_READY, timeout=timeout * 1000)
