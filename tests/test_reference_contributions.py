"""The contribution entry directs fresh cards to the repository that accepts them."""

import re
from datetime import date

from pipeline.data_source import DATA_PATHS, REPO_ROOT as ROOT
from scripts.data_freeze_guard import judge


def test_readme_routes_fresh_card_contributions_to_private_data():
    section = (ROOT / "README.md").read_text().split("## Contribute", 1)[1].split("## License", 1)[0]
    card_path = "models/lab/example.md"
    assert card_path.split("/", 1)[0] in DATA_PATHS
    verdict = judge([card_path], {}, None, "docs-example-card-update", date(2026, 11, 9))
    assert not verdict.ok
    target = re.search(r"Open the change against ([^.]+)\.", verdict.problems[0]).group(1)
    assert f"https://github.com/{target}" in section
    assert "frozen" in section
    assert "docs/design/data-split.md" in section
    assert "models/{provider}/{model-slug}.md" in section
    assert "Edit and open a PR." not in section
