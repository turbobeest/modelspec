"""Review metrics retain existing, newly added and removed MCP tools."""

from pipeline.agent_overhead import comparison_markdown


def test_comparison_markdown_shows_added_and_removed_tools_with_zero_columns():
    before = {
        "method": "literal-test",
        "openapi_bytes": 1000,
        "openapi_tokens": 250,
        "tools": {
            "rank": {"definition": 30, "description": 4},
            "decide": {"definition": 20, "description": 3},
        },
        "paths": {},
        "components": {},
    }
    after = {
        "method": "literal-test",
        "openapi_bytes": 1200,
        "openapi_tokens": 300,
        "tools": {
            "hardware_fit": {"definition": 50, "description": 6},
            "decide": {"definition": 25, "description": 5},
        },
        "paths": {},
        "components": {},
    }

    assert comparison_markdown(before, after) == (
        "Token method: literal-test. OpenAPI totals count the complete file. "
        "Path and schema rows count each value serialized as standalone YAML, so they "
        "do not sum to the total. MCP rows count actual SDK tools/list definitions "
        "serialized as JSON, including their schemas. No live agent or paid call is involved.\n"
        "\n| Artifact | Before | After |\n"
        "| --- | ---: | ---: |\n"
        "| OpenAPI bytes | 1,000 | 1,200 |\n"
        "| OpenAPI tokens | 250 | 300 |\n"
        "| MCP definitions, summed per tool | 50 | 75 |\n"
        "\n| MCP tool | Definition before | Definition after | Description before | Description after |\n"
        "| --- | ---: | ---: | ---: | ---: |\n"
        "| `decide` | 20 | 25 | 3 | 5 |\n"
        "| `hardware_fit` | 0 | 50 | 0 | 6 |\n"
        "| `rank` | 30 | 0 | 4 | 0 |\n"
        "\n| OpenAPI path | Tokens before | Tokens after |\n"
        "| --- | ---: | ---: |\n"
        "\n| OpenAPI schema component | Tokens before | Tokens after |\n"
        "| --- | ---: | ---: |\n"
    )
