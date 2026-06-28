import pcobra
from core.ast_nodes import NodoImprimir, NodoValor
from cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_python_generacion():
    ast = [NodoImprimir(NodoValor("'hola'"))]
    codigo = TranspiladorPython().generate_code(ast)
    assert "from pcobra.cobra.core.nativos import *" in codigo
    assert "import pcobra.corelibs as _pcobra_corelibs" in codigo
    assert "import pcobra.standard_library as _pcobra_standard_library" in codigo
    assert "print(" in codigo
    assert "hola" in codigo
    compile(codigo, "<cobra-transpilado>", "exec")
