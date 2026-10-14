"""The source-derived checks must still reject lost plans and citations."""

import shutil

import pytest
import yaml

from tests import test_decision_model as model_tests
from tests import test_decision_snapshot as snapshot_tests


@pytest.mark.parametrize("check", ["loader", "snapshot"])
@pytest.mark.parametrize("mutation", ["missing_file", "unsourced_fact"])
def test_subscription_integration_rejects_corrupt_source(
    tmp_path,
    subscription_repository,
    check,
    mutation,
):
    root = tmp_path / "source"
    root.mkdir()
    for name in (".git", "models", "benchmarks", "hardware", "registry", "verification"):
        (root / name).symlink_to(subscription_repository / name)
    shutil.copytree(subscription_repository / "offerings", root / "offerings")
    path = root / "offerings/subscriptions/mistral.yaml"
    if mutation == "missing_file":
        path.unlink()
        message = "missing subscription files"
    else:
        rows = yaml.safe_load(path.read_text())
        fact = next(fact for row in rows for fact in row["facts"] if fact["state"] == "known")
        fact["sources"] = []
        path.write_text(yaml.safe_dump(rows))
        message = "unsourced known subscription fact"

    with pytest.raises(AssertionError, match=message):
        if check == "loader":
            model_tests.test_repository_subscription_offerings_validate_against_the_real_registry(
                root
            )
        else:
            snapshot_tests.test_production_snapshot_admits_supported_subscription_facts(
                tmp_path, root
            )
