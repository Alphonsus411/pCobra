from src.core.lexer import Lexer
from src.core.parser import Parser

def visit_import(self, nodo):
    """Carga y transpila el módulo indicado."""
    try:
        with open(nodo.ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Módulo no encontrado: {nodo.ruta}")

    lexer = Lexer(codigo)
    tokens = lexer.analizar_token()
    ast = Parser(tokens).parsear()
    for subnodo in ast:
        subnodo.aceptar(self)
