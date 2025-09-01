from cobra.core import Lexer
from cobra.core import Parser
from cobra.transpilers.common.utils import load_mapped_module


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
