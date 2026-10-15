"""The published recipe uses real CLI syntax and a registry-backed Spec."""

import json
import re
import shlex
from html.parser import HTMLParser

import pytest
import typer
from typer.core import TyperGroup
from typer.main import get_command

from cli.modelspec.cli import app
from cli.modelspec.spec import validate_spec
from decision.templates import template_by_id
from pipeline import live
from tests.test_holding import trees  # noqa: F401


class CodeBlocks(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.blocks = []
        self.current = None
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        if tag == "code":
            self.current = ""

    def handle_data(self, data):
        if self.current is not None:
            self.current += data

    def handle_endtag(self, tag):
        if tag == "code" and self.current is not None:
            self.blocks.append(self.current)
            self.current = None


@pytest.fixture(scope="module")
def recipe(trees):
    page = trees["live"] / "modelspec/orchestrators/index.html"
    assert page.is_file(), "the live build must publish /orchestrators/"
    return page.read_text(encoding="utf-8")


def parse_command(line):
    """Walk Click's actual group parsers without invoking keyed callbacks."""
    name, *args = shlex.split(line)
    assert name == "modelspec"
    command = get_command(app)
    parent = None
    while True:
        context = command.make_context(name, args, parent=parent)
        if not isinstance(command, TyperGroup):
            assert not context.args
            return context.params
        remaining = [*context._protected_args, *context.args]
        name, command, args = command.resolve_command(context, remaining)
        parent = context


def test_every_published_command_parses_with_the_cli(recipe):
    commands = []
    for block in CodeBlocks(recipe).blocks:
        if block.startswith("modelspec "):
            commands.extend(block.splitlines())
        else:
            commands.extend(re.findall(r"`(modelspec [^`]+)`", block))
    assert commands, "the recipe must contain executable CLI examples"
    params = [parse_command(command) for command in commands]
    assert any(row.get("router_format") == "litellm" for row in params)
    assert any(row.get("router_format") == "openrouter" for row in params)
    assert any(row.get("router_format") == "json" for row in params)
    assert any(row.get("to") for row in params)
    assert any(row.get("client") for row in params)
    assert any(row.get("rating") for row in params)


@pytest.mark.parametrize("command", [
    "modelspec imaginary-command", "modelspec decide --invented-flag value",
    "modelspec setup imaginary-subcommand",
])
def test_command_check_rejects_nonexistent_commands_and_flags(command):
    with pytest.raises(typer.Exit):
        parse_command(command)


def test_example_spec_validates_against_bundled_decide_request(recipe):
    specs = [json.loads(block) for block in CodeBlocks(recipe).blocks
             if block.lstrip().startswith("{")]
    assert len(specs) == 1, "publish one complete worked Spec"
    validate_spec(specs[0])
    assert specs[0] == template_by_id("coding-balanced")["spec"]


def test_recipe_is_discoverable_and_has_structured_data(recipe, trees):
    tree = trees["live"] / "modelspec"
    url = "https://modelspec.dev/orchestrators/"
    assert f'<link rel="canonical" href="{url}">' in recipe
    assert 'data-structured-data>' in recipe
    assert '"@type":"BreadcrumbList"' in recipe
    assert '<h1>' in recipe
    assert url in (tree / "sitemap.xml").read_text()
    assert url in (tree / "llms.txt").read_text()
    assert url in (tree / "agents.md").read_text()
    assert live.dead_links(tree) == []
