from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def ruta_ejemplos() -> Path:
    """Devuelve el directorio donde se guardan los programas ``.cobra`` de prueba."""
    base = Path(__file__).resolve().parent
    local = base / "data"
    if local.exists():
        return local
    # Si los ejemplos están en el paquete principal ``pCobra/tests/data``
    return base.parent / "pCobra" / "tests" / "data"


@pytest.fixture
def cargar_programa(ruta_ejemplos: Path) -> Callable[[str], str]:
    """Carga el contenido de un programa ``.cobra`` por nombre."""

    def _cargar(nombre: str) -> str:
        archivo = ruta_ejemplos / f"{nombre}.cobra"
        return archivo.read_text(encoding="utf-8")

    return _cargar
