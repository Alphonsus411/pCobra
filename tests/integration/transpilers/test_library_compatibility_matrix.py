from __future__ import annotations

import pytest

from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY
from pcobra.cobra.transpilers.library_compatibility import (
    LIBRARY_AREAS,
    LIBRARY_COMPATIBILITY,
    SEVERITY_ORDER,
    get_library_compatibility,
    highest_severity_for_backend,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_library_compatibility_matrix_covers_exactly_8_official_backends(backend: str):
    assert set(LIBRARY_COMPATIBILITY) == set(OFFICIAL_TARGETS)
    assert len(LIBRARY_COMPATIBILITY) == 8
    assert backend in LIBRARY_COMPATIBILITY


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
@pytest.mark.parametrize("area", LIBRARY_AREAS)
def test_library_compatibility_record_has_stable_contract_shape(backend: str, area: str):
    record = get_library_compatibility(backend, area)
    assert record.level in {"none", "partial", "full"}
    assert record.severity in SEVERITY_ORDER
    assert record.incompatibility.strip()
    assert record.workaround.strip()


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_runtime_library_level_matches_backend_contract_floor(backend: str):
    runtime_level = get_library_compatibility(backend, "runtime").level
    contract_level = BACKEND_COMPATIBILITY[backend]["corelibs"]

    # runtime no puede prometer más que el contrato mínimo oficial de corelibs/standard_library
    allowed = {
        "none": {"none"},
        "partial": {"none", "partial"},
        "full": {"none", "partial", "full"},
    }
    assert runtime_level in allowed[contract_level]


@pytest.mark.parametrize("backend", OFFICIAL_TARGETS)
def test_highest_severity_for_backend_is_declared_consistently(backend: str):
    computed = highest_severity_for_backend(backend)
    expected = max(
        (rec.severity for rec in LIBRARY_COMPATIBILITY[backend].values()),
        key=lambda sev: SEVERITY_ORDER[sev],
    )
    assert computed == expected
