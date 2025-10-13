"""Gestión de importaciones para Hololang."""

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.transpilers.common.utils import load_mapped_module


def visit_import(self, nodo):
    """Transpila una instrucción ``import`` evaluando mapeos específicos."""
    codigo, ruta = load_mapped_module(nodo.ruta, "hololang")
    if ruta.endswith(".co"):
        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        for linea in codigo.splitlines():
            if linea.strip():
                self.agregar_linea(linea.rstrip())
