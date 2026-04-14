import argparse

import pytest

from cobra.cli.commands_v2.run_cmd import RunCommandV2
from cobra.cli.commands_v2.test_cmd import TestCommandV2
from cobra.cli.target_policies import VERIFICATION_EXECUTABLE_TARGETS


def _build_subparsers() -> argparse._SubParsersAction:
    parser = argparse.ArgumentParser()
    return parser.add_subparsers(dest="command")


def test_run_v2_container_acepta_solo_targets_oficiales_runtime():
    subparsers = _build_subparsers()
    command = RunCommandV2()
    command.register_subparser(subparsers)

    parser = subparsers.choices[command.name]
    parsed = parser.parse_args(["programa.co", "--container", "rust"])
    assert parsed.container == "rust"

    with pytest.raises(SystemExit):
        parser.parse_args(["programa.co", "--container", "cpp"])


def test_test_v2_langs_es_opcional_y_usa_default_de_politica_oficial():
    subparsers = _build_subparsers()
    command = TestCommandV2()
    command.register_subparser(subparsers)

    parser = subparsers.choices[command.name]
    parsed = parser.parse_args(["programa.co"])

    assert parsed.langs == list(VERIFICATION_EXECUTABLE_TARGETS)
