#!/usr/bin/env python3
"""Valida que los targets mencionados respeten la política oficial vigente.

Política oficial pública:
- Tier 1: python, rust, javascript, wasm
- Tier 2: go, cpp, java, asm

La fuente de verdad es ``src/pcobra/cobra/transpilers/targets.py``. Los aliases
legacy solo se toleran como compatibilidad interna controlada y nunca como
nombres canónicos públicos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.targets_policy_common import (
    LEGACY_ALIAS_ALLOWLIST,
    PUBLIC_TEXT_PATH_STRS,
    VALIDATION_SCAN_PATHS,
    read_target_policy,
)

# Rutas clave a escanear según política.
SCAN_ROOTS = tuple(
    path.relative_to(ROOT).as_posix() for path in VALIDATION_SCAN_PATHS
)

# Rutas generadas que no deben escanearse para evitar falsos positivos en artefactos.
GENERATED_PATH_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "site",
    "build",
    "dist",
    "docs/_build",
}

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

# Catálogo amplio para detectar nomenclatura obsoleta o fuera de política.
# La aceptación real se decide en tiempo de validación según si el término es
# canónico público, alias legacy interno o término completamente fuera de política.
KNOWN_LANGUAGE_ALIASES: set[str] | None = None

AMBIGUOUS_ARCHIVE_LINK_LABELS = (
    "experimental",
    "histórico",
    "historico",
    "interno",
    "interna",
    "internal",
    "fuera de política",
    "fuera de politica",
    "sin vigencia",
)

PUBLIC_NON_OFFICIAL_CONTEXT_PATTERNS = {
    "hololang": re.compile(
        r"(?=.*\bhololang\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|salida|output)\b)",
        re.IGNORECASE,
    ),
    "llvm": re.compile(
        r"(?=.*\bllvm\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|salida|output)\b)",
        re.IGNORECASE,
    ),
    "latex": re.compile(
        r"(?=.*\blatex\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|origen|orígenes|origenes|salida|output)\b)",
        re.IGNORECASE,
    ),
    "reverse-wasm": re.compile(
        r"\b(?:reverse\s+(?:desde|from)\s+(?:wasm|webassembly)|(?:wasm|webassembly)\s+reverse)\b",
        re.IGNORECASE,
    ),
}

PUBLIC_NON_OFFICIAL_REQUIRED_LABELS = {
    "hololang": ("interno", "interna", "internal", "experimental", "ir"),
    "llvm": ("experimental", "fuera de política", "fuera de politica", "interno", "interna", "internal"),
    "latex": ("experimental", "fuera de política", "fuera de politica", "interno", "interna", "internal"),
    "reverse-wasm": ("experimental", "retirado", "histórico", "historico", "fuera de política", "fuera de politica"),
}


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
            rel = path.relative_to(root).as_posix()
            if any(part in rel for part in GENERATED_PATH_PARTS):
                continue
            files.append(path)
            continue
        for candidate in path.rglob("*"):
            if not candidate.is_file():
                continue
            rel = candidate.relative_to(root).as_posix()
            if any(part in rel for part in GENERATED_PATH_PARTS):
                continue
            files.append(candidate)
    return files


def is_historical_exception(rel_path: str, line: str) -> tuple[bool, str | None]:
    if rel_path.startswith("docs/experimental/") or rel_path.startswith("docs/historico/"):
        return True, "Contenido archivado/experimental fuera de la documentación normativa."
    return False, None


def is_allowed_legacy_public_line(rel_path: str, line: str) -> bool:
    if rel_path not in PUBLIC_TEXT_PATH_STRS:
        return True
    allow_patterns = LEGACY_ALIAS_ALLOWLIST.get(rel_path, ())
    return any(pattern.search(line) for pattern in allow_patterns)


def main() -> int:
    policy = read_target_policy()
    tier1_targets = policy["tier1_targets"]
    tier2_targets = policy["tier2_targets"]
    official_targets = policy["official_targets"]
    expected_official_targets = tuple((*tier1_targets, *tier2_targets))
    if tuple(official_targets) != expected_official_targets:
        raise RuntimeError(
            "Política inválida: OFFICIAL_TARGETS debe ser exactamente tier1 + tier2 -> "
            f"official={official_targets}, tier1={tier1_targets}, tier2={tier2_targets}"
        )
    public_names = set(policy["public_names"])
    legacy_aliases = set(policy["legacy_aliases"])
    non_canonical_public_names = dict(policy["non_canonical_public_names"])
    out_of_policy_terms = set(policy["out_of_policy_language_terms"])
    known_language_aliases = (
        public_names
        | legacy_aliases
        | set(non_canonical_public_names)
        | out_of_policy_terms
    )
    language_pattern = re.compile(
        r"(?<![\w#.+-])("
        + "|".join(sorted(re.escape(term) for term in known_language_aliases))
        + r")(?![\w#.+-])",
        re.IGNORECASE,
    )

    errors: list[str] = []

    for path in iter_scan_files(ROOT):
        if not is_text_file(path):
            continue

        rel = path.relative_to(ROOT).as_posix()

        if rel in {
            "scripts/validate_targets_policy.py",
            "scripts/ci/validate_targets.py",
            "scripts/targets_policy_common.py",
        }:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Archivos textuales no UTF-8 se ignoran para evitar falsos positivos.
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            lowered = line.lower()
            if rel in PUBLIC_TEXT_PATH_STRS:
                if ("docs/experimental/" in line or "docs/historico/" in line) and not any(
                    label in lowered for label in AMBIGUOUS_ARCHIVE_LINK_LABELS
                ):
                    errors.append(
                        f"{rel}:{line_no}: enlace ambiguo a documentación experimental/histórica; añade etiqueta visible (experimental/interno/fuera de política/histórico)"
                    )

                for label, pattern in PUBLIC_NON_OFFICIAL_CONTEXT_PATTERNS.items():
                    if not pattern.search(line):
                        continue
                    if label == "hololang" and any(
                        marker in lowered
                        for marker in ("no expone", "no es", "no describe", "pipeline interno")
                    ):
                        continue
                    if not any(
                        marker in lowered
                        for marker in PUBLIC_NON_OFFICIAL_REQUIRED_LABELS[label]
                    ):
                        errors.append(
                            f"{rel}:{line_no}: referencia pública ambigua a {label}; debe etiquetarse como interno/experimental/fuera de política según corresponda"
                        )

            for match in language_pattern.finditer(line):
                term = match.group(1)
                normalized = term.lower().strip()

                if normalized in public_names:
                    continue

                if normalized in legacy_aliases:
                    if (
                        rel not in PUBLIC_TEXT_PATH_STRS
                        or is_allowed_legacy_public_line(rel, line)
                    ):
                        continue
                    errors.append(
                        f"{rel}:{line_no}: alias legacy expuesto como nombre público -> '{term}' "
                        f"(canónicos públicos: {', '.join(official_targets)})"
                    )
                    continue

                if normalized in non_canonical_public_names:
                    if rel not in PUBLIC_TEXT_PATH_STRS:
                        continue
                    errors.append(
                        f"{rel}:{line_no}: nombre público no canónico -> '{term}' "
                        f"(usar: {non_canonical_public_names[normalized]}; canónicos públicos: {', '.join(official_targets)})"
                    )
                    continue

                exempted, reason = is_historical_exception(rel, line)
                if exempted:
                    continue

                errors.append(
                    f"{rel}:{line_no}: referencia fuera de política -> '{term}' "
                    f"(tier1: {', '.join(tier1_targets)}; tier2: {', '.join(tier2_targets)}; "
                    f"canónicos públicos: {', '.join(official_targets)})"
                )

    if errors:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)

        print(
            "\nExcepciones históricas documentadas: docs/experimental/ y docs/historico/.",
            file=sys.stderr,
        )

        return 1

    print("✅ Validación de política de targets: OK")
    print(f"   Tier 1: {', '.join(tier1_targets)}")
    print(f"   Tier 2: {', '.join(tier2_targets)}")
    print(f"   Canónicos públicos: {', '.join(official_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
