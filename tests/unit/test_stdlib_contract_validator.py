from __future__ import annotations

from dataclasses import replace

from pcobra.cobra.stdlib_contract import CONTRACTS, get_contract_matrix
from pcobra.cobra.stdlib_contract.base import FunctionCoverage
from pcobra.cobra.stdlib_contract.validator import (
    ContractValidationError,
    validate_contract_descriptor,
    validate_contracts,
)


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


def test_stdlib_contract_rejects_duplicate_coverage_rows() -> None:
    contract = CONTRACTS[0]
    duplicated_coverage = (
        contract.coverage[0],
        FunctionCoverage(
            function=contract.coverage[0].function,
            backend_levels=contract.coverage[1].backend_levels,
        ),
    )
    duplicated_contract = replace(contract, coverage=duplicated_coverage)

    try:
        validate_contract_descriptor(duplicated_contract)
    except ContractValidationError as exc:
        assert "cobertura duplicada" in str(exc)
    else:
        raise AssertionError("Se esperaba ContractValidationError por cobertura duplicada")
