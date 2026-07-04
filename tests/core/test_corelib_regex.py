from __future__ import annotations

import importlib
import pytest

import pcobra.corelibs.regex as regex


def test_import_directo_y_all_presente() -> None:
    modulo = importlib.import_module("pcobra.corelibs.regex")

    assert modulo is regex
    assert isinstance(regex.__all__, list)
    assert "buscar" in regex.__all__
    assert callable(getattr(regex, "buscar"))


def test_buscar_reemplazar_y_encontrar_todos_exitosos() -> None:
    texto = "cobra 123 cobra 456"

    assert regex.buscar(r"\d+", texto) == "123"
    assert regex.reemplazar(r"cobra", "Cobra", texto, limite=1).startswith("Cobra")
    assert regex.encontrar_todos(r"\d+", texto) == ["123", "456"]


def test_patron_invalido_lanza_value_error() -> None:
    with pytest.raises(ValueError):
        regex.buscar("(", "texto")
