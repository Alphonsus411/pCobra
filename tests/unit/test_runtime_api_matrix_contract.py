from __future__ import annotations

from pcobra.cobra.transpilers.runtime_api_matrix import (
    build_runtime_api_matrix,
    validate_runtime_api_parity_snapshot,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def test_runtime_api_snapshot_contract_is_up_to_date() -> None:
    validate_runtime_api_parity_snapshot()


def test_runtime_api_matrix_has_all_official_backends_and_python_full() -> None:
    matrix = build_runtime_api_matrix()

    available = matrix["available_api_by_backend"]
    missing = matrix["missing_api_by_backend"]

    assert set(available) == set(OFFICIAL_TARGETS)
    assert set(missing) == set(OFFICIAL_TARGETS)

    assert missing["python"]["global"] == []
    assert missing["python"]["corelibs"] == []
    assert missing["python"]["standard_library"] == []

    for backend in OFFICIAL_TARGETS:
        assert isinstance(available[backend]["global"], list)
        assert isinstance(missing[backend]["global"], list)
