from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import pcobra  # noqa: F401
from pcobra.cobra.transpilers.registry import get_transpilers
from cobra.core import Lexer, Parser
from tests.integration.test_transpile_semantics import obtener_salida_interprete
from tests.utils.runtime import execute_transpiled_code
from tests.utils.targets import OFFICIAL_RUNTIME_TARGETS, SUPPORTED_TARGETS

TRANSPILERS = get_transpilers()


@pytest.mark.parametrize("lang", SUPPORTED_TARGETS)
def test_generate_and_syntax(tmp_path, lang):
    src = Path("tests/data/ejemplo.co")
    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    codigo = TRANSPILERS[lang]().generate_code(ast)
    assert isinstance(codigo, str)
    assert codigo.strip() != ""

    if lang in OFFICIAL_RUNTIME_TARGETS:
        esperado = obtener_salida_interprete(src)
        salida = execute_transpiled_code(lang, codigo, tmp_path)
        assert salida == esperado
