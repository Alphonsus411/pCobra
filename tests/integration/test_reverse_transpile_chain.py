from cobra.transpilers.reverse.from_python import ReverseFromPython
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP


def test_python_to_cobra_to_cpp():
    codigo = "x = 1\nprint(x)"
    ast = ReverseFromPython().generate_ast(codigo)
    cpp_code = TranspiladorCPP().generate_code(ast)
    esperado = "auto x = 1;\nprint(x);"
    assert cpp_code == esperado
