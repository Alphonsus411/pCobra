"""Capa de compatibilidad para la caché incremental basada en SQLite."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import warnings
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from . import database

logger = logging.getLogger(__name__)

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

_NODE_CLASSES: dict[str, type] | None = None
_ENUM_CLASSES: dict[str, type] | None = None
_ALIAS_CONFIGURED = False
_NULL_JSON = json.dumps(None)
_FULL_TOKENS_KEY = "full_tokens"
_FRAGMENT_TOKENS_KEY = "fragment_tokens"
_FRAGMENT_AST_KEY = "fragment_ast"


def _is_token_like(obj: Any) -> bool:
    try:
        from pcobra.core.lexer import Token
    except ModuleNotFoundError:  # pragma: no cover - entornos acotados
        Token = None  # type: ignore

    if Token is not None and isinstance(obj, Token):
        return True

    if obj.__class__.__name__ != "Token":
        return False
    return all(hasattr(obj, attr) for attr in ("tipo", "valor", "linea", "columna"))


def _serialize_token(obj: Any) -> dict[str, Any]:
    tipo = getattr(obj, "tipo", None)
    tipo_valor = getattr(tipo, "value", tipo)
    return {
        "__token__": True,
        "tipo": tipo_valor,
        "valor": getattr(obj, "valor", None),
        "linea": getattr(obj, "linea", None),
        "columna": getattr(obj, "columna", None),
    }


def _get_node_classes() -> dict[str, type]:
    global _NODE_CLASSES
    if _NODE_CLASSES is None:
        from . import ast_nodes as _ast_nodes

        _NODE_CLASSES = {name: getattr(_ast_nodes, name) for name in AST_NODE_CLASS_NAMES}
    return _NODE_CLASSES


def _get_enum_classes() -> dict[str, type]:
    global _ENUM_CLASSES
    if _ENUM_CLASSES is None:
        from pcobra.core.lexer import TipoToken

        _ENUM_CLASSES = {"TipoToken": TipoToken}
    return _ENUM_CLASSES


def _serialize(obj: Any) -> Any:
    if is_dataclass(obj):
        data: dict[str, Any] = {"__class__": obj.__class__.__name__}
        for f in fields(obj):
            data[f.name] = _serialize(getattr(obj, f.name))
        return data
    if _is_token_like(obj):
        return _serialize_token(obj)
    if isinstance(obj, Enum):
        return {"__enum__": obj.__class__.__name__, "value": obj.value}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def _deserialize(data: Any) -> Any:
    from pcobra.core.lexer import Token, TipoToken

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


def _ensure_alias_configured() -> None:
    global _ALIAS_CONFIGURED
    if _ALIAS_CONFIGURED:
        return

    alias = os.environ.get("COBRA_AST_CACHE")
    if not alias:
        _ALIAS_CONFIGURED = True
        return

    db_path_env = database.COBRA_DB_PATH_ENV
    key_env = database.SQLITE_DB_KEY_ENV
    existing_path = os.environ.get(db_path_env)
    if existing_path:
        warnings.warn(
            "El uso de 'COBRA_AST_CACHE' está obsoleto; utilice 'COBRA_DB_PATH' en su lugar.",
            DeprecationWarning,
            stacklevel=2,
        )
        _ALIAS_CONFIGURED = True
        return

    target = Path(alias).expanduser()
    if target.suffix.lower() == ".db":
        db_path = target
    elif target.is_dir() or not target.suffix:
        db_path = target / "cache.db"
    else:
        db_path = target.with_suffix(".db")

    os.environ[db_path_env] = str(db_path)
    warnings.warn(
        "El uso de 'COBRA_AST_CACHE' está obsoleto; utilice 'COBRA_DB_PATH' en su lugar.",
        DeprecationWarning,
        stacklevel=2,
    )
    if os.environ.get(key_env) is None:
        warnings.warn(
            "El alias heredado 'COBRA_AST_CACHE' no configura la clave 'SQLITE_DB_KEY'; "
            "defínela antes de acceder a la caché.",
            RuntimeWarning,
            stacklevel=2,
        )
    logger.debug("Alias 'COBRA_AST_CACHE' redirigido a %s", db_path)
    _ALIAS_CONFIGURED = True


def _checksum(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _encode_payload(obj: Any) -> str:
    return json.dumps(_serialize(obj), ensure_ascii=False)


def _decode_payload(serialized: str) -> Any:
    return _deserialize(json.loads(serialized))


def _with_connection(action: Callable[[Any], Any]) -> Any:
    _ensure_alias_configured()
    with database.get_connection() as conn:
        return action(conn)


def _load_ast(hash_key: str) -> Any | None:
    def _query(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT ast_json FROM ast_cache WHERE hash = ?", (hash_key,))
        row = cursor.fetchone()
        return row[0] if row else None

    serialized = _with_connection(_query)
    if not serialized or serialized == _NULL_JSON:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Cache AST sin datos para hash %s", hash_key)
        return None

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Cache AST encontrada para hash %s", hash_key)
    return _decode_payload(serialized)


def _store_ast(hash_key: str, source: str, ast_obj: Any) -> None:
    payload = _encode_payload(ast_obj)

    def _insert(conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ast_cache(hash, source, ast_json)
            VALUES (?, ?, ?)
            ON CONFLICT(hash) DO UPDATE
            SET source = excluded.source,
                ast_json = excluded.ast_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (hash_key, source, payload),
        )
        conn.commit()

    _with_connection(_insert)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("AST almacenado para hash %s", hash_key)


def _load_fragment(hash_key: str, fragment_name: str) -> Any | None:
    def _query(conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM ast_fragments WHERE hash = ? AND fragment_name = ?",
            (hash_key, fragment_name),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    serialized = _with_connection(_query)
    if serialized is None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Cache de fragmento '%s' ausente para hash %s", fragment_name, hash_key
            )
        return None

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Cache de fragmento '%s' recuperada para hash %s", fragment_name, hash_key
        )
    return _decode_payload(serialized)


def _store_fragment(hash_key: str, source: str, fragment_name: str, payload_obj: Any) -> None:
    payload = _encode_payload(payload_obj)

    def _insert(conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO ast_cache(hash, source, ast_json)
            VALUES (?, ?, ?)
            """,
            (hash_key, source, _NULL_JSON),
        )
        cursor.execute(
            "UPDATE ast_cache SET source = ? WHERE hash = ?",
            (source, hash_key),
        )
        cursor.execute(
            """
            INSERT OR REPLACE INTO ast_fragments(hash, fragment_name, content)
            VALUES (?, ?, ?)
            """,
            (hash_key, fragment_name, payload),
        )
        conn.commit()

    _with_connection(_insert)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Fragmento '%s' almacenado para hash %s", fragment_name, hash_key
        )


def obtener_tokens(codigo: str):
    """Obtiene los tokens reutilizando la caché persistida si existe."""

    hash_key = _checksum(codigo)
    tokens = _load_fragment(hash_key, _FULL_TOKENS_KEY)
    if tokens is not None:
        return tokens

    from pcobra.core import Lexer

    tokens = Lexer(codigo).tokenizar()
    _store_fragment(hash_key, codigo, _FULL_TOKENS_KEY, tokens)
    return tokens


def obtener_ast(codigo: str):
    """Obtiene el AST reutilizando la caché persistida si existe."""

    hash_key = _checksum(codigo)
    ast = _load_ast(hash_key)
    if ast is not None:
        return ast

    tokens = obtener_tokens(codigo)
    from pcobra.core import Parser

    ast = Parser(tokens).parsear()
    _store_ast(hash_key, codigo, ast)
    return ast


def obtener_tokens_fragmento(codigo: str):
    """Obtiene los tokens de un fragmento reutilizando la caché si existe."""

    hash_key = _checksum(codigo)
    tokens = _load_fragment(hash_key, _FRAGMENT_TOKENS_KEY)
    if tokens is not None:
        return tokens

    from pcobra.core import Lexer

    tokens = Lexer(codigo).tokenizar()
    _store_fragment(hash_key, codigo, _FRAGMENT_TOKENS_KEY, tokens)
    return tokens


def obtener_ast_fragmento(codigo: str):
    """Obtiene el AST de un fragmento reutilizando la caché si existe."""

    hash_key = _checksum(codigo)
    ast = _load_fragment(hash_key, _FRAGMENT_AST_KEY)
    if ast is not None:
        return ast

    tokens = obtener_tokens_fragmento(codigo)
    from pcobra.core import Parser

    ast = Parser(tokens).parsear()
    _store_fragment(hash_key, codigo, _FRAGMENT_AST_KEY, ast)
    return ast


def limpiar_cache(*, vacuum: bool = False) -> None:
    """Elimina todas las entradas de la caché persistida."""

    def _wipe(conn):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ast_fragments")
        cursor.execute("DELETE FROM ast_cache")
        conn.commit()
        if vacuum:
            conn.execute("VACUUM")

    _with_connection(_wipe)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Caché de AST limpiada (vacuum=%s)", vacuum)
