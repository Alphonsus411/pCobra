import os
import hashlib
import json
from dataclasses import is_dataclass, fields
from enum import Enum

# Las importaciones de ``Lexer`` y ``Parser`` se realizan de forma
# perezosa dentro de las funciones para evitar dependencias circulares
# cuando estos módulos utilizan a su vez la caché incremental.

# La caché se almacena en formato JSON para evitar la ejecución de código
# arbitrario asociada al uso de ``pickle``.


AST_NODE_CLASS_NAMES = [
    "NodoAST",
    "NodoAsignacion",
    "NodoHolobit",
    "NodoCondicional",
    "NodoBucleMientras",
    "NodoFor",
    "NodoLista",
    "NodoDiccionario",
    "NodoListaComprehension",
    "NodoDiccionarioComprehension",
    "NodoListaTipo",
    "NodoDiccionarioTipo",
    "NodoDecorador",
    "NodoFuncion",
    "NodoMetodoAbstracto",
    "NodoInterface",
    "NodoClase",
    "NodoEnum",
    "NodoMetodo",
    "NodoInstancia",
    "NodoAtributo",
    "NodoLlamadaMetodo",
    "NodoOperacionBinaria",
    "NodoOperacionUnaria",
    "NodoValor",
    "NodoIdentificador",
    "NodoLlamadaFuncion",
    "NodoHilo",
    "NodoRetorno",
    "NodoYield",
    "NodoEsperar",
    "NodoOption",
    "NodoRomper",
    "NodoContinuar",
    "NodoPasar",
    "NodoAssert",
    "NodoDel",
    "NodoGlobal",
    "NodoNoLocal",
    "NodoLambda",
    "NodoWith",
    "NodoThrow",
    "NodoTryCatch",
    "NodoImport",
    "NodoUsar",
    "NodoImportDesde",
    "NodoExport",
    "NodoPara",
    "NodoProyectar",
    "NodoTransformar",
    "NodoGraficar",
    "NodoImprimir",
    "NodoMacro",
    "NodoPattern",
    "NodoGuard",
    "NodoCase",
    "NodoSwitch",
    "NodoBloque",
    "NodoDeclaracion",
    "NodoModulo",
    "NodoExpresion",
]


# -- Serialización -----------------------------------------------------------

_NODE_CLASSES = None
_ENUM_CLASSES = None


def _get_node_classes():
    global _NODE_CLASSES
    if _NODE_CLASSES is None:
        from core import ast_nodes as _ast_nodes
        _NODE_CLASSES = {name: getattr(_ast_nodes, name) for name in AST_NODE_CLASS_NAMES}
    return _NODE_CLASSES


def _get_enum_classes():
    global _ENUM_CLASSES
    if _ENUM_CLASSES is None:
        from cobra.core.lexer import TipoToken
        _ENUM_CLASSES = {"TipoToken": TipoToken}
    return _ENUM_CLASSES


def _serialize(obj):
    from cobra.core.lexer import Token

    if is_dataclass(obj):
        data = {"__class__": obj.__class__.__name__}
        for f in fields(obj):
            data[f.name] = _serialize(getattr(obj, f.name))
        return data
    if isinstance(obj, Token):
        return {
            "__token__": True,
            "tipo": obj.tipo.value,
            "valor": obj.valor,
            "linea": obj.linea,
            "columna": obj.columna,
        }
    if isinstance(obj, Enum):
        return {"__enum__": obj.__class__.__name__, "value": obj.value}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def _deserialize(data):
    from cobra.core.lexer import Token, TipoToken

    if isinstance(data, list):
        return [_deserialize(i) for i in data]
    if isinstance(data, dict):
        if data.get("__token__"):
            return Token(
                TipoToken(data["tipo"]),
                data.get("valor"),
                data.get("linea"),
                data.get("columna"),
            )
        if "__enum__" in data:
            enum_cls = _get_enum_classes()[data["__enum__"]]
            return enum_cls(data["value"])
        if "__class__" in data:
            cls = _get_node_classes()[data["__class__"]]
            kwargs = {k: _deserialize(v) for k, v in data.items() if k != "__class__"}
            return cls(**kwargs)
        return {k: _deserialize(v) for k, v in data.items()}
    return data


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
        with open(ruta, "r", encoding="utf-8") as f:
            return _deserialize(json.load(f))

    from cobra.core import Lexer

    tokens = Lexer(codigo).tokenizar()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(_serialize(tokens), f)

    return tokens


def obtener_ast(codigo: str):
    """Obtiene el AST del codigo reutilizando una version en cache si existe."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    ruta = _ruta_cache(codigo)

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return _deserialize(json.load(f))

    tokens = obtener_tokens(codigo)
    from cobra.core import Parser

    ast = Parser(tokens).parsear()

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(_serialize(ast), f)

    return ast


# -- Almacenamiento por secciones -------------------------------------------


def _ruta_fragmento(codigo: str, ext: str) -> str:
    """Devuelve la ruta del archivo de caché para un fragmento."""
    checksum = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    frag_dir = os.path.join(CACHE_DIR, "fragmentos")
    os.makedirs(frag_dir, exist_ok=True)
    return os.path.join(frag_dir, f"{checksum}.{ext}")


def obtener_tokens_fragmento(codigo: str):
    """Devuelve los tokens de un fragmento, reutilizando la caché si existe."""
    ruta = _ruta_fragmento(codigo, "tok")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return _deserialize(json.load(f))

    from cobra.core import Lexer

    tokens = Lexer(codigo).tokenizar()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(_serialize(tokens), f)
    return tokens


def obtener_ast_fragmento(codigo: str):
    """Obtiene el AST de un fragmento reutilizando la caché si existe."""
    ruta = _ruta_fragmento(codigo, "ast")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return _deserialize(json.load(f))

    tokens = obtener_tokens_fragmento(codigo)
    from cobra.core import Parser

    ast = Parser(tokens).parsear()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(_serialize(ast), f)
    return ast


def limpiar_cache():
    """Elimina todos los archivos de cache generados."""
    if not os.path.isdir(CACHE_DIR):
        return
    for nombre in os.listdir(CACHE_DIR):
        ruta = os.path.join(CACHE_DIR, nombre)
        if os.path.isfile(ruta) and (
            nombre.endswith(".ast") or nombre.endswith(".tok")
        ):
            os.remove(ruta)
        elif os.path.isdir(ruta) and nombre == "fragmentos":
            for archivo in os.listdir(ruta):
                os.remove(os.path.join(ruta, archivo))
            os.rmdir(ruta)
