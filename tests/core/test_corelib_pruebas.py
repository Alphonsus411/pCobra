from __future__ import annotations

import pytest

import pcobra.corelibs.pruebas as pruebas


def test_import_directo_y_all_presente() -> None:
    assert isinstance(pruebas.__all__, list)
    assert "igual" in pruebas.__all__


def test_aserciones_principales_exitosas() -> None:
    assert pruebas.igual(2 + 2, 4) is True
    assert pruebas.verdadero("cobra") is True
    assert pruebas.contiene(["a", "b"], "a") is True


def test_igual_distinto_lanza_assertion_error() -> None:
    with pytest.raises(AssertionError):
        pruebas.igual("obtenido", "esperado")
