from argparse import Namespace

from pcobra.cobra.cli.commands_v2.build_cmd import BuildCommandV2
from pcobra.cobra.cli.commands_v2.test_cmd import TestCommandV2


def test_test_v2_parses_langs_before_delegating(monkeypatch):
    command = TestCommandV2()
    captured = {}

    def fake_run(args):
        captured["args"] = args
        return 0

    monkeypatch.setattr(command._legacy, "run", fake_run)

    rc = command.run(Namespace(file="sample.cobra", langs="python,rust", modo="mixto"))

    assert rc == 0
    assert captured["args"].archivo == "sample.cobra"
    assert captured["args"].lenguajes == ["python", "rust"]


def test_build_v2_defaults_target_to_python(monkeypatch):
    command = BuildCommandV2()
    captured = {}

    def fake_run(args):
        captured["args"] = args
        return 0

    monkeypatch.setattr(command._legacy, "run", fake_run)

    rc = command.run(Namespace(file="sample.cobra", target=None, targets=None, modo="mixto"))

    assert rc == 0
    assert captured["args"].tipo == "python"
    assert captured["args"].backend == "python"


def test_build_v2_requires_sqlite_key_enabled():
    assert BuildCommandV2.requires_sqlite_key is True
