import pytest

from pcobra.corelibs import holobit
from pcobra.cobra import usar_loader


def test_holobit_adapter_public_contract_roundtrip():
    hb = holobit.crear_holobit([1, 2, 3])
    assert set(holobit.__all__) == {
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
    assert hb["__cobra_tipo__"] == "holobit"
    assert holobit.validar_holobit(hb) is True

    payload = holobit.serializar_holobit(hb)
    hb2 = holobit.deserializar_holobit(payload)
    assert hb2["valores"] == [1.0, 2.0, 3.0]


def test_holobit_adapter_combinar_medir_y_transformar():
    a = holobit.crear_holobit([1, 2])
    b = holobit.crear_holobit([3])
    c = holobit.combinar(a, b)
    assert c["valores"] == [1.0, 2.0, 3.0]
    metricas = holobit.medir(c)
    assert metricas["dimension"] == 3
    assert metricas["magnitud"] > 0

    t = holobit.transformar(c, "rotar", "x", 90)
    assert t["__cobra_tipo__"] == "holobit"


def test_policy_rechaza_holobit_sdk_en_usar():
    with pytest.raises(PermissionError):
        usar_loader.obtener_modulo("holobit_sdk")
