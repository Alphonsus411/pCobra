import importlib
import sqlite3
import sys

import pytest
from pcobra.cobra.core import Lexer, Parser


def _reload_ast_cache(monkeypatch):
    monkeypatch.delenv("COBRA_AST_CACHE", raising=False)
    sys.modules.pop("core.ast_cache", None)
    module = importlib.import_module("core.ast_cache")
    module = importlib.reload(module)
    module.limpiar_cache()
    return module


def _count_rows(db_path, table):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return cursor.fetchone()[0]


def test_obtener_ast_reutiliza(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    llamadas = {"count": 0}

    def fake_parsear(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Parser, "parsear", fake_parsear)

    codigo = "var x = 1"
    ast_cache.obtener_ast(codigo)
    ast_cache.obtener_ast(codigo)

    assert llamadas["count"] == 1
    with sqlite3.connect(base_datos_temporal) as conn:
        rows = conn.execute("SELECT source FROM ast_cache").fetchall()
    assert rows == [(codigo,)]


@pytest.mark.timeout(5)
def test_limpiar_cache(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)
    codigo = "var y = 2"

    monkeypatch.setattr(Parser, "parsear", lambda self: [])
    ast_cache.obtener_ast(codigo)
    assert _count_rows(base_datos_temporal, "ast_cache") > 0
    assert _count_rows(base_datos_temporal, "ast_fragments") > 0
    ast_cache.limpiar_cache(vacuum=True)
    assert _count_rows(base_datos_temporal, "ast_cache") == 0
    assert _count_rows(base_datos_temporal, "ast_fragments") == 0


def test_obtener_tokens_reutiliza(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    llamadas = {"count": 0}

    def fake_tokenizar(self):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "tokenizar", fake_tokenizar)

    codigo = "var z = 3"
    ast_cache.obtener_tokens(codigo)
    ast_cache.obtener_tokens(codigo)

    assert llamadas["count"] == 1
    with sqlite3.connect(base_datos_temporal) as conn:
        rows = conn.execute(
            "SELECT fragment_name FROM ast_fragments ORDER BY fragment_name"
        ).fetchall()
    assert rows == [("full_tokens",)]


def test_obtener_ast_reutiliza_tokens(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

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

    with sqlite3.connect(base_datos_temporal) as conn:
        conn.execute("UPDATE ast_cache SET ast_json = 'null'")
        conn.commit()

    ast_cache.obtener_ast(codigo)

    assert token_calls["count"] == 1
    assert parse_calls["count"] == 2


def test_cache_fragmentos(monkeypatch, base_datos_temporal):
    ast_cache = _reload_ast_cache(monkeypatch)

    llamadas = {"count": 0}

    def fake_tokenizar(self, *a, **k):
        llamadas["count"] += 1
        return []

    monkeypatch.setattr(Lexer, "_tokenizar_base", fake_tokenizar, raising=False)

    codigo = "imprimir(1)\n"
    ast_cache.obtener_tokens_fragmento(codigo)
    ast_cache.obtener_tokens_fragmento(codigo)
    assert llamadas["count"] == 1
    assert _count_rows(base_datos_temporal, "ast_fragments") >= 1
