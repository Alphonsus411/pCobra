"""Gestión centralizada de la base de datos SQLitePlus para pCobra.

Este módulo encapsula la inicialización perezosa de ``SQLitePlus`` evitando
importaciones directas de los submódulos ``core`` y ``utils`` del paquete
``sqliteplus-enhanced``. Además, expone utilidades de alto nivel para
almacenar y recuperar ASTs, limpiar la caché y persistir el estado de
"qualia" manteniendo compatibilidad con la configuración existente basada en
variables de entorno.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import sqlite3
import sys
import threading
import types
import warnings
from contextlib import contextmanager
from dataclasses import is_dataclass, asdict
from importlib import util as importlib_util
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import Any, Iterable, Mapping

__all__ = [
    "DatabaseDependencyError",
    "DatabaseKeyError",
    "DEFAULT_DB_PATH",
    "SQLITE_DB_KEY_ENV",
    "get_connection",
    "store_ast",
    "load_ast",
    "clear_cache",
    "save_qualia_state",
]


class DatabaseDependencyError(RuntimeError):
    """Error lanzado cuando ``sqliteplus-enhanced`` no está disponible."""


class DatabaseKeyError(RuntimeError):
    """Error lanzado cuando la clave o ruta configurada no es válida."""


SQLITE_DB_KEY_ENV = "SQLITE_DB_KEY"
COBRA_DB_PATH_ENV = "COBRA_DB_PATH"

_default_home = Path.home() / ".cobra" / "sqliteplus"
DEFAULT_DB_PATH = (_default_home / "core.db").expanduser()

_SQLITEPLUS_CLASS = None
_SQLITEPLUS_INSTANCE = None
_TABLES_READY = False
_INIT_LOCK = threading.Lock()
_DB_LOCK = threading.Lock()

_PATH_PREFIXES = ("path:", "file:")


def _looks_like_path(value: str) -> bool:
    """Heurística sencilla para determinar si un valor parece una ruta."""

    if not value:
        return False
    candidate = value.strip()
    if _looks_like_base64_token(candidate):
        return False
    if candidate.startswith(("/", "./", "../", "~")):
        return True
    if candidate.endswith(".db"):
        return True
    seps = {os.sep}
    if os.altsep:
        seps.add(os.altsep)
    return any(sep in candidate for sep in seps)


def _looks_like_base64_token(value: str) -> bool:
    """Detecta valores que parecen pertenecer claramente a una clave base64."""

    candidate = value.strip()
    if len(candidate) < 16:
        return False
    std_alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    url_alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=")
    if all(ch in std_alphabet for ch in candidate):
        normalized = candidate
    elif all(ch in url_alphabet for ch in candidate):
        normalized = candidate.replace("-", "+").replace("_", "/")
    else:
        return False

    padding = len(normalized) % 4
    if padding:
        normalized = normalized + "=" * (4 - padding)
    try:
        base64.b64decode(normalized, validate=True)
    except (binascii.Error, ValueError):
        return False
    return True


def _load_sqliteplus_class():
    global _SQLITEPLUS_CLASS
    if _SQLITEPLUS_CLASS is not None:
        return _SQLITEPLUS_CLASS

    try:
        dist = distribution("sqliteplus-enhanced")
    except PackageNotFoundError:  # pragma: no cover - dependencia ausente
        warnings.warn(
            "'sqliteplus-enhanced' no está instalado; se utilizará una base de datos SQLite "
            "simplificada sin cifrado.",
            RuntimeWarning,
        )

        class SQLitePlusFallback:
            def __init__(self, db_path: str, cipher_key: str | None = None):
                self._db_path = db_path
                self._cipher_key = cipher_key

            def get_connection(self) -> sqlite3.Connection:
                return sqlite3.connect(self._db_path)

        _SQLITEPLUS_CLASS = SQLitePlusFallback
        return _SQLITEPLUS_CLASS

    module_path = dist.locate_file("utils/sqliteplus_sync.py")
    if not Path(module_path).exists():  # pragma: no cover - instalación dañada
        raise DatabaseDependencyError(
            "No se pudo localizar 'utils/sqliteplus_sync.py' dentro de 'sqliteplus-enhanced'."
        )

    # El módulo depende de ``sqliteplus.utils.constants`` pero el paquete no se
    # exporta como paquete instalable. Creamos entradas mínimas en ``sys.modules``
    # para satisfacer esas importaciones sin tocar directamente los paquetes
    # originales.
    constants_name = "sqliteplus.utils.constants"
    if constants_name not in sys.modules:
        constants_path = Path(dist.locate_file("utils/constants.py"))
        if not constants_path.exists():  # pragma: no cover - instalación dañada
            raise DatabaseDependencyError(
                "No se encontró 'utils/constants.py' en sqliteplus-enhanced."
            )
        constants_spec = importlib_util.spec_from_file_location(
            constants_name, constants_path
        )
        if constants_spec is None or constants_spec.loader is None:  # pragma: no cover
            raise DatabaseDependencyError(
                "No se pudo cargar 'sqliteplus.utils.constants'."
            )
        constants_module = importlib_util.module_from_spec(constants_spec)
        constants_spec.loader.exec_module(constants_module)
        utils_module = sys.modules.setdefault(
            "sqliteplus.utils", types.ModuleType("sqliteplus.utils")
        )
        utils_module.__path__ = [str(constants_path.parent)]
        setattr(utils_module, "constants", constants_module)
        package_module = sys.modules.setdefault(
            "sqliteplus", types.ModuleType("sqliteplus")
        )
        setattr(package_module, "utils", utils_module)
        sys.modules[constants_name] = constants_module

    spec = importlib_util.spec_from_file_location(
        "sqliteplus_utils_sync", module_path
    )
    if spec is None or spec.loader is None:  # pragma: no cover - casos extremos
        raise DatabaseDependencyError(
            "No se pudo cargar dinámicamente 'SQLitePlus' desde sqliteplus-enhanced."
        )

    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _SQLITEPLUS_CLASS = getattr(module, "SQLitePlus")
    return _SQLITEPLUS_CLASS


def _resolve_paths() -> tuple[Path, str | None]:
    """Resuelve la ruta de la base de datos y la clave de cifrado (si aplica)."""

    raw_key = os.environ.get(SQLITE_DB_KEY_ENV)
    if raw_key is None:
        raise DatabaseKeyError(
            "La variable de entorno 'SQLITE_DB_KEY' es obligatoria para configurar la base de datos."
        )

    env_path = os.environ.get(COBRA_DB_PATH_ENV)
    cipher_key = raw_key or None
    path_value = None
    path_source = None

    if env_path:
        path_value = env_path
        path_source = "environment"
    else:
        for prefix in _PATH_PREFIXES:
            if raw_key.startswith(prefix):
                path_value = raw_key[len(prefix) :].strip()
                cipher_key = None
                path_source = "prefix"
                break

    if path_value:
        if not _looks_like_path(path_value):
            warnings.warn(
                "El valor utilizado para la ruta de la base de datos no parece una ruta válida: %s"
                % path_value,
                RuntimeWarning,
            )
        db_path = Path(path_value).expanduser()
    else:
        if _looks_like_path(raw_key):
            warnings.warn(
                "El valor de 'SQLITE_DB_KEY' parece una ruta. Usa 'COBRA_DB_PATH' o el prefijo 'path:'"
                " si deseas desactivar el cifrado. Se tratará el valor como clave de cifrado.",
                RuntimeWarning,
            )
        db_path = DEFAULT_DB_PATH

    if path_source == "prefix" and not path_value:
        raise DatabaseKeyError(
            "El prefijo de ruta en 'SQLITE_DB_KEY' requiere una ruta no vacía."
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path, cipher_key


def _get_sqliteplus_instance():
    global _SQLITEPLUS_INSTANCE
    if _SQLITEPLUS_INSTANCE is not None:
        return _SQLITEPLUS_INSTANCE

    with _INIT_LOCK:
        if _SQLITEPLUS_INSTANCE is not None:
            return _SQLITEPLUS_INSTANCE
        sqliteplus_cls = _load_sqliteplus_class()
        db_path, cipher_key = _resolve_paths()
        _SQLITEPLUS_INSTANCE = sqliteplus_cls(db_path=str(db_path), cipher_key=cipher_key)
        return _SQLITEPLUS_INSTANCE


def _ensure_tables(connection: sqlite3.Connection) -> None:
    global _TABLES_READY
    if _TABLES_READY:
        return

    with _INIT_LOCK:
        if _TABLES_READY:
            return
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ast_cache (
                hash TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                ast_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ast_fragments (
                hash TEXT NOT NULL,
                fragment_name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (hash, fragment_name),
                FOREIGN KEY (hash) REFERENCES ast_cache(hash) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS qualia_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload BLOB,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_ast_cache_timestamp
            AFTER UPDATE ON ast_cache
            BEGIN
                UPDATE ast_cache SET updated_at = CURRENT_TIMESTAMP WHERE hash = NEW.hash;
            END
            """
        )
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_qualia_state_timestamp
            AFTER UPDATE ON qualia_state
            BEGIN
                UPDATE qualia_state SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """
        )
        connection.commit()
        _TABLES_READY = True


@contextmanager
def get_connection():
    """Devuelve una conexión lista para usar y garantiza la creación de tablas."""

    instance = _get_sqliteplus_instance()
    connection = instance.get_connection()
    try:
        _ensure_tables(connection)
        yield connection
    finally:
        connection.close()


def _serialize_ast(ast_obj: Any) -> str:
    """Serializa un AST a JSON evitando ejecución arbitraria."""

    if isinstance(ast_obj, str):
        return ast_obj
    if isinstance(ast_obj, (bytes, bytearray)):
        return ast_obj.decode("utf-8")
    if is_dataclass(ast_obj):
        return json.dumps(asdict(ast_obj), ensure_ascii=False)
    if isinstance(ast_obj, Mapping | list | tuple | set):
        return json.dumps(ast_obj, ensure_ascii=False, default=_json_default)
    return json.dumps(ast_obj, ensure_ascii=False, default=_json_default)


def _json_default(value: Any):  # pragma: no cover - caminos poco frecuentes
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Objeto no serializable: {value!r}")


def _deserialize_ast(serialized: str) -> Any:
    try:
        return json.loads(serialized)
    except json.JSONDecodeError:
        return serialized


def store_ast(
    hash_key: str,
    source: str,
    ast_obj: Any,
    fragments: Iterable[tuple[str, str]] | None = None,
) -> None:
    """Guarda el AST y, opcionalmente, fragmentos asociados."""

    payload = _serialize_ast(ast_obj)
    with _DB_LOCK:
        with get_connection() as conn:
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
            if fragments:
                cursor.executemany(
                    """
                    INSERT INTO ast_fragments(hash, fragment_name, content)
                    VALUES (?, ?, ?)
                    ON CONFLICT(hash, fragment_name) DO UPDATE
                    SET content = excluded.content
                    """,
                    [(hash_key, name, content) for name, content in fragments],
                )
            conn.commit()


def load_ast(hash_key: str) -> dict[str, Any] | None:
    """Recupera un AST almacenado y sus fragmentos asociados."""

    with _DB_LOCK:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT source, ast_json FROM ast_cache WHERE hash = ?", (hash_key,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            source, serialized = row
            cursor.execute(
                "SELECT fragment_name, content FROM ast_fragments WHERE hash = ?",
                (hash_key,),
            )
            fragments = {name: content for name, content in cursor.fetchall()}
    return {
        "source": source,
        "ast": _deserialize_ast(serialized),
        "fragments": fragments,
    }


def clear_cache() -> None:
    """Limpia por completo la caché de AST."""

    with _DB_LOCK:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ast_fragments")
            cursor.execute("DELETE FROM ast_cache")
            conn.commit()


def save_qualia_state(state: Any) -> None:
    """Persiste el estado de "qualia" como JSON o BLOB genérico."""

    if isinstance(state, (dict, list, tuple, set)) or is_dataclass(state):
        payload: bytes | str = json.dumps(state, ensure_ascii=False, default=_json_default)
    elif isinstance(state, (bytes, bytearray)):
        payload = bytes(state)
    else:
        payload = str(state)

    with _DB_LOCK:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO qualia_state(id, payload)
                VALUES (1, ?)
                ON CONFLICT(id) DO UPDATE
                SET payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (payload,),
            )
            conn.commit()
