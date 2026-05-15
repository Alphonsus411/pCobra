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


def test_stdlib_holobit_exporta_exactamente_api_permitida() -> None:
    from pcobra.standard_library import holobit as stdlib_holobit

    assert set(stdlib_holobit.__all__) == {
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
    assert all(callable(getattr(stdlib_holobit, nombre)) for nombre in stdlib_holobit.__all__)


def test_internals_holobit_sdk_no_importables_directo_desde_usar_loader() -> None:
    with pytest.raises(PermissionError) as excinfo:
        usar_loader.obtener_modulo("holobit_sdk")

    mensaje = str(excinfo.value)
    assert "Importación no permitida" in mensaje
    assert "holobit_sdk" in mensaje


@pytest.mark.parametrize("nombre", ["numpy", "holobit_sdk"])
def test_blocklist_se_aplica_antes_de_cualquier_import_dinamico(monkeypatch, nombre: str) -> None:
    def _import_dinamico_no_permitido(*_args, **_kwargs):
        raise AssertionError("No debe intentarse import dinámico para módulos bloqueados en `usar`.")

    monkeypatch.setattr(usar_loader.importlib.util, "spec_from_file_location", _import_dinamico_no_permitido)

    with pytest.raises(PermissionError) as excinfo:
        usar_loader.obtener_modulo(nombre)

    assert "Importación no permitida" in str(excinfo.value)


@pytest.mark.parametrize("simbolo", sorted(PROHIBIDOS))
def test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje(simbolo: str) -> None:
    resultado = sanear_simbolo_para_usar(simbolo, lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo == "cobra_public_equivalent"
    assert isinstance(resultado.mensaje, str)
    assert resultado.mensaje.strip()


@pytest.mark.parametrize("simbolo", ["_SDKHolobit", "Holobit", "holobit_sdk"])
def test_politica_bloquea_simbolos_sdk_holobit_en_superficie_usar(simbolo: str) -> None:
    resultado = sanear_simbolo_para_usar(simbolo, lambda: None)
    assert resultado.rechazado is True
    assert resultado.codigo in {"private_prefix", "cobra_public_equivalent"}


@pytest.mark.parametrize("payload", ['{"tipo":"holobit","valores":[1,"Holobit"]}', '{"tipo":"holobit_sdk","valores":[1,2]}'])
def test_holobit_deserializar_bloquea_referencias_sdk(payload: str) -> None:
    modulo = usar_loader.obtener_modulo("holobit")
    with pytest.raises(TypeError):
        modulo.deserializar_holobit(payload)


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




def test_superficie_usar_no_expone_aliases_ni_internals_prohibidos() -> None:
    modulos = ("numero", "texto", "datos", "archivo")
    prohibidos_exactos = {"self", "append", "map", "filter", "unwrap", "expect"}
    prohibidos_internals = {"_backend", "__all__", "os", "pathlib"}

    for nombre_modulo in modulos:
        modulo = usar_loader.obtener_modulo(nombre_modulo)
        simbolos = _simbolos_publicos(modulo)

        for simbolo in simbolos:
            assert "__" not in simbolo, f"{nombre_modulo} exporta símbolo dunder: {simbolo}"
            assert simbolo not in prohibidos_exactos, (
                f"{nombre_modulo} exporta símbolo no permitido: {simbolo}"
            )
            assert simbolo not in prohibidos_internals, (
                f"{nombre_modulo} exporta internals no permitidos: {simbolo}"
            )


def test_apertura_allowlist_archivo_existe_no_afecta_resolucion_publica() -> None:
    modulo_archivo = usar_loader.obtener_modulo("archivo")
    modulo_datos = usar_loader.obtener_modulo("datos")

    simbolos_archivo = _simbolos_publicos(modulo_archivo)
    simbolos_datos = _simbolos_publicos(modulo_datos)

    assert "existe" in simbolos_archivo
    assert "longitud" in simbolos_datos
    assert "_backend" not in simbolos_datos
    assert "__all__" not in simbolos_datos
    assert "pathlib" not in simbolos_datos


def test_arranque_normal_import_pcobra_no_precarga_legacy() -> None:
    import importlib
    import sys

    importlib.import_module("pcobra")

    legacy = {
        "pcobra.cobra.transpilers.transpiler.to_go",
        "pcobra.cobra.transpilers.transpiler.to_cpp",
        "pcobra.cobra.transpilers.transpiler.to_java",
        "pcobra.cobra.transpilers.transpiler.to_wasm",
        "pcobra.cobra.transpilers.transpiler.to_asm",
    }
    assert not (legacy & set(sys.modules))


def test_contrato_publico_backends_y_configuracion_publica_sin_extras() -> None:
    import re
    from pathlib import Path

    from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")

    contenido_pcobra_toml = Path("pcobra.toml").read_text(encoding="utf-8")
    requeridos = re.search(r'required_targets\s*=\s*\[(.*?)\]', contenido_pcobra_toml, re.DOTALL)
    assert requeridos is not None
    assert requeridos.group(1).replace('"', "").replace(" ", "") == "python,javascript,rust"

    contenido_readme = Path("README.md").read_text(encoding="utf-8")
    assert "Backends oficiales públicos para `cobra build`: `python`, `javascript`, `rust`." in contenido_readme

def test_politica_publica_permanece_exactamente_python_javascript_rust() -> None:
    from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
