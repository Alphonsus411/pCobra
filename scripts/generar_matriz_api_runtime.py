#!/usr/bin/env python3
"""Genera la matriz viva de paridad de API runtime (JSON + Markdown)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from pcobra.cobra.transpilers.runtime_api_matrix import (  # noqa: E402
    build_runtime_api_matrix,
    render_runtime_api_matrix_markdown,
    validate_runtime_api_parity_snapshot,
)


def main() -> None:
    validate_runtime_api_parity_snapshot()
    matrix = build_runtime_api_matrix()

    output_dir = ROOT / "docs" / "_generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "runtime_api_matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "runtime_api_matrix.md").write_text(
        render_runtime_api_matrix_markdown(matrix),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
