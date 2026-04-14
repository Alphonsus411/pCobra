"""Genera artefactos de contrato stdlib (manifiestos + docs)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pcobra.cobra.stdlib_contract.generator import sync_contract_artifacts  # noqa: E402


def main() -> int:
    sync_contract_artifacts(
        contract_dir=ROOT / "src" / "pcobra" / "cobra" / "stdlib_contract",
        docs_path=ROOT / "docs" / "_generated" / "stdlib_contract_matrix.md",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
