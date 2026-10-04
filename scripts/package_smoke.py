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
        assert json.loads(request.content) == spec
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
        assert result.exit_code == 0, result.output
    assert not seen
    result = runner.invoke(app, ["vocab", "--json"], env={"MODELSPEC_API_KEY": ""})
    assert result.exit_code == 5 and json.loads(result.stdout)["next"]
    with TemporaryDirectory() as directory:
        path = Path(directory) / "spec.json"
        path.write_text(json.dumps(spec))
        result = runner.invoke(
            app,
            ["decide", "--spec", str(path), "--json"],
            env={"MODELSPEC_API_KEY": "live_package_smoke"},
        )
        assert result.exit_code == 0, result.output
        assert result.stdout == '{"status":"ok","snapshot":"package-smoke"}'
    assert len(seen) == 1
    print("Installed wheel: offline guidance, key gate, exact Spec and hosted response verified.")


if __name__ == "__main__":
    main()
