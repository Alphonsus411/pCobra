import importlib
import os
import sys
import json

import pytest


def _prepare_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    if "core.ast_cache" in sys.modules:
        importlib.reload(sys.modules["core.ast_cache"])
    return cache_dir


def _escribir_malicioso(ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("{malformed json]")


def test_carga_ast_malicioso(monkeypatch, tmp_path):
    _prepare_cache(monkeypatch, tmp_path)
    from core.ast_cache import _ruta_cache, obtener_ast

    codigo = "var x = 1"
    ruta = _ruta_cache(codigo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    _escribir_malicioso(ruta)

    with pytest.raises(json.JSONDecodeError):
        obtener_ast(codigo)


def test_carga_tokens_maliciosos(monkeypatch, tmp_path):
    _prepare_cache(monkeypatch, tmp_path)
    from core.ast_cache import _ruta_tokens, obtener_tokens

    codigo = "var x = 1"
    ruta = _ruta_tokens(codigo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    _escribir_malicioso(ruta)

    with pytest.raises(json.JSONDecodeError):
        obtener_tokens(codigo)

