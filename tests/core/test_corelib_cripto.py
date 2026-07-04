from __future__ import annotations

import importlib
import pytest

import pcobra.corelibs.cripto as cripto


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.cripto")

    assert modulo is cripto
    assert isinstance(cripto.__all__, list)
    assert "sha256" in cripto.__all__
    assert callable(getattr(cripto, "sha256"))


def test_hash_y_token_hexadecimal_exitosos() -> None:
    assert cripto.sha256("cobra") == cripto.sha256(b"cobra")
    assert cripto.comparar_seguro("abc", "abc") is True
    assert len(cripto.token_hexadecimal(4)) == 8


def test_token_rechaza_tamano_no_positivo() -> None:
    with pytest.raises(ValueError):
        cripto.token_seguro(0)
