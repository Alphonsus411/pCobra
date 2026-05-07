import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def holobit_module():
    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_corelib_domain", ruta)
    modulo = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(modulo)
    return modulo


def test_deserializar_holobit_retorna_error_dominio_en_json_invalido(holobit_module) -> None:
    with pytest.raises(holobit_module.ErrorHolobit, match="JSON válido"):
        holobit_module.deserializar_holobit("{json_invalido")


def test_adaptador_traduce_error_runtime_sdk_a_error_dominio(monkeypatch: pytest.MonkeyPatch, holobit_module) -> None:
    class _Boom(Exception):
        pass

    monkeypatch.setattr(holobit_module, "_SDKHolobit", lambda *_args, **_kwargs: (_ for _ in ()).throw(_Boom("sdk raw")))

    with pytest.raises(holobit_module.ErrorHolobit, match="runtime de Cobra"):
        holobit_module.serializar_holobit({"tipo": "holobit", "valores": [1, 2, 3]})
