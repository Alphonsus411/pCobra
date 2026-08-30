import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def holobit_module():
    ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
    spec = importlib.util.spec_from_file_location("_holobit_graficar_contract", ruta)
    modulo = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(modulo)
    return modulo


def test_graficar_retorna_solo_estado_publico_json_safe(
    monkeypatch: pytest.MonkeyPatch, holobit_module
) -> None:
    monkeypatch.setattr(
        holobit_module._AdaptadorInternoHolobit,
        "graficar",
        lambda _holobit: None,
    )

    resultado = holobit_module.graficar(
        {"tipo": "holobit", "valores": [1, 2, 3]}
    )

    assert resultado == {"estado": "ok"}
    assert json.dumps(resultado) == '{"estado": "ok"}'
    assert all(isinstance(clave, str) for clave in resultado)
    assert all(
        valor is None or isinstance(valor, (str, int, float, bool))
        for valor in resultado.values()
    )


def test_graficar_ignora_resultado_interno_del_sdk(
    monkeypatch: pytest.MonkeyPatch, holobit_module
) -> None:
    class CentinelaSdk:
        pass

    CentinelaSdk.__module__ = "holobit_sdk.core.holobit"
    centinela = CentinelaSdk()
    monkeypatch.setattr(
        holobit_module._AdaptadorInternoHolobit,
        "graficar",
        lambda _holobit: centinela,
    )

    resultado = holobit_module.graficar(
        {"tipo": "holobit", "valores": [1, 2, 3]}
    )

    assert resultado == {"estado": "ok"}
    assert centinela not in resultado.values()
    json.dumps(resultado)


def test_graficar_sanea_excepcion_interna_del_sdk(
    monkeypatch: pytest.MonkeyPatch, holobit_module
) -> None:
    class FalloInternoHolobitSdk(Exception):
        pass

    FalloInternoHolobitSdk.__module__ = "holobit_sdk.core.holobit"
    mensaje_original = "holobit_sdk fallo secreto de FalloInternoHolobitSdk"

    def fallar(_holobit):
        raise FalloInternoHolobitSdk(mensaje_original)

    monkeypatch.setattr(
        holobit_module._AdaptadorInternoHolobit, "graficar", fallar
    )

    with pytest.raises(holobit_module.ErrorHolobit) as captura:
        holobit_module.graficar(
            {"tipo": "holobit", "valores": [1, 2, 3]}
        )

    mensaje_publico = str(captura.value)
    assert "Cobra" in mensaje_publico
    assert "graficar" in mensaje_publico
    assert "holobit_sdk" not in mensaje_publico
    assert "FalloInternoHolobitSdk" not in mensaje_publico
    assert mensaje_original not in mensaje_publico
