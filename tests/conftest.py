from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest

# Añade los directorios necesarios al ``PYTHONPATH`` para simplificar los imports
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
PCOBRA_PATH = SRC_ROOT / "pcobra"

for path in (SRC_ROOT, PCOBRA_PATH):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Carga opcionalmente el paquete principal para mantener compatibilidad
try:  # nosec B001
    import pcobra  # noqa: F401
except Exception:
    pass


@pytest.fixture
def ruta_ejemplos() -> Path:
    """Devuelve el directorio donde se guardan los programas ``.cobra`` de prueba."""
    return Path(__file__).resolve().parent / "data"


@pytest.fixture
def cargar_programa(ruta_ejemplos: Path) -> Callable[[str], str]:
    """Carga el contenido de un programa ``.cobra`` por nombre."""

    def _cargar(nombre: str) -> str:
        archivo = ruta_ejemplos / f"{nombre}.cobra"
        return archivo.read_text(encoding="utf-8")

    return _cargar


@pytest.fixture
def codigo_imprimir() -> str:
    """Snippet Cobra que imprime el valor de una variable."""
    return "x = 1\nimprimir(x)"


@pytest.fixture
def codigo_bucle_simple() -> str:
    """Snippet Cobra con un bucle ``mientras`` que imprime valores."""
    return (
        "x = 0\n"
        "mientras x < 2:\n"
        "    imprimir(x)\n"
        "    x = x + 1\n"
        "fin"
    )
