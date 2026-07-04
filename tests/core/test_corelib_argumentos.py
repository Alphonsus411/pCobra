from __future__ import annotations

import pytest

import pcobra.corelibs.argumentos as argumentos


def test_import_directo_y_all_presente() -> None:
    assert isinstance(argumentos.__all__, list)
    assert "parsear_pares" in argumentos.__all__


def test_parsear_pares_y_obtener_opcion_exitoso() -> None:
    argv = ["--modo", "rapido", "-v", "--salida=archivo.txt", "posicional"]

    assert argumentos.parsear_pares(argv) == {
        "modo": "rapido",
        "v": True,
        "salida": "archivo.txt",
    }
    assert argumentos.obtener_opcion("modo", argv) == "rapido"
    assert argumentos.contiene_flag("v", argv) is True


def test_obtener_argumentos_rechaza_texto_plano() -> None:
    with pytest.raises(TypeError):
        argumentos.obtener_argumentos("--modo rapido")
