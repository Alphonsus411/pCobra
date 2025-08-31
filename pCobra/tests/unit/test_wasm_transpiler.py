from cobra.core import Lexer, Parser
from cobra.transpilers.transpiler.to_wasm import TranspiladorWasm


def test_transpilar_funcion_simple() -> None:
    codigo = """func main():\n    retorno 2 + 2\nfin"""
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    transpiler = TranspiladorWasm()
    wat = transpiler.generate_code(ast)
    assert "(func $main" in wat
    assert "(return" in wat and "4" in wat
