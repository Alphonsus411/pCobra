#!/usr/bin/env python3
"""Detecta drift de policy canónica en rutas públicas (set oficial de 3 backends públicos)."""

from __future__ import annotations

import re
import sys
import tokenize
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.architecture.backend_policy import (
    PUBLIC_BACKENDS,
    assert_public_targets_contract,
)

SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "examples",
    ROOT / "scripts",
    ROOT / ".github/workflows",
    ROOT / "docker",
    ROOT / "pcobra.toml",
    ROOT / "cobra.toml",
)
TEXT_EXTS = {".md", ".rst", ".toml", ".yml", ".yaml", ".txt", ".py", ".sh"}
SKIP_PREFIXES = ("docs/historico/", "docs/experimental/", "docs/frontend/api/", "docs/auditorias/")
SKIP_FILES = {
    "scripts/ci/validate_targets.py",
    "scripts/lint_legacy_aliases.py",
    "scripts/audit_retired_targets.py",
    "scripts/targets_policy_common.py",
}
assert_public_targets_contract(
    tuple(PUBLIC_BACKENDS), source="scripts/lint_policy_drift.py"
)
OFFICIAL = set(PUBLIC_BACKENDS)
CONTEXT = re.compile(r"(?i)(targets?|backends?|destinos?|--tipo|--destino|--origen)")
TOKEN = re.compile(r"(?<![\w.+/-])([a-z][a-z0-9_+-]{1,20})(?![\w.+/-])", re.IGNORECASE)
NODE_IDENTIFIER = re.compile(r"\bnode\s+ids?\b", re.IGNORECASE)
KNOWN_DISALLOWED = {
    "assembly",
    "assembler",
    "js",
    "py",
    "python3",
    "nodejs",
    "node",
    "golang",
    "jvm",
    "llvm",
    "latex",
    "hololang",
}
STOPWORDS = {
    "target",
    "targets",
    "backend",
    "backends",
    "runtime",
    "tier",
    "tiers",
    "oficial",
    "oficiales",
    "official",
    "reverse",
}

# Excepciones estrictamente acotadas: este checklist documenta el auditor que
# impide reintroducir aliases retirados, por lo que necesita enumerar los
# términos que dicho auditor rechaza. No es una declaración de targets válidos.
DOCUMENTED_CONTEXT_EXCEPTIONS = {
    "docs/architecture/backend-pipeline-checklist.md": (
        "audit_public_backend_exposure_terms.py",
    ),
    # Este gate define patrones de rechazo para backends retirados. Sus mensajes
    # y expresiones regulares son evidencia del control, no oferta pública.
    "scripts/ci/validate_workflow_target_matrix.py": (
        "backend retirado",
        "referencia de target/pipeline retirado",
    ),
}


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_ROOTS:
        if not base.exists():
            continue
        if base.is_file():
            files.append(base)
            continue
        for candidate in sorted(base.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() in TEXT_EXTS:
                rel = candidate.relative_to(ROOT).as_posix()
                if rel.startswith(SKIP_PREFIXES):
                    continue
                if rel in SKIP_FILES:
                    continue
                files.append(candidate)
    return files


def _python_name_spans(line: str) -> set[tuple[int, int]]:
    """Devuelve identificadores Python para no confundir nombres homónimos con backends."""
    spans: set[tuple[int, int]] = set()
    try:
        tokens = tokenize.generate_tokens(StringIO(line).readline)
        for token in tokens:
            if token.type == tokenize.NAME:
                spans.add((token.start[1], token.end[1]))
    except (IndentationError, tokenize.TokenError):
        pass
    return spans


def _find_policy_drift(path: Path, content: str) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    exceptions = DOCUMENTED_CONTEXT_EXCEPTIONS.get(rel, ())
    errors: list[str] = []
    for line_no, line in enumerate(content.splitlines(), start=1):
        lowered = line.lower()
        if not CONTEXT.search(lowered):
            continue
        if any(context in lowered for context in exceptions):
            continue
        python_names = (
            _python_name_spans(line) if path.suffix.lower() == ".py" else set()
        )
        for match in TOKEN.finditer(lowered):
            token = match.group(1).strip()
            if token in OFFICIAL or token in STOPWORDS:
                continue
            if token == "node" and NODE_IDENTIFIER.search(line):
                continue
            if token in KNOWN_DISALLOWED and match.span(1) not in python_names:
                errors.append(
                    f"{rel}:{line_no}: target fuera de policy pública detectado -> {token}"
                )
    return errors


def main() -> int:
    errors: list[str] = []
    for path in _iter_files():
        content = path.read_text(encoding="utf-8", errors="ignore")
        errors.extend(_find_policy_drift(path, content))
    if errors:
        print("❌ Policy drift detectado (targets no permitidos en rutas públicas):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("✅ Policy drift: sin targets no permitidos en rutas públicas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
