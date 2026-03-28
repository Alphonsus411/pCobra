from __future__ import annotations

import pytest

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
                if key != "asm"
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
    monkeypatch.setattr(registry, "TRANSPILER_CLASS_PATHS", patched_registry)

    with pytest.raises(RuntimeError, match=expected_fragment):
        registry._validate_registry_contract()
