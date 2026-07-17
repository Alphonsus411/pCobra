from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib


FORBIDDEN_STARTUP_MODULE_PARTS = (
    "interpreter",
    "transpiler",
    "transpilador",
)
FORBIDDEN_STARTUP_ROOTS = {"agix", "numpy", "flet"}


def _run_lightweight_global_option(option: str) -> dict[str, object]:
    probe = f"""
import contextlib
import io
import json
import sys
from pcobra import cli

stdout = io.StringIO()
with contextlib.redirect_stdout(stdout):
    result = cli.main([{option!r}])
print(json.dumps({{"result": result, "stdout": stdout.getvalue(), "modules": sorted(sys.modules)}}))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path("src").resolve())
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(completed.stdout)


def _assert_no_heavy_startup_modules(modules: list[str]) -> None:
    offenders = [
        module
        for module in modules
        if module.split(".", 1)[0] in FORBIDDEN_STARTUP_ROOTS
        or any(part in module.lower() for part in FORBIDDEN_STARTUP_MODULE_PARTS)
    ]
    assert offenders == []


def test_opciones_globales_no_cargan_runtime_pesado() -> None:
    for option in ("--help", "-h", "--version"):
        probe = _run_lightweight_global_option(option)
        assert probe["result"] == 0
        assert probe["stdout"]
        _assert_no_heavy_startup_modules(probe["modules"])


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
