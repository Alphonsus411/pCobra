from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_no_parallel_transpilers_registry import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_patron_transpilers_literal_fuera_allowlist(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "tools" / "bad.py",
        "TRANSPILERS = {'python': object()}\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "patrón prohibido `TRANSPILERS = {`" in violations[0]
    assert "src/pcobra/cobra/tools/bad.py:1" in violations[0]


def test_permite_patron_transpilers_literal_en_modulo_explicito(tmp_path: Path) -> None:
    _write(
        tmp_path / "tests" / "unit" / "test_transpiler_backend_regression.py",
        "TRANSPILERS = {'python': object()}\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_detecta_import_directo_registry_en_cli(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "bad.py",
        "from pcobra.cobra.transpilers.registry import get_transpilers\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "import directo de `pcobra.cobra.transpilers.registry`" in violations[0]
    assert "src/pcobra/cobra/cli/commands/bad.py:1" in violations[0]


def test_permite_fachada_cli_transpiler_registry(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "ok.py",
        "from pcobra.cobra.cli.transpiler_registry import cli_transpilers\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_detecta_import_directo_module_map_en_comandos_cli(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "bad_map.py",
        "from pcobra.cobra.imports._module_map_api import get_toml_map\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "import directo de `pcobra.cobra.imports._module_map_api`" in violations[0]
    assert "src/pcobra/cobra/cli/commands/bad_map.py:1" in violations[0]


def test_permite_cli_toml_map_en_comandos_cli(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "ok_map.py",
        "from pcobra.cobra.cli.transpiler_registry import cli_toml_map\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_detecta_catalogo_paralelo_con_nombre_contractual(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "bad_catalog.py",
        "TRANSPILER_CLASS_PATHS = {'python': ('m', 'C')}\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "catálogo paralelo prohibido `TRANSPILER_CLASS_PATHS`" in violations[0]
    assert "src/pcobra/cobra/cli/commands/bad_catalog.py:1" in violations[0]
