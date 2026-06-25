"""INTERNAL COMPATIBILITY ONLY. Shim histórico para la ruta legacy to_wasm.

La implementación legacy vive en el módulo legacy.to_wasm. Este alias se
conserva para importadores internos durante la migración y sigue requiriendo
PCOBRA_ENABLE_LEGACY_TRANSPILERS=1 porque el módulo legacy canónico valida
ese opt-in al importarse.
"""
# pcobra-compat: allow-legacy-transpiler-shim

from pcobra.cobra.transpilers.transpiler.legacy.to_wasm import TranspiladorWasm

__all__ = ["TranspiladorWasm"]
