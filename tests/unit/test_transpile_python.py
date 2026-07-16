import py_compile
from pathlib import Path
from core.ast_nodes import NodoImprimir, NodoValor
from cobra.core import Lexer, Parser
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


def test_transpile_async_top_level_esperar_uses_asyncio_run(tmp_path):
    source = Path("tests/data/async_await.co").read_text(encoding="utf-8")
    ast = Parser(Lexer(source).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "asyncio.run(principal())" in codigo
    assert "await principal()" not in codigo
    archivo = tmp_path / "async_await.py"
    archivo.write_text(codigo, encoding="utf-8")
    py_compile.compile(str(archivo), doraise=True)
