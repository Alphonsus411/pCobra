"""Fuente única de verdad para targets oficiales de transpilación."""

from __future__ import annotations

from typing import Final, Literal, TypedDict


class TargetMetadata(TypedDict):
    """Metadatos mínimos por target oficial."""

    status: str
    release_priority: int
    maintainer: str | None
    holobit_contract: Literal["full", "partial", "none"]
    sdk_contract: Literal["full", "partial", "none"]


ALLOWED_TARGETS: Final[tuple[str, ...]] = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)

TARGETS_BY_TIER: Final[dict[str, tuple[str, ...]]] = {
    "tier_1": ("python", "rust", "javascript", "wasm"),
    "tier_2": ("go", "cpp", "java", "asm"),
}

TARGET_METADATA: Final[dict[str, TargetMetadata]] = {
    "python": {
        "status": "supported",
        "release_priority": 1,
        "maintainer": "core",
        "holobit_contract": "full",
        "sdk_contract": "full",
    },
    "rust": {
        "status": "supported",
        "release_priority": 2,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "javascript": {
        "status": "supported",
        "release_priority": 3,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "wasm": {
        "status": "supported",
        "release_priority": 4,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "go": {
        "status": "supported",
        "release_priority": 5,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "cpp": {
        "status": "supported",
        "release_priority": 6,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "java": {
        "status": "supported",
        "release_priority": 7,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
    "asm": {
        "status": "supported",
        "release_priority": 8,
        "maintainer": None,
        "holobit_contract": "partial",
        "sdk_contract": "partial",
    },
}


def _validate_target_config() -> None:
    allowed = set(ALLOWED_TARGETS)

    if set(TARGETS_BY_TIER) != {"tier_1", "tier_2"}:
        raise RuntimeError(
            "La configuración de tiers debe definir exactamente 'tier_1' y 'tier_2'. "
            f"current={tuple(TARGETS_BY_TIER)}"
        )

    tier_1 = TARGETS_BY_TIER["tier_1"]
    tier_2 = TARGETS_BY_TIER["tier_2"]
    merged = tier_1 + tier_2
    if tuple(merged) != ALLOWED_TARGETS:
        raise RuntimeError(
            "Los tiers deben concatenar exactamente los targets permitidos. "
            f"tier_1={tier_1}; tier_2={tier_2}; allowed={ALLOWED_TARGETS}"
        )

    if set(merged) != allowed:
        extras = tuple(sorted(set(merged) - allowed))
        missing = tuple(sorted(allowed - set(merged)))
        raise RuntimeError(
            "Targets inválidos en TARGETS_BY_TIER. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    metadata_keys = set(TARGET_METADATA)
    if metadata_keys != allowed:
        extras = tuple(sorted(metadata_keys - allowed))
        missing = tuple(sorted(allowed - metadata_keys))
        raise RuntimeError(
            "TARGET_METADATA debe cubrir exactamente la lista permitida. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    for target, meta in TARGET_METADATA.items():
        if meta["status"] != "supported":
            raise RuntimeError(
                f"Target '{target}' tiene estado inválido '{meta['status']}'. Debe ser 'supported'."
            )
        if not isinstance(meta["release_priority"], int):
            raise RuntimeError(f"Target '{target}' debe declarar release_priority entero")
        if meta["maintainer"] is not None and not isinstance(meta["maintainer"], str):
            raise RuntimeError(f"Target '{target}' debe usar maintainer string o None")
        if meta["holobit_contract"] not in {"none", "partial", "full"}:
            raise RuntimeError(
                f"Target '{target}' debe declarar holobit_contract en none|partial|full"
            )
        if meta["sdk_contract"] not in {"none", "partial", "full"}:
            raise RuntimeError(
                f"Target '{target}' debe declarar sdk_contract en none|partial|full"
            )



_validate_target_config()

TIER1_TARGETS: Final[tuple[str, ...]] = TARGETS_BY_TIER["tier_1"]
TIER2_TARGETS: Final[tuple[str, ...]] = TARGETS_BY_TIER["tier_2"]
OFFICIAL_TARGETS: Final[tuple[str, ...]] = TIER1_TARGETS + TIER2_TARGETS


def target_metadata(target: str) -> TargetMetadata:
    """Devuelve metadatos del target canónico o falla si no es oficial."""
    if target not in TARGET_METADATA:
        raise KeyError(
            "Target no permitido en configuración central: "
            f"{target}. Permitidos: {', '.join(ALLOWED_TARGETS)}"
        )
    return TARGET_METADATA[target]
