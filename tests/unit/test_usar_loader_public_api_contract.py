from __future__ import annotations


import pytest

from cobra import usar_loader
from pcobra.core.usar_symbol_policy import sanear_simbolo_para_usar


PROHIBIDOS = {"self", "append", "map", "filter", "unwrap", "expect"}


def _simbolos_publicos(modulo) -> set[str]:
    if hasattr(modulo, "__all__"):
        return set(modulo.__all__)
    return {
        nombre
        for nombre, valor in vars(modulo).items()
        if not nombre.startswith("_") and callable(valor)
    }


def test_usar_numero_expone_solo_callables_en_espanol() -> None:
    modulo = usar_loader.obtener_modulo("numero")
    simbolos = _simbolos_publicos(modulo)

    assert simbolos
    assert all("__" not in nombre for nombre in simbolos)
    assert not (simbolos & PROHIBIDOS)
    assert all(hasattr(modulo, nombre) and callable(getattr(modulo, nombre)) for nombre in simbolos)
    assert all("_" in nombre or nombre.isalpha() for nombre in simbolos)


def test_usar_texto_expone_solo_callables_en_espanol() -> None:
    modulo = usar_loader.obtener_modulo("texto")
    simbolos = _simbolos_publicos(modulo)

    assert simbolos
    assert all("__" not in nombre for nombre in simbolos)
    assert not (simbolos & PROHIBIDOS)
    assert all(hasattr(modulo, nombre) and callable(getattr(modulo, nombre)) for nombre in simbolos)
    assert all("_" in nombre or nombre.isalpha() for nombre in simbolos)


def test_usar_datos_expone_operaciones_funcionales_clave() -> None:
    modulo = usar_loader.obtener_modulo("datos")
    simbolos = _simbolos_publicos(modulo)

    assert {"filtrar", "mapear", "reducir"}.issubset(simbolos)
    assert all("__" not in nombre for nombre in simbolos)
    assert not (simbolos & PROHIBIDOS)


def test_usar_numpy_rechazado_con_error_estructurado() -> None:
    with pytest.raises(PermissionError) as excinfo:
        usar_loader.obtener_modulo("numpy")

    mensaje = str(excinfo.value)
    assert "Importación no permitida" in mensaje
    assert "numpy" in mensaje
    assert "Módulos permitidos" in mensaje


def test_usar_holobit_expone_solo_api_cobra_sin_internals_sdk() -> None:
    modulo = usar_loader.obtener_modulo("holobit")
    simbolos = _simbolos_publicos(modulo)

    assert simbolos == {
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
    assert all("sdk" not in nombre.lower() for nombre in simbolos)
    assert all("__" not in nombre for nombre in simbolos)


def test_internals_holobit_sdk_no_importables_directo_desde_usar_loader() -> None:
    with pytest.raises(PermissionError) as excinfo:
        usar_loader.obtener_modulo("holobit_sdk")

    mensaje = str(excinfo.value)
    assert "Importación no permitida" in mensaje
    assert "holobit_sdk" in mensaje


@pytest.mark.parametrize("simbolo", sorted(PROHIBIDOS))
def test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje(simbolo: str) -> None:
    resultado = sanear_simbolo_para_usar(simbolo, lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "cobra_public_equivalent"
    assert isinstance(resultado.mensaje, str)
    assert resultado.mensaje.strip()


def test_backends_legacy_no_se_cargan_en_startup_normal() -> None:
    import sys
    from pcobra.cobra.bindings.runtime_manager import RuntimeManager

    RuntimeManager()
    legacy = {
        "pcobra.cobra.transpilers.transpiler.to_go",
        "pcobra.cobra.transpilers.transpiler.to_cpp",
        "pcobra.cobra.transpilers.transpiler.to_java",
        "pcobra.cobra.transpilers.transpiler.to_wasm",
        "pcobra.cobra.transpilers.transpiler.to_asm",
    }
    assert not (legacy & set(sys.modules))


def test_politica_publica_permanece_exactamente_python_javascript_rust() -> None:
    from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
