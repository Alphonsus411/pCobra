#!/usr/bin/env python3
"""Valida que los targets mencionados respeten la política oficial (lista blanca).

Política oficial de targets permitidos:
- python
- rust
- javascript / js
- wasm
- go
- cpp
- java
- asm

El escaneo cubre rutas clave del repositorio y permite excepciones históricas
explícitas/documentadas para no bloquear referencias archivísticas preexistentes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TARGET_ALIASES

# Rutas clave a escanear según política.
SCAN_ROOTS = (
    "README.md",
    "docs",
    "examples",
    "docker",
    "scripts",
)

# Extensiones típicamente no textuales o no relevantes para política de targets.
BINARY_OR_GENERATED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".svgz",
    ".ico",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".bz2",
    ".xz",
    ".7z",
    ".jar",
    ".class",
    ".o",
    ".a",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".wasm",
    ".pyc",
    ".pyo",
    ".pyd",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
}

LOCKFILES = {
    "poetry.lock",
    "Pipfile.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.lock",
}

# Lista blanca de términos/alias permitidos para targets.
ALLOWED_TARGET_ALIASES = {
    *OFFICIAL_TARGETS,
    *TARGET_ALIASES.keys(),
    "c++",  # Alias textual común de cpp.
    "assembly",  # Alias de asm.
    "ensamblador",  # Alias de asm en español.
}

# Diccionario de aliases/lenguajes conocidos para detectar restos fuera de política.
# Nota: NO es una lista negra de prohibidos, sino un catálogo de términos de lenguaje
# conocidos; la validación real la decide ALLOWED_TARGET_ALIASES.
KNOWN_LANGUAGE_ALIASES = {
    # Permitidos
    *ALLOWED_TARGET_ALIASES,
    # Históricos/no permitidos en política actual
    "cobol",
    "ruby",
    "kotlin",
    "swift",
    "typescript",
    "php",
    "perl",
    "pascal",
    "fortran",
    "visualbasic",
    "visual basic",
    "matlab",
    "mojo",
    "julia",
    "latex",
    "scala",
    "haskell",
    "lua",
    "dart",
    "elixir",
    "clojure",
    "f#",
    "c#",
}

# Excepciones históricas explícitas (archivo + patrón + motivo).
# Se usan para no bloquear PRs por referencias archivísticas preexistentes.
HISTORICAL_EXCEPTIONS: dict[str, tuple[tuple[str, str], ...]] = {
    "README.md": (
        (r"latex", "Referencia al cheatsheet en formato LaTeX (documentación de formato)."),
    ),
    "docs/README.en.md": (
        (r"latex", "Referencia al cheatsheet en formato LaTeX (documentación de formato)."),
    ),
    "docs/frontend/recursos_adicionales.rst": (
        (r"latex", "Enlace a recurso .tex del cheatsheet."),
    ),
    "docs/soporte_latex.md": (
        (r"latex", "Documento de soporte del parser de LaTeX, no target de compilación."),
    ),
    "docs/cheatsheet.tex": (
        (r"kotlin|ruby", "Comparativas pedagógicas en cheatsheet heredado."),
    ),
    "docs/MANUAL_COBRA.md": (
        (
            r"kotlin|swift",
            "Comparativas históricas de API en manual; no declara targets soportados.",
        ),
    ),
    "docs/MANUAL_COBRA.rst": (
        (
            r"kotlin|swift",
            "Comparativas históricas de API en manual; no declara targets soportados.",
        ),
    ),
    "docs/standard_library/logica.md": (
        (r"kotlin", "Comparativa puntual de comportamiento de función."),
    ),
    "docs/estructura_ast.md": (
        (
            r"kotlin|swift|r|julia|cobol|fortran|pascal|visual\s*basic|ruby|php|perl|matlab|mojo|latex|c",
            "Sección explícitamente histórica sobre targets descartados.",
        ),
    ),
    "docs/proposals/plan_nuevas_funcionalidades.md": (
        (
            r"kotlin|swift|r|julia|matlab",
            "Propuesta histórica, no documentación normativa de targets.",
        ),
    ),
}

LANGUAGE_PATTERN = re.compile(
    r"(?<![\w#.+-])(" + "|".join(sorted(re.escape(t) for t in KNOWN_LANGUAGE_ALIASES)) + r")(?![\w#.+-])",
    re.IGNORECASE,
)


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_OR_GENERATED_SUFFIXES:
        return False
    if path.name in LOCKFILES:
        return False

    try:
        with path.open("rb") as fh:
            sample = fh.read(4096)
    except OSError:
        return False

    # Heurística simple para binarios.
    if b"\x00" in sample:
        return False

    return True


def iter_scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for entry in SCAN_ROOTS:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        files.extend(p for p in path.rglob("*") if p.is_file())
    return files


def is_historical_exception(rel_path: str, line: str) -> tuple[bool, str | None]:
    rules = HISTORICAL_EXCEPTIONS.get(rel_path)
    if not rules:
        return False, None

    for pattern, reason in rules:
        if re.search(pattern, line, flags=re.IGNORECASE):
            return True, reason

    return False, None


def main() -> int:
    root = ROOT
    errors: list[str] = []

    for path in iter_scan_files(root):
        if not is_text_file(path):
            continue

        rel = path.relative_to(root).as_posix()

        if rel == "scripts/validate_targets_policy.py":
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Archivos textuales no UTF-8 se ignoran para evitar falsos positivos.
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            for match in LANGUAGE_PATTERN.finditer(line):
                term = match.group(1)
                normalized = term.lower().strip()
                if normalized in ALLOWED_TARGET_ALIASES:
                    continue

                exempted, reason = is_historical_exception(rel, line)
                if exempted:
                    continue

                errors.append(
                    f"{rel}:{line_no}: referencia fuera de política -> '{term}'"
                    f" (permitidos: {', '.join(OFFICIAL_TARGETS)}; aliases: {', '.join(sorted(TARGET_ALIASES))})"
                )

    if errors:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)

        print("\nExcepciones históricas documentadas:", file=sys.stderr)
        for rel, rules in sorted(HISTORICAL_EXCEPTIONS.items()):
            for pattern, reason in rules:
                print(f" - {rel}: /{pattern}/ -> {reason}", file=sys.stderr)

        return 1

    print("✅ Validación de política de targets: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
