import importlib
import sqlite3
import sys

import pytest
from pcobra.cobra.core import Lexer, Parser
import pcobra.core.database as core_database


def _reload_ast_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DB_PATH", raising=False)
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


def _count_rows(db_path, table):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]


def test_obtener_ast_reutiliza(monkeypatch, tmp_path):
    ast_cache, cache_dir = _reload_ast_cache(monkeypatch, tmp_path)

    llamadas = {"count": 0}

    def fake_parsear(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Parser, "parsear", fake_parsear)

    codigo = "var x = 1"
    ast_cache.obtener_ast(codigo)
    ast_cache.obtener_ast(codigo)

    assert llamadas["count"] == 1
    assert _count_rows(_db_path(cache_dir), "ast_cache") == 1


@pytest.mark.timeout(5)
def test_limpiar_cache(monkeypatch, tmp_path):
    ast_cache, cache_dir = _reload_ast_cache(monkeypatch, tmp_path)
    codigo = "var y = 2"

    monkeypatch.setattr(Parser, "parsear", lambda self: [])
    ast_cache.obtener_ast(codigo)
    assert _count_rows(_db_path(cache_dir), "ast_cache") > 0

    ast_cache.limpiar_cache(vacuum=True)
    assert _count_rows(_db_path(cache_dir), "ast_cache") == 0
    assert _count_rows(_db_path(cache_dir), "ast_fragments") == 0


def test_obtener_tokens_reutiliza(monkeypatch, tmp_path):
    ast_cache, cache_dir = _reload_ast_cache(monkeypatch, tmp_path)

    llamadas = {"count": 0}

    def fake_tokenizar(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)

    codigo = "var z = 3"
    ast_cache.obtener_tokens(codigo)
    ast_cache.obtener_tokens(codigo)

    assert llamadas["count"] == 1
    assert _count_rows(_db_path(cache_dir), "ast_fragments") == 1


def test_obtener_ast_reutiliza_tokens(monkeypatch, tmp_path):
    ast_cache, cache_dir = _reload_ast_cache(monkeypatch, tmp_path)

    token_calls = {"count": 0}
    parse_calls = {"count": 0}

    def fake_tokenizar(self):
        token_calls["count"] += 1
        return []

    def fake_parsear(self):
        parse_calls["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)
    monkeypatch.setattr(Parser, "parsear", fake_parsear)

    codigo = "var a = 5"
    ast_cache.obtener_ast(codigo)

    with sqlite3.connect(_db_path(cache_dir)) as conn:
        conn.execute("UPDATE ast_cache SET ast_json = 'null'")
        conn.commit()

    ast_cache.obtener_ast(codigo)

    assert token_calls["count"] == 1
    assert parse_calls["count"] == 2


def test_cache_fragmentos(monkeypatch, tmp_path):
    ast_cache, cache_dir = _reload_ast_cache(monkeypatch, tmp_path)

    llamadas = {"count": 0}

    def fake_tokenizar(self, *a, **k):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "_tokenizar_base", fake_tokenizar, raising=False)

    codigo = "imprimir(1)\n"
    ast_cache.obtener_tokens_fragmento(codigo)
    ast_cache.obtener_tokens_fragmento(codigo)
    assert llamadas["count"] == 1
    assert _count_rows(_db_path(cache_dir), "ast_fragments") >= 1
