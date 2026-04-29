from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_no_cross_command_imports import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_entre_comandos(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "from pcobra.cobra.cli.commands.compile_cmd import CompileCommand\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/cli/commands/a.py:1" in violations[0]


def test_permite_import_desde_base(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands_v2" / "ok.py",
        "from pcobra.cobra.cli.commands.base import BaseCommand\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_detecta_import_relativo_entre_comandos(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "from .compile_cmd import CompileCommand\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "pcobra.cobra.cli.commands.compile_cmd" in violations[0]
