import importlib
import os
import pickle
import sys

import pytest


def _prepare_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))
    if "core.ast_cache" in sys.modules:
        importlib.reload(sys.modules["core.ast_cache"])
    return cache_dir


def _escribir_malicioso(ruta):
    with open(ruta, "wb") as f:
        f.write(pickle.dumps(eval))


def test_carga_ast_malicioso(monkeypatch, tmp_path):
    _prepare_cache(monkeypatch, tmp_path)
    from core.ast_cache import _ruta_cache, obtener_ast

    codigo = "var x = 1"
    ruta = _ruta_cache(codigo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    _escribir_malicioso(ruta)

    with pytest.raises(pickle.UnpicklingError):
        obtener_ast(codigo)


def test_carga_tokens_maliciosos(monkeypatch, tmp_path):
    _prepare_cache(monkeypatch, tmp_path)
    from core.ast_cache import _ruta_tokens, obtener_tokens

    codigo = "var x = 1"
    ruta = _ruta_tokens(codigo)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    _escribir_malicioso(ruta)

    with pytest.raises(pickle.UnpicklingError):
        obtener_tokens(codigo)

