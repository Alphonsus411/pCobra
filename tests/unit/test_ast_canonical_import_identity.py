"""Contratos de colección para preservar una única identidad canónica del AST."""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

from pcobra.core import ast_nodes


ROOT = Path(__file__).resolve().parents[2]
NEW_IMPORT_CONTRACT_TESTS = (Path(__file__).resolve(),)
CANONICAL_MODULE_NAMES = (
    "pcobra.core.ast_nodes",
    "pcobra.core.interpreter",
    "pcobra.core.parser",
    "pcobra.cobra.core.ast_nodes",
    "pcobra.cobra.core.interpreter",
    "pcobra.cobra.core.parser",
    "pcobra.cobra.transpilers.transpiler.to_js",
    "pcobra.cobra.transpilers.transpiler.to_python",
    "pcobra.cobra.transpilers.transpiler.to_rust",
)
FORBIDDEN_IMPORT_SURFACES = ("core.ast_nodes", "cobra.core")
CANONICAL_MODULES = {
    name: importlib.import_module(name)
    for name in CANONICAL_MODULE_NAMES
}


def test_clases_ast_activas_proceden_del_modulo_canonico() -> None:
    canonical_class = ast_nodes.NodoAST

    assert canonical_class.__module__ == "pcobra.core.ast_nodes"
    for name, module in CANONICAL_MODULES.items():
        exported_class = getattr(module, "NodoAST", None)
        if exported_class is not None:
            assert exported_class is canonical_class, name
            assert exported_class.__module__ == "pcobra.core.ast_nodes", name


def test_modulos_oficiales_tienen_una_sola_clave_canonica() -> None:
    # Un proceso limpio evita que los contratos de compatibilidad legacy de
    # otros casos contaminen sys.modules y simulen una segunda carga oficial.
    script = f"""
import importlib
import pathlib
import sys

names = {CANONICAL_MODULE_NAMES!r}
modules = {{name: importlib.import_module(name) for name in names}}
for canonical_name, module in modules.items():
    module_path = pathlib.Path(module.__file__).resolve()
    names_for_same_file = {{
        name
        for name, loaded in sys.modules.items()
        if getattr(loaded, '__file__', None)
        and pathlib.Path(loaded.__file__).resolve() == module_path
    }}
    assert module.__name__ == canonical_name
    assert names_for_same_file == {{canonical_name}}, (canonical_name, names_for_same_file)
    assert canonical_name.startswith('pcobra.')
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_import_legacy_ast_reutiliza_identidad_canonica_en_ambos_ordenes() -> None:
    clases = ("NodoAST", "NodoValor", "NodoAsignacion", "NodoFuncion", "NodoUsar")
    ordenes = (
        ("pcobra.core.ast_nodes", "core.ast_nodes"),
        ("core.ast_nodes", "pcobra.core.ast_nodes"),
    )

    for primero, segundo in ordenes:
        script = f"""
import importlib

primero = importlib.import_module({primero!r})
segundo = importlib.import_module({segundo!r})
canonical = importlib.import_module('pcobra.core.ast_nodes')
legacy = importlib.import_module('core.ast_nodes')

assert canonical is legacy, (canonical, legacy)
for nombre in {clases!r}:
    assert getattr(canonical, nombre) is getattr(legacy, nombre), nombre
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr


def test_pruebas_nuevas_no_importan_superficies_legacy() -> None:
    violations: list[str] = []

    for path in NEW_IMPORT_CONTRACT_TESTS:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported_names = (node.module,)
            else:
                continue

            for imported_name in imported_names:
                if any(
                    imported_name == surface or imported_name.startswith(f"{surface}.")
                    for surface in FORBIDDEN_IMPORT_SURFACES
                ):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno} -> {imported_name}"
                    )

    assert violations == []
