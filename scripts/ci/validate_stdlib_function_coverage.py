#!/usr/bin/env python3
"""Valida cobertura por función (`full`/`partial`) frente a runtime_api_matrix."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.stdlib_contract.validator import (  # noqa: E402
    validate_contracts,
    validate_contracts_against_runtime_matrix,
    validate_generated_stdlib_contract_matrix,
)


def main() -> int:
    validate_contracts()
    validate_contracts_against_runtime_matrix()
    validate_generated_stdlib_contract_matrix()
    print("✅ Stdlib coverage by function valida contra runtime_api_matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
