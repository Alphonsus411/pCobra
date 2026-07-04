from __future__ import annotations

import sys

import pytest

from pcobra.corelibs.argumentos import (
    contiene_flag,
    obtener_argumentos,
    obtener_opcion,
    parsear_pares,
)


def test_obtener_argumentos_usa_sys_argv_solo_al_llamar(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cobra", "--modo", "dev"])
    assert obtener_argumentos() == ["--modo", "dev"]

    monkeypatch.setattr(sys, "argv", ["cobra", "--modo", "prod"])
    assert obtener_argumentos() == ["--modo", "prod"]


def test_obtener_argumentos_copia_argv_explicito_completo():
    assert obtener_argumentos(["programa", "--flag", 3]) == ["programa", "--flag", "3"]


@pytest.mark.parametrize("nombre", ["", "-", "--", "   "])
def test_nombres_vacios_lanzan_value_error(nombre):
    with pytest.raises(ValueError):
        contiene_flag(nombre, [])
    with pytest.raises(ValueError):
        obtener_opcion(nombre, [])


def test_contiene_flag_soporta_largos_y_cortos_simples():
    argv = ["--debug", "--modo=dev", "-v", "--salida", "archivo"]

    assert contiene_flag("debug", argv) is True
    assert contiene_flag("--debug", argv) is True
    assert contiene_flag("v", argv) is True
    assert contiene_flag("-v", argv) is True
    assert contiene_flag("modo", argv) is False
    assert contiene_flag("ausente", argv) is False


def test_obtener_opcion_soporta_igual_separado_corto_y_defecto():
    argv = ["--modo=dev", "--salida", "archivo.txt", "-n", "10", "--debug"]

    assert obtener_opcion("modo", argv) == "dev"
    assert obtener_opcion("salida", argv) == "archivo.txt"
    assert obtener_opcion("n", argv) == "10"
    assert obtener_opcion("debug", argv, por_defecto="no") == "no"
    assert obtener_opcion("ausente", argv, por_defecto="x") == "x"


def test_parsear_pares_parsea_patrones_basicos_e_ignora_posicionales():
    argv = [
        "entrada.cobra",
        "--debug",
        "--modo=dev",
        "--salida",
        "archivo.txt",
        "-v",
        "-n",
        "10",
        "--sin-valor",
        "--negativo",
        "-1",
    ]

    assert parsear_pares(argv) == {
        "debug": True,
        "modo": "dev",
        "salida": "archivo.txt",
        "v": True,
        "n": "10",
        "sin-valor": True,
        "negativo": "-1",
    }
