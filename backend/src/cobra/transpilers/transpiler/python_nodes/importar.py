from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from ...import_helper import load_mapped_module


def visit_import(self, nodo):
    """Transpila una declaración de importación consultando el mapeo."""
    codigo, ruta = load_mapped_module(nodo.ruta, "python")

    if ruta.endswith(".co"):
        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo += codigo + "\n"
