import argparse

import pytest

from cobra.cli.commands_v2.run_cmd import RunCommandV2
from cobra.cli.commands_v2.build_cmd import BuildCommandV2
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


def test_build_v2_resuelve_backend_via_pipeline(monkeypatch):
    command = BuildCommandV2()
    called = {}

    monkeypatch.setattr(
        "cobra.cli.commands_v2.build_cmd.backend_pipeline.resolve_backend",
        lambda file, hints: called.setdefault(
            "resolution",
            type("R", (), {"backend": "python", "reason_for": lambda self, debug: None})(),
        ),
    )
    monkeypatch.setattr(command._legacy, "run", lambda _args: 0)

    status = command.run(
        argparse.Namespace(file="programa.co", modo="mixto", debug=False)
    )
    assert status == 0
    assert "resolution" in called


def test_run_v2_no_resuelve_backend_antes_de_delegar(monkeypatch):
    command = RunCommandV2()

    import cobra.cli.commands_v2.run_cmd as run_cmd_module

    assert not hasattr(run_cmd_module, "backend_pipeline")

    received = {}

    def _legacy_run(args):
        received["args"] = args
        return 0

    monkeypatch.setattr(command._legacy, "run", _legacy_run)

    status = command.run(
        argparse.Namespace(
            file="programa.co",
            debug=True,
            sandbox=False,
            container="python",
            formatear=False,
            modo="mixto",
        )
    )

    assert status == 0
    assert received["args"].archivo == "programa.co"
    assert not hasattr(received["args"], "backend_reason")


def test_test_v2_no_resuelve_backend_antes_de_delegar(monkeypatch):
    command = TestCommandV2()

    import cobra.cli.commands_v2.test_cmd as test_cmd_module

    assert not hasattr(test_cmd_module, "backend_pipeline")

    received = {}

    def _legacy_run(args):
        received["args"] = args
        return 0

    monkeypatch.setattr(command._legacy, "run", _legacy_run)

    status = command.run(argparse.Namespace(file="programa.co", langs=["python"], modo="mixto"))

    assert status == 0
    assert received["args"].archivo == "programa.co"
    assert received["args"].lenguajes == ["python"]
    assert not hasattr(received["args"], "backend_reason")
