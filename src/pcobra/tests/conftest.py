import sys
from pathlib import Path

import pytest

# Añade los directorios necesarios al ``PYTHONPATH`` para simplificar los imports
SRC_ROOT = Path(__file__).resolve().parents[2]
PCOBRA_PATH = SRC_ROOT / 'pcobra'

for path in (SRC_ROOT, PCOBRA_PATH):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Carga opcionalmente el paquete ``backend`` para mantener compatibilidad
try:  # nosec B001
    import backend  # noqa: F401
except Exception:
    pass


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
