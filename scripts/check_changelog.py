#!/usr/bin/env python3
"""Verifica que CHANGELOG.md contenga la entrada de version actual."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

CHANGELOG = Path("CHANGELOG.md")
PYPROJECT = Path("pyproject.toml")


def current_version() -> str:
    """Obtiene la version numerica definida en pyproject.toml."""
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    raw_version: str = data.get("project", {}).get("version", "")
    match = re.match(r"\d+\.\d+\.\d+", raw_version)
    if not match:
        raise ValueError("version invalida en pyproject.toml")
    return match.group(0)


def main() -> None:
    version = current_version()
    pattern = re.compile(
        rf"^## v{re.escape(version)} - (\d{{4}}-\d{{2}}-\d{{2}})\n((?:- .+\n)+)",
        re.MULTILINE,
    )
    text = CHANGELOG.read_text(encoding="utf-8")
    match = pattern.search(text)
    if not match:
        sys.exit(f"Entrada para v{version} no encontrada o con formato invalido")
    entries = [line.strip() for line in match.group(2).strip().splitlines()]
    if "Cambios pendientes." in entries:
        sys.exit("La entrada del changelog contiene un marcador pendiente")
    print(f"Changelog verificado para v{version}: {match.group(1)}")


if __name__ == "__main__":
    main()
