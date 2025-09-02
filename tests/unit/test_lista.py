import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import standard_library.lista as lista


def test_lista():
    datos = [1, 2, 3]
    assert lista.cabeza(datos) == 1
    assert lista.cola(datos) == [2, 3]
    assert lista.longitud(datos) == 3
    assert lista.combinar([1], [2, 3]) == [1, 2, 3]

