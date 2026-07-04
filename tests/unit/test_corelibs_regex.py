from __future__ import annotations

import re

import pytest

from pcobra.corelibs import regex


def test_buscar_y_coincidir_devuelven_texto_o_none() -> None:
    assert regex.buscar(r"\d+", "abc123") == "123"
    assert regex.buscar(r"\d+", "abc") is None
    assert regex.coincidir(r"abc", "abcdef") == "abc"
    assert regex.coincidir(r"\d+", "abc123") is None


def test_operaciones_regex_respetan_limites_flags_y_listas() -> None:
    assert regex.reemplazar(r"a", "x", "banana", limite=2) == "bxnxna"
    assert regex.dividir(r"\s+", "uno  dos\ttres", maximo=1) == ["uno", "dos\ttres"]
    assert regex.encontrar_todos(r"[a-z]+", "A b C d", flags=re.IGNORECASE) == [
        "A",
        "b",
        "C",
        "d",
    ]


@pytest.mark.parametrize("funcion,args", [
    (regex.buscar, ("[", "texto")),
    (regex.coincidir, ("[", "texto")),
    (regex.reemplazar, ("[", "x", "texto")),
    (regex.dividir, ("[", "texto")),
    (regex.encontrar_todos, ("[", "texto")),
])
def test_patrones_invalidos_generan_value_error_en_espanol(funcion, args) -> None:
    with pytest.raises(ValueError, match="patrón de expresión regular inválido"):
        funcion(*args)


def test_all_solo_expone_api_publica_canonica() -> None:
    assert regex.__all__ == [
        "buscar",
        "coincidir",
        "reemplazar",
        "dividir",
        "encontrar_todos",
    ]
