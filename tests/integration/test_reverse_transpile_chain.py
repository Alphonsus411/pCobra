from cobra.transpilers.reverse.from_python import ReverseFromPython
try:
    from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
except ImportError:
    TranspiladorCPP = None

import pytest

@pytest.mark.skipif(TranspiladorCPP is None, reason="TranspiladorCPP module not found")
def test_python_to_cobra_to_cpp():
    codigo = "x = 1\nprint(x)"
    ast = ReverseFromPython().generate_ast(codigo)
    cpp_code = TranspiladorCPP().generate_code(ast)
    esperado = "auto x = 1;\nprint(x);"
    assert cpp_code == esperado
