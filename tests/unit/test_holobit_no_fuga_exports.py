import importlib
import importlib.util
from pathlib import Path

import pytest

EXPECTED_API = {
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "combinar",
    "medir",
}


def _load_corelib_module():
    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_no_fuga", ruta)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize(
    "mod_name",
    ["pcobra.standard_library.holobit", "pcobra.core.holobits"],
)
def test_superficies_holobit_solo_exportan_api_canonica(mod_name):
    mod = importlib.import_module(mod_name)
    assert set(mod.__all__) == EXPECTED_API


def test_corelibs_holobit_solo_exporta_api_canonica():
    mod = _load_corelib_module()
    assert set(mod.__all__) == EXPECTED_API


@pytest.mark.parametrize(
    "mod_name,symbol",
    [
        ("pcobra.standard_library.holobit", "holobit_sdk"),
        ("pcobra.standard_library.holobit", "Holobit"),
        ("pcobra.core.holobits", "holobit_sdk"),
        ("pcobra.core.holobits", "Holobit"),
    ],
)
def test_no_fuga_de_sdk_ni_clases_internas(mod_name, symbol):
    mod = importlib.import_module(mod_name)
    with pytest.raises(AttributeError):
        getattr(mod, symbol)


def test_no_fuga_en_corelibs_por_getattr():
    mod = _load_corelib_module()
    for symbol in ("holobit_sdk", "Holobit"):
        with pytest.raises(AttributeError):
            getattr(mod, symbol)
