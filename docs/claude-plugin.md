# Claude Code plugin

The official ModelSpec plugin adds `modelspec:report-modelspec-answer`, a skill
for reporting ModelSpec summaries, caveats and supported next steps. Install it
inside Claude Code:

```text
/plugin marketplace add turbobeest/modelspec
/plugin install modelspec@modelspec
```

Or install it from your terminal:

```sh
claude plugin marketplace add turbobeest/modelspec
claude plugin install modelspec@modelspec
```

The plugin contains no MCP server. Configure the [ModelSpec MCP connection](api.md#mcp)
and API key separately.
