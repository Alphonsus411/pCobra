#!/usr/bin/env python3
"""Genera una matriz de características soportadas por cada transpilador."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List

# Permitir importar los módulos desde `src`
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from cobra.transpilers.feature_inspector import extract_features  # noqa: E402


def _build_markdown_table(data: Dict[str, List[str]]) -> str:
    languages = list(data.keys())
    all_features = sorted({f for features in data.values() for f in features})
    header = ["Característica"] + languages
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for feature in all_features:
        row = [feature] + ["✅" if feature in data[lang] else "" for lang in languages]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _write_csv(data: Dict[str, List[str]], path: Path) -> None:
    languages = list(data.keys())
    all_features = sorted({f for features in data.values() for f in features})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["caracteristica"] + languages)
        for feature in all_features:
            writer.writerow([feature] + [1 if feature in data[lang] else 0 for lang in languages])


def main() -> None:
    data = extract_features()
    docs_dir = RAIZ / "docs"
    docs_dir.mkdir(exist_ok=True)

    markdown = _build_markdown_table(data)
    (docs_dir / "matriz_transpiladores.md").write_text(markdown, encoding="utf-8")
    _write_csv(data, docs_dir / "matriz_transpiladores.csv")


if __name__ == "__main__":
    main()
