import hashlib
import importlib
import json
import sqlite3
import sys
import warnings

import pytest
import pcobra.core.database as core_database


def _prepare_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DB_PATH", raising=False)
    monkeypatch.setenv("SQLITE_DB_KEY", "security-test-key")
    database_module = importlib.reload(core_database)

    class SQLitePlusStub:
        def __init__(self, db_path: str, cipher_key: str | None = None):
            self._db_path = db_path

        def get_connection(self):
            conn = sqlite3.connect(self._db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

    monkeypatch.setattr(
        database_module,
        "_load_sqliteplus_class",
        lambda: SQLitePlusStub,
        raising=False,
    )
    monkeypatch.setattr(
        database_module, "_SQLITEPLUS_CLASS", SQLitePlusStub, raising=False
    )
    monkeypatch.setattr(
        database_module, "_SQLITEPLUS_INSTANCE", None, raising=False
    )
    sys.modules.pop("core.ast_cache", None)
    module = importlib.import_module("core.ast_cache")
    return module, cache_dir


def _db_path(cache_dir):
    return cache_dir / "cache.db"


def test_carga_ast_malicioso(monkeypatch, tmp_path):
    ast_cache, cache_dir = _prepare_cache(monkeypatch, tmp_path)

    codigo = "var x = 1"
    from pcobra.cobra.core import Parser
    monkeypatch.setattr(Parser, "parsear", lambda self: [])
    ast_cache.obtener_ast(codigo)

    hash_key = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    with sqlite3.connect(_db_path(cache_dir)) as conn:
        conn.execute(
            "UPDATE ast_cache SET ast_json = '{malformed json]' WHERE hash = ?",
            (hash_key,),
        )
        conn.commit()

    with pytest.raises(json.JSONDecodeError):
        ast_cache.obtener_ast(codigo)


def test_carga_tokens_maliciosos(monkeypatch, tmp_path):
    ast_cache, cache_dir = _prepare_cache(monkeypatch, tmp_path)

    codigo = "var x = 1"
    from pcobra.cobra.core import Parser
    monkeypatch.setattr(Parser, "parsear", lambda self: [])
    ast_cache.obtener_tokens(codigo)

    hash_key = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
    with sqlite3.connect(_db_path(cache_dir)) as conn:
        conn.execute(
            """
            UPDATE ast_fragments
            SET content = '{malformed json]'
            WHERE hash = ? AND fragment_name = 'full_tokens'
            """,
            (hash_key,),
        )
        conn.commit()

    with pytest.raises(json.JSONDecodeError):
        ast_cache.obtener_tokens(codigo)


def test_alias_sin_clave_emite_advertencia_y_falla(monkeypatch, tmp_path):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DB_PATH", raising=False)
    monkeypatch.setenv("COBRA_AST_CACHE", str(tmp_path / "legacy"))

    sys.modules.pop("pcobra.core.ast_cache", None)
    sys.modules.pop("core.ast_cache", None)
    ast_cache_module = importlib.import_module("pcobra.core.ast_cache")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(core_database.DatabaseKeyError) as excinfo:
            ast_cache_module._with_connection(lambda conn: None)

    messages = [str(item.message) for item in caught]
    assert any("COBRA_AST_CACHE" in message for message in messages)
    assert any("'SQLITE_DB_KEY'" in message for message in messages)
    assert "'SQLITE_DB_KEY' es obligatoria" in str(excinfo.value)
