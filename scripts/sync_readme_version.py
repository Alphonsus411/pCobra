#!/usr/bin/env python3
"""Sincroniza el bloque 'Versión ...' de README.md con [project].version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"
VERSION_PATTERN = re.compile(r"(^\s*Versión\s+)(\d+\.\d+\.\d+)(\s*$)", re.MULTILINE)


def project_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("[project].version inválida en pyproject.toml")
    return version


def sync(check: bool) -> int:
    version = project_version()
    original = README.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(original)
    if not match:
        raise ValueError("No se encontró un bloque 'Versión X.Y.Z' en README.md")

    current = match.group(2)
    if current == version:
        print(f"README.md ya está sincronizado con pyproject.toml ({version}).")
        return 0

    if check:
        print(
            "README.md desincronizado: "
            f"Versión {current} != [project].version {version}",
            file=sys.stderr,
        )
        return 1

    updated = VERSION_PATTERN.sub(rf"\g<1>{version}\g<3>", original, count=1)
    README.write_text(updated, encoding="utf-8")
    print(f"README.md actualizado: Versión {current} -> Versión {version}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="No modifica archivos; falla si README.md y pyproject.toml no coinciden.",
    )
    args = parser.parse_args()
    return sync(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
