import os
import hashlib
import pickle
import sys

from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser


class SafeUnpickler(pickle.Unpickler):
    """Deserializador seguro que limita los módulos y clases permitidos."""

    # Módulos de los que se permitirá cargar clases
    ALLOWED_MODULES = {
        "src.core.ast_nodes",
        "src.cobra.lexico.lexer",
        "builtins",
    }

    def find_class(self, module: str, name: str):
        if module not in self.ALLOWED_MODULES:
            raise pickle.UnpicklingError(
                f"Importación no permitida: {module}.{name}"
            )
        __import__(module)
        return getattr(sys.modules[module], name)

# Directorio donde se almacenará el cache de AST. Puede modificarse con la
# variable de entorno `COBRA_AST_CACHE`.
CACHE_DIR = os.environ.get(
    "COBRA_AST_CACHE",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "cache")),
)


def _ruta_cache(codigo: str) -> str:
    """Devuelve la ruta del archivo de cache para un código determinado."""
    checksum = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{checksum}.ast")


def _ruta_tokens(codigo: str) -> str:
    """Ruta del archivo cache que almacena los tokens."""
    checksum = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{checksum}.tok")


def obtener_tokens(codigo: str):
    """Obtiene la lista de tokens reutilizando la versión en caché si existe."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    ruta = _ruta_tokens(codigo)

    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return SafeUnpickler(f).load()

    tokens = Lexer(codigo).tokenizar()
    with open(ruta, "wb") as f:
        pickle.dump(tokens, f)

    return tokens


def obtener_ast(codigo: str):
    """Obtiene el AST del codigo reutilizando una version en cache si existe."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    ruta = _ruta_cache(codigo)

    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            # Cargamos únicamente archivos generados por Cobra mediante
            # un unpickler que restringe los módulos permitidos.
            return SafeUnpickler(f).load()

    tokens = obtener_tokens(codigo)
    ast = Parser(tokens).parsear()

    with open(ruta, "wb") as f:
        # Guardamos usando ``pickle.dump``. Solo se cargarán archivos
        # generados por esta herramienta mediante ``SafeUnpickler``.
        pickle.dump(ast, f)

    return ast


def limpiar_cache():
    """Elimina todos los archivos de cache generados."""
    if not os.path.isdir(CACHE_DIR):
        return
    for nombre in os.listdir(CACHE_DIR):
        if nombre.endswith(".ast") or nombre.endswith(".tok"):
            os.remove(os.path.join(CACHE_DIR, nombre))
