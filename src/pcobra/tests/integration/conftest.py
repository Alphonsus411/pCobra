import csv
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_FILE = DATA_DIR / "transpiler_outputs.csv"


def _cargar_casos():
    casos = {}
    with CSV_FILE.open(newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            archivo = DATA_DIR / fila["archivo"]
            salida = fila["salida"].encode("utf-8").decode("unicode_escape")
            salida = salida.replace("\\n", "\n")
            casos.setdefault(archivo, {})[fila["lenguaje"]] = salida
    return list(casos.items())


@pytest.fixture(params=_cargar_casos())
def transpiler_case(request):
    """Devuelve (archivo, salidas_esperadas) por cada entrada del CSV."""
    return request.param
