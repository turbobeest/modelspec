"""The holding runbook reflects the checked-in billing flag and installed CLI."""

import re
import shlex

from typer.testing import CliRunner

from cli.modelspec.cli import app
from pipeline.data_source import REPO_ROOT as ROOT
from pipeline.worker_flags import enabled, production_vars


def test_holding_runbook_matches_checkout_flag_and_current_cli():
    text = (ROOT / "docs/handoff/holding-mode.md").read_text()
    intro = text.split("## The switch", 1)[0]
    configured = enabled(production_vars(ROOT), "BILLING_ENABLED")
    if configured:
        assert "Checkout remains closed" not in intro
    claim = re.search(r"`BILLING_ENABLED=(true|false)`", intro)
    assert claim is not None, "State the checked-in Checkout flag separately from SITE_MODE"
    assert (claim.group(1) == "true") == configured
    assert "independently of `SITE_MODE`" in intro

    examples = re.findall(r"`(modelspec [^`]+)`", text)
    assert examples
    for example in examples:
        command = shlex.split(example)[1]
        result = CliRunner().invoke(app, [command, "--help"])
        assert result.exit_code == 0, (example, result.output)
    serving = text.split("## What production serves while dark", 1)[1].split("## Billing", 1)[0]
    assert "`DATA_SPLIT_ENABLED=true`" in serving
    assert "bundled exports" in serving
    assert "thin keyed CLI" in serving
    assert "no data download" in serving
