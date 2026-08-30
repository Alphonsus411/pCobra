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
    hb = holobit.crear_holobit([1, 0, -2, 3.5])
    assert set(holobit.__all__) == EXPECTED_PUBLIC_API
    assert hb == {"tipo": "holobit", "valores": [1.0, 0.0, -2.0, 3.5]}
    assert all(isinstance(valor, float) for valor in hb["valores"])
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


def test_holobit_adapter_normaliza_tipos_cobra_facing():
    hb = holobit.crear_holobit((1, 2.5, 3))

    proyectado = holobit.proyectar(hb, "2d")
    transformado = holobit.transformar(hb, "rotar", "z", 90)
    combinado = holobit.combinar(hb, holobit.crear_holobit([4]))
    metricas = holobit.medir(hb)

    assert isinstance(hb, dict)
    assert isinstance(proyectado, dict)
    assert isinstance(transformado, dict)
    assert isinstance(combinado, dict)
    assert isinstance(metricas, dict)
    assert hb["tipo"] == "holobit"
    assert all(isinstance(v, float) for v in hb["valores"])
    assert isinstance(metricas["dimension"], int)
    assert isinstance(metricas["magnitud"], float)


def test_graficar_devuelve_estado_json_e_ignora_retorno_interno(monkeypatch):
    hb = holobit.crear_holobit([1, 2, 3])
    proyectados = []
    retorno_sdk = object()

    def proyectar(interno):
        proyectados.append(interno)
        return retorno_sdk

    monkeypatch.setattr(holobit, "_runtime_graficar", proyectar)

    resultado = holobit.graficar(hb)

    assert resultado == {"estado": "ok"}
    assert len(proyectados) == 1
    assert proyectados[0].valores == [1.0, 2.0, 3.0]
    holobit._garantizar_json_estable(resultado)


@pytest.mark.parametrize("valor_invalido", [True, False])
def test_crear_holobit_rechaza_booleanos(valor_invalido):
    with pytest.raises(TypeError):
        holobit.crear_holobit([valor_invalido, 1])


@pytest.mark.parametrize("valor_no_finito", [float("nan"), float("inf"), float("-inf")])
def test_crear_holobit_rechaza_valores_no_finitos(valor_no_finito):
    with pytest.raises(ValueError, match="valores del holobit deben ser finitos"):
        holobit.crear_holobit([valor_no_finito])


@pytest.mark.parametrize(
    "payload",
    [
        '{"tipo":"holobit","valores":[NaN]}',
        '{"tipo":"holobit","valores":[Infinity]}',
        '{"tipo":"holobit","valores":[-Infinity]}',
    ],
)
def test_deserializar_holobit_rechaza_valores_no_finitos(payload):
    with pytest.raises(ValueError):
        holobit.deserializar_holobit(payload)


@pytest.mark.parametrize("valor_no_finito", [float("nan"), float("inf"), float("-inf")])
def test_validar_holobit_devuelve_false_para_valores_no_finitos(valor_no_finito):
    assert (
        holobit.validar_holobit({"tipo": "holobit", "valores": [valor_no_finito]})
        is False
    )


@pytest.mark.parametrize(
    ("operacion", "argumentos"),
    [
        (holobit.serializar_holobit, ()),
        (holobit.proyectar, ("2d",)),
        (holobit.transformar, ("rotar", "z", 90)),
        (holobit.combinar, ({"tipo": "holobit", "valores": [1]},)),
        (holobit.medir, ()),
    ],
)
def test_operaciones_rechazan_estructuras_con_valores_no_finitos(operacion, argumentos):
    estructura = {"tipo": "holobit", "valores": [float("inf")]}

    with pytest.raises(ValueError):
        operacion(estructura, *argumentos)


def test_policy_rechaza_holobit_sdk_en_usar():
    with pytest.raises(PermissionError):
        usar_loader.obtener_modulo("holobit_sdk")


def test_internals_no_se_exportan_en_public_api():
    exports = set(holobit.__all__)
    for bloqueado in (
        "Holobit",
        "_SDKHolobit",
        "_validar_estructura_holobit",
        "holobit_sdk",
    ):
        assert bloqueado not in exports


@pytest.mark.parametrize(
    "estructura_invalida",
    [
        {"tipo": "holobit"},
        {"valores": [1, 2, 3]},
        {"tipo": "holobit", "valores": [1, 2], "legacy": True},
        {"tipo": "holobit_sdk", "valores": [1, 2]},
        {"tipo": "holobit", "valores": [1, "Holobit"]},
    ],
)
def test_validar_holobit_rechaza_payloads_fuera_del_contrato_serializable(
    estructura_invalida,
):
    assert holobit.validar_holobit(estructura_invalida) is False


def test_serializar_holobit_rechaza_objeto_sdk_o_clase_interna():
    class LegacyHolobit:
        tipo = "holobit"
        valores = [1, 2, 3]

    with pytest.raises(TypeError):
        holobit.serializar_holobit(LegacyHolobit())  # type: ignore[arg-type]


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
