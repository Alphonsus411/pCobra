from __future__ import annotations

import pytest

from pcobra.cobra.cli.target_policies import SDK_COMPATIBLE_TARGETS
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    BACKEND_FEATURE_GAPS,
    CONTRACT_FEATURES,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.holobits.graficar import (
    _HOLOBIT_SDK_ERROR,
    _to_sdk_holobit,
    graficar,
)
from pcobra.core.holobits.holobit import Holobit
from pcobra.core.holobits.proyeccion import proyectar
from pcobra.core.holobits.transformacion import escalar, mover, transformar


def test_to_sdk_holobit_builds_stub_object_even_without_sdk_in_misaligned_env():
    sdk_hb = _to_sdk_holobit(Holobit([1, 2, 3]))

    assert hasattr(sdk_hb, "quarks")
    assert hasattr(sdk_hb, "antiquarks")
    assert len(sdk_hb.quarks) == 6
    assert len(sdk_hb.antiquarks) == 6


@pytest.mark.skipif(
    _HOLOBIT_SDK_ERROR is None,
    reason="Solo aplica cuando el entorno no tiene holobit_sdk instalado.",
)
@pytest.mark.parametrize(
    ("funcion", "args"),
    (
        (graficar, (Holobit([1, 2, 3]),)),
        (proyectar, (Holobit([1, 2, 3]), "2d")),
        (transformar, (Holobit([1, 2, 3]), "rotar", "z", 45)),
    ),
)
def test_holobit_sdk_fallback_raises_explicit_error_when_required_sdk_is_missing(funcion, args):
    with pytest.raises(ModuleNotFoundError, match="holobit_sdk|dependencia obligatoria"):
        funcion(*args)


@pytest.mark.skipif(
    _HOLOBIT_SDK_ERROR is None,
    reason="Solo aplica cuando el entorno no tiene holobit_sdk instalado.",
)
@pytest.mark.parametrize(
    ("funcion", "args"),
    (
        (escalar, (Holobit([1, 2, 3]), 2)),
        (mover, (Holobit([1, 2, 3]), 1, 2, 3)),
    ),
)
def test_holobit_sdk_helpers_also_raise_explicit_error_without_required_sdk(funcion, args):
    with pytest.raises(ModuleNotFoundError, match="holobit_sdk|dependencia obligatoria"):
        funcion(*args)


def test_gap_contract_non_python_declara_no_paridad_sdk():
    for backend in ("javascript", "rust", "wasm", "go", "cpp", "java", "asm"):
        assert len(BACKEND_FEATURE_GAPS[backend]["holobit"]) >= 1


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_fallback_contract_no_promueve_sdk_full_fuera_de_python(backend: str):
    if backend == "python":
        assert backend in SDK_COMPATIBLE_TARGETS
        return

    assert backend not in SDK_COMPATIBLE_TARGETS
    for feature in CONTRACT_FEATURES:
        assert BACKEND_COMPATIBILITY[backend][feature] != "full"
        assert len(BACKEND_FEATURE_GAPS[backend][feature]) >= 1
