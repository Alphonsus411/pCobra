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


def test_deserializar_holobit_retorna_error_dominio_en_json_invalido(
    holobit_module,
) -> None:
    with pytest.raises(holobit_module.ErrorHolobit, match="JSON válido"):
        holobit_module.deserializar_holobit("{json_invalido")


def test_adaptador_traduce_error_runtime_sdk_a_error_dominio(
    monkeypatch: pytest.MonkeyPatch, holobit_module
) -> None:
    class _Boom(Exception):
        pass

    monkeypatch.setattr(
        holobit_module,
        "_SDKHolobit",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(_Boom("sdk raw")),
    )

    with pytest.raises(holobit_module.ErrorHolobit, match="runtime de Cobra"):
        holobit_module.serializar_holobit({"tipo": "holobit", "valores": [1, 2, 3]})


@pytest.mark.parametrize("fase", ["adaptacion", "proyeccion"])
def test_graficar_oculta_errores_internos_en_toda_la_operacion(
    monkeypatch: pytest.MonkeyPatch, holobit_module, fase: str
) -> None:
    class _FalloSdkSecreto(Exception):
        pass

    def fallar(*_args, **_kwargs):
        raise _FalloSdkSecreto("mensaje privado de holobit_sdk")

    if fase == "adaptacion":
        monkeypatch.setattr(holobit_module, "_SDKHolobit", fallar)
    else:
        monkeypatch.setattr(holobit_module, "_runtime_graficar", fallar)

    with pytest.raises(holobit_module.ErrorHolobit) as captura:
        holobit_module.graficar({"tipo": "holobit", "valores": [1, 2, 3]})

    error = captura.value
    assert str(error) == (
        "No se pudo ejecutar la operación 'graficar' de holobit en runtime Cobra"
    )
    assert error.__cause__ is None
    assert error.__suppress_context__ is True
    assert "ErrorHolobit" not in holobit_module.PUBLIC_API_HOLOBIT
    assert "ErrorHolobit" not in holobit_module.__all__


@pytest.mark.parametrize(
    "entrada",
    [
        None,
        "abc",
        123,
        {"a": 1},
        [1, "dos", 3],
        [1, True, 3],
    ],
)
def test_crear_holobit_rechaza_entradas_invalidas_y_tipos_mixtos(
    holobit_module, entrada
) -> None:
    with pytest.raises(TypeError):
        holobit_module.crear_holobit(entrada)


@pytest.mark.parametrize(
    "payload",
    [
        "",
        "{",
        '{"tipo":"holobit"',
        '{"tipo":"holobit","valores":[1],}',
        '{"tipo":"otro","valores":[1]}',
        '{"tipo":"holobit","valores":"1,2"}',
    ],
)
def test_deserializar_holobit_rechaza_payloads_corruptos_o_invalidos(
    holobit_module, payload
) -> None:
    with pytest.raises((TypeError, holobit_module.ErrorHolobit)):
        holobit_module.deserializar_holobit(payload)


def test_formato_canonico_dict_estable_en_roundtrip(holobit_module) -> None:
    original = holobit_module.crear_holobit([1, 2.5, 3])
    assert original == {"tipo": "holobit", "valores": [1.0, 2.5, 3.0]}

    serializado = holobit_module.serializar_holobit(original)
    restaurado = holobit_module.deserializar_holobit(serializado)

    assert restaurado == {"tipo": "holobit", "valores": [1.0, 2.5, 3.0]}


def test_errores_de_dominio_holobit_en_espanol(holobit_module) -> None:
    with pytest.raises(holobit_module.ErrorHolobit, match="payload de holobit"):
        holobit_module.deserializar_holobit("{json malo")
