from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser


def visit_import(self, nodo):
    with open(nodo.ruta, "r", encoding="utf-8") as f:
        codigo = f.read()
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    for sub in ast:
        sub.aceptar(self)
