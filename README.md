<p align="center">
<img width="2816" height="797" alt="modelspec" src="https://github.com/user-attachments/assets/1e344d67-605d-4577-8ea4-84148d5ae3d5" />
</p>

ModelSpec catalogs AI models as YAML+Markdown cards, exports them to versioned JSON on Cloudflare Pages ([modelspec.dev](https://modelspec.dev)), and ranks from that export — in the browser, or offline from a local snapshot. **No database is on the serving path.**

- Site: [modelspec.dev](https://modelspec.dev) · [graph](https://modelspec.dev/graph/) · [downselect](https://modelspec.dev/downselect/)
- CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md)
- Current state: [`docs/handoff/current.md`](docs/handoff/current.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)

## Quick start

```bash
git clone https://github.com/turbobeest/modelspec.git
cd modelspec
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
modelspec snapshot fetch
modelspec offline rank coding --json
```

`snapshot fetch` is the only networked command. After that, rank and fit read the cache.

The supported interface is [`docs/cli-contract.md`](docs/cli-contract.md):

```
modelspec snapshot fetch [--origin URL]
modelspec snapshot status [--json]
modelspec offline rank <use-case> [...]
modelspec offline fit [<hardware-id>]
```

Graph commands (`stats`, `search`, `info`, `compare`, `rank`, `hardware`, …) need a local FalkorDB and are outside this contract.

## Serving path

```
models/*.md ──▶ pipeline/build.py ──▶ static JSON on Cloudflare Pages
                                      (modelspec.dev /api/*.json)
                                            │
CLI `snapshot fetch` ───────────────────────┘
Wizard / 3D graph read the same JSON in the browser.
```

FalkorDB is optional local graph exploration only. It is not required to rank, fit, or render the sites.

## Contribute

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). Sign off commits (`git commit -s`) to agree to the [`CLA.md`](CLA.md). Every fact carries a source and the date it was read; unknown means an empty field.

Cards live in `models/{provider}/{model-slug}.md`. Edit and open a PR.

## License

Two licences, because the code and the corpus want different things.

| Part | Licence |
| --- | --- |
| Code (everything outside the data directories) | MIT |
| Data (`models/`, `benchmarks/`) | CC BY-SA 4.0 |

The corpus is share-alike: build on it, including commercially, but if you redistribute it or a derivative, credit ModelSpec and publish yours under the same terms. The code is permissive so the CLI can go anywhere. Full text in [`LICENSE`](LICENSE) and [`LICENSE-DATA`](LICENSE-DATA).

Every card and page records the sources it draws on and the date each was read. Those sources keep their own licences.
