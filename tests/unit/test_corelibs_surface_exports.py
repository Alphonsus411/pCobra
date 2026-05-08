from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORELIBS = ROOT / "src" / "pcobra" / "corelibs"

MODULOS = {
    "numero": "EQUIVALENCIAS_SEMANTICAS_NUMERO",
    "texto": "EQUIVALENCIAS_SEMANTICAS_TEXTO",
    "datos": "EQUIVALENCIAS_SEMANTICAS_DATOS",
    "logica": "EQUIVALENCIAS_SEMANTICAS_LOGICA",
    "asincrono": "EQUIVALENCIAS_SEMANTICAS_ASINCRONO",
    "sistema": "EQUIVALENCIAS_SEMANTICAS_SISTEMA",
    "archivo": "EQUIVALENCIAS_SEMANTICAS_ARCHIVO",
    "tiempo": "EQUIVALENCIAS_SEMANTICAS_TIEMPO",
    "red": "EQUIVALENCIAS_SEMANTICAS_RED",
    "holobit": "EQUIVALENCIAS_SEMANTICAS_HOLOBIT",
}

RESERVADOS = {"__dict__", "__class__", "__getattribute__", "eval", "exec"}


def _cargar_modulo(nombre: str):
    ruta = CORELIBS / f"{nombre}.py"
    spec = importlib.util.spec_from_file_location(f"_corelib_{nombre}_tests", ruta)
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.mark.parametrize("nombre,tabla", MODULOS.items())
def test_tabla_equivalencias_y_superficie_publica(nombre: str, tabla: str):
    modulo = _cargar_modulo(nombre)

    equivalencias = getattr(modulo, tabla)
    assert isinstance(equivalencias, dict)
    assert equivalencias
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in equivalencias.items())

    assert isinstance(modulo.__all__, list)
    assert modulo.__all__
    assert len(modulo.__all__) == len(set(modulo.__all__))

    for simbolo in modulo.__all__:
        assert simbolo.isidentifier()
        assert not simbolo.startswith("_")
        assert simbolo not in RESERVADOS
        assert hasattr(modulo, simbolo)
