import importlib.util
from pathlib import Path

import pytest

from pcobra.cobra import usar_loader

ruta = Path("src/pcobra/corelibs/holobit.py").resolve()
spec = importlib.util.spec_from_file_location("_holobit_corelib_tests", ruta)
holobit = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(holobit)

EXPECTED_PUBLIC_API = {
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


def test_holobit_adapter_public_contract_roundtrip():
    hb = holobit.crear_holobit([1, 2, 3])
    assert set(holobit.__all__) == EXPECTED_PUBLIC_API
    assert hb == {"tipo": "holobit", "valores": [1.0, 2.0, 3.0]}
    assert holobit.validar_holobit(hb) is True

    payload = holobit.serializar_holobit(hb)
    hb2 = holobit.deserializar_holobit(payload)
    assert hb2 == hb


def test_holobit_adapter_combinar_medir_y_transformar():
    a = holobit.crear_holobit([1, 2])
    b = holobit.crear_holobit([3])
    c = holobit.combinar(a, b)
    assert c["valores"] == [1.0, 2.0, 3.0]
    metricas = holobit.medir(c)
    assert metricas["dimension"] == 3
    assert metricas["magnitud"] > 0

    t = holobit.transformar(c, "rotar", "x", 90)
    assert t["tipo"] == "holobit"


def test_policy_rechaza_holobit_sdk_en_usar():
    with pytest.raises(PermissionError):
        usar_loader.obtener_modulo("holobit_sdk")


def test_internals_no_se_exportan_en_public_api():
    exports = set(holobit.__all__)
    for bloqueado in ("Holobit", "_SDKHolobit", "_validar_estructura_holobit", "holobit_sdk"):
        assert bloqueado not in exports


@pytest.mark.parametrize(
    "payload",
    [
        "[1,2,3]",
        '{"tipo":"otro","valores":[1]}',
        '{"tipo":"holobit","valores":"123"}',
        '{"tipo":"holobit","valores":[1],"extra":true}',
    ],
)
def test_deserializar_holobit_rechaza_payload_invalido(payload):
    with pytest.raises((TypeError, ValueError, KeyError)):
        holobit.deserializar_holobit(payload)
