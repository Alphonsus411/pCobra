import pytest
from core.ast_nodes import (
    NodoTryCatch,
    NodoThrow,
    NodoImprimir,
    NodoIdentificador,
    NodoValor,
    NodoImport,
    NodoUsar,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_transpilar_try_catch_throw():
    nodo = NodoTryCatch(
        [NodoThrow(NodoValor("1"))],
        "e",
        [NodoImprimir(NodoIdentificador("e"))],
    )
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = (
        IMPORTS
        + "try:\n    raise Exception(1)\nexcept Exception as e:\n    print(e)\n"
    )
    assert codigo == esperado


def test_transpilar_import(tmp_path):
    mod = tmp_path / "mod.cobra"
    mod.write_text("var dato = 5")
    nodo = NodoImport(str(mod))
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = IMPORTS + "dato = 5\n"
    assert codigo == esperado


def test_transpilar_usar():
    nodo = NodoUsar("math")
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = (
        IMPORTS
        + "from pcobra.cobra.usar_loader import usar_modulo\n"
        + "_usar_exports = usar_modulo('math')\n"
        + "globals().update(dict(_usar_exports.get('simbolos', [])))\n"
    )
    assert codigo == esperado
