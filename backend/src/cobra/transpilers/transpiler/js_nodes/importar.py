from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from ...module_map import get_mapped_path

def visit_import(self, nodo):
    """Carga y transpila el módulo indicado usando el mapeo."""
    ruta = get_mapped_path(nodo.ruta, "js")

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Módulo no encontrado: {ruta}")

    if ruta.endswith(".co"):
        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo.extend(codigo.splitlines())
