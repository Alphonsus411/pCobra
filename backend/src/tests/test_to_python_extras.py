import pytest
from src.core.ast_nodes import (
    NodoTryCatch,
    NodoThrow,
    NodoImprimir,
    NodoIdentificador,
    NodoValor,
    NodoImport,
    NodoUsar,
)
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilar_try_catch_throw():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    codigo = TranspiladorPython().transpilar([nodo])
    esperado = (
        "from src.core.nativos import *\n"
        "try:\n    raise Exception(1)\nexcept Exception as e:\n    print(e)\n"
    )
    assert codigo == esperado


def test_transpilar_import(tmp_path):
    mod = tmp_path / "mod.cobra"
    mod.write_text("var dato = 5")
    nodo = NodoImport(str(mod))
    codigo = TranspiladorPython().transpilar([nodo])
    esperado = "from src.core.nativos import *\ndato = 5\n"
    assert codigo == esperado


def test_transpilar_usar():
    nodo = NodoUsar("math")
    codigo = TranspiladorPython().transpilar([nodo])
    esperado = (
        "from src.core.nativos import *\n"
        "from src.cobra.usar_loader import obtener_modulo\n"
        "math = obtener_modulo('math')\n"
    )
    assert codigo == esperado
