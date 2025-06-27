from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from ...import_helper import load_mapped_module

def visit_import(self, nodo):
    """Carga y transpila el módulo indicado usando el mapeo."""
    codigo, ruta = load_mapped_module(nodo.ruta, "js")

    if ruta.endswith(".co"):
        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo.extend(codigo.splitlines())
