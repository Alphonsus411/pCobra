import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch
import importlib
import types

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

if not hasattr(importlib, "ModuleType"):
    importlib.ModuleType = types.ModuleType

import pcobra  # noqa: F401
from core.interpreter import InterpretadorCobra
from cobra.core import Lexer
from cobra.core import Parser
from pcobra.cobra.transpilers.registry import get_transpilers
from tests.utils.runtime import execute_transpiled_code
from tests.utils.targets import BEST_EFFORT_INTERNAL_RUNTIME_TARGETS, OFFICIAL_RUNTIME_TARGETS

TRANSPILERS = get_transpilers()


def obtener_salida_interprete(archivo: Path) -> str:
    codigo = archivo.read_text()
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    with patch("sys.stdout", new_callable=StringIO) as out:
        InterpretadorCobra().ejecutar_ast(ast)
    return out.getvalue()


@pytest.mark.parametrize("lang", OFFICIAL_RUNTIME_TARGETS)
def test_transpile_semantics(tmp_path, lang):
    src = Path("tests/data/ejemplo.co")
    esperado = obtener_salida_interprete(src)

    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()
    codigo = TRANSPILERS[lang]().generate_code(ast)

    salida = execute_transpiled_code(lang, codigo, tmp_path)
    assert salida == esperado


@pytest.mark.experimental
@pytest.mark.parametrize("lang", BEST_EFFORT_INTERNAL_RUNTIME_TARGETS)
def test_transpile_semantics_experimental_runtime(tmp_path, lang):
    """Cobertura best-effort para runtimes no oficiales conservados manualmente."""
    src = Path("tests/data/ejemplo.co")
    esperado = obtener_salida_interprete(src)

    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()
    codigo = TRANSPILERS[lang]().generate_code(ast)

    salida = execute_transpiled_code(lang, codigo, tmp_path, allow_experimental=True)
    assert salida == esperado
