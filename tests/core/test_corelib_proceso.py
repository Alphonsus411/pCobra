from __future__ import annotations

import sys

import pytest

import pcobra.corelibs.proceso as proceso


def test_import_directo_y_all_presente() -> None:
    assert isinstance(proceso.__all__, list)
    assert "ejecutar" in proceso.__all__


def test_ejecutar_python_portable_ok() -> None:
    resultado = proceso.ejecutar(sys.executable, argumentos=["-c", "print('ok')"])

    assert proceso.codigo_salida(resultado) == 0
    assert proceso.salida(resultado).strip() == "ok"
    assert proceso.errores(resultado) == ""


def test_argumentos_texto_plano_lanza_type_error() -> None:
    with pytest.raises(TypeError):
        proceso.ejecutar(sys.executable, argumentos="-c print('ok')")
