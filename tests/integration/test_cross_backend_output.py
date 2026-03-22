import sys
from pathlib import Path
import importlib
import types

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

if not hasattr(importlib, "ModuleType"):
    importlib.ModuleType = types.ModuleType

import pcobra
import core.ast_nodes as core_ast_nodes
import cobra.core as cobra_core
import cobra.core.ast_nodes as cobra_ast_nodes
for nombre in dir(core_ast_nodes):
    if nombre.startswith("Nodo"):
        obj = getattr(core_ast_nodes, nombre)
        if not hasattr(cobra_ast_nodes, nombre):
            setattr(cobra_ast_nodes, nombre, obj)
        if not hasattr(cobra_core, nombre):
            setattr(cobra_core, nombre, obj)
from cobra.core import Lexer
from cobra.core import Parser
from cobra.cli.commands.compile_cmd import TRANSPILERS

from tests.utils.runtime import execute_transpiled_code
from tests.utils.targets import BEST_EFFORT_INTERNAL_RUNTIME_TARGETS, OFFICIAL_RUNTIME_TARGETS


def _collect_output_differences(tmp_path, archivo, esperados, *, langs, allow_experimental=False):
    tokens = Lexer(archivo.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    diferencias = {}
    for lang in langs:
        if lang not in esperados:
            continue
        transpiler = TRANSPILERS[lang]()
        if lang == "python":
            transpiler.codigo = ""
        try:
            codigo = transpiler.generate_code(ast)
        except NotImplementedError as e:
            diferencias[lang] = f"Error: {e}"
            continue
        try:
            salida = execute_transpiled_code(
                lang,
                codigo,
                tmp_path,
                allow_experimental=allow_experimental,
            )
        except pytest.skip.Exception:
            continue
        except Exception as e:  # pylint: disable=broad-except
            diferencias[lang] = f"Error: {e}"
            continue
        if salida != esperados[lang]:
            diferencias[lang] = salida
    return diferencias


def test_cross_backend_output(tmp_path, transpiler_case):
    """Compara únicamente los runtimes oficiales equivalentes entre backends."""
    archivo, esperados = transpiler_case

    diferencias = _collect_output_differences(
        tmp_path,
        archivo,
        esperados,
        langs=OFFICIAL_RUNTIME_TARGETS,
    )
    assert not diferencias, f"Salidas distintas: {diferencias}"


@pytest.mark.experimental
def test_cross_backend_output_experimental_best_effort(tmp_path, transpiler_case):
    """Go/Java se validan aparte como cobertura experimental, no contractual."""
    archivo, esperados = transpiler_case

    diferencias = _collect_output_differences(
        tmp_path,
        archivo,
        esperados,
        langs=BEST_EFFORT_INTERNAL_RUNTIME_TARGETS,
        allow_experimental=True,
    )
    assert not diferencias, f"Salidas experimentales distintas: {diferencias}"
