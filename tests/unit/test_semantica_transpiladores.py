from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from src.cobra.transpilers.transpiler.to_c import TranspiladorC
from src.core.ast_nodes import NodoAsignacion, NodoBucleMientras, NodoValor


def test_asignacion_compartida():
    ast = [NodoAsignacion("x", NodoValor(1))]
    resultados = [
        TranspiladorPython().transpilar(ast),
        TranspiladorJavaScript().transpilar(ast),
        TranspiladorC().transpilar(ast),
    ]
    for codigo in resultados:
        assert "x" in codigo
        assert "1" in codigo


def test_bucle_mientras_compartido():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", NodoValor("x - 1"))])]
    resultados = [
        TranspiladorPython().transpilar(ast),
        TranspiladorJavaScript().transpilar(ast),
        TranspiladorC().transpilar(ast),
    ]
    for codigo in resultados:
        assert "x" in codigo
        assert "0" in codigo or "x - 1" in codigo
