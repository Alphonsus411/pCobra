"""INTERNAL COMPATIBILITY ONLY. Shim histórico de compatibilidad para ``cobra.transpilers.targets``.

Fuente canónica: :mod:`pcobra.cobra.transpilers.targets`.
"""
# pcobra-compat: allow-legacy-imports

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS

__all__ = ["TIER1_TARGETS", "TIER2_TARGETS", "OFFICIAL_TARGETS"]
