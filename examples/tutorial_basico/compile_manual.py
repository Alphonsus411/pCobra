import sys
import backend
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.core.ast_nodes import NodoValor, NodoImprimir

codigo = open('examples/tutorial_basico/hola_mundo.co').read()
lex = Lexer(codigo)
tokens = lex.analizar_token()
ast = Parser(tokens).parsear()

for nodo in ast:
    if isinstance(nodo, NodoImprimir) and isinstance(nodo.expresion, NodoValor):
        val = nodo.expresion.valor
        if isinstance(val, str) and not (val.startswith("'") or val.startswith('"')):
            nodo.expresion.valor = repr(val)

resultado = TranspiladorPython().generate_code(ast)
print(resultado)
