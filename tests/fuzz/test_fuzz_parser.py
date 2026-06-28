from pathlib import Path
import sys

import pytest

pytest.importorskip("hypothesis")

# Asegura que los módulos del proyecto sean importables
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from hypothesis import given, strategies as st, settings

from cobra.core import Lexer
from cobra.core import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython


# Estrategias para construir identificadores y valores simples
identificadores = st.text("xyz", min_size=1, max_size=5)

# Usamos sólo enteros para evitar ambigüedades al transpilar
valores = st.integers(min_value=0, max_value=100)


def construir_sentencia(id_: str, val: str) -> st.SearchStrategy[str]:
    """Devuelve una estrategia que genera sentencias básicas."""
    asignacion = st.just(f"var {id_} = {val}")
    imprimir = st.just(f"imprimir({val})")
    return st.one_of(asignacion, imprimir)


@st.composite
def programas(draw):
    id_ = draw(identificadores)
    val = draw(valores)
    sentencia1 = draw(construir_sentencia(id_, val))
    sentencia2 = draw(construir_sentencia(id_, val))
    return f"{sentencia1}\n{sentencia2}\n"


@pytest.mark.timeout(20)
@settings(max_examples=20, deadline=None)
@given(programas())
def test_fuzz_parser(programa: str):
    tokens = Lexer(programa).analizar_token()
    ast = Parser(tokens).parsear()
    codigo_py = TranspiladorPython().generate_code(ast)
    assert isinstance(codigo_py, str)
    assert codigo_py.strip()
    compile(codigo_py, "<cobra-fuzz>", "exec")
