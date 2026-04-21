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

    assert any("import entre comandos no permitido" in item for item in violations)
    assert any("patrón *_cmd no permitido" in item for item in violations)
    assert any("src/pcobra/cobra/cli/commands/a.py:1" in item for item in violations)


def test_no_aplica_regla_en_commands_v2(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands_v2" / "run_cmd.py",
        "from pcobra.cobra.cli.commands_v2.build_cmd import BuildCommandV2\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_permite_import_desde_base(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands_v2" / "ok.py",
        "from pcobra.cobra.cli.commands.base import BaseCommand\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_permite_solo_basecommand_desde_base(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "ok.py",
        "from pcobra.cobra.cli.commands.base import BaseCommand\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_rechaza_import_desde_base_que_no_es_basecommand(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "bad.py",
        "from pcobra.cobra.cli.commands.base import _normalize_name\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "import entre comandos no permitido" in violations[0]
    assert "src/pcobra/cobra/cli/commands/bad.py:1" in violations[0]


def test_detecta_import_relativo_a_otro_comando(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "bad.py",
        "from .compile_cmd import CompileCommand\n",
    )

    violations = find_violations(tmp_path)

    assert any("import entre comandos no permitido" in item for item in violations)
    assert any("patrón *_cmd no permitido" in item for item in violations)
    assert any("src/pcobra/cobra/cli/commands/bad.py:1" in item for item in violations)


def test_detecta_import_directo_registry_en_comando(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "from pcobra.cobra.transpilers.registry import get_transpilers\n",
    )

    violations = find_violations(tmp_path)

    assert "import directo no permitido" in violations[0]
    assert "src/pcobra/cobra/cli/commands/a.py:1" in violations[0]


def test_detecta_constante_transpilers_en_comando(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "TRANSPILERS = {'python': object()}\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "constante local no permitida en comandos (TRANSPILERS)" in violations[0]
    assert "src/pcobra/cobra/cli/commands/a.py:1" in violations[0]


def test_detecta_constante_backends_en_comando(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "a.py",
        "BACKENDS = {'python': object()}\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "constante local no permitida en comandos (BACKENDS)" in violations[0]
