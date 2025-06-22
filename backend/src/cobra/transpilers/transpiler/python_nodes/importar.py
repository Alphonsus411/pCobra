from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser


def visit_import(self, nodo):
    """Transpila una declaración de importación cargando y procesando el módulo."""
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
