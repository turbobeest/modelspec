<p align="center">
<img width="2816" height="797" alt="modelspec" src="https://github.com/user-attachments/assets/1e344d67-605d-4577-8ea4-84148d5ae3d5" />
</p>

ModelSpec is a decision engine for AI models. It reads a spec, filters models and offerings against its constraints, and explains the decision from a versioned snapshot. The catalogue starts as YAML and Markdown, then exports to JSON on Cloudflare Pages ([modelspec.dev](https://modelspec.dev)). **No database is on the serving path.**

- Site: [modelspec.dev](https://modelspec.dev) · [decide](https://modelspec.dev/decide/)
- Historical CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md)
- Current state: [`docs/handoff/current.md`](docs/handoff/current.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)

## Use ModelSpec

Use the free, rate-limited [decision board](https://modelspec.dev/decide/).
Machines use the paid [hosted API](https://api.modelspec.dev/v1/decide) or
[remote MCP Worker](https://api.modelspec.dev/mcp) with an API key.
See [the decision contract](docs/decision-contract.md) and [MCP setup](mcp/README.md).

The CLI was retired on 2026-09-30 and is no longer distributed. All PyPI
releases were yanked and the trusted publisher was removed. Its MIT source
remains here; [the CLI contract](docs/cli-contract.md) is historical.

## Serving path

```
models/*.md ──▶ pipeline/build.py ──▶ static JSON on Cloudflare Pages
                                      (modelspec.dev /api/*.json)
                                            │
Hosted API ──────────────────────────────────┘
```

FalkorDB is optional local graph exploration only. It is not required to rank, fit, or render the sites.

## Contribute

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). Sign off commits (`git commit -s`) to certify the [`DCO`](DCO) — not a copyright assignment. Every fact carries a source and the date it was read; unknown means an empty field.

Cards live in `models/{provider}/{model-slug}.md`. Edit and open a PR.

## License

Two licences, because the code and the corpus want different things.

| Part | Licence |
| --- | --- |
| Code (everything outside the data directories) | MIT |
| Data (`models/`, `benchmarks/`, `hardware/`, `hosts/`) | CC BY-SA 4.0 |

The corpus is share-alike: build on it, including commercially, but if you redistribute it or a derivative, credit ModelSpec and publish yours under the same terms. The CLI source remains MIT-licensed. Full text in [`LICENSE`](LICENSE) and [`LICENSE-DATA`](LICENSE-DATA).

Every card and page records the sources it draws on and the date each was read. Those sources keep their own licences.
