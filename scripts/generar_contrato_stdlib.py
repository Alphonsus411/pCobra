"""Genera artefactos de contrato stdlib (manifiestos + docs + JSON)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.stdlib_contract.generator import sync_contract_artifacts  # noqa: E402
from pcobra.cobra.stdlib_contract.validator import validate_contracts  # noqa: E402


def main() -> int:
    validate_contracts()
    sync_contract_artifacts(
        contract_dir=ROOT / "src" / "pcobra" / "cobra" / "stdlib_contract",
        docs_generated_md=ROOT / "docs" / "_generated" / "stdlib_contract_matrix.md",
        docs_generated_json=ROOT / "docs" / "_generated" / "stdlib_contract_matrix.json",
        docs_stdlib_md=ROOT / "docs" / "standard_library" / "matriz_stdlib_unificada.md",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
