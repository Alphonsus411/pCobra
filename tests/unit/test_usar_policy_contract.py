from __future__ import annotations

from pathlib import Path
import importlib

import pytest

from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial
from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    REPL_COBRA_MODULE_INTERNAL_PATH_MAP,
    REPL_COBRA_MODULE_MAP,
    REPL_COBRA_MODULE_PACKAGE_MAP,
    USAR_COBRA_PUBLIC_MODULES,
    USAR_RUNTIME_EXPORT_OVERRIDES,
    validar_paridad_superficie_publica_modulos_canonicos,
)


def test_repl_module_map_contiene_exactamente_modulos_canonicos() -> None:
    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    assert tuple(REPL_COBRA_MODULE_MAP.keys()) == canonicos
    assert tuple(REPL_COBRA_MODULE_MAP.values()) == canonicos
    assert set(REPL_COBRA_MODULE_INTERNAL_PATH_MAP) == set(canonicos)


def test_modulos_oficiales_se_resuelven_como_paquetes_instalables() -> None:
    for alias, canonical in REPL_COBRA_MODULE_MAP.items():
        modulo = obtener_modulo_cobra_oficial(canonical)
        expected_package = REPL_COBRA_MODULE_PACKAGE_MAP[alias]
        legacy_path = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
        assert legacy_path != expected_package
        assert (Path(__file__).resolve().parents[2] / legacy_path).is_file()
        assert importlib.util.find_spec(expected_package) is not None
        assert modulo.__name__ == expected_package
        assert expected_package.startswith(
            ("pcobra.corelibs.", "pcobra.standard_library.")
        )

    assert REPL_COBRA_MODULE_INTERNAL_PATH_MAP is not REPL_COBRA_MODULE_PACKAGE_MAP


def test_contrato_superficie_publica_cubre_modulos_canonicos() -> None:
    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    assert set(CANONICAL_MODULE_SURFACE_CONTRACTS) == set(canonicos)


def test_validacion_paridad_superficie_publica_ejecutable() -> None:
    validar_paridad_superficie_publica_modulos_canonicos()


@pytest.mark.parametrize("modulo", USAR_COBRA_PUBLIC_MODULES)
def test_cada_export_oficial_tiene_una_clasificacion_explicita_de_capacidades(
    modulo: str,
) -> None:
    assert modulo in CANONICAL_MODULE_SURFACE_CONTRACTS
    assert modulo in USAR_COBRA_PUBLIC_MODULES

    contrato = CANONICAL_MODULE_SURFACE_CONTRACTS[modulo]
    exports_declarados = tuple(
        getattr(obtener_modulo_cobra_oficial(modulo), "__all__", ())
    )
    exports_oficiales = USAR_RUNTIME_EXPORT_OVERRIDES.get(modulo, exports_declarados)

    assert exports_declarados == exports_oficiales
    assert len(exports_oficiales) == len(set(exports_oficiales))
    assert set(contrato.symbol_capabilities) == set(exports_oficiales)

    for alias, destino in contrato.allowed_aliases.items():
        assert (
            contrato.symbol_capabilities[alias] == contrato.symbol_capabilities[destino]
        )


def test_consistencia_runtime_loader_docs_modulos_canonicos() -> None:
    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)

    assert tuple(REPL_COBRA_MODULE_MAP.keys()) == canonicos
    assert tuple(REPL_COBRA_MODULE_MAP.values()) == canonicos
    assert set(CANONICAL_MODULE_SURFACE_CONTRACTS) == set(canonicos)
    assert set(USAR_RUNTIME_EXPORT_OVERRIDES).issubset(set(canonicos))

    repo_root = Path(__file__).resolve().parents[2]
    for modulo in canonicos:
        doc_path = repo_root / "docs" / "standard_library" / f"{modulo}.md"
        assert doc_path.exists(), f"Falta doc pública para módulo canónico: {modulo}"
