from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import pcobra  # noqa: F401
from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.core import Lexer, Parser
from tests.integration.test_transpile_semantics import (
    ejecutar_codigo,
    obtener_salida_interprete,
)
from tests.utils.targets import RUNNABLE_TARGETS, SUPPORTED_TARGETS


@pytest.mark.parametrize("lang", SUPPORTED_TARGETS)
def test_generate_and_syntax(tmp_path, lang):
    src = Path("tests/data/ejemplo.co")
    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    codigo = TRANSPILERS[lang]().generate_code(ast)
    assert isinstance(codigo, str)
    assert codigo.strip() != ""

    if lang in RUNNABLE_TARGETS:
        esperado = obtener_salida_interprete(src)
        salida = ejecutar_codigo(lang, codigo, tmp_path)
        assert salida == esperado
