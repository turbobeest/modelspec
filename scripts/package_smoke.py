"""Run the installed wheel offline, outside the checkout, with mocked hosted HTTP."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from typer.testing import CliRunner

from cli.modelspec import client
from cli.modelspec.cli import app


def main():
    seen = []
    spec = {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}

    def hosted(request):
        seen.append(request)
        assert request.url.host == "api.modelspec.dev"
        assert request.headers.get("authorization") == "Bearer live_package_smoke"
        assert request.url.path == "/v1/decide"
        body = json.loads(request.content)
        assert body == expected_request, (body, expected_request)
        return httpx.Response(200, text='{"status":"ok","snapshot":"package-smoke"}')

    client._transport = httpx.MockTransport(hosted)
    runner = CliRunner()
    for args in (
        [],
        ["help", "agent", "--json"],
        ["key", "--json"],
        ["setup", "mcp", "--client", "codex", "--json"],
    ):
        result = runner.invoke(app, args)
        assert result.exit_code == 0, (args, result.output, result.exception)
    assert not seen
    result = runner.invoke(app, ["vocab", "--json"], env={"MODELSPEC_API_KEY": ""})
    assert result.exit_code == 5 and json.loads(result.stdout)["next"]
    with TemporaryDirectory() as directory:
        path = Path(directory) / "spec.json"
        for supplied_spec, expected_request in (
            (spec, {**spec, "fields": [
                "model_rank", "cost_per_task", "estimates", "p_best", "contributions", "evidence",
            ]}),
            ({**spec, "fields": None}, {**spec, "fields": None}),
            ({**spec, "fields": ["model_rank"]}, {**spec, "fields": ["model_rank"]}),
        ):
            path.write_text(json.dumps(supplied_spec))
            result = runner.invoke(
                app,
                ["decide", "--spec", str(path), "--json"],
                env={"MODELSPEC_API_KEY": "live_package_smoke"},
            )
            assert result.exit_code == 0, (supplied_spec, result.output, result.exception)
            assert result.stdout == '{"status":"ok","snapshot":"package-smoke"}'
    assert len(seen) == 3
    print("Installed wheel: offline guidance, key gate, bounded default, explicit fields "
          "and hosted response verified.")


if __name__ == "__main__":
    main()
