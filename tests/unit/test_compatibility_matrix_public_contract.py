from pcobra.cobra.config.transpile_targets import LEGACY_INTERNAL_TARGETS
from pcobra.cobra.transpilers.compatibility_matrix import (
    AST_FEATURE_MINIMUM_CONTRACT,
    BACKEND_COMPATIBILITY,
    BACKEND_COMPATIBILITY_NOTES,
    BACKEND_FEATURE_GAPS,
    BACKEND_HOLOBIT_SDK_CAPABILITIES,
    HOLOBIT_CAPABILITY_FALLBACKS,
    LEGACY_BACKEND_INVENTORY,
    PUBLIC_BACKEND_COMPATIBILITY,
    SDK_PARTIAL_BACKENDS,
)


def test_public_contract_excludes_legacy_backends():
    legacy = set(LEGACY_INTERNAL_TARGETS)

    public_structures = {
        "PUBLIC_BACKEND_COMPATIBILITY": PUBLIC_BACKEND_COMPATIBILITY,
        "BACKEND_COMPATIBILITY": BACKEND_COMPATIBILITY,
        "SDK_PARTIAL_BACKENDS": {backend: {} for backend in SDK_PARTIAL_BACKENDS},
        "AST_FEATURE_MINIMUM_CONTRACT": AST_FEATURE_MINIMUM_CONTRACT,
        "BACKEND_COMPATIBILITY_NOTES": BACKEND_COMPATIBILITY_NOTES,
        "BACKEND_FEATURE_GAPS": BACKEND_FEATURE_GAPS,
        "BACKEND_HOLOBIT_SDK_CAPABILITIES": BACKEND_HOLOBIT_SDK_CAPABILITIES,
        "HOLOBIT_CAPABILITY_FALLBACKS": HOLOBIT_CAPABILITY_FALLBACKS,
    }

    for name, structure in public_structures.items():
        leaked = sorted(set(structure) & legacy)
        assert not leaked, f"{name} expone backends legacy en superficie pública: {leaked}"


def test_legacy_inventory_stays_internal_only_and_alias_points_to_public():
    assert set(LEGACY_BACKEND_INVENTORY) == set(LEGACY_INTERNAL_TARGETS)
    assert set(PUBLIC_BACKEND_COMPATIBILITY).isdisjoint(LEGACY_BACKEND_INVENTORY)
    assert BACKEND_COMPATIBILITY is PUBLIC_BACKEND_COMPATIBILITY
