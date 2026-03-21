#!/usr/bin/env python3
"""Genera la matriz contractual pública de transpiladores.

Este script ya no intenta inferir una cobertura amplia/exploratoria del AST.
Su objetivo es regenerar la tabla pública alineada con:
- los 8 targets oficiales de transpilación;
- el subconjunto con runtime oficial;
- el subconjunto conservado como runtime experimental/best-effort.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from pcobra.cobra.cli.target_policies import OFFICIAL_RUNTIME_TARGETS, TRANSPILATION_ONLY_TARGETS  # noqa: E402
from pcobra.cobra.transpilers.compatibility_matrix import BACKEND_COMPATIBILITY, CONTRACT_FEATURES  # noqa: E402
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, target_label  # noqa: E402

EXPERIMENTAL_RUNTIME_TARGETS = ("go", "java")
NO_RUNTIME_TARGETS = tuple(
    target for target in TRANSPILATION_ONLY_TARGETS if target not in EXPERIMENTAL_RUNTIME_TARGETS
)


def _runtime_policy(target: str) -> str:
    if target in OFFICIAL_RUNTIME_TARGETS:
        return "runtime_oficial"
    if target in EXPERIMENTAL_RUNTIME_TARGETS:
        return "runtime_experimental_best_effort"
    if target in NO_RUNTIME_TARGETS:
        return "solo_transpilacion"
    raise RuntimeError(f"Target fuera de política conocida: {target}")


def _build_markdown() -> str:
    lines = [
        "# Matriz de transpiladores",
        "",
        "Generado desde `scripts/generar_matriz_transpiladores.py`.",
        "",
        "## Resumen de política",
        "",
        f"- **Targets oficiales de transpilación**: {', '.join(f'`{t}`' for t in OFFICIAL_TARGETS)}.",
        f"- **Targets con runtime oficial**: {', '.join(f'`{t}`' for t in OFFICIAL_RUNTIME_TARGETS)}.",
        f"- **Targets con runtime experimental/best-effort**: {', '.join(f'`{t}`' for t in EXPERIMENTAL_RUNTIME_TARGETS)}.",
        f"- **Targets solo de transpilación**: {', '.join(f'`{t}`' for t in NO_RUNTIME_TARGETS)}.",
        "",
        "## Matriz contractual",
        "",
        "| Backend | Nombre | Tier | runtime_policy | " + " | ".join(CONTRACT_FEATURES) + " |",
        "|---|---|---|---|" + "---|" * len(CONTRACT_FEATURES),
    ]
    for backend in OFFICIAL_TARGETS:
        contract = BACKEND_COMPATIBILITY[backend]
        row = [
            f"`{backend}`",
            target_label(backend),
            contract["tier"].replace("tier", "Tier "),
            _runtime_policy(backend),
            *[contract[feature] for feature in CONTRACT_FEATURES],
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.extend(
        [
            "",
            "> `runtime_policy` distingue explícitamente entre transpilación oficial, runtime oficial y runtime experimental/best-effort.",
        ]
    )
    return "\n".join(lines) + "\n"



def _write_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["backend", "label", "tier", "runtime_policy", *CONTRACT_FEATURES])
        for backend in OFFICIAL_TARGETS:
            contract = BACKEND_COMPATIBILITY[backend]
            writer.writerow(
                [
                    backend,
                    target_label(backend),
                    contract["tier"],
                    _runtime_policy(backend),
                    *[contract[feature] for feature in CONTRACT_FEATURES],
                ]
            )


def main() -> None:
    docs_dir = RAIZ / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "matriz_transpiladores.md").write_text(_build_markdown(), encoding="utf-8")
    _write_csv(docs_dir / "matriz_transpiladores.csv")


if __name__ == "__main__":
    main()
