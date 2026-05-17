from __future__ import annotations

import importlib

import pytest

from pcobra.cobra.usar_loader import validar_nombre_modulo_usar
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
