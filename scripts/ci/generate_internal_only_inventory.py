#!/usr/bin/env python3
"""Genera inventario de referencias a backends internal-only fuera de rutas internas.

Estrategia:
1) Búsqueda por path (rutas/documentos públicos vigilados).
2) Búsqueda por símbolos (tokens backend y claves de diccionarios de registro).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/compatibility/internal_only_refs_inventory.md"

TARGETS = ("go", "cpp", "java", "wasm", "asm")

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".rst",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".sh",
}

# Rutas con scope interno/histórico permitido para conservar compatibilidad temporal.
INTERNAL_ALLOWED_PREFIXES = (
    "src/pcobra/cobra/cli/internal_compat/",
    "docs/compatibility/",
    "docs/historico/",
    "docs/migracion_targets_retirados.md",
    "docs/migracion_cli_unificada.md",
    "tests/",
)

SYMBOL_PATTERNS: dict[str, re.Pattern[str]] = {
    "target_token": re.compile(r"(?<![\w.+/-])(?:go|cpp|java|wasm|asm)(?![\w.+/-])", re.IGNORECASE),
    "backend_flag": re.compile(r"--(?:backend|tipo)\s+(?:go|cpp|java|wasm|asm)(?![A-Za-z0-9_])", re.IGNORECASE),
    "registry_key": re.compile(r"[\"'](?:go|cpp|java|wasm|asm)[\"']\s*:", re.IGNORECASE),
}


@dataclass(frozen=True)
class Finding:
    rel_path: str
    line_number: int
    symbol: str
    line: str


def _is_scannable(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    parts = set(path.parts)
    if {".git", "node_modules", "__pycache__"} & parts:
        return False
    return path.is_file()


def _is_internal_allowed(rel: str) -> bool:
    return rel.startswith(INTERNAL_ALLOWED_PREFIXES)


def _scan() -> list[Finding]:
    findings: list[Finding] = []
    for path in ROOT.rglob("*"):
        if not _is_scannable(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if _is_internal_allowed(rel):
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for idx, line in enumerate(lines, start=1):
            for symbol, pattern in SYMBOL_PATTERNS.items():
                if pattern.search(line):
                    findings.append(Finding(rel, idx, symbol, line.strip()))
                    break
    return findings


def _render(findings: list[Finding]) -> str:
    grouped_by_path: dict[str, int] = defaultdict(int)
    grouped_by_symbol: dict[str, int] = defaultdict(int)
    for f in findings:
        grouped_by_path[f.rel_path] += 1
        grouped_by_symbol[f.symbol] += 1

    top_paths = sorted(grouped_by_path.items(), key=lambda item: (-item[1], item[0]))[:25]
    sample = sorted(findings, key=lambda item: (item.rel_path, item.line_number))[:80]

    lines = [
        "# Inventario de referencias internal-only (go/cpp/java/wasm/asm)",
        "",
        "Este reporte se genera con `scripts/ci/generate_internal_only_inventory.py`.",
        "",
        "## Método",
        "",
        "1. **Búsqueda por path**: se recorren archivos de texto fuera de rutas internas permitidas.",
        "2. **Búsqueda por símbolos**: detección de tokens directos, flags (`--backend`/`--tipo`) y claves de registro.",
        "",
        "## Rutas internas excluidas",
        "",
    ]
    lines.extend(f"- `{prefix}`" for prefix in INTERNAL_ALLOWED_PREFIXES)
    lines.extend(
        [
            "",
            "## Resumen",
            "",
            f"- Hallazgos fuera de rutas internas: **{len(findings)}**.",
            f"- Archivos afectados: **{len(grouped_by_path)}**.",
            "",
            "### Hallazgos por símbolo",
            "",
        ]
    )
    for symbol in sorted(SYMBOL_PATTERNS):
        lines.append(f"- `{symbol}`: {grouped_by_symbol.get(symbol, 0)}")

    lines.extend(["", "### Top paths con más hallazgos", "", "| path | hallazgos |", "|---|---:|"])
    for rel, count in top_paths:
        lines.append(f"| `{rel}` | {count} |")

    lines.extend(["", "### Muestra de hallazgos", "", "| path | línea | símbolo | extracto |", "|---|---:|---|---|"])
    for finding in sample:
        excerpt = finding.line.replace("|", "\\|")
        lines.append(
            f"| `{finding.rel_path}` | {finding.line_number} | `{finding.symbol}` | `{excerpt}` |"
        )

    lines.extend(
        [
            "",
            "## Nota de uso",
            "",
            "Este inventario es de diagnóstico. La eliminación se ejecuta por fases según `docs/compatibility/internal_only_backend_removal_checklist.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    findings = _scan()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(_render(findings), encoding="utf-8")
    print(f"[inventory] generado: {OUTPUT.relative_to(ROOT)} ({len(findings)} hallazgos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
