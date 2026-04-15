from __future__ import annotations

from pcobra.cobra.stdlib_contract import CONTRACTS, get_contract_matrix
from pcobra.cobra.stdlib_contract.validator import validate_contracts


def test_stdlib_contracts_validate() -> None:
    validate_contracts()


def test_stdlib_matrix_contains_all_contract_modules() -> None:
    matrix = get_contract_matrix()
    modules = matrix["modules"]
    assert isinstance(modules, list)

    declared = {contract.module for contract in CONTRACTS}
    rendered = {item["module"] for item in modules}
    assert rendered == declared

    for module in modules:
        assert isinstance(module["public_api"], list)
        assert isinstance(module["coverage"], list)
        assert isinstance(module["runtime_mapping"], dict)
        coverage_rows = module["coverage"]
        assert coverage_rows
        for row in coverage_rows:
            assert row["level"] in {"full", "partial"}
