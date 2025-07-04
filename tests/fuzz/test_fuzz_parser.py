from pathlib import Path
import sys

# Asegura que los módulos del proyecto sean importables
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from hypothesis import given, strategies as st

from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.core.sandbox import ejecutar_en_sandbox


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


@given(programas())
def test_fuzz_parser(programa: str):
    tokens = Lexer(programa).analizar_token()
    ast = Parser(tokens).parsear()
    codigo_py = TranspiladorPython().transpilar(ast)
    # Eliminar importaciones globales que RestrictedPython no permite
    codigo_py = "\n".join(
        linea for linea in codigo_py.splitlines() if not linea.startswith("from ")
    )
    try:
        ejecutar_en_sandbox(codigo_py)
    except KeyError:
        # No hubo llamadas a print en el código generado
        pass
