from __future__ import annotations

from pathlib import Path

from pcobra.cobra.usar_loader import USAR_COBRA_PUBLIC_MODULES, obtener_modulo_cobra_oficial
from pcobra.cobra.usar_policy import (
    CANONICAL_MODULE_SURFACE_CONTRACTS,
    REPL_COBRA_MODULE_INTERNAL_PATH_MAP,
    REPL_COBRA_MODULE_MAP,
    validar_paridad_superficie_publica_modulos_canonicos,
)


def test_repl_module_map_contiene_exactamente_modulos_canonicos() -> None:
    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    assert tuple(REPL_COBRA_MODULE_MAP.keys()) == canonicos
    assert tuple(REPL_COBRA_MODULE_MAP.values()) == canonicos
    assert set(REPL_COBRA_MODULE_INTERNAL_PATH_MAP) == set(canonicos)


def test_modulos_oficiales_se_resuelven_a_rutas_internas() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for alias, canonical in REPL_COBRA_MODULE_MAP.items():
        modulo = obtener_modulo_cobra_oficial(canonical)
        modulo_path = Path(modulo.__file__).resolve()

        expected_rel_path = REPL_COBRA_MODULE_INTERNAL_PATH_MAP[alias]
        expected_path = (repo_root / expected_rel_path).resolve()
        assert modulo_path == expected_path, (
            f"alias={alias} canonical={canonical} debe resolver a {expected_rel_path}, "
            f"obtuvo {modulo_path}"
        )


def test_contrato_superficie_publica_cubre_modulos_canonicos() -> None:
    canonicos = tuple(USAR_COBRA_PUBLIC_MODULES)
    assert set(CANONICAL_MODULE_SURFACE_CONTRACTS) == set(canonicos)


def test_validacion_paridad_superficie_publica_ejecutable() -> None:
    validar_paridad_superficie_publica_modulos_canonicos()
