import py_compile
from core.ast_nodes import NodoImprimir, NodoValor
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.sandbox import ejecutar_en_sandbox


def test_transpile_python_and_execute(tmp_path):
    transpiler = TranspiladorPython()
    transpiler.codigo = ""  # Evitar importaciones que bloquea la sandbox
    ast = [NodoImprimir(NodoValor("'hola'"))]

    codigo = transpiler.generate_code(ast)

    archivo = tmp_path / "script.py"
    archivo.write_text(codigo)

    py_compile.compile(str(archivo), doraise=True)

    salida = ejecutar_en_sandbox(archivo.read_text())
    assert salida.strip() == "hola"

