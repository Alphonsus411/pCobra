"""Utilidades compartidas para leer fuente Cobra desde CLI/pipeline."""

from __future__ import annotations

from pathlib import Path
from os import PathLike


def normalize_cobra_source(text: str) -> str:
    """Normaliza fuente Cobra antes de tokenizar sin cambiar la gramática.

    Solo elimina el BOM UTF-8 inicial cuando existe. Usar ``utf-8-sig`` en la
    lectura ya lo consume, pero ``removeprefix`` conserva compatibilidad si el
    texto llega desde otra frontera.
    """

    return text.removeprefix("\ufeff")


def read_cobra_source(path: str | PathLike[str]) -> str:
    """Lee un archivo Cobra aceptando UTF-8 con o sin BOM inicial."""

    text = Path(path).read_text(encoding="utf-8-sig")
    return normalize_cobra_source(text)
