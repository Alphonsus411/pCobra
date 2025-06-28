import os
import hashlib
import pickle

from backend.src.cobra.lexico.lexer import Lexer
from backend.src.cobra.parser.parser import Parser

# Directorio donde se almacenará el cache de AST. Puede modificarse con la
# variable de entorno `COBRA_AST_CACHE`.
CACHE_DIR = os.environ.get(
    "COBRA_AST_CACHE",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "cache")),
)


def _ruta_cache(codigo: str) -> str:
    """Devuelve la ruta del archivo de cache para un codigo determinado."""
    checksum = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{checksum}.ast")


def obtener_ast(codigo: str):
    """Obtiene el AST del codigo reutilizando una version en cache si existe."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    ruta = _ruta_cache(codigo)

    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return pickle.load(f)

    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()

    with open(ruta, "wb") as f:
        pickle.dump(ast, f)

    return ast


def limpiar_cache():
    """Elimina todos los archivos de cache generados."""
    if not os.path.isdir(CACHE_DIR):
        return
    for nombre in os.listdir(CACHE_DIR):
        if nombre.endswith(".ast"):
            os.remove(os.path.join(CACHE_DIR, nombre))
