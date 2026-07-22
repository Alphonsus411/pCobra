"""Contrato canónico de extensiones de archivos Cobra."""

from __future__ import annotations

from pathlib import Path


COBRA_SOURCE_EXTENSION = ".cobra"
COBRA_PACKAGE_EXTENSION = ".co"

COBRA_SOURCE_EXTENSIONS: frozenset[str] = frozenset({COBRA_SOURCE_EXTENSION})
COBRA_PACKAGE_EXTENSIONS: frozenset[str] = frozenset({COBRA_PACKAGE_EXTENSION})


def es_fuente_cobra(path: str | Path) -> bool:
    """Indica si ``path`` declara una fuente Cobra por su extensión."""

    return Path(path).suffix.lower() in COBRA_SOURCE_EXTENSIONS


def es_ruta_paquete_cobra(path: str | Path) -> bool:
    """Indica si ``path`` declara un paquete Cobra, sea válido o corrupto."""

    return Path(path).suffix.lower() in COBRA_PACKAGE_EXTENSIONS
