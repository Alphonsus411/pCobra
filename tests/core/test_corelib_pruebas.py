from __future__ import annotations

import importlib
import pytest

import pcobra.corelibs.pruebas as pruebas


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.pruebas")

    assert modulo is pruebas
    assert isinstance(pruebas.__all__, list)
    assert "igual" in pruebas.__all__
    assert callable(getattr(pruebas, "igual"))


def test_aserciones_principales_exitosas() -> None:
    assert pruebas.igual(2 + 2, 4) is True
    assert pruebas.verdadero("cobra") is True
    assert pruebas.contiene(["a", "b"], "a") is True


def test_igual_distinto_lanza_assertion_error() -> None:
    with pytest.raises(AssertionError):
        pruebas.igual("obtenido", "esperado")
