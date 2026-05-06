from __future__ import annotations

import importlib

from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP


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
