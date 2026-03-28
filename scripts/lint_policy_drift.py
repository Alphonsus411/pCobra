#!/usr/bin/env python3
"""Detecta drift de policy en rutas públicas: solo targets oficiales."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

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
SKIP_PREFIXES = ("docs/historico/", "docs/experimental/", "docs/frontend/api/")
SKIP_FILES = {
    "scripts/ci/validate_targets.py",
    "scripts/lint_legacy_aliases.py",
    "scripts/targets_policy_common.py",
}
OFFICIAL = set(OFFICIAL_TARGETS)
CONTEXT = re.compile(
    r"(?i)(targets?|backends?|destinos?|--tipo|--destino|--origen)"
)
TOKEN = re.compile(r"(?<![\w.+/-])([a-z][a-z0-9_+-]{1,20})(?![\w.+/-])", re.IGNORECASE)
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


def main() -> int:
    errors: list[str] = []
    for path in _iter_files():
        rel = path.relative_to(ROOT).as_posix()
        content = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(content.splitlines(), start=1):
            lowered = line.lower()
            if not CONTEXT.search(lowered):
                continue
            for match in TOKEN.finditer(lowered):
                token = match.group(1).strip()
                if token in OFFICIAL or token in STOPWORDS:
                    continue
                if token in KNOWN_DISALLOWED:
                    errors.append(
                        f"{rel}:{line_no}: target fuera de policy pública detectado -> {token}"
                    )
    if errors:
        print("❌ Policy drift detectado (targets no permitidos en rutas públicas):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("✅ Policy drift: sin targets no permitidos en rutas públicas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
