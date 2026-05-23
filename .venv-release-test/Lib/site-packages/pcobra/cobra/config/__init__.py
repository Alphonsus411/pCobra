"""Configuración central compartida para Cobra."""

from .transpile_targets import (
    ALLOWED_TARGETS,
    OFFICIAL_TARGETS,
    TARGET_METADATA,
    TARGETS_BY_TIER,
    TIER1_TARGETS,
    TIER2_TARGETS,
    target_metadata,
)

__all__ = [
    "ALLOWED_TARGETS",
    "OFFICIAL_TARGETS",
    "TARGET_METADATA",
    "TARGETS_BY_TIER",
    "TIER1_TARGETS",
    "TIER2_TARGETS",
    "target_metadata",
]
