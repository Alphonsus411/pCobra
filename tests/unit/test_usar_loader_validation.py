from __future__ import annotations

import importlib

import pytest

from pcobra.cobra.usar_loader import (
    _verificar_path_dentro_de_root,
    validar_nombre_modulo_cobra_proyecto,
    validar_nombre_modulo_usar,
)
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP, USAR_COBRA_FACING_MODULE_FLAGS


def test_repl_alias_map_contiene_modulos_base_numero_texto_datos():
    assert "numero" in REPL_COBRA_MODULE_MAP
    assert "texto" in REPL_COBRA_MODULE_MAP
    assert "datos" in REPL_COBRA_MODULE_MAP


def test_import_pcobra_no_hace_eager_load_de_backends_legacy():
    import sys

    legacy = (
        "pcobra.cobra.transpilers.transpiler.to_go",
        "pcobra.cobra.transpilers.transpiler.to_cpp",
        "pcobra.cobra.transpilers.transpiler.to_java",
        "pcobra.cobra.transpilers.transpiler.to_wasm",
        "pcobra.cobra.transpilers.transpiler.to_asm",
    )

    importlib.import_module("pcobra")

    for nombre in legacy:
        assert nombre not in sys.modules


def test_rechaza_imports_directos_backend_en_usar():
    for modulo in ("numpy", "node-fetch", "serde", "holobit_sdk"):
        with pytest.raises(PermissionError):
            validar_nombre_modulo_usar(modulo)


def test_flags_cobra_facing_cubren_modulos_repl():
    assert tuple(USAR_COBRA_FACING_MODULE_FLAGS.keys()) == tuple(REPL_COBRA_MODULE_MAP.keys())
    assert all(USAR_COBRA_FACING_MODULE_FLAGS.values())


def test_fuera_de_catalogo_no_llega_a_resolucion_de_modulo(monkeypatch):
    from pcobra.cobra import usar_loader

    def _no_debe_llamarse(*_args, **_kwargs):
        raise AssertionError("No debe intentarse resolver/cargar módulo fuera de catálogo.")

    monkeypatch.setattr(usar_loader, "obtener_modulo_cobra_oficial", _no_debe_llamarse)

    with pytest.raises(PermissionError) as excinfo:
        usar_loader.obtener_modulo("numpy")

    assert "fuera del catálogo público" in str(excinfo.value) or "Importación no permitida" in str(excinfo.value)


def test_modulo_no_publico_error_controlado_sin_traceback():
    with pytest.raises(PermissionError) as excinfo:
        validar_nombre_modulo_usar("modulo_interno_privado")

    mensaje = str(excinfo.value)
    assert "fuera del catálogo público" in mensaje or "módulo externo no permitido" in mensaje
    assert "Traceback" not in mensaje


def test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co(tmp_path):
    from pcobra.cobra.usar_loader import resolver_modulo_cobra_proyecto

    modulo = tmp_path / "utilidades" / "fechas.co"
    modulo.parent.mkdir()
    modulo.write_text("", encoding="utf-8")

    ruta = resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=tmp_path)

    assert ruta == modulo.resolve()


@pytest.mark.parametrize(
    "nombre",
    [
        "",
        "utilidades..fechas",
        ".utilidades",
        "utilidades.",
        "../secreto",
        "a/../b",
        "/tmp/x",
        r"C:\tmp\x",
        "C:tmp",
        r"a\b",
        "a/b",
        "utilidades/fechas",
        r"utilidades\\fechas",
        "C:secreto",
        "utilidades.fecha$",
        "utilidades.-fecha",
    ],
)
def test_resolver_modulo_cobra_proyecto_rechaza_nombres_inseguros(tmp_path, nombre):
    from pcobra.cobra.usar_loader import resolver_modulo_cobra_proyecto

    with pytest.raises(ValueError):
        resolver_modulo_cobra_proyecto(nombre, project_root=tmp_path)


def test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink(tmp_path):
    from pcobra.cobra.usar_loader import resolver_modulo_cobra_proyecto

    destino_externo = tmp_path.parent / f"{tmp_path.name}_externo"
    destino_externo.mkdir()
    (destino_externo / "fechas.co").write_text("", encoding="utf-8")
    (tmp_path / "utilidades").symlink_to(destino_externo, target_is_directory=True)

    with pytest.raises(ValueError, match="fuera de la raíz autorizada"):
        resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=tmp_path)


def test_resolver_modulo_cobra_proyecto_valida_current_file_dentro_de_root(tmp_path):
    from pcobra.cobra.usar_loader import resolver_modulo_cobra_proyecto

    externo = tmp_path.parent / f"{tmp_path.name}_archivo_externo.co"
    externo.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="fuera de la raíz autorizada"):
        resolver_modulo_cobra_proyecto(
            "utilidades.fechas",
            project_root=tmp_path,
            current_file=externo,
        )



@pytest.mark.parametrize(
    "nombre",
    ["../secreto", "a/../b", "/tmp/x", r"C:\tmp\x", "C:tmp", r"a\b", "a/b"],
)
def test_validar_nombre_modulo_cobra_proyecto_rechaza_rutas_manipuladas(nombre):
    with pytest.raises(ValueError):
        validar_nombre_modulo_cobra_proyecto(nombre)


def test_verificar_path_dentro_de_root_canonicaliza_antes_de_commonpath(tmp_path):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    ruta_manipulada = proyecto / "subdir" / ".." / ".." / "secreto.co"

    with pytest.raises(ValueError, match="fuera de la raíz autorizada"):
        _verificar_path_dentro_de_root(ruta_manipulada, proyecto)

def test_validacion_oficial_sigue_rechazando_nombres_punteados():
    with pytest.raises(ValueError):
        validar_nombre_modulo_usar("utilidades.fechas", require_allowlist=False)
