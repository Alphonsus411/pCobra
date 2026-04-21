from __future__ import annotations

import ast
from pathlib import Path
import tomllib


def test_cli_bootstrap_no_importa_comandos_directamente() -> None:
    cli_path = Path("src/pcobra/cobra/cli/cli.py")
    tree = ast.parse(cli_path.read_text(encoding="utf-8"))

    forbidden_prefixes = (
        "pcobra.cobra.cli.commands.",
        "pcobra.cobra.cli.commands_v2.",
    )
    allowed = {
        "pcobra.cobra.cli.commands.base",
    }

    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in allowed:
                continue
            if module.startswith(forbidden_prefixes):
                offenders.append(module)

    assert offenders == []


def test_distribucion_publica_no_expone_namespaces_legacy() -> None:
    pyproject_path = Path("pyproject.toml")
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    package_find = data["tool"]["setuptools"]["packages"]["find"]
    include = package_find.get("include", [])

    assert include == ["pcobra*"]
    assert "cobra*" not in include
    assert "core*" not in include
    assert "cli*" not in include
    assert "lsp*" not in include
    assert "bindings*" not in include


def test_script_entrypoint_cobra_se_mantiene_en_pcobra_cli_main() -> None:
    pyproject_path = Path("pyproject.toml")
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    scripts = data["project"]["scripts"]
    assert scripts["cobra"] == "pcobra.cli:main"
