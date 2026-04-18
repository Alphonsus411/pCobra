#!/usr/bin/env python3
"""Valida que la versión pública en documentación esté unificada."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
PUBLIC_DOCS = (
    ROOT / "docs/MANUAL_COBRA.md",
    ROOT / "docs/MANUAL_COBRA.rst",
    ROOT / "docs/README.en.md",
    ROOT / "docs/guia_basica.md",
)
SEMVER_RE = re.compile(r"\b(\d+\.\d+\.\d+)\b")


def project_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        raise ValueError("[project].version inválida en pyproject.toml")
    return version


def extract_doc_versions(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    versions: set[str] = set()

    for match in re.finditer(r"(?mi)^\s*(?:versión|version)\s+(\d+\.\d+\.\d+)\s*$", content):
        versions.add(match.group(1))
    for match in re.finditer(r"releases/download/v(\d+\.\d+\.\d+)/", content):
        versions.add(match.group(1))

    return versions


def main() -> int:
    canonical = project_version()
    all_versions: set[str] = set()
    mismatches: list[tuple[Path, set[str]]] = []

    for doc in PUBLIC_DOCS:
        versions = extract_doc_versions(doc)
        if not versions:
            print(f"ERROR: no se encontró versión pública en {doc.relative_to(ROOT)}.", file=sys.stderr)
            return 1
        if versions != {canonical}:
            mismatches.append((doc, versions))
        all_versions.update(versions)

    if len(all_versions) > 1 or mismatches:
        print(
            "ERROR: se detectaron versiones públicas inconsistentes. "
            f"Versión canónica (pyproject.toml): {canonical}.",
            file=sys.stderr,
        )
        for doc, versions in mismatches:
            printable = ", ".join(sorted(versions))
            print(f" - {doc.relative_to(ROOT)} => {printable}", file=sys.stderr)
        return 1

    print(f"OK: documentación pública unificada en versión {canonical}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
