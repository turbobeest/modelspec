<p align="center">
<img width="2816" height="797" alt="modelspec" src="https://github.com/user-attachments/assets/1e344d67-605d-4577-8ea4-84148d5ae3d5" />
</p>

ModelSpec is an analysis of alternatives for AI models: it decides which models fit a job from your requirements, sourced benchmarks and real cost, and shows its work. It reads a spec, filters models and offerings against its constraints, and explains the decision from a versioned snapshot. The catalogue starts as YAML and Markdown, then exports to JSON on Cloudflare Pages ([modelspec.dev](https://modelspec.dev)). **No database is on the serving path.**

- Site: [modelspec.dev](https://modelspec.dev) · [decide](https://modelspec.dev/decide/)
- CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md)
- Current state: [`docs/handoff/current.md`](docs/handoff/current.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)

## Use ModelSpec

Use the free, rate-limited [decision board](https://modelspec.dev/decide/).
Machines have three ways in: the keyed CLI, the
[remote MCP Worker](https://api.modelspec.dev/mcp), and the
[HTTP API](https://api.modelspec.dev/v1/decide). Decisions require a ModelSpec
API key. No data download and no local decision cache.

```sh
uvx --from modelspec-dev modelspec       # run without installing
pipx install modelspec-dev
pip install modelspec-dev
```

`pip install modelspec` is an unrelated project. Use `modelspec-dev`.
Version 0.2.0 was yanked; 0.3.0 is the thin keyed client.

Run `modelspec` or `modelspec help agent --json` for orientation,
`modelspec key` for prices and access, and `modelspec auth set` to store a key
in a 0600 file under your user config directory. `MODELSPEC_API_KEY` wins.
Then use `modelspec decide --spec FILE|-` or `modelspec decide --template ID`.
`modelspec setup mcp --client claude-desktop` prints a client configuration;
`--write` shows a diff and needs confirmation or `--yes`.

The CLI sends no telemetry and reads no provider API keys. Every error supplies
next steps. See the [agent guide](https://modelspec.dev/agents.md),
[OpenAPI](https://modelspec.dev/openapi.yaml), [pricing and keys](https://modelspec.dev/pricing/),
[decision contract](docs/decision-contract.md), and [CLI contract](docs/cli-contract.md).

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
