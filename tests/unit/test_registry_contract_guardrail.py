from __future__ import annotations

import pytest

from pcobra.cobra.transpilers import legacy_registry
from pcobra.cobra.transpilers import registry


@pytest.mark.parametrize(
    "patched_registry, expected_fragment",
    [
        (
            {
                **registry.TRANSPILER_CLASS_PATHS,
                "fantasy": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
            },
            "claves fuera de contrato",
        ),
        (
            {
                key: value
                for key, value in registry.TRANSPILER_CLASS_PATHS.items()
                if key != "rust"
            },
            "claves fuera de contrato",
        ),
    ],
)
def test_validate_registry_contract_falla_si_el_registro_sale_de_la_matriz_oficial(
    monkeypatch,
    patched_registry,
    expected_fragment,
):
    monkeypatch.setattr(registry, "PUBLIC_TRANSPILER_CLASS_PATHS", patched_registry)

    with pytest.raises(RuntimeError, match="PUBLIC_TRANSPILER_CLASS_PATHS"):
        registry._validate_complete_registry_contract()


def test_validate_public_registry_contract_falla_con_clave_extra(monkeypatch):
    monkeypatch.setattr(
        registry,
        "PUBLIC_TRANSPILER_CLASS_PATHS",
        {
            **registry.PUBLIC_TRANSPILER_CLASS_PATHS,
            "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
        },
    )

    with pytest.raises(RuntimeError, match="PUBLIC_TRANSPILER_CLASS_PATHS"):
        registry._validate_public_registry_contract()


def test_validate_internal_legacy_registry_contract_falla_si_falta_backend(monkeypatch):
    removed_backend = next(iter(legacy_registry.INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS))
    monkeypatch.setattr(legacy_registry, "_ORDERED_INTERNAL_LEGACY_TARGETS_CACHE", None)
    monkeypatch.setattr(
        legacy_registry,
        "INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS",
        {
            key: value
            for key, value in legacy_registry.INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS.items()
            if key != removed_backend
        },
    )

    with pytest.raises(
        RuntimeError,
        match="INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS",
    ):
        legacy_registry._validate_internal_legacy_registry_contract()
