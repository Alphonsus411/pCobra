#!/usr/bin/env python3
"""Valida la política final de 8 backends oficiales."""

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
    NON_CANONICAL_PUBLIC_NAMES,
    PUBLIC_TEXT_PATH_STRS,
    VALIDATION_SCAN_PATHS,
    read_target_policy,
)

SCAN_ROOTS = tuple(path.relative_to(ROOT).as_posix() for path in VALIDATION_SCAN_PATHS)
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
SKIPPED_REL_PATHS = frozenset(
    {
        "scripts/validate_targets_policy.py",
        "scripts/ci/validate_targets.py",
        "scripts/targets_policy_common.py",
    }
)


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_OR_GENERATED_SUFFIXES:
        return False
    if path.name in LOCKFILES:
        return False
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample



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



def _normalized_public_line(line: str) -> str:
    return (
        line.replace(".js", "")
        .replace(".mjs", "")
        .replace(".cjs", "")
        .replace(".cpp", "")
        .replace(".wasm", "")
        .replace("Node.js", "Node")
    )



def _find_public_alias_errors(rel: str, content: str) -> list[str]:
    if rel not in PUBLIC_TEXT_PATH_STRS:
        return []
    errors: list[str] = []
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        line = _normalized_public_line(raw_line)
        for alias, canonical in NON_CANONICAL_PUBLIC_NAMES.items():
            pattern = re.compile(rf"(?<![\w.+/-]){re.escape(alias)}(?![\w.+/-])", re.IGNORECASE)
            if pattern.search(line):
                errors.append(
                    f"{rel}:{line_no}: alias público no canónico -> '{alias}' (usar: {canonical})"
                )
    return errors






def main() -> int:
    policy = read_target_policy()
    tier1_targets = tuple(policy["tier1_targets"])
    tier2_targets = tuple(policy["tier2_targets"])
    official_targets = tuple(policy["official_targets"])
    if official_targets != tier1_targets + tier2_targets:
        raise RuntimeError(
            "Política inválida: OFFICIAL_TARGETS debe ser exactamente TIER1_TARGETS + TIER2_TARGETS -> "
            f"official={official_targets}, tier1={tier1_targets}, tier2={tier2_targets}"
        )

    public_names = tuple(policy["public_names"])
    internal_names = tuple(policy["internal_names"])
    if public_names != official_targets:
        raise RuntimeError(
            "Política inválida: public_names debe coincidir exactamente con OFFICIAL_TARGETS -> "
            f"public={public_names}, official={official_targets}"
        )
    if internal_names != official_targets:
        raise RuntimeError(
            "Política inválida: internal_names debe coincidir exactamente con OFFICIAL_TARGETS -> "
            f"internal={internal_names}, official={official_targets}"
        )

    errors: list[str] = []

    for path in iter_scan_files(ROOT):
        if not is_text_file(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in SKIPPED_REL_PATHS:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        errors.extend(_find_public_alias_errors(rel, content))

    if errors:
        print("❌ Validación de política de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación de política de targets: OK")
    print(f"   Tier 1: {', '.join(tier1_targets)}")
    print(f"   Tier 2: {', '.join(tier2_targets)}")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
