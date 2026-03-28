#!/usr/bin/env python3
"""Auditoría de mantenimiento histórico para detectar aliases/targets retirados (fuera de CI canónico)."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Mantener sincronizado con ``src/pcobra/cobra/transpilers/target_utils.py``.
DEPRECATION_WINDOW_START_VERSION = "10.0.10"
DEPRECATION_WINDOW_REMOVAL_VERSION = "10.2.0"
TARGET_ALIASES = {"ensamblador": "asm", "c++": "cpp"}
LEGACY_OR_AMBIGUOUS_TARGETS = (
    "assembly",
    "js",
    "c",
    "cxx",
    "cpp11",
    "cpp17",
    "asm64",
    "assembler",
    "node",
    "nodejs",
    "py",
    "python3",
    "golang",
    "jvm",
)
RETIRED_TARGET_REPLACEMENTS = {
    "assembly": "asm",
    "js": "javascript",
    "c": "cpp",
    "cxx": "cpp",
    "cpp11": "cpp",
    "cpp17": "cpp",
    "asm64": "asm",
    "assembler": "asm",
    "node": "javascript",
    "nodejs": "javascript",
    "py": "python",
    "python3": "python",
    "golang": "go",
    "jvm": "java",
}

DEFAULT_GLOBS = (
    "*.md",
    "*.rst",
    "*.txt",
    "*.yaml",
    "*.yml",
    "*.toml",
    "*.json",
    "*.py",
    "*.sh",
    "*.ps1",
    "*.co",
)


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    matched: str
    recommendation: str


def _build_token_pattern(tokens: tuple[str, ...]) -> re.Pattern[str]:
    escaped = [re.escape(token) for token in sorted(tokens, key=len, reverse=True)]
    alternatives = "|".join(escaped)
    return re.compile(
        rf"(?:--(?:backend|tipo|contenedor|sandbox-docker|lenguajes)\s+|"
        rf"(?:backend|tipo|target|lenguajes)\s*[:=]\s*)"
        rf"[\"']?({alternatives})[\"']?(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )


def _iter_candidate_files(root: Path, globs: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for pattern in globs:
        files.extend(path for path in root.rglob(pattern) if path.is_file())
    return sorted(set(files))


def _scan_file(path: Path, token_pattern: re.Pattern[str]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings

    for idx, line in enumerate(lines, start=1):
        for match in token_pattern.finditer(line):
            raw = match.group(1)
            normalized = raw.lower()
            recommendation = RETIRED_TARGET_REPLACEMENTS.get(
                normalized,
                TARGET_ALIASES.get(normalized, "<target-canónico>"),
            )
            findings.append(
                Finding(
                    path=path,
                    line_number=idx,
                    matched=raw,
                    recommendation=recommendation,
                )
            )
    return findings


def run_audit(root: Path, *, globs: tuple[str, ...]) -> list[Finding]:
    retired_tokens = tuple(sorted(set(LEGACY_OR_AMBIGUOUS_TARGETS) | set(TARGET_ALIASES)))
    token_pattern = _build_token_pattern(retired_tokens)
    findings: list[Finding] = []
    for path in _iter_candidate_files(root, globs):
        if any(part in {".git", ".venv", "__pycache__", "node_modules"} for part in path.parts):
            continue
        findings.extend(_scan_file(path, token_pattern))
    return findings


def _print_report(findings: list[Finding], *, root: Path) -> None:
    print(
        "Auditoría de targets retirados\n"
        f"- Ventana deprecación: v{DEPRECATION_WINDOW_START_VERSION}\n"
        f"- Eliminación definitiva: v{DEPRECATION_WINDOW_REMOVAL_VERSION}\n"
        f"- Raíz auditada: {root}"
    )
    if not findings:
        print("OK: no se detectaron targets/aliases retirados.")
        return
    print(f"Se detectaron {len(findings)} hallazgos:")
    for finding in findings:
        rel = finding.path.relative_to(root)
        print(
            f"- {rel}:{finding.line_number} -> '{finding.matched}' "
            f"(migrar a '{finding.recommendation}')"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Ruta del proyecto a auditar (por defecto: directorio actual).",
    )
    parser.add_argument(
        "--glob",
        action="append",
        dest="globs",
        help="Glob adicional de archivos a auditar (puede repetirse).",
    )
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    globs = tuple(args.globs) if args.globs else DEFAULT_GLOBS
    findings = run_audit(root, globs=globs)
    _print_report(findings, root=root)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
