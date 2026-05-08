from __future__ import annotations


def test_startup_normal_no_carga_legacy_backends():
    import importlib
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
