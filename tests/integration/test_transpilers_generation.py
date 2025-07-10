import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch
import subprocess
import shutil

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import backend  # noqa: F401
from backend.src.core.interpreter import InterpretadorCobra
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from backend.src.cli.commands.compile_cmd import TRANSPILERS
from backend.src.core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js

from tests.integration.test_transpile_semantics import (
    ejecutar_codigo,
    obtener_salida_interprete,
)


RUNTIME_LANGS = {
    "python",
    "js",
    "ruby",
    "c",
    "cpp",
    "go",
    "rust",
    "java",
}


@pytest.mark.parametrize("lang", sorted(TRANSPILERS.keys()))
def test_generate_and_syntax(tmp_path, lang):
    src = Path("tests/data/ejemplo.co")
    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    codigo = TRANSPILERS[lang]().generate_code(ast)
    assert isinstance(codigo, str)
    assert codigo.strip() != ""

    if lang in RUNTIME_LANGS:
        esperado = obtener_salida_interprete(src)
        salida = ejecutar_codigo(lang, codigo, tmp_path)
        assert salida == esperado
