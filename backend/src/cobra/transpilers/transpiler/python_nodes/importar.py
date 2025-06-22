from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from ...module_map import get_map


def visit_import(self, nodo):
    """Transpila una declaración de importación consultando el mapeo."""
    mapa = get_map()
    ruta = mapa.get(nodo.ruta, {}).get("python", nodo.ruta)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Módulo no encontrado: {ruta}")

    if ruta.endswith(".cobra"):
        lexer = Lexer(codigo)
        tokens = lexer.analizar_token()
        ast = Parser(tokens).parsear()
        for subnodo in ast:
            subnodo.aceptar(self)
    else:
        self.codigo += codigo + "\n"
