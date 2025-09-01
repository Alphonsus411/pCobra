import json
import importlib.util
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
# ``ROOT`` apunta al directorio ``src`` dentro del repositorio. Construimos la
# ruta al módulo ``holobit`` de forma relativa a este directorio para evitar
# errores de carga por rutas inexistentes.
holobit_path = ROOT / "core" / "holobits" / "holobit.py"
spec = importlib.util.spec_from_file_location("holobit", holobit_path)
holobit_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = holobit_module
spec.loader.exec_module(holobit_module)
Holobit = holobit_module.Holobit


def test_holobit_len_and_indexing():
    datasets = [
        [],
        [1],
        [1, 2, 3],
        [0.1, -0.2, 3.5, 4.1, 5.0]
    ]
    for data in datasets:
        hb = Holobit(data)
        assert len(hb) == len(data)
        for i, value in enumerate(data):
            assert hb[i] == pytest.approx(float(value))
        assert json.loads(hb.to_json()) == [float(v) for v in data]
