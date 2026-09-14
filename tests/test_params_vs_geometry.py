"""Reject catalogue totals that cannot exist given the card's own geometry.

Hub `safetensors.total` is not always the full-weight count. AutoGLM Phone
shipped `model.safetensors.index.json` with `metadata.total_parameters: 934400`
while `metadata.total_size` described 10.29B BF16 weights; the Hub copied the
index field into `safetensors.total` and the seeder stored it. That figure then
produced fake FITS_ON throughput (MODEL-46).

The floor is a lower bound, not an estimate of the true total:

* embeddings counted once (`vocab_size * hidden_size`). Tied embeddings share
  that table, so counting it twice would false-fire on them.
* one `hidden_size ** 2` matrix per layer. That is a single attention
  projection (Q or O). GQA shrinks K/V below H×H; MoE only adds experts on
  top. Neither architecture can undercut this floor.

Cards missing `total_parameters` or any of `num_layers`, `hidden_size`,
`vocab_size` are skipped. A null is not a contradiction.
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import Architecture, ModelCard  # noqa: E402


def geometry_lower_bound(
    num_layers: int, hidden_size: int, vocab_size: int
) -> int:
    """Embeddings plus one H×H attention term per layer."""
    return vocab_size * hidden_size + num_layers * hidden_size * hidden_size


def implausibly_small(
    total_parameters: int | None,
    num_layers: int | None,
    hidden_size: int | None,
    vocab_size: int | None,
) -> bool:
    if total_parameters is None or num_layers is None or hidden_size is None:
        return False
    if vocab_size is None:
        return False
    if min(total_parameters, num_layers, hidden_size, vocab_size) <= 0:
        return False
    return total_parameters < geometry_lower_bound(
        num_layers, hidden_size, vocab_size
    )


def test_lower_bound_is_embeddings_plus_one_hxh_per_layer() -> None:
    # AutoGLM Phone geometry. 4×H×H would be ~3.3B; one H×H is the GQA-safe floor.
    bound = geometry_lower_bound(40, 4096, 151552)
    assert bound == 151552 * 4096 + 40 * 4096 * 4096
    assert bound == 1_291_845_632


def test_autoglm_shard_total_fails_its_own_geometry() -> None:
    """The Hub index field 934400 is 0.07% of the embeddings-plus-layer floor."""
    assert implausibly_small(934_400, 40, 4096, 151_552)


def test_hub_bf16_total_clears_the_same_geometry() -> None:
    """zai-org/AutoGLM-Phone-9B safetensors.parameters.BF16, not the name '9B'."""
    assert not implausibly_small(10_292_777_472, 40, 4096, 151_552)


def test_tied_embeddings_are_counted_once() -> None:
    """A tied model whose total is just the table plus one H×H per layer must pass."""
    layers, hidden, vocab = 6, 512, 50_257
    floor = geometry_lower_bound(layers, hidden, vocab)
    assert not implausibly_small(floor, layers, hidden, vocab)
    assert implausibly_small(floor - 1, layers, hidden, vocab)


def test_gqa_and_moe_totals_are_not_false_alarms() -> None:
    # Mixtral-8x7B: GQA (32/8) and 8 experts. Real Hub total is 46.7B.
    assert not implausibly_small(46_702_792_704, 32, 4096, 32_000)
    # Llama-3.2-1B-class GQA (32/8) with tied embeddings at ~1.24B.
    assert not implausibly_small(1_235_814_400, 16, 2048, 128_256)


def test_null_total_or_geometry_is_not_a_contradiction() -> None:
    assert not implausibly_small(None, 40, 4096, 151_552)
    assert not implausibly_small(934_400, None, 4096, 151_552)
    assert not implausibly_small(934_400, 40, None, 151_552)
    assert not implausibly_small(934_400, 40, 4096, None)


def _catalogue_cards() -> list[tuple[Path, ModelCard]]:
    files = [
        Path(f)
        for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
        if not f.endswith("LICENSE.md")
    ]
    return [(path, ModelCard.from_yaml_file(path)) for path in files]


def test_catalogue_totals_are_not_below_geometry_floor() -> None:
    flags: list[str] = []
    for path, card in _catalogue_cards():
        arch: Architecture = card.architecture
        if implausibly_small(
            arch.total_parameters,
            arch.num_layers,
            arch.hidden_size,
            arch.vocab_size,
        ):
            bound = geometry_lower_bound(
                arch.num_layers, arch.hidden_size, arch.vocab_size
            )
            flags.append(
                f"{card.identity.model_id} total={arch.total_parameters} "
                f"floor={bound} ({path.relative_to(REPO_ROOT)})"
            )
    assert flags == [], (
        "total_parameters is below embeddings + one H×H per layer:\n"
        + "\n".join(flags)
    )
